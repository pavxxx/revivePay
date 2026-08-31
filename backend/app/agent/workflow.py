from datetime import datetime, timezone
from typing import Dict, Any, Optional
from sqlalchemy.orm import Session

from app.db.models import (
    RecoveryCase, Payment, Customer, Subscription, RecoveryDecision,
    RecoveryAttempt, AuditEvent, ModelPrediction, Notification
)
from app.ml.predictor import predict_recovery_probability
from app.engine.decision_engine import make_recovery_decision
from app.engine.policy_engine import evaluate_policy_guardrails
from app.services.payment_service import get_payment_service

class AgentWorkflowEngine:
    """
    Deterministic Agent State Machine for RevivePay Revenue Recovery.
    Core Loop: Detect -> Diagnose -> Predict -> Decide -> Guard -> Act -> Measure -> Audit.
    """

    def __init__(self, db: Session):
        self.db = db
        self.payment_service = get_payment_service()

    def _log_audit_event(
        self,
        case_id: str,
        event_type: str,
        actor: str,
        action: str,
        reason: Optional[str] = None,
        policy_result: Optional[str] = None,
        outcome: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> AuditEvent:
        """Helper to append an audit log record to the append-only audit trail in the database."""
        event = AuditEvent(
            case_id=case_id,
            event_type=event_type,
            actor=actor,
            action=action,
            reason=reason,
            policy_result=policy_result,
            outcome=outcome,
            metadata_json=metadata or {},
            timestamp=datetime.now(timezone.utc)
        )
        self.db.add(event)
        self.db.flush()
        return event

    def process_failed_payment_event(self, payment_id: str) -> RecoveryCase:
        """
        Main Agent State Machine Pipeline for a failed payment case.
        """
        # Step 1: EVENT_RECEIVED
        payment = self.db.query(Payment).filter(Payment.id == payment_id).first()
        if not payment:
            raise ValueError(f"Payment {payment_id} not found.")

        # Find or create case
        case = self.db.query(RecoveryCase).filter(RecoveryCase.payment_id == payment_id).first()
        if not case:
            case_ref = f"CASE-{datetime.now().strftime('%Y%m%d')}-{payment.payment_ref[-6:]}"
            case = RecoveryCase(
                case_ref=case_ref,
                payment_id=payment.id,
                customer_id=payment.customer_id,
                status="DETECTED",
                amount_at_risk=payment.amount,
                failure_category=payment.failure_category,
                retry_count=0
            )
            self.db.add(case)
            self.db.flush()

        self._log_audit_event(
            case_id=case.id,
            event_type="FAILURE_DETECTED",
            actor="SYSTEM",
            action="INGEST_FAILED_PAYMENT",
            reason=f"Payment failure detected: {payment.failure_reason or payment.failure_category}",
            outcome="CASE_CREATED",
            metadata={"amount": payment.amount, "currency": payment.currency, "payment_ref": payment.payment_ref}
        )

        # Step 2: CONTEXT_COLLECTION
        case.status = "ANALYZING"
        customer = self.db.query(Customer).filter(Customer.id == payment.customer_id).first()
        subscription = None
        if payment.subscription_id:
            subscription = self.db.query(Subscription).filter(Subscription.id == payment.subscription_id).first()

        prior_attempts_count = len(case.attempts)
        
        self._log_audit_event(
            case_id=case.id,
            event_type="CONTEXT_COLLECTED",
            actor="SYSTEM",
            action="FETCH_CUSTOMER_AND_PAYMENT_HISTORY",
            reason=f"Collected context for customer {customer.name if customer else 'Unknown'}",
            outcome="CONTEXT_READY",
            metadata={
                "customer_tenure": customer.tenure_days if customer else 0,
                "historical_success_rate": customer.historical_success_rate if customer else 0.8,
                "prior_attempts": prior_attempts_count,
                "has_subscription": subscription is not None
            }
        )

        # Step 3: FAILURE_ANALYSIS
        self._log_audit_event(
            case_id=case.id,
            event_type="FAILURE_CLASSIFIED",
            actor="SYSTEM",
            action="CLASSIFY_FAILURE_REASON",
            reason=f"Classified failure as category '{payment.failure_category}'",
            outcome=payment.failure_category,
            metadata={"raw_reason": payment.failure_reason, "category": payment.failure_category}
        )

        # Step 4: RECOVERY_PREDICTION
        context_dict = {
            "amount": payment.amount,
            "tenure_days": customer.tenure_days if customer else 30,
            "total_payments": customer.total_payments if customer else 5,
            "successful_payments": customer.successful_payments if customer else 4,
            "failed_payments": customer.failed_payments if customer else 1,
            "historical_success_rate": customer.historical_success_rate if customer else 0.8,
            "avg_txn_amount": customer.avg_txn_amount if customer else payment.amount,
            "prior_recovery_attempts": prior_attempts_count,
            "days_since_last_success": 7,
            "has_active_subscription": subscription is not None and subscription.status == "ACTIVE",
            "recent_failure_freq_30d": 1,
            "failure_category": payment.failure_category,
            "payment_method": payment.payment_method
        }

        prob, feat_contrib = predict_recovery_probability(context_dict)
        case.recovery_probability = prob

        model_pred = ModelPrediction(
            case_id=case.id,
            model_version="v1.0-xgboost",
            predicted_probability=prob,
            feature_vector_json=feat_contrib,
            calibration_score=0.92
        )
        self.db.add(model_pred)
        self.db.flush()

        self._log_audit_event(
            case_id=case.id,
            event_type="MODEL_EVALUATED",
            actor="ML_MODEL",
            action="PREDICT_RECOVERY_PROBABILITY",
            reason=f"Calculated recovery probability: {prob * 100:.1f}%",
            outcome=f"{prob:.4f}",
            metadata={"probability": prob, "top_feature_factors": feat_contrib}
        )

        # Step 5: RECOVERY_PLAN (Decision Engine)
        decision_dict = make_recovery_decision(
            probability=prob,
            failure_category=payment.failure_category,
            amount=payment.amount,
            retry_count=case.retry_count,
            customer_history={
                "historical_success_rate": customer.historical_success_rate if customer else 0.8,
                "tenure_days": customer.tenure_days if customer else 30
            },
            has_subscription=subscription is not None
        )

        proposed_action = decision_dict["decision"]
        reasoning = decision_dict["reason"]
        rule_applied = decision_dict["policy_rule_applied"]

        decision_obj = RecoveryDecision(
            case_id=case.id,
            decision=proposed_action,
            probability=prob,
            reason=reasoning,
            supporting_factors_json=decision_dict["supporting_factors"],
            policy_rule_applied=rule_applied
        )
        self.db.add(decision_obj)
        self.db.flush()

        case.recommended_action = proposed_action

        self._log_audit_event(
            case_id=case.id,
            event_type="DECISION_MADE",
            actor="DECISION_ENGINE",
            action="PROPOSE_INTERVENTION_ACTION",
            reason=reasoning,
            outcome=proposed_action,
            metadata=decision_dict
        )

        # Step 6: POLICY_CHECK (Policy Guardrails Gate)
        is_allowed, rule_results, override_reason = evaluate_policy_guardrails(
            proposed_action=proposed_action,
            probability=prob,
            amount=payment.amount,
            failure_category=payment.failure_category,
            retry_count=case.retry_count
        )

        policy_summary_str = "PASSED" if is_allowed else "FAILED_VIOLATION"
        
        self._log_audit_event(
            case_id=case.id,
            event_type="POLICY_CHECKED",
            actor="POLICY_ENGINE",
            action="VALIDATE_GUARDRAILS",
            reason=override_reason or "All policy safety checks passed successfully.",
            policy_result=policy_summary_str,
            outcome="APPROVED" if is_allowed else "BLOCKED",
            metadata={"rules_evaluated": [r.to_dict() for r in rule_results]}
        )

        # Step 7: BRANCHING EXECUTION / ESCALATION / STOP
        if proposed_action == "STOP" or (not is_allowed and "PERMANENT_FAILURE_CHECK" in str(override_reason)):
            case.status = "STOPPED"
            case.stop_reason = override_reason or reasoning
            self._log_audit_event(
                case_id=case.id,
                event_type="CASE_STOPPED",
                actor="POLICY_ENGINE",
                action="HALT_RECOVERY_AUTOMATION",
                reason=case.stop_reason,
                outcome="STOPPED"
            )
            self.db.commit()
            return case

        elif proposed_action == "ESCALATE" or not is_allowed:
            case.status = "ESCALATED"
            case.is_escalated = True
            case.escalation_reason = override_reason or reasoning
            self._log_audit_event(
                case_id=case.id,
                event_type="CASE_ESCALATED",
                actor="POLICY_ENGINE",
                action="FLAG_FOR_HUMAN_REVIEW",
                reason=case.escalation_reason,
                outcome="ESCALATED"
            )
            self.db.commit()
            return case

        # Step 8: APPROVED -> EXECUTE INTERVENTION
        case.status = "IN_PROGRESS"
        
        if proposed_action in ["RETRY", "WAIT_AND_RETRY"]:
            case.retry_count += 1
            
            # Execute payment retry via PaymentService abstraction
            retry_res = self.payment_service.retry_payment(
                payment_id=payment.id,
                case_id=case.id,
                failure_category=payment.failure_category,
                probability=prob
            )
            
            attempt_status = "SUCCESS" if retry_res.get("is_success") else "FAILED"
            
            attempt_obj = RecoveryAttempt(
                case_id=case.id,
                attempt_number=case.retry_count,
                action_type=proposed_action,
                status=attempt_status,
                payment_reference=retry_res.get("retry_reference"),
                error_message=retry_res.get("error_message")
            )
            self.db.add(attempt_obj)
            self.db.flush()

            self._log_audit_event(
                case_id=case.id,
                event_type="ACTION_EXECUTED",
                actor="PAYMENT_SERVICE",
                action=f"EXECUTE_{proposed_action}",
                reason=f"Executed payment retry via {retry_res.get('provider')} ({retry_res.get('environment')})",
                outcome=attempt_status,
                metadata=retry_res
            )

            # Step 9: MEASURE OUTCOME & RECORD REVENUE
            if attempt_status == "SUCCESS":
                case.status = "RECOVERED"
                case.recovered_amount = payment.amount
                payment.status = "SUCCESS"
                
                # Update customer statistics
                if customer:
                    customer.successful_payments += 1
                    customer.historical_success_rate = round(
                        customer.successful_payments / max(1, customer.total_payments), 4
                    )
                
                self._log_audit_event(
                    case_id=case.id,
                    event_type="OUTCOME_RECORDED",
                    actor="SYSTEM",
                    action="RECORD_RECOVERED_REVENUE",
                    reason=f"Successfully recovered ₹{payment.amount:,.2f}",
                    outcome="RECOVERED",
                    metadata={"recovered_amount": payment.amount}
                )
            else:
                # If retry failed, check if max retries now reached
                if case.retry_count >= 3:
                    case.status = "ESCALATED"
                    case.is_escalated = True
                    case.escalation_reason = "Retry attempt failed and maximum retry threshold reached."
                    self._log_audit_event(
                        case_id=case.id,
                        event_type="CASE_ESCALATED",
                        actor="SYSTEM",
                        action="ESCALATE_AFTER_FAILED_RETRY",
                        reason=case.escalation_reason,
                        outcome="ESCALATED"
                    )
                else:
                    case.status = "IN_PROGRESS"
                    self._log_audit_event(
                        case_id=case.id,
                        event_type="OUTCOME_RECORDED",
                        actor="SYSTEM",
                        action="RECORD_FAILED_ATTEMPT",
                        reason=f"Attempt {case.retry_count} failed. Case remains in progress for scheduled retry.",
                        outcome="FAILED_ATTEMPT"
                    )

        elif proposed_action in ["SEND_RECOVERY_NOTIFICATION", "REQUEST_CUSTOMER_ACTION"]:
            case.retry_count += 1
            
            # Send Notification record
            notif = Notification(
                case_id=case.id,
                customer_id=customer.id if customer else None,
                channel="EMAIL",
                template_name=f"TEMPLATE_{proposed_action}",
                recipient=customer.email if customer else "customer@example.com",
                status="SENT"
            )
            self.db.add(notif)
            self.db.flush()

            attempt_obj = RecoveryAttempt(
                case_id=case.id,
                attempt_number=case.retry_count,
                action_type=proposed_action,
                status="SUCCESS",
                payment_reference=f"notif_{notif.id[:8]}"
            )
            self.db.add(attempt_obj)
            self.db.flush()

            self._log_audit_event(
                case_id=case.id,
                event_type="ACTION_EXECUTED",
                actor="NOTIFICATION_SERVICE",
                action=f"DISPATCH_{proposed_action}",
                reason=f"Dispatched customer recovery communication via email to {notif.recipient}",
                outcome="SENT",
                metadata={"notification_id": notif.id, "channel": "EMAIL"}
            )
            
            # Case stays in progress waiting for customer link click/action
            case.status = "IN_PROGRESS"

        self.db.commit()
        return case

    def manual_human_action(self, case_id: str, action: str, note: Optional[str] = None) -> RecoveryCase:
        """
        Allows merchant ops user to manually approve, escalate, or stop a case from the UI.
        """
        case = self.db.query(RecoveryCase).filter(RecoveryCase.id == case_id).first()
        if not case:
            raise ValueError(f"Case {case_id} not found.")

        payment = case.payment

        if action == "APPROVE":
            case.status = "IN_PROGRESS"
            case.is_escalated = False
            case.retry_count += 1
            
            retry_res = self.payment_service.retry_payment(
                payment_id=payment.id,
                case_id=case.id,
                failure_category=payment.failure_category,
                probability=max(0.75, case.recovery_probability) # Manual ops override probability boost
            )
            
            attempt_status = "SUCCESS" if retry_res.get("is_success") else "FAILED"
            
            attempt_obj = RecoveryAttempt(
                case_id=case.id,
                attempt_number=case.retry_count,
                action_type="MANUAL_APPROVED_RETRY",
                status=attempt_status,
                payment_reference=retry_res.get("retry_reference"),
                error_message=retry_res.get("error_message")
            )
            self.db.add(attempt_obj)
            
            if attempt_status == "SUCCESS":
                case.status = "RECOVERED"
                case.recovered_amount = payment.amount
                payment.status = "SUCCESS"
                outcome_str = "RECOVERED"
            else:
                case.status = "FAILED"
                outcome_str = "FAILED"

            self._log_audit_event(
                case_id=case.id,
                event_type="ACTION_EXECUTED",
                actor="HUMAN_OPERATOR",
                action="MANUAL_APPROVE_AND_EXECUTE",
                reason=note or "Merchant Ops user approved manual recovery attempt.",
                outcome=outcome_str,
                metadata=retry_res
            )

        elif action == "ESCALATE":
            case.status = "ESCALATED"
            case.is_escalated = True
            case.escalation_reason = note or "Escalated manually by Ops user."
            self._log_audit_event(
                case_id=case.id,
                event_type="CASE_ESCALATED",
                actor="HUMAN_OPERATOR",
                action="MANUAL_ESCALATE",
                reason=case.escalation_reason,
                outcome="ESCALATED"
            )

        elif action == "STOP":
            case.status = "STOPPED"
            case.stop_reason = note or "Stopped manually by Ops user."
            self._log_audit_event(
                case_id=case.id,
                event_type="CASE_STOPPED",
                actor="HUMAN_OPERATOR",
                action="MANUAL_STOP",
                reason=case.stop_reason,
                outcome="STOPPED"
            )

        self.db.commit()
        return case
