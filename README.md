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

---

## Recent Updates - Grace Mandiangu

### ✅ Implemented (November 2024)

**1. Data Ingestion Module** (`src/data_ingest.py`) - Grace Mandiangu
- Created `MAPAQDataIngestor` class for data loading
- CSV file loading with UTF-8 encoding support
- URL download functionality for remote datasets
- Data information and statistics extraction
- Logging system for tracking operations

**2. Regulations Configuration** (`data/regulations.json`) - Grace Mandiangu
- Structured JSON file for regulatory changes
- Regulation metadata with effective dates
- Impact weight system for temporal adjustments
- Version control and source tracking

**3. Data Cleaning & Normalization Module** (`src/data_cleaner.py`) - Grace Mandiangu
- Created `DataCleaner` class for data cleaning pipeline
- Column name normalization
- Duplicate removal and missing value handling
- Text field cleaning and standardization
- Cleaning report generation

**4. Conditional Probability Engine v2** (`src/probability_model.py`) - Grace Mandiangu
- Advanced Bayesian probability calculations for risk prediction
- Multi-factor risk assessment (cuisine, staff, infractions, kitchen size, region)
- Three-level risk categorization (Low/Medium/High)
- Conditional probability P(A|B) calculations from historical data
- Bayes theorem implementation for probabilistic inference
- Joint probability calculations P(A ∩ B ∩ C...) for multiple events
- Automatic learning of cuisine-specific risk probabilities from data
- Probability matrix generation for risk analysis
- Prior probability updates with new data
- Integration with temporal regulation adjustments

**5. REST API with /predict Endpoint** (`src/api.py`) - Grace Mandiangu
- Flask-based REST API implementation
- POST `/predict` endpoint for single restaurant risk prediction
- POST `/predict/batch` endpoint for multiple predictions
- GET `/health` endpoint for API health checks
- Input validation and error handling
- JSON response format with probabilities and confidence scores
- Support for temporal regulation adjustments via `inspection_date` parameter

**6. Temporal Regulation Weighting** (`src/regulation_adapter.py`) - Grace Mandiangu
- Automatic temporal adjustment of risk scores based on regulatory changes
- Loads regulation metadata from `data/regulations.json`
- Applies time-based impact weights to risk probabilities
- Calculates cumulative regulatory impact for specific inspection dates
- Integration with probability engine for seamless temporal adjustments
- Timeline tracking and regulation history management

### 📁 Current Project Structure
```
mapaq-risk-intelligence/
├── data/
│   ├── raw/                    # Raw data directory
│   ├── cleaned/                # Cleaned data directory
│   └── regulations.json        # Regulations config (Grace Mandiangu)
├── src/
│   ├── data_ingest.py          # Data ingestion module (Grace Mandiangu)
│   ├── data_cleaner.py         # Data cleaning module (Grace Mandiangu)
│   ├── probability_model.py    # Probability engine v2 (Grace Mandiangu)
│   ├── regulation_adapter.py   # Temporal regulation weighting (Grace Mandiangu)
│   └── api.py                  # REST API /predict (Grace Mandiangu)
├── dashboard/
│   └── templates/
└── tests/
```

### 🔄 Next Steps
- Implement `theme_classifier.py` for cuisine type classification
- Develop `address_geocoder.py` for address normalization and geocoding
- Build interactive dashboard with Flask/React
- Expand automated test coverage (pytest)
- Add data visualization components

---

## Usage Examples

### Using Temporal Regulation Weighting

```python
from datetime import datetime
from src.probability_model import ConditionalProbabilityEngine

# Initialize engine with temporal adjustments enabled
engine = ConditionalProbabilityEngine(enable_temporal_adjustment=True)

# Predict risk for a specific inspection date
risk_level, confidence = engine.predict_risk_level(
    cuisine_type="Sushi",
    staff_count=10,
    infractions_history=2,
    kitchen_size=35.0,
    region="Montreal",
    inspection_date=datetime(2023, 6, 15)
)

print(f"Risk Level: {risk_level} (Confidence: {confidence:.2%})")
```

### API Request with Inspection Date

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine_type": "Sushi",
    "staff_count": 10,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Quebec",
    "inspection_date": "2023-06-15"
  }'
```

### Managing Regulations

```python
from src.regulation_adapter import RegulationAdapter

adapter = RegulationAdapter()

# View regulation timeline
timeline = adapter.get_regulation_timeline()
for reg in timeline:
    print(f"{reg['effective_date']}: {reg['name']} (impact: {reg['impact_weight']})")

# Add new regulation
adapter.add_regulation(
    regulation_id="REG-2024-001",
    name="New Food Safety Standard",
    effective_date="2024-01-01",
    description="Enhanced hygiene requirements",
    impact_weight=1.3
)

# Save changes
adapter.save_regulations()
```

### Using Advanced Probability Features (v2) - Grace Mandiangu

```python
import pandas as pd
from src.probability_model import ConditionalProbabilityEngine

# Initialize engine
engine = ConditionalProbabilityEngine()

# Sample historical data
historical_data = pd.DataFrame({
    'cuisine_type': ['Sushi', 'Sushi', 'Italian', 'Fast Food', 'Sushi'],
    'risk_level': ['High', 'Medium', 'Low', 'Medium', 'High'],
    'region': ['Montreal', 'Montreal', 'Quebec', 'Laval', 'Montreal']
})

# 1. Calculate conditional probability P(High Risk | Sushi)
prob = engine.calculate_conditional_probability(
    event_a='High',
    event_b='Sushi',
    data=historical_data,
    column_a='risk_level',
    column_b='cuisine_type'
)
print(f"P(High Risk | Sushi) = {prob:.2%}")

# 2. Apply Bayes theorem
posterior = engine.calculate_bayes_theorem(
    hypothesis='High',
    evidence='Sushi',
    data=historical_data
)
print(f"Posterior probability: {posterior:.2%}")

# 3. Calculate joint probability P(Sushi ∩ High Risk ∩ Montreal)
joint_prob = engine.calculate_joint_probability(
    events={'cuisine_type': 'Sushi', 'risk_level': 'High', 'region': 'Montreal'},
    data=historical_data
)
print(f"Joint probability: {joint_prob:.2%}")

# 4. Learn probabilities from data
engine.learn_cuisine_probabilities(historical_data)

# 5. Generate probability matrix
prob_matrix = engine.get_probability_matrix(historical_data)
print("\nProbability Matrix:")
print(prob_matrix)

# 6. Update priors with new data
engine.update_priors(historical_data)
```

---

**Author:** Grace Mandiangu  
**Last Updated:** November 27, 2025