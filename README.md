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
- Bayesian probability calculations for risk prediction
- Multi-factor risk assessment (cuisine, staff, infractions, kitchen size, region)
- Three-level risk categorization (Low/Medium/High)
- Conditional probability adjustments based on restaurant features
- Prior probability updates with new data

**5. REST API with /predict Endpoint** (`src/api.py`) - Grace Mandiangu
- Flask-based REST API implementation
- POST `/predict` endpoint for single restaurant risk prediction
- POST `/predict/batch` endpoint for multiple predictions
- GET `/health` endpoint for API health checks
- Input validation and error handling
- JSON response format with probabilities and confidence scores

### 📁 Current Project Structure
```
mapaq-risk-intelligence/
├── data/
│   ├── raw/                    # Raw data directory
│   ├── cleaned/                # Cleaned data directory
│   └── regulations.json        # ✅ Regulations config (Grace Mandiangu)
├── src/
│   ├── data_ingest.py          # ✅ Data ingestion module (Grace Mandiangu)
│   ├── data_cleaner.py         # ✅ Data cleaning module (Grace Mandiangu)
│   ├── probability_model.py    # ✅ Probability engine v2 (Grace Mandiangu)
│   └── api.py                  # ✅ REST API /predict (Grace Mandiangu)
├── dashboard/
│   └── templates/
└── tests/
```

### 🔄 Next Steps
- Implement `theme_classifier.py` for cuisine type classification
- Develop `address_geocoder.py` for address normalization and geocoding
- Create `regulation_adapter.py` for temporal regulation adjustments
- Build interactive dashboard with Flask/React
- Add automated tests (pytest)

---

**Author:** Grace Mandiangu  
**Last Updated:** November 24, 2025