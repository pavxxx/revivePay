from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.models import AuditEvent
from app.schemas.pydantic_schemas import AuditEventResponse

router = APIRouter(prefix="/audit", tags=["Audit Trail"])

@router.get("", response_model=List[AuditEventResponse])
def get_audit_trail(
    case_id: Optional[str] = None,
    event_type: Optional[str] = None,
    actor: Optional[str] = None,
    outcome: Optional[str] = None,
    search: Optional[str] = None,
    limit: int = 200,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(AuditEvent)
    if case_id:
        query = query.filter(AuditEvent.case_id == case_id)
    if event_type:
        query = query.filter(AuditEvent.event_type == event_type)
    if actor:
        query = query.filter(AuditEvent.actor == actor)
    if outcome:
        query = query.filter(AuditEvent.outcome == outcome)
    if search:
        query = query.filter(
            (AuditEvent.action.ilike(f"%{search}%")) |
            (AuditEvent.reason.ilike(f"%{search}%"))
        )
        
    events = query.order_by(AuditEvent.timestamp.desc()).offset(offset).limit(limit).all()
    return events

@router.get("/{case_id}", response_model=List[AuditEventResponse])
def get_case_audit_trail(case_id: str, db: Session = Depends(get_db)):
    events = db.query(AuditEvent).filter(
        AuditEvent.case_id == case_id
    ).order_by(AuditEvent.timestamp.asc()).all()
    return events
