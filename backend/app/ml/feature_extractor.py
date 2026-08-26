import numpy as np
import pandas as pd
from typing import Dict, Any, List

FEATURE_NAMES = [
    "amount",
    "log_amount",
    "tenure_days",
    "total_payments",
    "successful_payments",
    "failed_payments",
    "historical_success_rate",
    "avg_txn_amount",
    "prior_recovery_attempts",
    "days_since_last_success",
    "has_active_subscription",
    "recent_failure_freq_30d",
    # One-hot failure categories
    "cat_TRANSIENT_NETWORK",
    "cat_INSUFFICIENT_FUNDS",
    "cat_AUTHENTICATION_REQUIRED",
    "cat_CARD_EXPIRED",
    "cat_PERMANENT_HARD_DECLINE",
    "cat_FRAUD_OR_STOLEN",
    # One-hot payment methods
    "method_CARD",
    "method_UPI",
    "method_NETBANKING",
    "method_AUTOPAY"
]

def extract_features_from_dict(raw: Dict[str, Any]) -> List[float]:
    """
    Converts a dictionary containing payment, customer, and failure context into a 1D feature vector matching FEATURE_NAMES.
    """
    amount = float(raw.get("amount", 1000.0))
    log_amount = float(np.log1p(amount))
    tenure_days = float(raw.get("tenure_days", 30))
    total_payments = float(raw.get("total_payments", 5))
    successful_payments = float(raw.get("successful_payments", 4))
    failed_payments = float(raw.get("failed_payments", 1))
    
    hist_rate = float(raw.get("historical_success_rate", 0.80))
    avg_txn_amount = float(raw.get("avg_txn_amount", amount))
    prior_attempts = float(raw.get("prior_recovery_attempts", 0))
    days_last_success = float(raw.get("days_since_last_success", 7))
    has_sub = 1.0 if raw.get("has_active_subscription", False) else 0.0
    recent_freq = float(raw.get("recent_failure_freq_30d", 1))
    
    cat = raw.get("failure_category", "TRANSIENT_NETWORK")
    method = raw.get("payment_method", "CARD")
    
    features = [
        amount,
        log_amount,
        tenure_days,
        total_payments,
        successful_payments,
        failed_payments,
        hist_rate,
        avg_txn_amount,
        prior_attempts,
        days_last_success,
        has_sub,
        recent_freq,
        1.0 if cat == "TRANSIENT_NETWORK" else 0.0,
        1.0 if cat == "INSUFFICIENT_FUNDS" else 0.0,
        1.0 if cat == "AUTHENTICATION_REQUIRED" else 0.0,
        1.0 if cat == "CARD_EXPIRED" else 0.0,
        1.0 if cat == "PERMANENT_HARD_DECLINE" else 0.0,
        1.0 if cat == "FRAUD_OR_STOLEN" else 0.0,
        1.0 if method == "CARD" else 0.0,
        1.0 if method == "UPI" else 0.0,
        1.0 if method == "NETBANKING" else 0.0,
        1.0 if method == "AUTOPAY" else 0.0,
    ]
    return features

def extract_features_df(df: pd.DataFrame) -> pd.DataFrame:
    """
    Transforms DataFrame of raw records into feature matrix matching FEATURE_NAMES.
    """
    X = pd.DataFrame()
    X["amount"] = df["amount"]
    X["log_amount"] = np.log1p(df["amount"])
    X["tenure_days"] = df["tenure_days"]
    X["total_payments"] = df["total_payments"]
    X["successful_payments"] = df["successful_payments"]
    X["failed_payments"] = df["failed_payments"]
    X["historical_success_rate"] = df["historical_success_rate"]
    X["avg_txn_amount"] = df["avg_txn_amount"]
    X["prior_recovery_attempts"] = df["prior_recovery_attempts"]
    X["days_since_last_success"] = df["days_since_last_success"]
    X["has_active_subscription"] = df["has_active_subscription"]
    X["recent_failure_freq_30d"] = df["recent_failure_freq_30d"]
    
    cats = ["TRANSIENT_NETWORK", "INSUFFICIENT_FUNDS", "AUTHENTICATION_REQUIRED", "CARD_EXPIRED", "PERMANENT_HARD_DECLINE", "FRAUD_OR_STOLEN"]
    for c in cats:
        X[f"cat_{c}"] = (df["failure_category"] == c).astype(float)
        
    methods = ["CARD", "UPI", "NETBANKING", "AUTOPAY"]
    for m in methods:
        X[f"method_{m}"] = (df["payment_method"] == m).astype(float)
        
    return X[FEATURE_NAMES]
