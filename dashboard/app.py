# TODO: implement data ingestion logic
from flask import Flask, jsonify, render_template, request

from src.api import risk_service
from src.config import API_PREFIX

app = Flask(__name__, template_folder="templates")


@app.route("/")
def index() -> str:
    return render_template("index.html")


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


@app.post(f"{API_PREFIX}/predict")
def predict():
    """
    Expects a JSON body like:

    {
      "theme": "Sushi",
      "staff_count": 10,
      "infractions_history": 2,
      "kitchen_size": 30.0,
      "region": "Montreal",
      "inspection_date": "2024-11-01"
    }
    """
    data = request.get_json(silent=True)
    if data is None:
        return jsonify({"error": "Invalid JSON body"}), 400

    try:
        result = risk_service.predict(data)
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400

    return jsonify(result.to_dict())
