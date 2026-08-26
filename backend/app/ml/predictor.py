import os
import json
import joblib
import numpy as np
import pandas as pd
from typing import Dict, Any, Tuple

from app.ml.feature_extractor import extract_features_from_dict, FEATURE_NAMES
from app.ml.train import ARTIFACTS_DIR, train_and_evaluate

_MODEL_CACHE = None
_METRICS_CACHE = None

def get_model():
    global _MODEL_CACHE
    if _MODEL_CACHE is not None:
        return _MODEL_CACHE
        
    model_path = os.path.join(ARTIFACTS_DIR, "model.joblib")
    if not os.path.exists(model_path):
        train_and_evaluate()
        
    data = joblib.load(model_path)
    _MODEL_CACHE = data["model"]
    return _MODEL_CACHE

def get_model_metrics():
    global _METRICS_CACHE
    if _METRICS_CACHE is not None:
        return _METRICS_CACHE
        
    metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")
    if not os.path.exists(metrics_path):
        train_and_evaluate()
        
    with open(metrics_path, "r") as f:
        _METRICS_CACHE = json.load(f)
    return _METRICS_CACHE

def predict_recovery_probability(context: Dict[str, Any]) -> Tuple[float, Dict[str, float]]:
    """
    Predicts probability of payment recovery P(success | payment + customer + failure context).
    Returns (probability, feature_contribution_map).
    """
    model = get_model()
    features = extract_features_from_dict(context)
    X = pd.DataFrame([features], columns=FEATURE_NAMES)
    
    probs = model.predict_proba(X)
    prob_success = float(probs[0, 1])
    
    # Feature contributions for explainability
    feat_contrib = {}
    if hasattr(model, "feature_importances_"):
        for fname, val, imp in zip(FEATURE_NAMES, features, model.feature_importances_):
            feat_contrib[fname] = float(val * imp)
    else:
        for fname, val in zip(FEATURE_NAMES, features):
            feat_contrib[fname] = float(val)
            
    return round(prob_success, 4), feat_contrib
