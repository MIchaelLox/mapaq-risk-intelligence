# TODO: add tests for /predict endpoint
from dashboard.app import app


def test_health_endpoint():
    client = app.test_client()
    resp = client.get("/api/health")
    assert resp.status_code == 200
    assert resp.get_json()["status"] == "ok"


def test_predict_endpoint_ok():
    client = app.test_client()
    payload = {
        "theme": "Sushi",
        "staff_count": 10,
        "infractions_history": 1,
        "kitchen_size": 35.0,
        "region": "Montreal",
        "inspection_date": "2024-11-01",
    }
    resp = client.post("/api/v1/predict", json=payload)
    assert resp.status_code == 200
    data = resp.get_json()
    assert "probability" in data
    assert "risk_level" in data
    assert 0.0 <= data["probability"] <= 1.0
