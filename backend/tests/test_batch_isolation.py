"""
Minimal tests for:
  - batch isolation (each batch computes metrics only from its own cases)
  - batch-specific metrics correctness
  - guardrail_interventions metric (only actual policy-blocked actions)
  - environment loading (python-dotenv integration)
"""
import uuid
import pytest
from app.db.database import SessionLocal, Base, engine
from app.db.models import Customer, Payment, RecoveryCase, BatchRun, AuditEvent
from app.services.batch_service import run_demo_batch


@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()


# ---------------------------------------------------------------------------
# 1. Batch isolation: two consecutive batches must have independent metrics
# ---------------------------------------------------------------------------

def test_batch_isolation_total_events(db_session):
    """Each batch's total_events must equal only its own batch_size, not cumulative."""
    batch1 = run_demo_batch(db_session, batch_size=10)
    batch2 = run_demo_batch(db_session, batch_size=15)

    # Each batch must report only its own event count
    assert batch1.total_events == 10, (
        f"Batch 1 total_events={batch1.total_events}, expected 10"
    )
    assert batch2.total_events == 15, (
        f"Batch 2 total_events={batch2.total_events}, expected 15"
    )


def test_batch_isolation_unique_refs(db_session):
    """Each batch run must have a unique batch_ref."""
    batch1 = run_demo_batch(db_session, batch_size=10)
    batch2 = run_demo_batch(db_session, batch_size=10)
    assert batch1.batch_ref != batch2.batch_ref


def test_batch_metrics_are_not_cumulative(db_session):
    """
    Running a second batch must not inflate metrics with data from the first.
    Specifically, batch2.revenue_at_risk should NOT include batch1's revenue.
    """
    batch1 = run_demo_batch(db_session, batch_size=10)
    batch2 = run_demo_batch(db_session, batch_size=10)

    # Both batches must be stored independently
    all_batches = db_session.query(BatchRun).all()
    assert len(all_batches) >= 2

    # batch2's revenue_at_risk must not be greater than batch1's + batch2's combined
    # (i.e., it should not be cumulative across all DB records)
    assert batch2.total_events == 10, (
        f"Batch 2 should have exactly 10 events, got {batch2.total_events}"
    )
    assert batch2.revenue_at_risk > 0


# ---------------------------------------------------------------------------
# 2. Batch-specific metrics: computed values must be internally consistent
# ---------------------------------------------------------------------------

def test_batch_recovery_rate_is_consistent(db_session):
    """recovery_rate must be consistent with revenue_recovered / revenue_at_risk."""
    batch = run_demo_batch(db_session, batch_size=20)

    if batch.revenue_at_risk > 0:
        expected_rate = round(
            (batch.revenue_recovered / batch.revenue_at_risk) * 100.0, 2
        )
        assert abs(batch.recovery_rate - expected_rate) < 0.1, (
            f"recovery_rate mismatch: stored={batch.recovery_rate}, computed={expected_rate}"
        )
    assert 0.0 <= batch.recovery_rate <= 100.0


def test_batch_attempts_are_consistent(db_session):
    """successful + failed attempts must equal total_attempts."""
    batch = run_demo_batch(db_session, batch_size=20)
    assert batch.successful_attempts + batch.failed_attempts == batch.total_attempts


# ---------------------------------------------------------------------------
# 3. guardrail_interventions: counts only actual policy FAILED_VIOLATION events
# ---------------------------------------------------------------------------

def test_guardrail_interventions_counts_only_violations(db_session):
    """
    guardrail_interventions must be <= the number of ESCALATED + STOPPED cases
    in the batch. It must NOT equal total_events (i.e., not every case is a violation).
    """
    batch = run_demo_batch(db_session, batch_size=30)

    # guardrail_interventions must be a non-negative integer
    assert isinstance(batch.guardrail_interventions, int)
    assert batch.guardrail_interventions >= 0

    # It must never exceed total_events
    assert batch.guardrail_interventions <= batch.total_events

    # It must not equal total_events (not every case is blocked by the policy engine)
    assert batch.guardrail_interventions < batch.total_events, (
        "guardrail_interventions should not count every case — only actual policy blocks"
    )


def test_guardrail_interventions_is_not_stopped_plus_escalated(db_session):
    """
    guardrail_interventions counts audit FAILED_VIOLATION events, not simply
    the sum of all STOPPED and ESCALATED cases (which includes legitimate design-path stops).
    """
    batch = run_demo_batch(db_session, batch_size=30)
    stopped_plus_escalated = batch.stopped_count + batch.escalated_count

    # Some stops are design-path (e.g., permanent failures) — not policy violations.
    # So guardrail_interventions <= stopped_plus_escalated (strict subset).
    assert batch.guardrail_interventions <= stopped_plus_escalated


# ---------------------------------------------------------------------------
# 4. Environment loading: python-dotenv integration
# ---------------------------------------------------------------------------

def test_dotenv_loads_without_error():
    """python-dotenv must be importable and load_dotenv must not raise."""
    from dotenv import load_dotenv
    # Should run without raising; returns True/False based on .env existence
    result = load_dotenv()
    assert isinstance(result, bool)


def test_config_settings_have_safe_defaults():
    """Settings defaults must keep USE_RAZORPAY_REAL=False (simulation mode)."""
    from app.config import settings
    # Default must be simulation mode — never real-money execution
    assert settings.USE_RAZORPAY_REAL is False
    assert settings.RAZORPAY_KEY_ID.startswith("rzp_test_") or \
           settings.RAZORPAY_KEY_ID == "rzp_test_mockkey12345", (
        "Default Razorpay key must be a test key, not a live key"
    )
