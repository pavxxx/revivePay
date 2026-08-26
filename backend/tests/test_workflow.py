import uuid
import pytest
from app.db.database import SessionLocal, Base, engine
from app.db.models import Customer, Payment, RecoveryCase
from app.agent.workflow import AgentWorkflowEngine

@pytest.fixture
def db_session():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    yield db
    db.close()

def test_workflow_transient_failure_recovery(db_session):
    uid = uuid.uuid4().hex[:6]
    cust = Customer(
        customer_ref=f"cust_test_wf_1_{uid}",
        name="Test Workflow User",
        email=f"testwf_{uid}@example.com",
        tenure_days=100,
        historical_success_rate=0.90,
        avg_txn_amount=3000.0,
        total_payments=10,
        successful_payments=9,
        failed_payments=1
    )
    db_session.add(cust)
    db_session.flush()

    pay = Payment(
        payment_ref=f"pay_test_wf_1_{uid}",
        customer_id=cust.id,
        amount=3000.0,
        currency="INR",
        status="FAILED",
        failure_reason="Network timeout",
        failure_category="TRANSIENT_NETWORK",
        payment_method="CARD"
    )
    db_session.add(pay)
    db_session.commit()

    engine_wf = AgentWorkflowEngine(db_session)
    case = engine_wf.process_failed_payment_event(pay.id)

    assert case is not None
    assert case.status in ["RECOVERED", "IN_PROGRESS"]
    assert len(case.audit_events) >= 5
    assert len(case.decisions) >= 1

def test_workflow_permanent_failure_stop(db_session):
    uid = uuid.uuid4().hex[:6]
    cust = Customer(
        customer_ref=f"cust_test_wf_2_{uid}",
        name="Test Hard Decline User",
        email=f"testhard_{uid}@example.com",
        tenure_days=30,
        historical_success_rate=0.40,
        avg_txn_amount=1500.0,
        total_payments=5,
        successful_payments=2,
        failed_payments=3
    )
    db_session.add(cust)
    db_session.flush()

    pay = Payment(
        payment_ref=f"pay_test_wf_2_{uid}",
        customer_id=cust.id,
        amount=1500.0,
        currency="INR",
        status="FAILED",
        failure_reason="Card reported stolen",
        failure_category="FRAUD_OR_STOLEN",
        payment_method="CARD"
    )
    db_session.add(pay)
    db_session.commit()

    engine_wf = AgentWorkflowEngine(db_session)
    case = engine_wf.process_failed_payment_event(pay.id)

    assert case.status == "STOPPED"
    assert case.stop_reason is not None
