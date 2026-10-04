"""REQ-BR-001 ยกเลิกงานและสร้างรายการคืนมัดจำตาม BR-01"""
from datetime import datetime

from app.db.models import Job, Refund, set_status, SLOT_FREE
from app.refund.rules import decide, Decision


class CancelRejected(Exception):
    def __init__(self, decision: Decision, message: str):
        self.decision, self.message = decision, message


def cancel_job(db, job: Job, cancelled_by: str, now: datetime) -> tuple[Decision, Refund | None]:
    d = decide(job.status, cancelled_by, job.scheduled_start, now, job.deposit_amount)
    if d.outcome == "pending_question":
        raise CancelRejected(d, "ยกเลิกขณะช่างกำลังเดินทางยังไม่เปิดให้ทำ กรุณาติดต่อ call center (รอ Q-14)")
    if d.outcome == "not_allowed":
        raise CancelRejected(d, "งานที่กำลังดำเนินงานหรือเสร็จสิ้นแล้วยกเลิกไม่ได้ กรุณาใช้กระบวนการร้องเรียน")
    set_status(db, job, d.outcome, now)
    if job.slot and job.slot.state != SLOT_FREE:
        job.slot.state, job.slot.held_by_customer_id, job.slot.hold_expires_at = SLOT_FREE, None, None
    refund = None
    if d.refund_amount:  # R5 คืน 0 = ไม่มีรายการคืน เพราะไม่เคยตัดเงิน
        refund = Refund(job_id=job.id, amount=d.refund_amount, rule=d.rule)
        db.add(refund)
    db.commit()
    return d, refund
