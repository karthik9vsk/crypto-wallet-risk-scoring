import pandas as pd


def preprocess_dataframe(df: pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["Index", "Address", "Unnamed: 0"], errors="ignore")
    df = df.dropna()
    return df