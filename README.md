# 🧬 MAPAQ Risk Intelligence

## Overview
Probabilistic model predicting sanitary risk levels for restaurants using MAPAQ inspection data,  
machine learning, and rule-based adjustments.

---

## Features
- Automated data ingestion from public MAPAQ datasets  
- Address geocoding + cuisine classification  
- Conditional probability calculations  
- Regulation-aware weighting (temporal changes)  
- Risk scoring + trend analytics  
- Interactive dashboard (Flask/React)  
- REST API `/predict`

---

## Architecture

mapaq-risk-intelligence/

├── data/

│ ├── raw/

│ ├── cleaned/

│ └── regulations.json

├── src/

│ ├── data_ingest.py

│ ├── data_cleaner.py

│ ├── theme_classifier.py

│ ├── address_geocoder.py

│ ├── probability_model.py

│ ├── regulation_adapter.py

│ └── api.py

├── dashboard/

│ ├── app.py

│ └── templates/

├── tests/

│ ├── test_model.py

│ ├── test_api.py

│ └── test_regulation_adapter.py

└── README.md


---

## Risk Model
- Baseline: Logistic Regression / Naïve Bayes  
- Features: theme, staff count, infractions history, kitchen size, region.  
- Output: Probability ∈ [0, 1], categorized as Low / Medium / High.  

---

## Phase 2 Development Tasks
1. Rebuild data pipeline with robust cleaning and normalization.  
2. Implement regulation-aware temporal adjustment (effective dates).  
3. Extend model with conditional probabilities between variables.  
4. Build REST API `/predict` returning JSON scores.  
5. Design interactive dashboard with charts + map (Plotly/D3/Leaflet).  
6. Add automated tests and docs.

---

## Technologies
Python 3.10, pandas, scikit-learn, Flask/FastAPI, Plotly, Leaflet, pytest.
