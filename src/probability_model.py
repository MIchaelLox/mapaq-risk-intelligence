# TODO: implement data ingestion logic
from dataclasses import dataclass
from typing import Literal

import numpy as np

RiskLevel = Literal["Low", "Medium", "High"]


@dataclass
class RestaurantFeatures:
    theme: str
    staff_count: int
    infractions_history: int
    kitchen_size: float
    region: str


class RiskModel:
    """
    Simple rule-based risk model.

    API:
      - predict_probability(features) -> float in [0, 1]
      - categorize(prob) -> 'Low' | 'Medium' | 'High'

    We can later replace the internals with a real scikit-learn model.
    """

    def predict_probability(self, features: RestaurantFeatures) -> float:
        # Base score
        score = 0.15

        # Infractions history (cap at 5)
        score += 0.15 * min(features.infractions_history, 5) / 5.0

        # Kitchen size (cap at 200 m²)
        score += 0.10 * min(features.kitchen_size, 200.0) / 200.0

        # Staff count (cap at 30)
        score += 0.10 * min(features.staff_count, 30) / 30.0

        # Theme adjustment
        theme_lower = features.theme.lower()
        if "sushi" in theme_lower or "raw" in theme_lower:
            score += 0.15
        elif "bbq" in theme_lower or "fried" in theme_lower:
            score += 0.10
        elif "bakery" in theme_lower:
            score += 0.05

        # Region adjustment (example only)
        if "montreal" in features.region.lower():
            score += 0.05

        prob = float(np.clip(score, 0.0, 1.0))
        return prob

    @staticmethod
    def categorize(probability: float) -> RiskLevel:
        if probability < 0.33:
            return "Low"
        if probability < 0.66:
            return "Medium"
        return "High"

