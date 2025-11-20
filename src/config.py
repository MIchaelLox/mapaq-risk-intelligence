from pathlib import Path

# Base directory of the project (repo root)
BASE_DIR = Path(__file__).resolve().parent.parent

# Data folders
DATA_DIR = BASE_DIR / "data"
RAW_DIR = DATA_DIR / "raw"
CLEANED_DIR = DATA_DIR / "cleaned"
REGULATIONS_FILE = DATA_DIR / "regulations.json"

# Data files (you can rename these when you have the real CSVs)
MAPAQ_RAW_CSV = RAW_DIR / "mapaq_inspections.csv"
MAPAQ_CLEAN_CSV = CLEANED_DIR / "mapaq_cleaned.csv"

# Model directory (for a future trained model)
MODEL_DIR = BASE_DIR / "models"
MODEL_DIR.mkdir(exist_ok=True)

MODEL_FILE = MODEL_DIR / "risk_model.joblib"

# API prefix (used by Flask and the dashboard)
API_PREFIX = "/api/v1"

