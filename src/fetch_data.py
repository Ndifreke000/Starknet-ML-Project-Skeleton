# src/fetch_data.py
import asyncio
import json
import time
from pathlib import Path

import pandas as pd
from starknet_py.net.full_node_client import FullNodeClient
from src.config import RPC_URL

OUT_CSV = Path("data/raw.csv")
DEBUG_JSON = Path("data/fetch_debug.json")


def safe_getattr(obj, *names, default=None):
    for name in names:
        try:
            val = getattr(obj, name, None)
        except Exception:
            val = None
        if val is not None:
            return val
    # dict-like fallback
    try:
        if isinstance(obj, dict):
            for name in names:
                if name in obj and obj[name] is not None:
                    return obj[name]
    except Exception:
        pass
    return default


def _tx_hash_of(tx_obj, fallback):
    h = safe_getattr(tx_obj, "hash", "tx_hash", "transaction_hash", default=None)
    if h is not None:
        return str(h)
    # dict-like fallback
    try:
        if isinstance(tx_obj, dict):
            for k in ("hash", "tx_hash", "transaction_hash"):
                if k in tx_obj and tx_obj[k]:
                    return str(tx_obj[k])
    except Exception:
        pass
    return str(fallback) if fallback is not None else None


def _sender_of(tx_obj):
    s = safe_getattr(tx_obj, "sender_address", "from_address", "caller_address", default=None)
    return str(s) if s is not None else None


def _calldata_len(tx_obj):
    val = safe_getattr(tx_obj, "calldata", "call_data", "data", default=None)
    if val is None:
        return 0
    # list-like calldata
    if isinstance(val, (list, tuple)):
        return len(val)
    # hex / bytes fallback — estimate bytes
    if isinstance(val, (str, bytes)):
        try:
            s = val.decode() if isinstance(val, bytes) else val
            if s.startswith("0x"):
                s = s[2:]
            return max(0, len(s) // 2)
        except Exception:
            return len(val)
    return 0


async def fetch_blocks(n=10, sleep_between_tx=0.01):
    client = FullNodeClient(node_url=RPC_URL)

    try:
        latest = await client.get_block("latest")
    except Exception as e:
        print("Failed to fetch latest block:", e)
        return pd.DataFrame([])

    rows = []
    start = getattr(latest, "block_number", None)
    if start is None:
        print("Latest block missing block_number; aborting.")
        return pd.DataFrame([])

    end = max(0, start - n + 1)
    debug_samples = []

    for i in range(start, end - 1, -1):
        try:
            block = await client.get_block(block_number=i)
        except Exception as e:
            print(f"Error fetching block {i}: {e}")
            continue

        txs_field = safe_getattr(block, "transactions", default=[])
        tx_hashes_field = safe_getattr(block, "transaction_hashes", default=None)

        # Case A: block.transactions holds full tx objects (your node's case)
        if txs_field and not isinstance(txs_field[0], (str, bytes)):
            for tx_obj in txs_field:
                try:
                    tx_hash = _tx_hash_of(tx_obj, fallback=None)
                    tx_type = type(tx_obj).__name__
                    sender = _sender_of(tx_obj)
                    calldata_len = _calldata_len(tx_obj)
                except Exception as e:
                    tx_hash = None
                    tx_type = None
                    sender = None
                    calldata_len = None
                    print(f"Error extracting fields from tx object in block {i}: {e}")

                rows.append({
                    "block_number": i,
                    "block_timestamp": getattr(block, "timestamp", None),
                    "tx_hash": tx_hash,
                    "tx_type": tx_type,
                    "sender": sender,
                    "calldata_len": calldata_len,
                })
                if sleep_between_tx:
                    await asyncio.sleep(sleep_between_tx)

        # Case B: block.transactions is a list of hashes (strings) or node provided transaction_hashes
        else:
            tx_hashes = tx_hashes_field or txs_field or []
            # normalize hash bytes -> str
            tx_hashes = [h.decode() if isinstance(h, (bytes, bytearray)) else str(h) for h in tx_hashes]

            if not tx_hashes:
                debug_samples.append({
                    "block_number": i,
                    "transactions_field_type": type(txs_field).__name__,
                    "transactions_repr": repr(txs_field)[:400],
                })
                print(f"No usable tx info in block {i}.")
                continue

            for tx_hash in tx_hashes:
                try:
                    tx = await client.get_transaction(tx_hash)
                    tx_hash_final = _tx_hash_of(tx, tx_hash)
                    tx_type = type(tx).__name__
                    sender = _sender_of(tx)
                    calldata_len = _calldata_len(tx)
                except Exception as e:
                    # best-effort: record the hash even if get_transaction failed
                    tx_hash_final = tx_hash
                    tx_type = None
                    sender = None
                    calldata_len = None
                    print(f"Could not fetch tx {tx_hash} in block {i}: {e}")

                rows.append({
                    "block_number": i,
                    "block_timestamp": getattr(block, "timestamp", None),
                    "tx_hash": tx_hash_final,
                    "tx_type": tx_type,
                    "sender": sender,
                    "calldata_len": calldata_len,
                })
                if sleep_between_tx:
                    await asyncio.sleep(sleep_between_tx)

    # write debug samples if any
    if debug_samples:
        try:
            DEBUG_JSON.parent.mkdir(parents=True, exist_ok=True)
            with DEBUG_JSON.open("w") as f:
                json.dump({"samples": debug_samples, "timestamp": time.time()}, f, indent=2)
            print(f"Wrote debug samples to {DEBUG_JSON}")
        except Exception as e:
            print("Failed to write debug JSON:", e)

    if not rows:
        return pd.DataFrame([])

    return pd.DataFrame(rows)


if __name__ == "__main__":
    df = asyncio.run(fetch_blocks(20))
    if not df.empty:
        OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
        df.to_csv(OUT_CSV, index=False)
        print(f"✅ Saved {len(df)} transactions to {OUT_CSV}")
    else:
        print("⚠️ No transactions fetched.")
