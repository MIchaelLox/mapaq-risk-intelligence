# TODO: implement data ingestion logic
from dataclasses import dataclass
from datetime import date
from typing import Any, Dict

from .probability_model import RestaurantFeatures, RiskModel
from .regulation_adapter import RegulationAdapter


@dataclass
class PredictInput:
    theme: str
    staff_count: int
    infractions_history: int
    kitchen_size: float
    region: str
    inspection_date: date

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "PredictInput":
        # inspection_date is expected in ISO format: YYYY-MM-DD
        try:
            inspection_date_str = data["inspection_date"]
            inspection_dt = date.fromisoformat(inspection_date_str)
        except Exception as exc:
            raise ValueError("Invalid or missing 'inspection_date'") from exc

        try:
            return cls(
                theme=str(data["theme"]),
                staff_count=int(data["staff_count"]),
                infractions_history=int(data["infractions_history"]),
                kitchen_size=float(data["kitchen_size"]),
                region=str(data["region"]),
                inspection_date=inspection_dt,
            )
        except KeyError as exc:
            raise ValueError(f"Missing required field: {exc.args[0]}") from exc


@dataclass
class PredictOutput:
    probability: float
    risk_level: str

    def to_dict(self) -> Dict[str, Any]:
        return {"probability": self.probability, "risk_level": self.risk_level}


class RiskService:
    """
    Business layer that combines RiskModel and RegulationAdapter.
    """

    def __init__(
        self,
        model: RiskModel | None = None,
        adapter: RegulationAdapter | None = None,
    ) -> None:
        self.model = model or RiskModel()
        self.adapter = adapter or RegulationAdapter()

    def predict(self, payload: Dict[str, Any]) -> PredictOutput:
        predict_input = PredictInput.from_dict(payload)
        features = RestaurantFeatures(
            theme=predict_input.theme,
            staff_count=predict_input.staff_count,
            infractions_history=predict_input.infractions_history,
            kitchen_size=predict_input.kitchen_size,
            region=predict_input.region,
        )
        base_prob = self.model.predict_probability(features)
        adjusted_prob = self.adapter.adjust_probability(
            base_prob, predict_input.inspection_date
        )
        level = self.model.categorize(adjusted_prob)
        return PredictOutput(probability=adjusted_prob, risk_level=level)


# Default instance used by the Flask app
risk_service = RiskService()

