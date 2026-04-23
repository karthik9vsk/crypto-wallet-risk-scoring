# Crypto Fraud Intelligence API

A Python-based crypto wallet fraud detection system that serves wallet risk predictions through a FastAPI backend.

## Features
- Supervised fraud detection using transaction behavior features
- Risk scoring for suspicious wallets
- Rule-based explanation layer for interpretability
- API endpoints for prediction and explanation
- Interactive API documentation using FastAPI

## Tech Stack
- Python
- Pandas
- Scikit-learn
- FastAPI
- Uvicorn
- Joblib

## Project Structure
- `data/raw/` → raw datasets
- `src/train.py` → train and save model
- `src/app.py` → FastAPI backend
- `models/` → trained model artifacts

## Run the project
1. Install dependencies:
   ```bash
   pip install -r requirements.txt