"""POST /slots/{id}/hold, POST /bookings, GET /jobs/{id}, GET /jobs/{id}/technician-view (plan.md ข้อ 4)"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import TimeSlot, Customer, ServiceAddress, Job
from app.booking import service
from app.payments.gateway import get_gateway
from app.clock import get_now
from app.privacy import get_logger

router = APIRouter()
log = get_logger(__name__)


class HoldIn(BaseModel):
    customer_id: int


class BookingIn(BaseModel):
    customer_id: int
    slot_id: int
    address_id: int
    category: str


def job_out(job: Job) -> dict:
    return {"job_id": job.id, "status": job.status, "technician_id": job.technician_id,
            "slot_id": job.slot_id, "deposit_amount": job.deposit_amount,
            "scheduled_start": job.scheduled_start.isoformat()}


@router.post("/slots/{slot_id}/hold")
def hold(slot_id: int, body: HoldIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-FN-041
    slot = db.get(TimeSlot, slot_id)
    if not slot:
        raise HTTPException(404, "ไม่พบช่วงเวลา")
    try:
        slot = service.hold_slot(db, slot, body.customer_id, now)
    except service.SlotTaken as e:
        return JSONResponse({"reason": "slot_taken", "alternatives": e.alternatives}, status_code=409)
    return {"slot_id": slot.id, "hold_expires_at": slot.hold_expires_at.isoformat()}


@router.post("/bookings", status_code=201)
def create(body: BookingIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-FN-008, REQ-IF-001, REQ-IF-005
    customer, slot, address = db.get(Customer, body.customer_id), db.get(TimeSlot, body.slot_id), db.get(ServiceAddress, body.address_id)
    if not (customer and slot and address):
        raise HTTPException(404, "ไม่พบลูกค้า ช่วงเวลา หรือที่อยู่")
    try:
        job = service.create_booking(db, customer, slot, address, body.category, get_gateway(), now)
    except service.SlotTaken as e:
        return JSONResponse({"reason": "slot_taken", "alternatives": e.alternatives}, status_code=409)
    except service.PaymentFailed as e:
        return JSONResponse({"reason": "payment_failed", "detail": e.reason, "job_id": e.job_id}, status_code=402)
    log.info("booking created job=%s customer=%s", job.id, customer.id)  # ไม่มีเบอร์โทร (REQ-PRV-002)
    return job_out(job)


@router.get("/jobs/{job_id}")
def get_job(job_id: int, db: Session = Depends(get_db)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "ไม่พบงาน")
    return job_out(job)


@router.get("/jobs/{job_id}/technician-view")
def technician_view(job_id: int, technician_id: int, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    # รองรับ REQ-SEC-004
    job = db.get(Job, job_id)
    if not job or job.technician_id != technician_id:
        raise HTTPException(404, "ไม่พบงานของช่างคนนี้")
    data = service.technician_view(job, now)
    log.info("technician %s viewed job %s: %s", technician_id, job_id, data)
    return data
