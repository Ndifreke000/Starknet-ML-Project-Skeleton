# src/train.py
import joblib
import pandas as pd
from pathlib import Path
from sklearn.ensemble import IsolationForest

PROC = Path("data/processed.csv")
OUT = Path("data/processed_with_anomaly.csv")
MODEL_PATH = Path("models/if_model.pkl")

def train(input_csv: Path = PROC, model_path: Path = MODEL_PATH, out_csv: Path = OUT):
    df = pd.read_csv(input_csv)
    # choose simple numeric features
    features = df[["calldata_len", "hour", "tx_type_code"]].fillna(0)

    model = IsolationForest(n_estimators=200, contamination="auto", random_state=42)
    preds = model.fit_predict(features)  # -1 = anomaly, 1 = normal
    df["anomaly"] = (preds == -1).astype(int)

    model_path.parent.mkdir(parents=True, exist_ok=True)
    joblib.dump(model, model_path)
    out_csv.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_csv, index=False)
    print(f"✅ Trained model and wrote results to {out_csv} and model to {model_path}")
    return df

if __name__ == "__main__":
    train()
