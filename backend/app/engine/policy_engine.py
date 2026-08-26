from typing import Dict, Any, List, Tuple

DEFAULT_PERMANENT_FAILURES = ["PERMANENT_HARD_DECLINE", "FRAUD_OR_STOLEN"]

class PolicyRuleResult:
    def __init__(self, rule_name: str, passed: bool, description: str, recommendation: str = None):
        self.rule_name = rule_name
        self.passed = passed
        self.description = description
        self.recommendation = recommendation

    def to_dict(self):
        return {
            "rule_name": self.rule_name,
            "passed": self.passed,
            "description": self.description,
            "recommendation": self.recommendation
        }

def evaluate_policy_guardrails(
    proposed_action: str,
    probability: float,
    amount: float,
    failure_category: str,
    retry_count: int,
    policy_config: Dict[str, Any] = None
) -> Tuple[bool, List[PolicyRuleResult], str]:
    """
    Mandatory Policy Guardrail Engine.
    Validates any proposed intervention against configurable safety rules.
    Returns (is_allowed, rule_results, override_reason).
    """
    if policy_config is None:
        policy_config = {
            "max_automated_retries": 3,
            "probability_floor": 0.40,
            "min_amount_escalate": 50000.0,
            "permanent_failure_categories": DEFAULT_PERMANENT_FAILURES
        }
        
    max_retries = policy_config.get("max_automated_retries", 3)
    prob_floor = policy_config.get("probability_floor", 0.40)
    max_auto_amount = policy_config.get("min_amount_escalate", 50000.0)
    perm_failures = policy_config.get("permanent_failure_categories", DEFAULT_PERMANENT_FAILURES)
    
    rule_results = []
    violations = []
    
    # Rule 1: Permanent Failure Check
    is_perm = failure_category in perm_failures
    perm_passed = (not is_perm) or (proposed_action == "STOP")
    rule_results.append(PolicyRuleResult(
        rule_name="PERMANENT_FAILURE_CHECK",
        passed=perm_passed,
        description=f"Failure category '{failure_category}' compared against permanent hard decline list.",
        recommendation="STOP" if is_perm else None
    ))
    if not perm_passed:
        violations.append("PERMANENT_FAILURE_CHECK")

    # Rule 2: Probability Floor Check
    prob_passed = (probability >= prob_floor) or (proposed_action in ["STOP", "ESCALATE"])
    rule_results.append(PolicyRuleResult(
        rule_name="PROBABILITY_FLOOR_CHECK",
        passed=prob_passed,
        description=f"Predicted probability {probability:.2f} compared against floor {prob_floor:.2f}.",
        recommendation="STOP" if probability < prob_floor else None
    ))
    if not prob_passed:
        violations.append("PROBABILITY_FLOOR_CHECK")

    # Rule 3: Max Retries Exceeded Check
    retry_passed = (retry_count < max_retries) or (proposed_action in ["STOP", "ESCALATE"])
    rule_results.append(PolicyRuleResult(
        rule_name="MAX_RETRIES_CHECK",
        passed=retry_passed,
        description=f"Current retry count ({retry_count}) compared against limit ({max_retries}).",
        recommendation="ESCALATE" if retry_count >= max_retries else None
    ))
    if not retry_passed:
        violations.append("MAX_RETRIES_CHECK")

    # Rule 4: High Amount Escalation Threshold Check
    amount_passed = (amount < max_auto_amount) or (proposed_action == "ESCALATE")
    rule_results.append(PolicyRuleResult(
        rule_name="HIGH_VALUE_TRANSACTION_CHECK",
        passed=amount_passed,
        description=f"Transaction amount ₹{amount:,.2f} compared against auto-action limit ₹{max_auto_amount:,.2f}.",
        recommendation="ESCALATE" if amount >= max_auto_amount else None
    ))
    if not amount_passed:
        violations.append("HIGH_VALUE_TRANSACTION_CHECK")

    is_allowed = (len(violations) == 0)
    override_reason = None
    if not is_allowed:
        override_reason = f"Policy violation(s): {', '.join(violations)}. Action blocked and overridden."

    return is_allowed, rule_results, override_reason
