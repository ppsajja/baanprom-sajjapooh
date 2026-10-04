"""REQ-FN-041 ล็อกช่วงเวลา | REQ-FN-008 สร้างงาน | UC-07 ขั้น 3, 5, 6 รวม E1, E2"""
from datetime import datetime, timedelta

from app import config
from app.db.models import (TimeSlot, Job, Customer, ServiceAddress, set_status,
                           SLOT_FREE, SLOT_HELD, SLOT_BOOKED)
from app.payments.gateway import Gateway
from app.payments.service import charge_deposit
from app.notify.queue import queue
from app.technicians.service import release_expired_holds, find_alternatives


class SlotTaken(Exception):
    """UC-07 E2 ช่วงเวลาถูกลูกค้าอื่นจองหรือล็อกไปก่อน"""
    def __init__(self, alternatives: list[dict]):
        self.alternatives = alternatives


class PaymentFailed(Exception):
    """UC-07 E1 ชำระไม่สำเร็จ หรือ gateway ไม่ตอบและสอบถามแล้วไม่สำเร็จ"""
    def __init__(self, job_id: int, reason: str):
        self.job_id, self.reason = job_id, reason


def hold_slot(db, slot: TimeSlot, customer_id: int, now: datetime) -> TimeSlot:
    # รองรับ REQ-FN-041: ล็อก HOLD_MINUTES นาที (Q-18) ถ้าคนอื่นล็อกอยู่ให้ปฏิเสธ
    release_expired_holds(db, now)
    if slot.state == SLOT_BOOKED or (slot.state == SLOT_HELD and slot.held_by_customer_id != customer_id):
        raise SlotTaken(find_alternatives(db, slot, now, customer_id))
    slot.state = SLOT_HELD
    slot.held_by_customer_id = customer_id
    slot.hold_expires_at = now + timedelta(minutes=config.HOLD_MINUTES)
    db.commit()
    return slot


def deposit_for(category: str) -> int:
    """ยอดมัดจำ ปัดขึ้นหลักสิบ (REQ-BR-002 Computation) ตัวเลขตั้งต้นต่อประเภทงานมาจาก data dictionary"""
    base = {"ประปา": 350, "ไฟฟ้า": 400, "แอร์": 500}.get(category, 300)
    return -(-base // 10) * 10


def create_booking(db, customer: Customer, slot: TimeSlot, address: ServiceAddress,
                   category: str, gateway: Gateway, now: datetime) -> Job:
    """UC-07 ขั้น 5 ถึง 6: ตรวจล็อก สร้างงาน รอชำระเงิน ตัดมัดจำ แล้วยืนยันหรือยกเลิกอัตโนมัติ"""
    release_expired_holds(db, now)
    # รองรับ AC-07-04 (E2): ถ้า slot ไม่ได้ล็อกโดยลูกค้าคนนี้ ไม่ตัดเงิน และเสนอช่วงใกล้เคียง
    if slot.state == SLOT_BOOKED or (slot.state == SLOT_HELD and slot.held_by_customer_id != customer.id):
        raise SlotTaken(find_alternatives(db, slot, now, customer.id))
    if slot.state == SLOT_FREE:
        hold_slot(db, slot, customer.id, now)  # กดยืนยันโดยไม่ได้ล็อกก่อน ให้ล็อกให้ทันที

    job = Job(customer_id=customer.id, technician_id=slot.technician_id, slot_id=slot.id,
              address_id=address.id, category=category, status="pending_payment",
              deposit_amount=deposit_for(category), scheduled_start=slot.start, created_at=now)
    db.add(job)
    db.flush()
    set_status(db, job, "pending_payment", now)

    payment = charge_deposit(db, job, gateway, now)  # REQ-IF-001, REQ-IF-005
    if payment.result == "success":
        # รองรับ REQ-FN-008 ขั้น 6: งานยืนยันแล้ว ช่วงเวลาจองแล้ว
        set_status(db, job, "confirmed", now)
        slot.state, slot.held_by_customer_id, slot.hold_expires_at = SLOT_BOOKED, None, None
        # รองรับ REQ-FN-012: วางข้อความถึงสองฝ่ายลงคิว ไม่รอผลส่ง
        queue.enqueue("customer", customer.id, f"จองสำเร็จ งาน #{job.id} {slot.start:%d/%m %H:%M}", job.id, now)
        queue.enqueue("technician", slot.technician_id, f"มีงานใหม่ #{job.id} {slot.start:%d/%m %H:%M}", job.id, now)
        db.commit()
        return job

    # UC-07 E1 / BR-01 R5: ยกเลิกอัตโนมัติ ไม่มีการตัดเงิน ช่วงเวลากลับว่าง แจ้งลูกค้า
    set_status(db, job, "auto_cancelled", now)
    slot.state, slot.held_by_customer_id, slot.hold_expires_at = SLOT_FREE, None, None
    queue.enqueue("customer", customer.id, f"ชำระมัดจำไม่สำเร็จ งาน #{job.id} ถูกยกเลิก", job.id, now)
    db.commit()
    raise PaymentFailed(job.id, payment.result)


def technician_view(job: Job, now: datetime) -> dict:
    """REQ-SEC-004: มุมมองช่าง ใส่ customer_phone เฉพาะช่วง 2 ชั่วโมงก่อนนัดจนปิดงาน"""
    reveal_from = job.scheduled_start - timedelta(hours=config.PHONE_REVEAL_HOURS)
    data = {"job_id": job.id, "status": job.status, "category": job.category,
            "scheduled_start": job.scheduled_start.isoformat(), "customer_name": job.customer.name}
    if reveal_from <= now and job.status not in ("done", "cancelled", "auto_cancelled"):
        data["customer_phone"] = job.customer.phone
    return data
