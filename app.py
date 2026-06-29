# app.py
#
# PhishGuard REST API.
# POST /predict {"url": "..."} -> {"url", "label", "is_phishing", "confidence"}
# GET  /health  -> liveness check
# GET  /        -> simple web form for testing by hand

import pickle
import sys
from pathlib import Path

import pandas as pd
from flask import Flask, request, jsonify, render_template

BASE_DIR = Path(__file__).resolve().parent
sys.path.insert(0, str(BASE_DIR))
from feature_extraction import extract_features, FEATURE_NAMES

app = Flask(__name__)

MODEL_PATH = BASE_DIR / "models" / "phishguard_model.pkl"

try:
    with open(MODEL_PATH, "rb") as f:
        bundle = pickle.load(f)
        MODEL = bundle["model"]
        MODEL_FEATURES = bundle["feature_names"]
except FileNotFoundError:
    print(f"\n[ERROR] Model file not found at {MODEL_PATH}")
    print("[ERROR] Run 'python train_model.py' first to train and save the model.\n")
    sys.exit(1)


def predict_url(url: str) -> dict:
    feats = extract_features(url)
    X = pd.DataFrame([feats])[MODEL_FEATURES]
    proba = MODEL.predict_proba(X)[0]
    pred = int(MODEL.predict(X)[0])
    confidence = float(proba[pred])
    return {
        "url": url,
        "label": "phishing" if pred == 1 else "legitimate",
        "is_phishing": bool(pred),
        "confidence": round(confidence, 4),
    }


@app.route("/health", methods=["GET"])
def health():
    return jsonify({"status": "ok"})


@app.route("/predict", methods=["POST"])
def predict():
    data = request.get_json(silent=True) or {}
    url = data.get("url", "").strip()
    if not url:
        return jsonify({"error": "Missing 'url' field in request body"}), 400
    result = predict_url(url)
    return jsonify(result)


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html")


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5050, debug=False)
