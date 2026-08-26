import numpy as np
import pandas as pd
from typing import List, Dict, Any

FAILURE_CATEGORIES = [
    "TRANSIENT_NETWORK",       # high prob recovery
    "INSUFFICIENT_FUNDS",      # medium-high prob recovery with wait
    "AUTHENTICATION_REQUIRED", # high prob recovery with customer action
    "CARD_EXPIRED",            # medium prob recovery with card update
    "PERMANENT_HARD_DECLINE",  # zero/very low prob recovery
    "FRAUD_OR_STOLEN"          # zero prob recovery
]

PAYMENT_METHODS = ["CARD", "UPI", "NETBANKING", "AUTOPAY"]

def generate_synthetic_dataset(num_samples: int = 2000, seed: int = 42) -> pd.DataFrame:
    """
    Generates synthetic payment recovery dataset for ML model training and validation.
    Fully marked as synthetic and deterministic for reproducibility.
    """
    np.random.seed(seed)
    
    data = []
    for i in range(num_samples):
        amount = float(np.random.exponential(scale=2500) + 100)
        amount = round(min(amount, 100000.0), 2)
        
        tenure_days = int(np.random.exponential(scale=180) + 1)
        total_payments = int(np.random.poisson(lam=12) + 1)
        
        # Historical success rate: higher for longer tenure
        base_success = min(0.98, max(0.20, 0.60 + (tenure_days / 1000) + np.random.normal(0, 0.15)))
        successful_payments = int(round(total_payments * base_success))
        failed_payments = max(0, total_payments - successful_payments)
        
        avg_txn_amount = round(amount * np.random.uniform(0.7, 1.3), 2)
        payment_method = np.random.choice(PAYMENT_METHODS, p=[0.45, 0.35, 0.10, 0.10])
        
        failure_category = np.random.choice(
            FAILURE_CATEGORIES, 
            p=[0.30, 0.30, 0.15, 0.10, 0.10, 0.05]
        )
        
        prior_recovery_attempts = np.random.choice([0, 1, 2, 3, 4], p=[0.50, 0.25, 0.15, 0.07, 0.03])
        days_since_last_success = int(np.random.exponential(scale=14))
        has_active_subscription = bool(np.random.choice([True, False], p=[0.70, 0.30]))
        recent_failure_freq_30d = int(np.random.poisson(lam=0.8))
        
        # Calculate ground truth probability of recovery based on realistic domain heuristics
        p_recover = 0.50
        
        # Category weight
        if failure_category == "TRANSIENT_NETWORK":
            p_recover += 0.35
        elif failure_category == "INSUFFICIENT_FUNDS":
            p_recover += 0.15
        elif failure_category == "AUTHENTICATION_REQUIRED":
            p_recover += 0.25
        elif failure_category == "CARD_EXPIRED":
            p_recover += 0.05
        elif failure_category == "PERMANENT_HARD_DECLINE":
            p_recover -= 0.45
        elif failure_category == "FRAUD_OR_STOLEN":
            p_recover -= 0.50
            
        # Customer history impact
        p_recover += (base_success - 0.70) * 0.30
        
        # Attempt penalty
        p_recover -= prior_recovery_attempts * 0.12
        
        # Amount penalty for ultra-high transactions
        if amount > 50000:
            p_recover -= 0.15
            
        if has_active_subscription:
            p_recover += 0.10
            
        p_recover = max(0.02, min(0.98, p_recover))
        
        # Ground truth outcome
        is_recovered = 1 if np.random.rand() < p_recover else 0
        
        data.append({
            "amount": amount,
            "tenure_days": tenure_days,
            "total_payments": total_payments,
            "successful_payments": successful_payments,
            "failed_payments": failed_payments,
            "historical_success_rate": round(base_success, 4),
            "avg_txn_amount": avg_txn_amount,
            "payment_method": payment_method,
            "failure_category": failure_category,
            "prior_recovery_attempts": prior_recovery_attempts,
            "days_since_last_success": days_since_last_success,
            "has_active_subscription": 1 if has_active_subscription else 0,
            "recent_failure_freq_30d": recent_failure_freq_30d,
            "is_recovered": is_recovered,
            "true_prob": round(p_recover, 4)
        })
        
    return pd.DataFrame(data)
