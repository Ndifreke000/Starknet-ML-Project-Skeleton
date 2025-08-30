# src/preprocess.py
import pandas as pd
from pathlib import Path

RAW = Path("data/raw.csv")
OUT = Path("data/processed.csv")

def ensure_hex(s):
    if pd.isna(s): return None
    s = str(s)
    return s if s.startswith("0x") else "0x" + s

def preprocess(inpath: Path = RAW, outpath: Path = OUT):
    df = pd.read_csv(inpath, dtype=str)
    # cast numeric columns safely
    df["block_number"] = pd.to_numeric(df["block_number"], errors="coerce").astype("Int64")
    df["block_timestamp"] = pd.to_numeric(df["block_timestamp"], errors="coerce")
    df["tx_hash"] = df["tx_hash"].astype(str)
    df["tx_type"] = df["tx_type"].fillna("unknown").astype(str)
    df["sender"] = df["sender"].apply(ensure_hex)
    df["calldata_len"] = pd.to_numeric(df["calldata_len"], errors="coerce").fillna(0).astype(int)

    # time features
    df["block_datetime"] = pd.to_datetime(df["block_timestamp"], unit="s", origin="unix", errors="coerce")
    df["hour"] = df["block_datetime"].dt.hour.fillna(-1).astype(int)

    # encode tx_type as categorical code (simple)
    df["tx_type_code"] = df["tx_type"].astype("category").cat.codes

    # reorder & save
    cols = ["block_number", "block_timestamp", "block_datetime", "hour",
            "tx_hash", "tx_type", "tx_type_code", "sender", "calldata_len"]
    df = df[cols]
    outpath.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(outpath, index=False)
    print(f"✅ Wrote {len(df)} rows to {outpath}")
    return df

if __name__ == "__main__":
    preprocess()
