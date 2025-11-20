from pathlib import Path
import pandas as pd

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

def load_raw_mapaq() -> pd.DataFrame:
    csv_files = list(RAW_DIR.glob("*.csv"))
    if not csv_files:
        raise FileNotFoundError(f"No CSV files found in {RAW_DIR}")
    frames = [pd.read_csv(f) for f in csv_files]
    return pd.concat(frames, ignore_index=True)
