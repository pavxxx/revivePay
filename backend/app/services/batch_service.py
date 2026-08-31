import time
import uuid
import numpy as np
from typing import List
from sqlalchemy.orm import Session

from app.db.models import Customer, Payment, Subscription, RecoveryCase, BatchRun, RecoveryAttempt
from app.agent.workflow import AgentWorkflowEngine
from app.ml.synthetic import FAILURE_CATEGORIES, PAYMENT_METHODS

def run_demo_batch(db: Session, batch_size: int = 500) -> BatchRun:
    """
    Executes a deterministic demo batch run of `batch_size` (e.g. 500) synthetic payment failure events.
    Each batch gets a unique batch_ref. All metrics are calculated ONLY from the cases created in this batch.
    """
    start_time = time.time()
    np.random.seed(100)  # Reproducible batch seed

    workflow_engine = AgentWorkflowEngine(db)

    # 1. Generate synthetic customers & payments for THIS batch only
    batch_ref = f"BATCH-{uuid.uuid4().hex[:8].upper()}"

    # Deterministic scenario distribution within each batch:
    # Scenario A: Strong history + transient failure (25%) -> RETRY -> SUCCESS
    # Scenario B: Low probability / repeated failures (20%) -> STOP
    # Scenario C: High amount (> ₹50k) (15%) -> ESCALATE
    # Scenario D: Permanent failure (15%) -> STOP
    # Scenario E: Subscription renewal with strong history (25%) -> WAIT_AND_RETRY / RETRY

    created_payments: List[Payment] = []

    for i in range(batch_size):
        mod = i % 100

        if mod < 25:  # Scenario A
            cat = "TRANSIENT_NETWORK"
            amt = float(round(np.random.uniform(500, 15000), 2))
            hist_rate = 0.92
            tenure = 180
            method = "CARD"
            is_sub = False
        elif mod < 45:  # Scenario B
            cat = "CARD_EXPIRED"
            amt = float(round(np.random.uniform(1000, 12000), 2))
            hist_rate = 0.25
            tenure = 15
            method = "UPI"
            is_sub = False
        elif mod < 60:  # Scenario C
            cat = "TRANSIENT_NETWORK"
            amt = float(round(np.random.uniform(55000, 120000), 2))
            hist_rate = 0.88
            tenure = 300
            method = "CARD"
            is_sub = False
        elif mod < 75:  # Scenario D
            cat = np.random.choice(["PERMANENT_HARD_DECLINE", "FRAUD_OR_STOLEN"])
            amt = float(round(np.random.uniform(2000, 25000), 2))
            hist_rate = 0.50
            tenure = 60
            method = "NETBANKING"
            is_sub = False
        else:  # Scenario E
            cat = "INSUFFICIENT_FUNDS"
            amt = float(round(np.random.uniform(1500, 8000), 2))
            hist_rate = 0.95
            tenure = 240
            method = "AUTOPAY"
            is_sub = True

        cust_ref = f"cust_batch_{i}_{uuid.uuid4().hex[:6]}"
        cust = Customer(
            customer_ref=cust_ref,
            name=f"Customer {i+1}",
            email=f"user_{i+1}@example.com",
            tenure_days=tenure,
            historical_success_rate=hist_rate,
            avg_txn_amount=amt,
            total_payments=15,
            successful_payments=int(15 * hist_rate),
            failed_payments=15 - int(15 * hist_rate)
        )
        db.add(cust)
        db.flush()

        sub = None
        if is_sub:
            sub = Subscription(
                subscription_ref=f"sub_{uuid.uuid4().hex[:6]}",
                customer_id=cust.id,
                plan_name="Pro Premium Monthly",
                amount=amt,
                interval="monthly",
                status="PAST_DUE"
            )
            db.add(sub)
            db.flush()

        pay = Payment(
            payment_ref=f"pay_batch_{i}_{uuid.uuid4().hex[:6]}",
            customer_id=cust.id,
            subscription_id=sub.id if sub else None,
            amount=amt,
            currency="INR",
            status="FAILED",
            failure_reason=f"Batch generated {cat}",
            failure_category=cat,
            payment_method=method
        )
        db.add(pay)
        db.flush()
        created_payments.append(pay)

    db.commit()

    # 2. Process all created payments through Agent Workflow Engine.
    #    Track IDs of cases created in THIS batch for isolated metric calculation.
    #    guardrail_interventions = cases where the policy engine actively blocked an action
    #    (i.e. policy_result == "FAILED_VIOLATION" in audit, not just STOP/ESCALATE by design).
    batch_case_ids: List[str] = []
    guardrail_interventions = 0

    for pay in created_payments:
        try:
            case = workflow_engine.process_failed_payment_event(pay.id)
            batch_case_ids.append(case.id)
            # Count only cases where the policy engine raised a FAILED_VIOLATION (an actual guardrail trigger)
            from app.db.models import AuditEvent
            policy_blocked = db.query(AuditEvent).filter(
                AuditEvent.case_id == case.id,
                AuditEvent.event_type == "POLICY_CHECKED",
                AuditEvent.policy_result == "FAILED_VIOLATION"
            ).first()
            if policy_blocked:
                guardrail_interventions += 1
        except Exception as e:
            print(f"Error processing payment {pay.id}: {e}")

    elapsed_ms = (time.time() - start_time) * 1000.0

    # 3. Compute exact metrics FROM ONLY THIS BATCH's DB records (isolated by batch_case_ids).
    if batch_case_ids:
        batch_cases = db.query(RecoveryCase).filter(RecoveryCase.id.in_(batch_case_ids)).all()
    else:
        batch_cases = []

    total_events = len(batch_cases)

    rev_at_risk = sum(c.amount_at_risk for c in batch_cases)
    rev_recovered = sum(c.recovered_amount for c in batch_cases if c.status == "RECOVERED")
    recovery_rate = round((rev_recovered / max(1.0, rev_at_risk)) * 100.0, 2)

    recovered_cases = [c for c in batch_cases if c.status == "RECOVERED"]
    escalated_cases = [c for c in batch_cases if c.status == "ESCALATED"]
    stopped_cases = [c for c in batch_cases if c.status == "STOPPED"]

    total_attempts = 0
    succ_attempts = 0
    for c in batch_cases:
        total_attempts += len(c.attempts)
        succ_attempts += sum(1 for a in c.attempts if a.status == "SUCCESS")

    failed_attempts = total_attempts - succ_attempts
    avg_rec_amt = round(rev_recovered / max(1, len(recovered_cases)), 2) if recovered_cases else 0.0

    batch_run = BatchRun(
        batch_ref=batch_ref,
        total_events=total_events,
        revenue_at_risk=round(rev_at_risk, 2),
        revenue_recovered=round(rev_recovered, 2),
        recovery_rate=recovery_rate,
        total_attempts=total_attempts,
        successful_attempts=succ_attempts,
        failed_attempts=failed_attempts,
        escalated_count=len(escalated_cases),
        stopped_count=len(stopped_cases),
        avg_recovery_amount=avg_rec_amt,
        guardrail_interventions=guardrail_interventions,
        unnecessary_intervention_rate=round(
            (len(stopped_cases) + len(escalated_cases)) / max(1, total_events) * 100.0, 2
        ),
        processing_time_ms=round(elapsed_ms, 2)
    )
    db.add(batch_run)
    db.commit()
    db.refresh(batch_run)
    return batch_run
