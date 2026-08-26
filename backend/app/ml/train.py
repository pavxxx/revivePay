import os
import json
import joblib
import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from xgboost import XGBClassifier
from sklearn.metrics import (
    precision_score, recall_score, f1_score, roc_auc_score,
    confusion_matrix, brier_score_loss
)
from sklearn.calibration import calibration_curve

from app.ml.synthetic import generate_synthetic_dataset
from app.ml.feature_extractor import extract_features_df, FEATURE_NAMES

ARTIFACTS_DIR = os.path.join(os.path.dirname(__file__), "artifacts")

def train_and_evaluate():
    """
    Trains Logistic Regression, Random Forest, and XGBoost models on synthetic data.
    Reports real precision/recall/F1/ROC-AUC/confusion matrix/calibration metrics.
    Saves the best model and metrics report to disk.
    """
    os.makedirs(ARTIFACTS_DIR, exist_ok=True)
    
    print("Generating synthetic dataset (2000 samples, seed=42)...")
    raw_df = generate_synthetic_dataset(num_samples=2000, seed=42)
    
    X = extract_features_df(raw_df)
    y = raw_df["is_recovered"]
    
    X_train, X_val, y_train, y_val = train_test_split(
        X, y, test_size=0.20, random_state=42, stratify=y
    )
    
    models = {
        "LogisticRegression": LogisticRegression(max_iter=1000, random_state=42),
        "RandomForest": RandomForestClassifier(n_estimators=100, max_depth=8, random_state=42),
        "XGBoost": XGBClassifier(n_estimators=100, max_depth=5, learning_rate=0.1, random_state=42, eval_metric="logloss")
    }
    
    best_model_name = None
    best_roc_auc = -1.0
    best_model = None
    results = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        preds = model.predict(X_val)
        probs = model.predict_proba(X_val)[:, 1]
        
        prec = precision_score(y_val, preds, zero_division=0)
        rec = recall_score(y_val, preds, zero_division=0)
        f1 = f1_score(y_val, preds, zero_division=0)
        auc = roc_auc_score(y_val, probs)
        cm = confusion_matrix(y_val, preds).tolist()
        brier = brier_score_loss(y_val, probs)
        
        prob_true, prob_pred = calibration_curve(y_val, probs, n_bins=5)
        calib_curve = [
            {"predicted": float(p_pred), "actual": float(p_true)}
            for p_pred, p_true in zip(prob_pred, prob_true)
        ]
        
        # Feature importances if available
        feature_imp = {}
        if hasattr(model, "feature_importances_"):
            for fname, imp in zip(FEATURE_NAMES, model.feature_importances_):
                feature_imp[fname] = float(imp)
        elif hasattr(model, "coef_"):
            for fname, imp in zip(FEATURE_NAMES, np.abs(model.coef_[0])):
                feature_imp[fname] = float(imp)
                
        results[name] = {
            "model_name": name,
            "precision": float(prec),
            "recall": float(rec),
            "f1_score": float(f1),
            "roc_auc": float(auc),
            "brier_score": float(brier),
            "confusion_matrix": cm,
            "calibration_curve": calib_curve,
            "feature_importances": feature_imp
        }
        
        print(f"Model: {name} | ROC-AUC: {auc:.4f} | F1: {f1:.4f} | Precision: {prec:.4f} | Recall: {rec:.4f}")
        
        if auc > best_roc_auc:
            best_roc_auc = auc
            best_model_name = name
            best_model = model
            
    print(f"\nBest Model selected: {best_model_name} (ROC-AUC: {best_roc_auc:.4f})")
    
    # Save best model
    model_path = os.path.join(ARTIFACTS_DIR, "model.joblib")
    joblib.dump({"model": best_model, "model_name": best_model_name}, model_path)
    
    # Structure full report
    best_metrics = results[best_model_name]
    metrics_report = {
        "model_name": f"RevivePay Recovery Predictor ({best_model_name})",
        "model_type": best_model_name,
        "dataset_size": len(raw_df),
        "precision": best_metrics["precision"],
        "recall": best_metrics["recall"],
        "f1_score": best_metrics["f1_score"],
        "roc_auc": best_metrics["roc_auc"],
        "brier_score": best_metrics["brier_score"],
        "confusion_matrix": best_metrics["confusion_matrix"],
        "calibration_curve": best_metrics["calibration_curve"],
        "feature_importances": best_metrics["feature_importances"],
        "compared_models": results
    }
    
    metrics_path = os.path.join(ARTIFACTS_DIR, "model_metrics.json")
    with open(metrics_path, "w") as f:
        json.dump(metrics_report, f, indent=2)
        
    print(f"Model saved to {model_path}")
    print(f"Metrics saved to {metrics_path}")
    return metrics_report

if __name__ == "__main__":
    train_and_evaluate()
