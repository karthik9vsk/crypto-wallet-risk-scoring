import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier

DATA_PATH = "data/raw/transaction_dataset.csv"

def load_data():
    df = pd.read_csv(DATA_PATH)
    df = df.drop(columns=["Index", "Address", "Unnamed: 0"], errors="ignore")
    df = df.dropna()

    X = df.drop("FLAG", axis=1)
    X = X.select_dtypes(include=[np.number])
    y = df["FLAG"]

    return X, y

def train():
    X, y = load_data()

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)

    model = RandomForestClassifier(
        n_estimators=200,
        class_weight="balanced",
        random_state=42
    )
    model.fit(X_train_scaled, y_train)

    joblib.dump(model, "models/fraud_model.pkl")
    joblib.dump(scaler, "models/scaler.pkl")
    joblib.dump(list(X.columns), "models/feature_columns.pkl")

    print("Saved model, scaler, and feature columns.")

if __name__ == "__main__":
    train()