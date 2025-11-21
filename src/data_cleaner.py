# TODO: implement data ingestion logic
from dataclasses import dataclass
from typing import Dict

import pandas as pd


@dataclass
class CleaningStats:
    rows_before: int = 0
    rows_after: int = 0
    cols_before: int = 0
    cols_after: int = 0

    def to_dict(self) -> Dict[str, int]:
        return {
            "rows_before": self.rows_before,
            "rows_after": self.rows_after,
            "cols_before": self.cols_before,
            "cols_after": self.cols_after,
        }


class DataCleaner:
    """
    Simple cleaning pipeline.

    Responsibilities:
      - handle nulls
      - unify basic formats
      - encode categorical features (very basic version)
    """

    def __init__(self, null_strategy: str = "drop") -> None:
        """
        :param null_strategy: "drop" or "fill".
        """
        if null_strategy not in {"drop", "fill"}:
            raise ValueError("null_strategy must be 'drop' or 'fill'")
        self.null_strategy = null_strategy
        self.stats = CleaningStats()

    # --------- individual steps ---------

    def remove_nulls(self, df: pd.DataFrame) -> pd.DataFrame:
        if self.null_strategy == "drop":
            return df.dropna(how="any")

        # Simple fill strategy:
        fill_values = {
            col: 0 if pd.api.types.is_numeric_dtype(df[col]) else "Unknown"
            for col in df.columns
        }
        return df.fillna(fill_values)

    def unify_formats(self, df: pd.DataFrame) -> pd.DataFrame:
        # Example: normalize names and regions
        for col in df.columns:
            col_lower = col.lower()
            if "nom" in col_lower or "name" in col_lower:
                df[col] = df[col].astype(str).str.strip()
            if "region" in col_lower:
                df[col] = df[col].astype(str).str.strip().str.title()

        # Example: try parsing any column that looks like a date
        for col in df.columns:
            if "date" in col.lower():
                try:
                    df[col] = pd.to_datetime(df[col], errors="coerce")
                except Exception:
                    # keep original if parsing fails
                    pass
        return df

    def encode_categoricals(self, df: pd.DataFrame) -> pd.DataFrame:
        # Very simple rule: one-hot encode object columns with few unique values
        cat_cols = [
            c for c in df.columns if df[c].dtype == "object" and df[c].nunique() < 30
        ]
        if not cat_cols:
            return df

        df_encoded = pd.get_dummies(df, columns=cat_cols, drop_first=True)
        return df_encoded

    # --------- full pipeline ---------

    def clean_pipeline(self, df: pd.DataFrame) -> pd.DataFrame:
        self.stats.rows_before, self.stats.cols_before = df.shape

        df = self.remove_nulls(df)
        df = self.unify_formats(df)
        df = self.encode_categoricals(df)

        self.stats.rows_after, self.stats.cols_after = df.shape
        return df
