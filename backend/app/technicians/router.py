"""GET /technicians (plan.md ข้อ 4) รองรับ REQ-FN-008"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import ServiceAddress
from app.technicians import service
from app.clock import get_now

router = APIRouter()


@router.get("/technicians")
def list_available(category: str, address_id: int, customer_id: int | None = None,
                   db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    address = db.get(ServiceAddress, address_id)
    if not address:
        raise HTTPException(404, "ไม่พบที่อยู่ให้บริการ")
    return service.search_available(db, category, address, now, customer_id)
