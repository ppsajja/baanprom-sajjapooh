"""POST /jobs/{id}/cancel (plan.md ข้อ 4) รองรับ REQ-BR-001"""
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Job
from app.refund import service
from app.clock import get_now

router = APIRouter()


class CancelIn(BaseModel):
    cancelled_by: str  # customer / system


@router.post("/jobs/{job_id}/cancel")
def cancel(job_id: int, body: CancelIn, db: Session = Depends(get_db), now: datetime = Depends(get_now)):
    job = db.get(Job, job_id)
    if not job:
        raise HTTPException(404, "ไม่พบงาน")
    try:
        d, refund = service.cancel_job(db, job, body.cancelled_by, now)
    except service.CancelRejected as e:
        return JSONResponse({"rule": e.decision.rule, "outcome": e.decision.outcome, "message": e.message}, status_code=409)
    return {"job_id": job.id, "status": job.status, "rule": d.rule,
            "refund_amount": refund.amount if refund else 0}
