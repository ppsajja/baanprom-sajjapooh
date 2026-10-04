"""เวลาปัจจุบันของระบบ ให้ test กำหนดเวลาได้ (เช่น AC-07-09 เปิดดูงานเวลา 11:30 และ 12:00)
ผู้เรียก API ส่ง now=... (ISO 8601) มาได้เฉพาะตอนทดสอบ ระบบจริงไม่รับค่านี้"""
from datetime import datetime

from fastapi import Query


def get_now(now: datetime | None = Query(default=None, include_in_schema=False)) -> datetime:
    return now or datetime.now()
