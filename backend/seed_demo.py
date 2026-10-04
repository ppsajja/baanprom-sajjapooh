"""ใส่ข้อมูลสมมติสำหรับเปิดดูหน้าจอ (ไม่ใช่ส่วนของระบบ) รัน: python seed_demo.py"""
from datetime import datetime, timedelta

from app.db.session import engine, SessionLocal
from app.db.migrations.m001_init import upgrade
from app.db.models import Customer, ServiceAddress, Technician, TimeSlot

upgrade(engine)
db = SessionLocal()
if not db.get(Customer, 1):
    c = Customer(name="สมชาย", phone="081-234-5678"); db.add(c); db.flush()
    db.add(ServiceAddress(customer_id=c.id, text="บ้านเลขที่ 12 ซอยสุขใจ", lat=13.74, lng=100.53))
    t = Technician(name="ประสิทธิ์", skills="ประปา,ไฟฟ้า", base_lat=13.705, base_lng=100.53); db.add(t); db.flush()
    base = (datetime.now() + timedelta(days=1)).replace(hour=9, minute=0, second=0, microsecond=0)
    for d in range(3):
        for h in (0, 2, 5):
            s = base + timedelta(days=d, hours=h)
            db.add(TimeSlot(technician_id=t.id, start=s, end=s + timedelta(hours=2)))
    db.commit()
    print("seeded")
else:
    print("already seeded")
