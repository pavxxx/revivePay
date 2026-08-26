from typing import Dict, Any

ACTIONS = [
    "RETRY",
    "WAIT_AND_RETRY",
    "SEND_RECOVERY_NOTIFICATION",
    "REQUEST_CUSTOMER_ACTION",
    "ESCALATE",
    "STOP"
]

def make_recovery_decision(
    probability: float,
    failure_category: str,
    amount: float,
    retry_count: int,
    customer_history: Dict[str, Any],
    has_subscription: bool = False
) -> Dict[str, Any]:
    """
    Deterministic & Explainable Decision Engine.
    Evaluates ML probability + payment context + customer features to select optimal intervention action.
    """
    supporting_factors = {
        "predicted_probability": probability,
        "failure_category": failure_category,
        "amount": amount,
        "retry_count": retry_count,
        "customer_success_rate": customer_history.get("historical_success_rate", 0.8),
        "tenure_days": customer_history.get("tenure_days", 30),
        "has_subscription": has_subscription
    }
    
    # 1. Hard Stops for Permanent Failures
    if failure_category in ["PERMANENT_HARD_DECLINE", "FRAUD_OR_STOLEN"]:
        return {
            "decision": "STOP",
            "reason": f"Permanent decline category '{failure_category}' detected. Further automated retries halted to prevent fee waste and risk.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "PERMANENT_FAILURE_RULE"
        }
        
    # 2. High Amount Escalation
    if amount >= 50000.0:
        return {
            "decision": "ESCALATE",
            "reason": f"Transaction amount ₹{amount:,.2f} exceeds high-value automated threshold (₹50,000). Escalated to merchant ops for review.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "HIGH_VALUE_THRESHOLD_RULE"
        }
        
    # 3. Max Retry Exhaustion Escalation
    if retry_count >= 3:
        return {
            "decision": "ESCALATE",
            "reason": f"Maximum automated retry limit (3) reached for this transaction without successful recovery. Requires human ops review.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "MAX_RETRY_LIMIT_RULE"
        }
        
    # 4. Low Probability Stop
    if probability < 0.40:
        return {
            "decision": "STOP",
            "reason": f"Predicted recovery probability ({probability:.2f}) is below acceptable automation threshold (0.40). Automation stopped.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "PROBABILITY_FLOOR_RULE"
        }
        
    # 5. Failure-Type Specific Action Mapping for High/Medium Probabilities
    if failure_category == "TRANSIENT_NETWORK":
        return {
            "decision": "RETRY",
            "reason": f"Transient network failure detected with high recovery probability ({probability:.2f}). Immediate payment re-attempt recommended.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "TRANSIENT_NETWORK_RETRY_RULE"
        }
        
    elif failure_category == "INSUFFICIENT_FUNDS":
        return {
            "decision": "WAIT_AND_RETRY",
            "reason": f"Insufficient funds indicated. High/Medium recovery probability ({probability:.2f}). Wait for pay-cycle cooldown before re-attempting.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "INSUFFICIENT_FUNDS_COOLDOWN_RULE"
        }
        
    elif failure_category == "AUTHENTICATION_REQUIRED":
        return {
            "decision": "REQUEST_CUSTOMER_ACTION",
            "reason": f"3D Secure or 2FA authentication required. Prompting customer with secure re-authentication session link.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "CUSTOMER_AUTH_ACTION_RULE"
        }
        
    elif failure_category == "CARD_EXPIRED":
        return {
            "decision": "SEND_RECOVERY_NOTIFICATION",
            "reason": f"Card expired or invalid credentials. Dispatched payment update notification to customer.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "EXPIRED_CARD_NOTIFICATION_RULE"
        }
        
    # Default high probability fallback
    if probability >= 0.70:
        return {
            "decision": "RETRY",
            "reason": f"Strong customer payment history and high recovery probability ({probability:.2f}). Executing payment retry.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "HIGH_PROBABILITY_DEFAULT_RETRY"
        }
    else:
        return {
            "decision": "SEND_RECOVERY_NOTIFICATION",
            "reason": f"Moderate recovery probability ({probability:.2f}). Dispatched recovery reminder notification to customer.",
            "probability": probability,
            "supporting_factors": supporting_factors,
            "policy_rule_applied": "MODERATE_PROBABILITY_NOTIFICATION"
        }
