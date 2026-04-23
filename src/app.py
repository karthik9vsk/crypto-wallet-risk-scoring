import os
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from src.schemas import WalletFeatures
from src.explain import build_rule_based_explanation, generate_feature_reasons

openai_api_key = os.getenv("OPENAI_API_KEY")

client = None
if openai_api_key:
    from openai import OpenAI
    client = OpenAI(api_key=openai_api_key)

app = FastAPI(title="Crypto Fraud Intelligence API")

model = joblib.load("models/fraud_model.pkl")
scaler = joblib.load("models/scaler.pkl")
feature_columns = joblib.load("models/feature_columns.pkl")

app.mount("/static", StaticFiles(directory="static"), name="static")


def generate_ai_summary(probability: float, reasons: list[str], prediction: int) -> str:
    if client is None:
        raise RuntimeError("OPENAI_API_KEY not configured")

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
"""

    response = client.chat.completions.create(
        model="gpt-4.1-mini",
        messages=[{"role": "user", "content": prompt}]
    )

    return response.choices[0].message.content.strip()


@app.get("/", include_in_schema=False)
def home():
    return FileResponse("static/index.html")


@app.get("/health")
def health():
    return {"name": "Crypto Fraud Intelligence API", "status": "ok"}


@app.get("/sample-payload")
def sample_payload():
    df = pd.read_csv("data/raw/transaction_dataset.csv")
    df = df.drop(columns=["Index", "Address", "Unnamed: 0"], errors="ignore")
    df = df.dropna()

    X = df.drop("FLAG", axis=1)
    X = X.select_dtypes(include=[np.number])

    sample = X.iloc[0].to_dict()
    return {"features": sample}


@app.post("/predict")
def predict(payload: WalletFeatures):
    incoming = payload.features

    missing = [col for col in feature_columns if col not in incoming]
    if missing:
        raise HTTPException(
            status_code=400,
            detail=f"Missing features: {missing[:10]}"
        )

    row_df = pd.DataFrame([incoming])[feature_columns]
    row_scaled = scaler.transform(row_df)

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

    row_df = pd.DataFrame([incoming])[feature_columns]
    row_scaled = scaler.transform(row_df)

    pred = int(model.predict(row_scaled)[0])
    proba = float(model.predict_proba(row_scaled)[0][1])

    reasons = generate_feature_reasons(incoming)

    try:
        analyst_summary = generate_ai_summary(proba, reasons, pred)
        summary_source = "llm"
    except Exception:
        analyst_summary = build_rule_based_explanation(proba, incoming)
        summary_source = "rule_based_fallback"

    return {
        "prediction": pred,
        "fraud_probability": round(proba, 4),
        "top_signals": reasons,
        "analyst_summary": analyst_summary,
        "summary_source": summary_source
    }