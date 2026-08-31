import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Float, Integer, Boolean, DateTime, ForeignKey, Text, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

def generate_uuid():
    return str(uuid.uuid4())

def utc_now():
    return datetime.now(timezone.utc)

class User(Base):
    __tablename__ = "users"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    role = Column(String, default="ops_admin")
    created_at = Column(DateTime(timezone=True), default=utc_now)

class Customer(Base):
    __tablename__ = "customers"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    customer_ref = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    tenure_days = Column(Integer, default=30)
    historical_success_rate = Column(Float, default=0.85)
    avg_txn_amount = Column(Float, default=1500.0)
    total_payments = Column(Integer, default=10)
    successful_payments = Column(Integer, default=8)
    failed_payments = Column(Integer, default=2)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    payments = relationship("Payment", back_populates="customer")
    subscriptions = relationship("Subscription", back_populates="customer")
    recovery_cases = relationship("RecoveryCase", back_populates="customer")

class Subscription(Base):
    __tablename__ = "subscriptions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    subscription_ref = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    plan_name = Column(String, nullable=False)
    amount = Column(Float, nullable=False)
    interval = Column(String, default="monthly")
    status = Column(String, default="ACTIVE") # ACTIVE, PAST_DUE, CANCELLED
    next_billing_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    customer = relationship("Customer", back_populates="subscriptions")
    payments = relationship("Payment", back_populates="subscription")

class Payment(Base):
    __tablename__ = "payments"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    payment_ref = Column(String, unique=True, index=True, nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    subscription_id = Column(String, ForeignKey("subscriptions.id"), nullable=True)
    amount = Column(Float, nullable=False)
    currency = Column(String, default="INR")
    status = Column(String, default="FAILED") # FAILED, SUCCESS, PENDING
    failure_reason = Column(String, nullable=True)
    failure_category = Column(String, nullable=False, default="TRANSIENT_NETWORK")
    # Categories: TRANSIENT_NETWORK, INSUFFICIENT_FUNDS, CARD_EXPIRED, AUTHENTICATION_REQUIRED, PERMANENT_HARD_DECLINE, FRAUD_OR_STOLEN
    payment_method = Column(String, default="CARD") # CARD, UPI, NETBANKING, AUTOPAY
    razorpay_id = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    customer = relationship("Customer", back_populates="payments")
    subscription = relationship("Subscription", back_populates="payments")
    recovery_cases = relationship("RecoveryCase", back_populates="payment")

class RecoveryCase(Base):
    __tablename__ = "recovery_cases"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    case_ref = Column(String, unique=True, index=True, nullable=False)
    payment_id = Column(String, ForeignKey("payments.id"), nullable=False)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=False)
    
    status = Column(String, default="DETECTED", index=True) 
    # Statuses: DETECTED, ANALYZING, IN_PROGRESS, RECOVERED, FAILED, ESCALATED, STOPPED
    
    amount_at_risk = Column(Float, nullable=False)
    recovered_amount = Column(Float, default=0.0)
    recovery_probability = Column(Float, default=0.0)
    failure_category = Column(String, nullable=True)
    recommended_action = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    
    is_escalated = Column(Boolean, default=False)
    escalation_reason = Column(String, nullable=True)
    stop_reason = Column(String, nullable=True)
    
    created_at = Column(DateTime(timezone=True), default=utc_now)
    updated_at = Column(DateTime(timezone=True), default=utc_now, onupdate=utc_now)

    payment = relationship("Payment", back_populates="recovery_cases")
    customer = relationship("Customer", back_populates="recovery_cases")
    decisions = relationship("RecoveryDecision", back_populates="case")
    attempts = relationship("RecoveryAttempt", back_populates="case")
    audit_events = relationship("AuditEvent", back_populates="case")
    model_predictions = relationship("ModelPrediction", back_populates="case")

