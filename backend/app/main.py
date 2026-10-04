"""FastAPI app ของบ้านพร้อม R1 feature UC-07 (specs/002-booking)"""
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.db.session import engine
from app.db.migrations.m001_init import upgrade
from app.technicians.router import router as technicians_router
from app.booking.router import router as booking_router
from app.refund.router import router as refund_router
from app.notify.queue import queue

@asynccontextmanager
async def lifespan(app: FastAPI):
    upgrade(engine)  # T-01 สร้างตารางถ้ายังไม่มี
    yield


app = FastAPI(title="บ้านพร้อม R1 - UC-07 จองงานบริการซ่อมบำรุง", lifespan=lifespan)
app.include_router(technicians_router)
app.include_router(booking_router)
app.include_router(refund_router)


@app.get("/notifications/queue")
def notifications():
    # รองรับ REQ-FN-012 ใช้ตรวจใน test และหน้าแอดมิน
    return queue.as_dicts()


@app.get("/health")
def health():
    return {"ok": True}
