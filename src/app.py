import os
import joblib
import numpy as np
from fastapi import FastAPI, HTTPException
from openai import OpenAI

from src.schemas import WalletFeatures
from src.explain import build_rule_based_explanation, generate_feature_reasons

app = FastAPI(title="Crypto Fraud Intelligence API")

model = joblib.load("models/fraud_model.pkl")
scaler = joblib.load("models/scaler.pkl")
feature_columns = joblib.load("models/feature_columns.pkl")

openai_api_key = os.getenv("OPENAI_API_KEY")

client = None
if openai_api_key:
    from openai import OpenAI
    client = OpenAI(api_key=openai_api_key)


def generate_ai_summary(probability: float, reasons: list[str], prediction: int) -> str:
    
    print("⚡ Calling OpenAI...") 
    risk_band = (
        "high-risk" if probability >= 0.8
        else "medium-risk" if probability >= 0.5
        else "low-risk"
    )

    prompt = f"""
You are a blockchain fraud analyst.

Prediction: {prediction}
Fraud probability: {round(probability, 4)}
Risk band: {risk_band}
Key signals: {", ".join(reasons) if reasons else "No strong suspicious signals detected"}

Write a concise 2-3 sentence professional fraud risk summary.
Do not mention machine learning.
Sound like a real analyst writing an investigation note.
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


@app.get("/")
def root():
    return {"name": "Crypto Fraud Intelligence API", "status": "ok"}


@app.post("/predict")
def predict(payload: WalletFeatures):
    incoming = payload.features

    missing = [col for col in feature_columns if col not in incoming]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing features: {missing[:10]}"
        )

    row = np.array([[incoming[col] for col in feature_columns]])
    row_scaled = scaler.transform(row)

    pred = int(model.predict(row_scaled)[0])
    proba = float(model.predict_proba(row_scaled)[0][1])

    explanation = build_rule_based_explanation(proba, incoming)

    return {
        "prediction": pred,
        "fraud_probability": round(proba, 4),
        "explanation": explanation
    }


@app.post("/explain")
def explain(payload: WalletFeatures):
    incoming = payload.features

    missing = [col for col in feature_columns if col not in incoming]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing features: {missing[:10]}"
        )

    row = np.array([[incoming[col] for col in feature_columns]])
    row_scaled = scaler.transform(row)

    pred = int(model.predict(row_scaled)[0])
    proba = float(model.predict_proba(row_scaled)[0][1])

    reasons = generate_feature_reasons(incoming)

    try:
        print("🚀 Trying AI...") 
        analyst_summary = generate_ai_summary(proba, reasons, pred)
    except Exception as e:
        print("❌ AI failed:", e)
        analyst_summary = build_rule_based_explanation(proba, incoming)

    return {
        "prediction": pred,
        "fraud_probability": round(proba, 4),
        "top_signals": reasons,
        "analyst_summary": analyst_summary
    }