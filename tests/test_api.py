from fastapi.testclient import TestClient
from src.api import app

client = TestClient(app)

def test_predict_endpoint_works():
   resp = client.post("/predict", json={"theme": "fast_food", "city": "Montreal"})
   assert resp.status_code == 200
   data = resp.json()
   assert "probability" in data
   assert "risk_level" in data
