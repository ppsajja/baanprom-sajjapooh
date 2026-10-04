"""AC-07-05, AC-07-06, AC-07-07 จาก booking.feature (T-05) ใช้ FakeGateway สั่งพฤติกรรม gateway"""
from sqlalchemy import select

from app.db.models import Job, Payment
from app.notify.queue import queue
from tests.conftest import book


# รองรับ AC-07-05 (REQ-IF-001, REQ-IF-005, UC-07 E1)
def test_AC_07_05_payment_timeout(client, db, seed, gateway):
    # Given Payment Gateway ไม่ตอบคำขอ authorize ภายใน 30 วินาที (Q-19 ชั่วคราว)
    gateway.mode, gateway.inquiry_answer = "timeout", "unknown"
    # When ระบบสอบถามสถานะด้วย reference เดิม และได้คำตอบ unknown
    res = book(client, customer_id=seed["somchai"].id, slot_id=seed["slot"].id, address_id=seed["addr"].id)
    assert res.status_code == 402 and res.json()["reason"] == "payment_failed"
    job = db.get(Job, res.json()["job_id"]); db.refresh(job)
    # Then งานมีสถานะ ยกเลิกอัตโนมัติ
    assert job.status == "auto_cancelled"
    # And ช่วงเวลากลับเป็น ว่าง
    db.refresh(seed["slot"]); assert seed["slot"].state == "free"
    # And ไม่มีรายการชำระที่สถานะ สำเร็จ
    assert db.scalar(select(Payment).where(Payment.job_id == job.id, Payment.result == "success")) is None
    # inquiry ต้องใช้ ref เดิมกับ authorize
    refs = {c.split(":")[1] for c in gateway.calls if c.startswith(("authorize", "inquiry"))}
    assert len(refs) == 1
    # And ระบบรอ gateway ไม่เกิน 30 วินาที ตาม spec ข้อ 9 (Q-19 ค่าชั่วคราว) GAP-07: รอบแรก AI ตั้ง 60 ตาม IF-01
    assert gateway.last_timeout_seconds == 30


# รองรับ AC-07-06 (REQ-IF-001, UC-07 E1)
def test_AC_07_06_payment_declined(client, db, seed, gateway):
    # When Payment Gateway ตอบ declined
    gateway.mode = "declined"
    res = book(client, customer_id=seed["somchai"].id, slot_id=seed["slot"].id, address_id=seed["addr"].id)
    # Then งานมีสถานะ ยกเลิกอัตโนมัติ
    assert res.status_code == 402
    job = db.get(Job, res.json()["job_id"]); db.refresh(job)
    assert job.status == "auto_cancelled"
    # And ช่วงเวลากลับเป็น ว่าง
    db.refresh(seed["slot"]); assert seed["slot"].state == "free"
    # And ระบบแจ้งลูกค้าว่าชำระไม่สำเร็จ
    msgs = queue.for_job(job.id)
    assert any(m.to_role == "customer" and "ไม่สำเร็จ" in m.text for m in msgs)
    assert not any(c.startswith("capture") for c in gateway.calls)


# รองรับ AC-07-07 (REQ-IF-005)
def test_AC_07_07_inquiry_approved_no_double_charge(client, db, seed, gateway):
    # Given gateway ไม่ตอบ authorize แต่รายการนั้น approved ไปแล้วฝั่ง gateway
    gateway.mode, gateway.inquiry_answer = "timeout", "approved"
    # When ระบบสอบถามสถานะด้วย reference เดิม
    res = book(client, customer_id=seed["somchai"].id, slot_id=seed["slot"].id, address_id=seed["addr"].id)
    # Then งานมีสถานะ ยืนยันแล้ว
    assert res.status_code == 201
    job = db.get(Job, res.json()["job_id"]); db.refresh(job)
    assert job.status == "confirmed"
    # And มีรายการชำระที่สถานะ สำเร็จ 1 รายการเท่านั้น
    assert len(db.scalars(select(Payment).where(Payment.job_id == job.id, Payment.result == "success")).all()) == 1
    # And ไม่มีการส่งคำขอ authorize ครั้งที่สอง
    assert sum(1 for c in gateway.calls if c.startswith("authorize")) == 1
