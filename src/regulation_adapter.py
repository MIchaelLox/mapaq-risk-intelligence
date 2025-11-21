# TODO: implement data ingestion logic
from dataclasses import dataclass
from datetime import date


@dataclass
class RegulationAdapter:
    """
    Adjusts risk probabilities based on inspection date and regulation changes.

    Simple rule:
      - before early_year: slightly decrease probability (system was looser)
      - between early_year and strict_year: no change
      - after strict_year: slightly increase probability (stricter rules)
    """

    early_year: int = 2015
    strict_year: int = 2020
    early_factor: float = -0.05
    strict_factor: float = 0.05

    def adjust_probability(self, probability: float, inspection_date: date) -> float:
        adjusted = probability
        if inspection_date.year < self.early_year:
            adjusted += self.early_factor
        elif inspection_date.year >= self.strict_year:
            adjusted += self.strict_factor

        # Clip to [0, 1]
        adjusted = max(0.0, min(1.0, adjusted))
        return adjusted
