from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from typing import List, Dict, Any

from app.db.database import get_db
from app.db.models import RecoveryCase, Payment
from app.schemas.pydantic_schemas import FailureDistributionPoint

router = APIRouter(prefix="/analytics", tags=["Analytics"])

@router.get("/failures", response_model=List[FailureDistributionPoint])
def get_failure_distribution(db: Session = Depends(get_db)):
    """
    Returns distribution of payment failures grouped by category, total amount at risk, and calculated recovery rate.
    """
    cases = db.query(RecoveryCase).all()
    
    cat_map = {}
    for c in cases:
        cat = c.failure_category or "UNKNOWN"
        if cat not in cat_map:
            cat_map[cat] = {"count": 0, "amount": 0.0, "recovered": 0.0}
            
        cat_map[cat]["count"] += 1
        cat_map[cat]["amount"] += c.amount_at_risk
        if c.status == "RECOVERED":
            cat_map[cat]["recovered"] += c.recovered_amount

    points = []
    for cat, vals in cat_map.items():
        rec_rate = round((vals["recovered"] / max(1.0, vals["amount"])) * 100.0, 2)
        points.append(FailureDistributionPoint(
            category=cat,
            count=vals["count"],
            amount=round(vals["amount"], 2),
            recovery_rate=rec_rate
        ))
        
    return sorted(points, key=lambda x: x.amount, reverse=True)

@router.get("/recovery")
def get_recovery_analytics(db: Session = Depends(get_db)) -> Dict[str, Any]:
    """
    Returns breakdown of recovery success rate by probability buckets (<0.40, 0.40-0.60, 0.60-0.80, 0.80-1.00).
    """
    cases = db.query(RecoveryCase).all()
    
    buckets = {
        "0.00-0.40 (Low)": {"total": 0, "recovered": 0, "amount_at_risk": 0.0, "amount_recovered": 0.0},
        "0.40-0.60 (Medium)": {"total": 0, "recovered": 0, "amount_at_risk": 0.0, "amount_recovered": 0.0},
        "0.60-0.80 (High)": {"total": 0, "recovered": 0, "amount_at_risk": 0.0, "amount_recovered": 0.0},
        "0.80-1.00 (Very High)": {"total": 0, "recovered": 0, "amount_at_risk": 0.0, "amount_recovered": 0.0},
    }
    
    for c in cases:
        p = c.recovery_probability
        if p < 0.40:
            b_key = "0.00-0.40 (Low)"
        elif p < 0.60:
            b_key = "0.40-0.60 (Medium)"
        elif p < 0.80:
            b_key = "0.60-0.80 (High)"
        else:
            b_key = "0.80-1.00 (Very High)"
            
        buckets[b_key]["total"] += 1
        buckets[b_key]["amount_at_risk"] += c.amount_at_risk
        if c.status == "RECOVERED":
            buckets[b_key]["recovered"] += 1
            buckets[b_key]["amount_recovered"] += c.recovered_amount

    result = []
    for b_name, data in buckets.items():
        rec_rate = round((data["recovered"] / max(1, data["total"])) * 100.0, 2)
        rev_rate = round((data["amount_recovered"] / max(1.0, data["amount_at_risk"])) * 100.0, 2)
        result.append({
            "bucket": b_name,
            "total_cases": data["total"],
            "recovered_cases": data["recovered"],
            "case_recovery_rate": rec_rate,
            "amount_at_risk": round(data["amount_at_risk"], 2),
            "amount_recovered": round(data["amount_recovered"], 2),
            "revenue_recovery_rate": rev_rate
        })
        
    return {"probability_buckets": result}
