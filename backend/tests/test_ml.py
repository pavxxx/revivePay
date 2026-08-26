import pytest
import pandas as pd
from app.ml.synthetic import generate_synthetic_dataset
from app.ml.feature_extractor import extract_features_df, extract_features_from_dict, FEATURE_NAMES
from app.ml.predictor import predict_recovery_probability, get_model_metrics

def test_synthetic_data_generation():
    df = generate_synthetic_dataset(num_samples=100, seed=42)
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 100
    assert "is_recovered" in df.columns
    assert "true_prob" in df.columns

def test_feature_extraction():
    raw_ctx = {
        "amount": 2500.0,
        "tenure_days": 120,
        "total_payments": 10,
        "successful_payments": 9,
        "failed_payments": 1,
        "historical_success_rate": 0.90,
        "avg_txn_amount": 2500.0,
        "prior_recovery_attempts": 1,
        "days_since_last_success": 5,
        "has_active_subscription": True,
        "recent_failure_freq_30d": 0,
        "failure_category": "TRANSIENT_NETWORK",
        "payment_method": "CARD"
    }
    feats = extract_features_from_dict(raw_ctx)
    assert len(feats) == len(FEATURE_NAMES)
    assert feats[0] == 2500.0

def test_ml_prediction_and_metrics():
    raw_ctx = {
        "amount": 1500.0,
        "tenure_days": 180,
        "total_payments": 12,
        "successful_payments": 11,
        "failed_payments": 1,
        "historical_success_rate": 0.92,
        "avg_txn_amount": 1500.0,
        "prior_recovery_attempts": 0,
        "days_since_last_success": 2,
        "has_active_subscription": True,
        "recent_failure_freq_30d": 0,
        "failure_category": "TRANSIENT_NETWORK",
        "payment_method": "CARD"
    }
    prob, contrib = predict_recovery_probability(raw_ctx)
    assert 0.0 <= prob <= 1.0
    assert isinstance(contrib, dict)

    metrics = get_model_metrics()
    assert "precision" in metrics
    assert "recall" in metrics
    assert "f1_score" in metrics
    assert "roc_auc" in metrics
    assert "confusion_matrix" in metrics
