from flask import Flask, render_template, request
from src.probability_model import get_risk_for

app = Flask(__name__)

THEMES = ["fast_food", "casual_dining", "fine_dining"]
CITIES = ["Montreal", "Quebec", "Laval"]

@app.route("/", methods=["GET", "POST"])
def index():
   probability = None
   risk_level = None

   if request.method == "POST":
       theme = request.form["theme"]
       city = request.form["city"]
       p = get_risk_for(theme, city)
       probability = round(p, 3)
       if p < 0.33:
           risk_level = "Low"
       elif p < 0.66:
           risk_level = "Medium"
       else:
           risk_level = "High"

   return render_template(
       "index.html",
       themes=THEMES,
       cities=CITIES,
       probability=probability,
       risk_level=risk_level,
   )
