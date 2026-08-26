import pytest
from fastapi.testclient import TestClient
from app.main import app
from app.db.database import engine, Base

@pytest.fixture(autouse=True)
def setup_db():
    Base.metadata.create_all(bind=engine)

client = TestClient(app)

def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"

def test_dashboard_summary_endpoint():
    res = client.get("/api/dashboard/summary")
    assert res.status_code == 200
    data = res.json()
    assert "revenue_at_risk" in data
    assert "revenue_recovered" in data
    assert "recovery_rate" in data

def test_cases_endpoint():
    res = client.get("/api/cases")
    assert res.status_code == 200
    data = res.json()
    assert isinstance(data, list)

def test_model_metrics_endpoint():
    res = client.get("/api/model/metrics")
    assert res.status_code == 200
    data = res.json()
    assert "precision" in data
    assert "roc_auc" in data

def test_trigger_batch_endpoint():
    res = client.post("/api/batches/run?batch_size=20")
    assert res.status_code == 200
    data = res.json()
    assert "batch_ref" in data
    assert data["total_events"] >= 20
