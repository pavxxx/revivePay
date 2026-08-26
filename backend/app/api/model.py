from fastapi import APIRouter
from app.ml.predictor import get_model_metrics
from app.schemas.pydantic_schemas import ModelMetricsResponse

router = APIRouter(prefix="/model", tags=["ML Model"])

@router.get("/metrics", response_model=ModelMetricsResponse)
def get_ml_metrics():
    """
    Returns actual evaluated ML model metrics (precision, recall, f1, roc-auc, confusion matrix, calibration curve, feature importances).
    Computed from validation split on synthetic dataset.
    """
    metrics = get_model_metrics()
    return metrics
