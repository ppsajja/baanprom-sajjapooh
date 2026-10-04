"""REQ-IF-001 authorize แล้ว capture | REQ-IF-005 timeout แล้ว status-inquiry ด้วย ref เดิม (MD-SEQ-07-05)"""
from datetime import datetime
import uuid

from app import config
from app.db.models import Payment, Job
from app.payments.gateway import Gateway, GatewayTimeout
from app.privacy import get_logger

log = get_logger(__name__)


def charge_deposit(db, job: Job, gateway: Gateway, now: datetime) -> Payment:
    """คืน Payment ที่ result เป็น success / failed / timeout
    กติกา: authorize เรียกได้ครั้งเดียวต่อ ref (REQ-IF-005 ห้ามตัดเงินซ้ำ)"""
    ref = f"BP-{job.id}-{uuid.uuid4().hex[:8]}"
    try:
        # รอได้ไม่เกิน GATEWAY_TIMEOUT_SECONDS (Q-19 ค่าชั่วคราว 30 วินาที ตาม spec ข้อ 9)
        result = gateway.authorize(ref, job.deposit_amount, timeout_seconds=config.GATEWAY_TIMEOUT_SECONDS)
    except GatewayTimeout:
        # รองรับ REQ-IF-005: ไม่ตอบใน gateway-timeout ให้ถามสถานะด้วย ref เดิม ไม่ authorize ซ้ำ
        log.info("gateway timeout job=%s ref=%s -> status-inquiry", job.id, ref)
        result = gateway.status_inquiry(ref)

    if result.status == "approved":
        gateway.capture(ref)  # D-07-03 capture หลัง approved เท่านั้น
        payment = Payment(job_id=job.id, amount=job.deposit_amount, gateway_ref=ref,
                          result="success", authorized_at=now)
    elif result.status == "declined":
        payment = Payment(job_id=job.id, amount=job.deposit_amount, gateway_ref=ref,
                          result="failed", authorized_at=now)
    else:
        # unknown หลัง inquiry: ถือว่าไม่สำเร็จ และ void กันวงเงินที่อาจค้าง (BR-01 R5 ต้องไม่มีการตัดเงิน)
        gateway.void(ref)
        payment = Payment(job_id=job.id, amount=job.deposit_amount, gateway_ref=ref,
                          result="timeout", authorized_at=now)
    db.add(payment)
    return payment
