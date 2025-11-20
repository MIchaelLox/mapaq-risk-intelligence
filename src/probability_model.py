from typing import Dict, Tuple
import pandas as pd

from .data_cleaner import build_clean_dataset
from .regulation_adapter import get_regulation_weight

def compute_conditional_probabilities() -> Dict[Tuple[str, str], float]:
   df = build_clean_dataset()
   # assume 'theme' column exists later; for now you can stub or add a fake theme
   if "theme" not in df.columns:
       df["theme"] = "unknown"

   df["has_infraction"] = df["infraction_count"] > 0
   grouped = df.groupby(["theme", "city"])["has_infraction"].mean()

   return {(theme, city): float(p) for (theme, city), p in grouped.items()}

def get_risk_for(theme: str, city: str) -> float:
   probs = compute_conditional_probabilities()
   base_p = probs.get((theme, city), 0.0)
   # You can later adjust with regulation weights if using a date:
   # For now, return base probability only.
   return base_p
