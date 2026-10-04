"""REQ-FN-008 ค้นช่างว่างใน 7 วัน | BR-02 ไม่เสนอช่วงที่จองหรือล็อกโดยคนอื่น | BR-03 ระยะไม่เกิน 15 กม."""
from datetime import datetime, timedelta
import math

from sqlalchemy import select

from app import config
from app.db.models import Technician, TimeSlot, ServiceAddress, SLOT_FREE, SLOT_HELD, SLOT_BOOKED


def distance_km(lat1, lng1, lat2, lng2) -> float:
    """ระยะทางโดยประมาณ (IF-03 ในระบบจริงเรียกบริการแผนที่ ตอนนี้ใช้สูตร haversine)"""
    r = 6371.0
    p1, p2 = math.radians(lat1), math.radians(lat2)
    dp, dl = math.radians(lat2 - lat1), math.radians(lng2 - lng1)
    a = math.sin(dp / 2) ** 2 + math.cos(p1) * math.cos(p2) * math.sin(dl / 2) ** 2
    return 2 * r * math.asin(math.sqrt(a))


def release_expired_holds(db, now: datetime) -> None:
    # รองรับ AS-07: ล็อกหมดอายุเองโดยไม่ต้องมีใครปลด ตรวจทุกครั้งที่อ่าน slot
    for slot in db.scalars(select(TimeSlot).where(TimeSlot.state == SLOT_HELD)):
        if slot.hold_expires_at and slot.hold_expires_at <= now:
            slot.state, slot.held_by_customer_id, slot.hold_expires_at = SLOT_FREE, None, None


def slot_visible_to(slot: TimeSlot, customer_id: int | None) -> bool:
    # รองรับ BR-02: ช่วงที่จองแล้วไม่ว่าง ช่วงที่คนอื่นล็อกไว้ก็ไม่ว่าง (ของตัวเองยังเห็น)
    if slot.state == SLOT_BOOKED:
        return False
    if slot.state == SLOT_HELD and slot.held_by_customer_id != customer_id:
        return False
    return True


def search_available(db, category: str, address: ServiceAddress, now: datetime,
                     customer_id: int | None = None) -> list[dict]:
    """คืนรายการช่างพร้อมช่วงเวลาที่ว่างใน SEARCH_DAYS_AHEAD วันถัดไป (AS-06 ไม่รวมวันนี้)"""
    release_expired_holds(db, now)
    day_start = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
    day_end = day_start + timedelta(days=config.SEARCH_DAYS_AHEAD)
    result = []
    for tech in db.scalars(select(Technician)):
        if category not in [s.strip() for s in tech.skills.split(",")]:
            continue
        # รองรับ BR-03: ช่างที่ไกลเกินระยะให้บริการไม่ปรากฏในผลค้นหา
        if distance_km(tech.base_lat, tech.base_lng, address.lat, address.lng) > config.MAX_SERVICE_DISTANCE_KM:
            continue
        slots = db.scalars(
            select(TimeSlot).where(TimeSlot.technician_id == tech.id,
                                   TimeSlot.start >= day_start, TimeSlot.start < day_end)
            .order_by(TimeSlot.start)
        ).all()
        free = [s for s in slots if slot_visible_to(s, customer_id)]
        if free:
            result.append({
                "technician_id": tech.id, "name": tech.name,
                "slots": [{"slot_id": s.id, "start": s.start.isoformat(), "end": s.end.isoformat()} for s in free],
            })
    return result


def find_alternatives(db, taken: TimeSlot, now: datetime, customer_id: int | None = None) -> list[dict]:
    """AC-07-04 (CR-01): ช่วงที่ว่าง ซึ่งเริ่มห่างจากช่วงที่เลือกไม่เกิน ALTERNATIVE_WINDOW_HOURS ชั่วโมง"""
    release_expired_holds(db, now)
    window = timedelta(hours=config.ALTERNATIVE_WINDOW_HOURS)
    slots = db.scalars(
        select(TimeSlot).where(TimeSlot.start >= taken.start - window, TimeSlot.start <= taken.start + window,
                               TimeSlot.id != taken.id).order_by(TimeSlot.start)
    ).all()
    return [
        {"slot_id": s.id, "technician_id": s.technician_id, "technician_name": s.technician.name,
         "start": s.start.isoformat(), "end": s.end.isoformat()}
        for s in slots if slot_visible_to(s, customer_id)
    ]
