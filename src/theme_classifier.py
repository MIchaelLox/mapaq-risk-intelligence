# TODO: implement data ingestion logic
from dataclasses import dataclass, field
from typing import Dict, List


DEFAULT_THEME_KEYWORDS: Dict[str, List[str]] = {
    "Sushi": ["sushi", "sashimi", "izakaya"],
    "Italian": ["pasta", "pizza", "trattoria", "ristorante"],
    "BBQ": ["bbq", "barbecue", "smokehouse"],
    "Bakery": ["boulangerie", "bakery", "patisserie", "bakeshop"],
    "Fast Food": ["burger", "fries", "fast food", "quick"],
}


@dataclass
class ThemeClassifier:
    """
    Simple keyword-based classifier.

    We can later replace this with the full dictionary logic from the TRACK-B repo.
    """

    theme_keywords: Dict[str, List[str]] = field(
        default_factory=lambda: DEFAULT_THEME_KEYWORDS
    )

    def classify(self, restaurant_name: str) -> str:
        name = restaurant_name.lower()
        for theme, keywords in self.theme_keywords.items():
            if any(kw in name for kw in keywords):
                return theme
        return "Other"


