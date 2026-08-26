import pytest
from app.engine.policy_engine import evaluate_policy_guardrails

def test_policy_allowed_action():
    is_allowed, results, override = evaluate_policy_guardrails(
        proposed_action="RETRY",
        probability=0.85,
        amount=5000.0,
        failure_category="TRANSIENT_NETWORK",
        retry_count=1
    )
    assert is_allowed is True
    assert override is None
    assert len(results) == 4

def test_policy_rejected_action_due_to_high_amount():
    is_allowed, results, override = evaluate_policy_guardrails(
        proposed_action="RETRY",
        probability=0.85,
        amount=60000.0,
        failure_category="TRANSIENT_NETWORK",
        retry_count=0
    )
    assert is_allowed is False
    assert "HIGH_VALUE_TRANSACTION_CHECK" in override

def test_policy_rejected_action_due_to_low_probability():
    is_allowed, results, override = evaluate_policy_guardrails(
        proposed_action="RETRY",
        probability=0.20,
        amount=1000.0,
        failure_category="CARD_EXPIRED",
        retry_count=0
    )
    assert is_allowed is False
    assert "PROBABILITY_FLOOR_CHECK" in override
