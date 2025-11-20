from pathlib import Path
from typing import Dict
import pandas as pd

from .data_ingest import load_raw_mapaq

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
CLEANED_DIR = DATA_DIR / "cleaned"
CLEANED_DIR.mkdir(parents=True, exist_ok=True)
CLEANED_FILE = CLEANED_DIR / "mapaq_cleaned.csv"

# Standardize multiple possible column names
COLUMN_MAPPING: Dict[str, str] = {
    "RestaurantName": "name",
    "NomEtablissement": "name",
    "Address": "address",
    "Adresse": "address",
    "City": "city",
    "Ville": "city",
    "Theme": "theme",
    "Categorie": "theme",
    "InspectionDate": "inspection_date",
    "DateInspection": "inspection_date",
    "InfractionCount": "infraction_count",
    "NombreInfractions": "infraction_count",
}

REQUIRED_COLS = {"name", "address", "city", "theme", "infraction_count"}


def _standardize_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Map inconsistent column names to a consistent schema."""
    rename_map = {c: COLUMN_MAPPING[c] for c in df.columns if c in COLUMN_MAPPING}
    df = df.rename(columns=rename_map)
    return df


def _basic_cleanup(df: pd.DataFrame) -> pd.DataFrame:
    """Keep essential columns, clean datatypes, drop duplicates."""
    # Keep only required columns if present
    existing = [c for c in REQUIRED_COLS if c in df.columns]
    df = df[existing].copy()

    # Drop completely empty rows
    df = df.dropna(how="all")

    # Fill missing values
    if "infraction_count" in df.columns:
        df["infraction_count"] = (
            df["infraction_count"]
            .fillna(0)
            .astype(int)
        )

    # Optional: theme defaults
    if "theme" in df.columns:
        df["theme"] = df["theme"].fillna("unknown")

    return df


def build_clean_dataset() -> pd.DataFrame:
    """
    Load raw CSVs, normalize schema, ensure required columns exist,
    clean data, and save cleaned CSV.
    """
    raw = load_raw_mapaq()
    df = _standardize_columns(raw)

    # Check required columns exist
    missing = REQUIRED_COLS - set(df.columns)
    if missing:
        raise ValueError(f"Missing required columns after standardization: {missing}")

    df = _basic_cleanup(df)

    # Save cleaned CSV
    df.to_csv(CLEANED_FILE, index=False)
    return df


if __name__ == "__main__":
    df = build_clean_dataset()
    print(f"Saved cleaned dataset to {CLEANED_FILE} with {len(df)} rows")
