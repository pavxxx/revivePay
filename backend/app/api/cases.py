from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.models import RecoveryCase
from app.schemas.pydantic_schemas import RecoveryCaseResponse
from app.agent.workflow import AgentWorkflowEngine

router = APIRouter(prefix="/cases", tags=["Recovery Cases"])

@router.get("", response_model=List[RecoveryCaseResponse])
def get_cases(
    status: Optional[str] = None,
    failure_category: Optional[str] = None,
    is_escalated: Optional[bool] = None,
    min_amount: Optional[float] = None,
    search: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(RecoveryCase)
    
    if status:
        query = query.filter(RecoveryCase.status == status)
    if failure_category:
        query = query.filter(RecoveryCase.failure_category == failure_category)
    if is_escalated is not None:
        query = query.filter(RecoveryCase.is_escalated == is_escalated)
    if min_amount is not None:
        query = query.filter(RecoveryCase.amount_at_risk >= min_amount)
    if search:
        query = query.filter(
            (RecoveryCase.case_ref.ilike(f"%{search}%")) |
            (RecoveryCase.failure_category.ilike(f"%{search}%"))
        )
        
    cases = query.order_by(RecoveryCase.updated_at.desc()).offset(offset).limit(limit).all()
    return cases

@router.get("/{case_id}", response_model=RecoveryCaseResponse)
def get_case_detail(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(
        (RecoveryCase.id == case_id) | (RecoveryCase.case_ref == case_id)
    ).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery Case not found")
    return case

@router.post("/{case_id}/process", response_model=RecoveryCaseResponse)
def process_case(case_id: str, db: Session = Depends(get_db)):
    case = db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
    if not case:
        raise HTTPException(status_code=404, detail="Recovery Case not found")
        
    workflow = AgentWorkflowEngine(db)
    updated_case = workflow.process_failed_payment_event(case.payment_id)
    return updated_case

@router.post("/{case_id}/approve", response_model=RecoveryCaseResponse)
def approve_case_action(case_id: str, note: Optional[str] = None, db: Session = Depends(get_db)):
    workflow = AgentWorkflowEngine(db)
    try:
        case = workflow.manual_human_action(case_id, action="APPROVE", note=note)
        return case
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{case_id}/escalate", response_model=RecoveryCaseResponse)
def escalate_case_action(case_id: str, note: Optional[str] = None, db: Session = Depends(get_db)):
    workflow = AgentWorkflowEngine(db)
    try:
        case = workflow.manual_human_action(case_id, action="ESCALATE", note=note)
        return case
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.post("/{case_id}/stop", response_model=RecoveryCaseResponse)
def stop_case_action(case_id: str, note: Optional[str] = None, db: Session = Depends(get_db)):
    workflow = AgentWorkflowEngine(db)
    try:
        case = workflow.manual_human_action(case_id, action="STOP", note=note)
        return case
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
