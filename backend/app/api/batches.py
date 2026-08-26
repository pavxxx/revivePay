from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.db.models import BatchRun
from app.schemas.pydantic_schemas import BatchRunResponse
from app.services.batch_service import run_demo_batch

router = APIRouter(prefix="/batches", tags=["Batch Processing"])

@router.post("/run", response_model=BatchRunResponse)
def trigger_demo_batch(batch_size: int = Query(default=500, ge=10, le=1000), db: Session = Depends(get_db)):
    """
    Triggers a deterministic simulation demo batch run (default 500 events).
    Computes all batch performance metrics live from database state.
    """
    batch_run = run_demo_batch(db, batch_size=batch_size)
    return batch_run

@router.get("", response_model=List[BatchRunResponse])
def get_batches(limit: int = 20, db: Session = Depends(get_db)):
    batches = db.query(BatchRun).order_by(BatchRun.created_at.desc()).limit(limit).all()
    return batches

@router.get("/{batch_id}", response_model=BatchRunResponse)
def get_batch_detail(batch_id: str, db: Session = Depends(get_db)):
    batch = db.query(BatchRun).filter(
        (BatchRun.id == batch_id) | (BatchRun.batch_ref == batch_id)
    ).first()
    if not batch:
        raise HTTPException(status_code=404, detail="Batch run record not found")
    return batch
