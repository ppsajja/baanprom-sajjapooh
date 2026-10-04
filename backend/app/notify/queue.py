"""REQ-FN-012 คิวข้อความแจ้งเตือน API แค่วางลงคิว ไม่รอผลส่ง (IF-02)
ตอนนี้เป็นคิวในหน่วยความจำ (ทีมเลือกเอง) ระบบจริงเปลี่ยนเป็น Redis ได้โดยแก้ไฟล์นี้ไฟล์เดียว"""
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta

from app import config


@dataclass
class Message:
    to_role: str        # customer / technician
    to_id: int
    text: str
    job_id: int
    created_at: datetime
    due_at: datetime    # ต้องส่งก่อนเวลานี้ (REQ-FN-012: created_at + 60 วินาที)


class NotificationQueue:
    def __init__(self) -> None:
        self.items: list[Message] = []

    # รองรับ REQ-FN-012: ทุกข้อความมีกำหนดส่งภายใน NOTIFY_WITHIN_SECONDS
    def enqueue(self, to_role: str, to_id: int, text: str, job_id: int, now: datetime) -> Message:
        msg = Message(
            to_role=to_role, to_id=to_id, text=text, job_id=job_id,
            created_at=now, due_at=now + timedelta(seconds=config.NOTIFY_WITHIN_SECONDS),
        )
        self.items.append(msg)
        return msg

    def for_job(self, job_id: int) -> list[Message]:
        return [m for m in self.items if m.job_id == job_id]

    def as_dicts(self) -> list[dict]:
        return [asdict(m) for m in self.items]

    def clear(self) -> None:
        self.items.clear()


queue = NotificationQueue()
