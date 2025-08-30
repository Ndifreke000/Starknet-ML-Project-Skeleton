# src/visualize.py
import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

IN = Path("data/processed_with_anomaly.csv")

def plot(inpath: Path = IN):
    df = pd.read_csv(inpath)
    # scatter calldata_len vs block_number colored by anomaly
    plt.figure(figsize=(10,5))
    plt.scatter(df["calldata_len"], df["block_number"], c=df["anomaly"], alpha=0.6)
    plt.xlabel("calldata_len")
    plt.ylabel("block_number")
    plt.title("Anomalies (red=1) by calldata_len vs block")
    plt.tight_layout()
    plt.savefig("data/anomaly_scatter.png")
    print("✅ Saved data/anomaly_scatter.png")

if __name__ == "__main__":
    plot()
