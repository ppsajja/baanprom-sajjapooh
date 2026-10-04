"""AC-07-10 Scenario Outline จาก booking.feature (T-06) ทีละแถวของ BR-01
R3 ข้าม (รอ Q-14) ตาม D-07-04 แต่ยังตรวจพฤติกรรมชั่วคราวว่าปฏิเสธจริง"""
from datetime import timedelta

import pytest

from app.db.models import Job, set_status
from tests.conftest import NOW, book


def make_confirmed_job(client, db, seed):
    res = book(client, customer_id=seed["somchai"].id, slot_id=seed["slot"].id, address_id=seed["addr"].id)
    assert res.status_code == 201
    job = db.get(Job, res.json()["job_id"]); db.refresh(job)
    return job


def cancel(client, job_id, by, now):
    return client.post(f"/jobs/{job_id}/cancel?now={now.isoformat()}", json={"cancelled_by": by})


# รองรับ AC-07-10 (REQ-BR-001, BR-01)
@pytest.mark.parametrize("row,status,hours_before,by,expect_status,expect_refund", [
    ("R1", "confirmed", 48, "customer", "cancelled", 350),
    ("R2", "confirmed", 5, "customer", "cancelled", 180),
    ("R4", "rematching", 20, "system", "cancelled", 350),
    ("R5", "pending_payment", 30, "system", "auto_cancelled", 0),
])
def test_AC_07_10_refund(client, db, seed, row, status, hours_before, by, expect_status, expect_refund):
    # Given งานมัดจำ 350 บาท สถานะ <สถานะ> และเวลานัดอีก <ชั่วโมงก่อนนัด> ชั่วโมง
    job = make_confirmed_job(client, db, seed)
    assert job.deposit_amount == 350
    set_status(db, job, status, NOW); db.commit()
    now = job.scheduled_start - timedelta(hours=hours_before)
    # When <ผู้ยกเลิก> ยกเลิกงาน
    r = cancel(client, job.id, by, now)
    # Then ผลคือ <ผล> และยอดคืน <ยอดคืน> บาท ตามแถว <แถว>
    assert r.status_code == 200, r.text
    assert r.json()["rule"] == row
    assert r.json()["status"] == expect_status
    assert r.json()["refund_amount"] == expect_refund


# รองรับ AC-07-10 แถว R6: ยกเลิกไม่ได้
def test_AC_07_10_refund_R6_not_allowed(client, db, seed):
    job = make_confirmed_job(client, db, seed)
    set_status(db, job, "in_progress", NOW); db.commit()
    r = cancel(client, job.id, "customer", job.scheduled_start)
    assert r.status_code == 409 and r.json()["rule"] == "R6"
    db.refresh(job); assert job.status == "in_progress"


# รองรับ AC-07-10 แถว R3: รอ Q-14 ยังตัดสินยอดคืนไม่ได้ จึงข้าม แต่พฤติกรรมชั่วคราวต้องปฏิเสธ
@pytest.mark.skip(reason="รอ Q-14 (BR-01 R3) เจ้าของยังไม่ตอบว่าคืนเท่าไร ดู spec ข้อ 9 และ D-07-04")
def test_AC_07_10_refund_R3():
    pass


def test_AC_07_10_refund_R3_temporary_behaviour(client, db, seed):
    job = make_confirmed_job(client, db, seed)
    set_status(db, job, "en_route", NOW); db.commit()
    r = cancel(client, job.id, "customer", job.scheduled_start - timedelta(hours=1))
    assert r.status_code == 409 and r.json()["rule"] == "R3" and "call center" in r.json()["message"]
