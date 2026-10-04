"""BR-01 นโยบายคืนมัดจำ (rules.md) ตารางเดียวทั้งระบบ ห้ามมีตัวเลขเหล่านี้ที่อื่น"""
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Decision:
    rule: str            # R1..R6
    outcome: str         # cancelled / auto_cancelled / not_allowed / pending_question
    refund_amount: int | None


def round_up_tens(amount: float) -> int:
    """ปัดขึ้นหลักสิบ (rules.md ตัวอย่าง 175 -> 180)"""
    return -(-int(amount + 0.999999) // 10) * 10 if amount != int(amount) else -(-int(amount) // 10) * 10


def decide(status: str, cancelled_by: str, scheduled_start: datetime, now: datetime, deposit: int) -> Decision:
    hours_before = (scheduled_start - now).total_seconds() / 3600
    # อ่านจากบนลงล่าง แถวแรกที่ตรงคือแถวที่ใช้ (rules.md)
    if status == "confirmed" and cancelled_by == "customer" and hours_before >= 24:
        return Decision("R1", "cancelled", deposit)
    if status == "confirmed" and cancelled_by == "customer":
        return Decision("R2", "cancelled", round_up_tens(deposit / 2))
    if status == "en_route" and cancelled_by == "customer":
        # Q-14 ยังไม่ตอบ พฤติกรรมชั่วคราวตาม spec ข้อ 9: ไม่อนุญาตให้ยกเลิก
        return Decision("R3", "pending_question", None)
    if status == "rematching":
        return Decision("R4", "cancelled", deposit)
    if status == "pending_payment":
        return Decision("R5", "auto_cancelled", 0)
    if status in ("in_progress", "done"):
        return Decision("R6", "not_allowed", None)
    return Decision("R6", "not_allowed", None)