class RecoveryDecision(Base):
    __tablename__ = "recovery_decisions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=False)
    decision = Column(String, nullable=False) 
    # Actions: RETRY, WAIT_AND_RETRY, SEND_RECOVERY_NOTIFICATION, REQUEST_CUSTOMER_ACTION, ESCALATE, STOP
    probability = Column(Float, nullable=False)
    reason = Column(String, nullable=False)
    supporting_factors_json = Column(JSON, nullable=True)
    policy_rule_applied = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

    case = relationship("RecoveryCase", back_populates="decisions")

class RecoveryAttempt(Base):
    __tablename__ = "recovery_attempts"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=False)
    attempt_number = Column(Integer, nullable=False)
    action_type = Column(String, nullable=False)
    status = Column(String, default="PENDING") # PENDING, SUCCESS, FAILED, CANCELLED
    payment_reference = Column(String, nullable=True)
    error_code = Column(String, nullable=True)
    error_message = Column(String, nullable=True)
    executed_at = Column(DateTime(timezone=True), default=utc_now)

    case = relationship("RecoveryCase", back_populates="attempts")

class RecoveryPolicy(Base):
    __tablename__ = "recovery_policies"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    rule_name = Column(String, unique=True, nullable=False)
    max_automated_retries = Column(Integer, default=3)
    probability_floor = Column(Float, default=0.40)
    min_amount_escalate = Column(Float, default=50000.0)
    cooldown_hours = Column(Integer, default=24)
    permanent_failure_categories_json = Column(JSON, default=list)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class AuditEvent(Base):
    __tablename__ = "audit_events"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=True)
    event_type = Column(String, nullable=False, index=True)
    actor = Column(String, nullable=False) # SYSTEM, ML_MODEL, DECISION_ENGINE, POLICY_ENGINE, PAYMENT_SERVICE, HUMAN_OPERATOR
    action = Column(String, nullable=False)
    reason = Column(String, nullable=True)
    policy_result = Column(String, nullable=True)
    outcome = Column(String, nullable=True)
    metadata_json = Column(JSON, nullable=True)
    timestamp = Column(DateTime(timezone=True), default=utc_now, index=True)

    case = relationship("RecoveryCase", back_populates="audit_events")

class BatchRun(Base):
    __tablename__ = "batch_runs"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    batch_ref = Column(String, unique=True, index=True, nullable=False)
    total_events = Column(Integer, default=0)
    revenue_at_risk = Column(Float, default=0.0)
    revenue_recovered = Column(Float, default=0.0)
    recovery_rate = Column(Float, default=0.0)
    total_attempts = Column(Integer, default=0)
    successful_attempts = Column(Integer, default=0)
    failed_attempts = Column(Integer, default=0)
    escalated_count = Column(Integer, default=0)
    stopped_count = Column(Integer, default=0)
    avg_recovery_amount = Column(Float, default=0.0)
    guardrail_interventions = Column(Integer, default=0)
    unnecessary_intervention_rate = Column(Float, default=0.0)
    processing_time_ms = Column(Float, default=0.0)
    created_at = Column(DateTime(timezone=True), default=utc_now)

class ModelPrediction(Base):
    __tablename__ = "model_predictions"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=False)
    model_version = Column(String, default="v1.0-xgboost")
    predicted_probability = Column(Float, nullable=False)
    feature_vector_json = Column(JSON, nullable=False)
    calibration_score = Column(Float, default=0.92)
    prediction_timestamp = Column(DateTime(timezone=True), default=utc_now)

    case = relationship("RecoveryCase", back_populates="model_predictions")

class Notification(Base):
    __tablename__ = "notifications"
    
    id = Column(String, primary_key=True, default=generate_uuid)
    case_id = Column(String, ForeignKey("recovery_cases.id"), nullable=True)
    customer_id = Column(String, ForeignKey("customers.id"), nullable=True)
    channel = Column(String, default="EMAIL") # EMAIL, SMS, WHATSAPP, DASHBOARD
    template_name = Column(String, nullable=False)
    recipient = Column(String, nullable=False)
    status = Column(String, default="SENT") # SENT, FAILED, PENDING
    sent_at = Column(DateTime(timezone=True), default=utc_now)
