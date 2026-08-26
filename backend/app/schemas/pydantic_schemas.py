from datetime import datetime
from typing import Optional, List, Any, Dict
from pydantic import BaseModel, ConfigDict

class CustomerBase(BaseModel):
    customer_ref: str
    name: str
    email: str
    tenure_days: int
    historical_success_rate: float
    avg_txn_amount: float
    total_payments: int
    successful_payments: int
    failed_payments: int

class CustomerResponse(CustomerBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class PaymentBase(BaseModel):
    payment_ref: str
    customer_id: str
    subscription_id: Optional[str] = None
    amount: float
    currency: str = "INR"
    status: str
    failure_reason: Optional[str] = None
    failure_category: str
    payment_method: str
    razorpay_id: Optional[str] = None

class PaymentResponse(PaymentBase):
    id: str
    created_at: datetime
    customer: Optional[CustomerResponse] = None
    model_config = ConfigDict(from_attributes=True)

class SubscriptionBase(BaseModel):
    subscription_ref: str
    customer_id: str
    plan_name: str
    amount: float
    interval: str
    status: str
    next_billing_at: Optional[datetime] = None

class SubscriptionResponse(SubscriptionBase):
    id: str
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RecoveryDecisionResponse(BaseModel):
    id: str
    case_id: str
    decision: str
    probability: float
    reason: str
    supporting_factors_json: Optional[Dict[str, Any]] = None
    policy_rule_applied: Optional[str] = None
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class RecoveryAttemptResponse(BaseModel):
    id: str
    case_id: str
    attempt_number: int
    action_type: str
    status: str
    payment_reference: Optional[str] = None
    error_code: Optional[str] = None
    error_message: Optional[str] = None
    executed_at: datetime
    model_config = ConfigDict(from_attributes=True)

class AuditEventResponse(BaseModel):
    id: str
    case_id: Optional[str] = None
    event_type: str
    actor: str
    action: str
    reason: Optional[str] = None
    policy_result: Optional[str] = None
    outcome: Optional[str] = None
    metadata_json: Optional[Dict[str, Any]] = None
    timestamp: datetime
    model_config = ConfigDict(from_attributes=True)

class RecoveryCaseResponse(BaseModel):
    id: str
    case_ref: str
    payment_id: str
    customer_id: str
    status: str
    amount_at_risk: float
    recovered_amount: float
    recovery_probability: float
    failure_category: Optional[str] = None
    recommended_action: Optional[str] = None
    retry_count: int
    is_escalated: bool
    escalation_reason: Optional[str] = None
    stop_reason: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    payment: Optional[PaymentResponse] = None
    customer: Optional[CustomerResponse] = None
    decisions: List[RecoveryDecisionResponse] = []
    attempts: List[RecoveryAttemptResponse] = []
    audit_events: List[AuditEventResponse] = []
    model_config = ConfigDict(from_attributes=True)

class DashboardSummaryResponse(BaseModel):
    revenue_at_risk: float
    revenue_recovered: float
    recovery_rate: float
    active_cases_count: int
    total_cases_count: int
    recovered_cases_count: int
    escalated_cases_count: int
    stopped_cases_count: int
    failed_cases_count: int
    total_attempts_count: int
    successful_attempts_count: int
    attempt_success_rate: float

class RecoveryTrendPoint(BaseModel):
    date: str
    at_risk: float
    recovered: float

class FailureDistributionPoint(BaseModel):
    category: str
    count: int
    amount: float
    recovery_rate: float

class BatchRunResponse(BaseModel):
    id: str
    batch_ref: str
    total_events: int
    revenue_at_risk: float
    revenue_recovered: float
    recovery_rate: float
    total_attempts: int
    successful_attempts: int
    failed_attempts: int
    escalated_count: int
    stopped_count: int
    avg_recovery_amount: float
    policy_violations_prevented: int
    unnecessary_intervention_rate: float
    processing_time_ms: float
    created_at: datetime
    model_config = ConfigDict(from_attributes=True)

class ModelMetricsResponse(BaseModel):
    model_name: str
    model_type: str
    dataset_size: int
    precision: float
    recall: float
    f1_score: float
    roc_auc: float
    confusion_matrix: List[List[int]]
    calibration_curve: List[Dict[str, float]]
    feature_importances: Dict[str, float]
