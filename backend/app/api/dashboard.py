from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any
from datetime import datetime, timedelta, timezone

from app.db.database import get_db
from app.db.models import RecoveryCase, RecoveryAttempt, AuditEvent
from app.schemas.pydantic_schemas import DashboardSummaryResponse, RecoveryTrendPoint

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])

@router.get("/summary", response_model=DashboardSummaryResponse)
def get_dashboard_summary(db: Session = Depends(get_db)):
    """
    Computes real-time dashboard KPI summary entirely from database records.
    """
    cases = db.query(RecoveryCase).all()
    total_cases = len(cases)
    
    rev_at_risk = sum(c.amount_at_risk for c in cases if c.status != "RECOVERED")
    rev_recovered = sum(c.recovered_amount for c in cases if c.status == "RECOVERED")
    
    total_at_risk_pool = sum(c.amount_at_risk for c in cases)
    recovery_rate = round((rev_recovered / max(1.0, total_at_risk_pool)) * 100.0, 2)
    
    active_cases = [c for c in cases if c.status in ["DETECTED", "ANALYZING", "IN_PROGRESS"]]
    recovered_cases = [c for c in cases if c.status == "RECOVERED"]
    escalated_cases = [c for c in cases if c.status == "ESCALATED"]
    stopped_cases = [c for c in cases if c.status == "STOPPED"]
    failed_cases = [c for c in cases if c.status == "FAILED"]
    
    attempts = db.query(RecoveryAttempt).all()
    total_attempts = len(attempts)
    successful_attempts = sum(1 for a in attempts if a.status == "SUCCESS")
    attempt_success_rate = round((successful_attempts / max(1, total_attempts)) * 100.0, 2)
    
    return DashboardSummaryResponse(
        revenue_at_risk=round(rev_at_risk, 2),
        revenue_recovered=round(rev_recovered, 2),
        recovery_rate=recovery_rate,
        active_cases_count=len(active_cases),
        total_cases_count=total_cases,
        recovered_cases_count=len(recovered_cases),
        escalated_cases_count=len(escalated_cases),
        stopped_cases_count=len(stopped_cases),
        failed_cases_count=len(failed_cases),
        total_attempts_count=total_attempts,
        successful_attempts_count=successful_attempts,
        attempt_success_rate=attempt_success_rate
    )

@router.get("/recovery-trends", response_model=List[RecoveryTrendPoint])
def get_recovery_trends(days: int = 30, db: Session = Depends(get_db)):
    """
    Computes daily revenue at risk vs recovered trends over past N days from DB audit/case timestamps.
    """
    now = datetime.now(timezone.utc)
    start_date = now - timedelta(days=days)
    
    cases = db.query(RecoveryCase).filter(RecoveryCase.created_at >= start_date).all()
    
    # Group by date YYYY-MM-DD
    daily_map = {}
    for i in range(days + 1):
        d_str = (start_date + timedelta(days=i)).strftime("%Y-%m-%d")
        daily_map[d_str] = {"at_risk": 0.0, "recovered": 0.0}
        
    for c in cases:
        d_str = c.created_at.strftime("%Y-%m-%d")
        if d_str in daily_map:
            daily_map[d_str]["at_risk"] += c.amount_at_risk
            daily_map[d_str]["recovered"] += c.recovered_amount
            
    points = [
        RecoveryTrendPoint(
            date=d,
            at_risk=round(vals["at_risk"], 2),
            recovered=round(vals["recovered"], 2)
        )
        for d, vals in sorted(daily_map.items())
    ]
    return points
