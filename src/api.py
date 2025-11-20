from fastapi import FastAPI
from pydantic import BaseModel

from .probability_model import get_risk_for

app = FastAPI(title="MAPAQ Risk API")

class PredictRequest(BaseModel):
   theme: str
   city: str

class PredictResponse(BaseModel):
   probability: float
   risk_level: str

def _risk_label(p: float) -> str:
   if p < 0.33:
       return "low"
   if p < 0.66:
       return "medium"
   return "high"

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest):
   p = get_risk_for(req.theme, req.city)
   return PredictResponse(probability=p, risk_level=_risk_label(p))
