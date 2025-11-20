# TODO: implement data ingestion logic
from pathlib import Path
from typing import Optional

import pandas as pd

from .config import MAPAQ_RAW_CSV


class DataIngestor:
    """
    Data ingestion layer for MAPAQ inspections.

    For now it only reads a local CSV. Later we can add:
      - download from a URL
      - add caching
      - validate the full schema
    """

    def __init__(self, source_path: Optional[Path | str] = None) -> None:
        self.source_path = Path(source_path) if source_path else MAPAQ_RAW_CSV

    def load(self) -> pd.DataFrame:
        """
        Load the inspections CSV as a DataFrame.

        :raises FileNotFoundError: if the file does not exist.
        """
        if not self.source_path.exists():
            raise FileNotFoundError(
                f"MAPAQ inspections CSV not found at: {self.source_path}"
            )

        df = pd.read_csv(self.source_path)
        return df
