# main.py
import asyncio
from src.fetch_data import fetch_blocks
from src.preprocess import preprocess
from src.train import train
from src.visualize import plot

def run():
    # 1. fetch data
    df = asyncio.run(fetch_blocks(20))
    if df is None or df.empty:
        print("No rows fetched; aborting pipeline.")
        return
    df.to_csv("data/raw.csv", index=False)
    # 2. preprocess
    preprocess()
    # 3. train
    train()
    # 4. visualize
    plot()

if __name__ == "__main__":
    run()
