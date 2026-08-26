import pytest
from app.engine.decision_engine import make_recovery_decision

def test_decision_permanent_failure():
    res = make_recovery_decision(
        probability=0.85,
        failure_category="PERMANENT_HARD_DECLINE",
        amount=1000.0,
        retry_count=0,
        customer_history={"historical_success_rate": 0.9, "tenure_days": 100}
    )
    assert res["decision"] == "STOP"
    assert res["policy_rule_applied"] == "PERMANENT_FAILURE_RULE"

def test_decision_high_amount_escalation():
    res = make_recovery_decision(
        probability=0.90,
        failure_category="TRANSIENT_NETWORK",
        amount=75000.0,
        retry_count=0,
        customer_history={"historical_success_rate": 0.9, "tenure_days": 100}
    )
    assert res["decision"] == "ESCALATE"
    assert res["policy_rule_applied"] == "HIGH_VALUE_THRESHOLD_RULE"

def test_decision_max_retry_escalation():
    res = make_recovery_decision(
        probability=0.80,
        failure_category="TRANSIENT_NETWORK",
        amount=2500.0,
        retry_count=3,
        customer_history={"historical_success_rate": 0.9, "tenure_days": 100}
    )
    assert res["decision"] == "ESCALATE"
    assert res["policy_rule_applied"] == "MAX_RETRY_LIMIT_RULE"

def test_decision_low_probability_stop():
    res = make_recovery_decision(
        probability=0.25,
        failure_category="CARD_EXPIRED",
        amount=2500.0,
        retry_count=0,
        customer_history={"historical_success_rate": 0.3, "tenure_days": 10}
    )
    assert res["decision"] == "STOP"
    assert res["policy_rule_applied"] == "PROBABILITY_FLOOR_RULE"

def test_decision_transient_retry():
    res = make_recovery_decision(
        probability=0.88,
        failure_category="TRANSIENT_NETWORK",
        amount=2500.0,
        retry_count=0,
        customer_history={"historical_success_rate": 0.95, "tenure_days": 200}
    )
    assert res["decision"] == "RETRY"
