from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional

from app.db.database import get_db
from app.db.models import Payment, Customer, Subscription
from app.schemas.pydantic_schemas import PaymentResponse, CustomerResponse, SubscriptionResponse

router = APIRouter(prefix="/payments", tags=["Payments"])

@router.get("", response_model=List[PaymentResponse])
def get_payments(
    status: Optional[str] = None,
    failure_category: Optional[str] = None,
    limit: int = 100,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    query = db.query(Payment)
    if status:
        query = query.filter(Payment.status == status)
    if failure_category:
        query = query.filter(Payment.failure_category == failure_category)
        
    payments = query.order_by(Payment.created_at.desc()).offset(offset).limit(limit).all()
    return payments

@router.get("/{payment_id}", response_model=PaymentResponse)
def get_payment_detail(payment_id: str, db: Session = Depends(get_db)):
    pay = db.query(Payment).filter(
        (Payment.id == payment_id) | (Payment.payment_ref == payment_id)
    ).first()
    if not pay:
        raise HTTPException(status_code=404, detail="Payment record not found")
    return pay
