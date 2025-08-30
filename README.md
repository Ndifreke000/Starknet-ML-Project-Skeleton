# Starknet ML Project - Blockchain Transaction Anomaly Detection

A machine learning pipeline that fetches Starknet blockchain data, processes transactions, trains an Isolation Forest model to detect anomalies, and visualizes the results. The system analyzes transaction patterns to identify unusual activity based on calldata length, transaction timing, and type.

## Overview

This project implements a complete ML pipeline that:
1. **Fetches** recent transaction data from Starknet blocks
2. **Preprocesses** and engineers features from raw blockchain data
3. **Trains** an Isolation Forest model to detect anomalous transactions
4. **Visualizes** the detected anomalies

## Project Structure

```
Starknet-ML-Project-Skeleton/
├── main.py              # Main pipeline orchestrator
├── requirements.txt     # Python dependencies
├── pyproject.toml
├── .gitignore
├── uv.lock
├── data/               # Data storage
│   ├── raw.csv                # Raw transaction data
│   ├── processed.csv          # Preprocessed data
│   ├── processed_with_anomaly.csv  # Data with anomaly labels
│   └── anomaly_scatter.png    # Visualization output
├── models/             # Model storage
│   └── if_model.pkl          # Trained Isolation Forest model
├── .python-version
└── src/               # Source code
    ├── __init__.py           # Package initialization
    ├── config.py             # Configuration (RPC URL)
    ├── fetch_data.py         # Blockchain data fetching
    ├── preprocess.py         # Data preprocessing
    ├── train.py             # Model training
    └── visualize.py         # Result visualization
```

## Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/Ndifreke000/Starknet-ML-Project-Skeleton.git
   cd Starknet-ML-Project-Skeleton
   ```
2. **Activate a virtual environment (recommended)**
   ```bash
   uv venv
   source .venv/bin/activate  # On Windows use `.venv\Scripts\activate`
   ```

3. **Install dependencies**
   ```bash
   uv sync
   or
   pip install -r requirements.txt
   ```

   Dependencies include:
   - `starknet-py`: Starknet Python SDK for blockchain interaction
   - `pandas`: Data manipulation and analysis
   - `scikit-learn`: Machine learning algorithms
   - `matplotlib`: Data visualization
   - `joblib`: Model serialization

4. **Configure RPC endpoint**
   Edit `src/config.py` to set your Starknet RPC URL:
   ```python
   RPC_URL = "your-starknet-rpc-url-here"
   ```

## Usage

### Run Complete Pipeline
```bash
python main.py
```

This executes the full pipeline:
1. Fetches the last 20 blocks of transaction data
2. Preprocesses and engineers features
3. Trains an Isolation Forest model
4. Generates anomaly visualization

### Run Individual Components

**Fetch data only:**
```bash
python -m src.fetch_data
```

**Preprocess data:**
```bash
python -m src.preprocess
```

**Train model:**
```bash
python -m src.train
```

**Generate visualization:**
```bash
python -m src.visualize
```

## Pipeline Details

### 1. Data Fetching (`src/fetch_data.py`)
- Connects to Starknet RPC endpoint
- Fetches recent blocks and their transactions
- Extracts key features:
  - Block number and timestamp
  - Transaction hash and type
  - Sender address
  - Calldata length

### 2. Data Preprocessing (`src/preprocess.py`)
- Converts data types and handles missing values
- Creates datetime features from timestamps
- Encodes categorical transaction types
- Extracts hour-of-day features
- Ensures proper hexadecimal formatting for addresses

### 3. Model Training (`src/train.py`)
- Uses Isolation Forest algorithm for anomaly detection
- Features used: calldata length, hour of day, transaction type
- Automatically determines contamination rate
- Saves trained model and labeled data

### 4. Visualization (`src/visualize.py`)
- Generates scatter plot of anomalies
- X-axis: Calldata length
- Y-axis: Block number
- Color-coded by anomaly status (red = anomaly)

## Output Files

- `data/raw.csv`: Raw transaction data from Starknet
- `data/processed.csv`: Cleaned and feature-engineered data
- `data/processed_with_anomaly.csv`: Data with anomaly labels
- `models/if_model.pkl`: Serialized Isolation Forest model
- `data/anomaly_scatter.png`: Visualization of detected anomalies

## Configuration

Modify `src/config.py` to change the RPC endpoint:
```python
RPC_URL = "https://your-starknet-rpc-endpoint"
```

## Customization

### Adjust Number of Blocks
Edit `main.py` to change the number of blocks fetched:
```python
df = asyncio.run(fetch_blocks(50))  # Fetch 50 blocks instead of 20
```

### Modify Features
Edit `src/train.py` to use different features:
```python
features = df[["calldata_len", "hour", "tx_type_code", "block_number"]].fillna(0)
```

### Change Model Parameters
Adjust Isolation Forest parameters in `src/train.py`:
```python
model = IsolationForest(
    n_estimators=100, 
    contamination=0.1,  # Set specific contamination rate
    random_state=42
)
```

## Troubleshooting

### RPC Connection Issues
- Ensure your RPC endpoint is accessible
- Check network connectivity
- Verify the RPC URL in `src/config.py`

### Dependency Issues
```bash
# Reinstall dependencies if needed
pip install --upgrade -r requirements.txt
```

### Data Fetching Errors
- The script includes error handling for failed block/tx fetches
- Debug information is saved to `data/fetch_debug.json`

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the [MIT License](LICENSE).
