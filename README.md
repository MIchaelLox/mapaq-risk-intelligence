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

**4. Conditional Probability Engine v3 (Enhanced)** (`src/probability_model.py`) - Grace Mandiangu
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
- **Model calibration with historical data** (NEW - Grace Mandiangu)
- **Cross-validation and performance metrics** (accuracy, precision, recall, F1) (NEW - Grace Mandiangu)
- **Sensitivity analysis** for factor importance (NEW - Grace Mandiangu)
- **Confidence intervals** for predictions with entropy-based scoring (NEW - Grace Mandiangu)
- **Model persistence** (save/load calibrated models) (NEW - Grace Mandiangu)
- **Comprehensive test suite** (`test_enhanced_model.py`) (NEW - Grace Mandiangu)

**5. REST API with /predict Endpoint** (`src/api.py`) - Grace Mandiangu
- Flask-based REST API implementation
- POST `/predict` endpoint for single restaurant risk prediction
- POST `/predict/batch` endpoint for multiple predictions
- POST `/predict/explain` endpoint for detailed explanations with contributing factors (NEW - Grace Mandiangu)
- GET `/health` endpoint for API health checks
- Input validation and error handling
- JSON response format with probabilities and confidence scores
- Support for temporal regulation adjustments via `inspection_date` parameter
- Automated recommendation system based on risk factors (NEW - Grace Mandiangu)
- Confidence interpretation for prediction reliability (NEW - Grace Mandiangu)
- Startup script `run_api.py` for easy deployment (NEW - Grace Mandiangu)
- Comprehensive API documentation in `API_EXAMPLES.md` (NEW - Grace Mandiangu)

**6. Temporal Regulation Weighting** (`src/regulation_adapter.py`) - Grace Mandiangu
- Automatic temporal adjustment of risk scores based on regulatory changes
- Loads regulation metadata from `data/regulations.json`
- Applies time-based impact weights to risk probabilities
- Calculates cumulative regulatory impact for specific inspection dates
- Integration with probability engine for seamless temporal adjustments
- Timeline tracking and regulation history management

**7. Interactive Dashboard** (`dashboard/`) - Grace Mandiangu
- Flask-based web dashboard with modern UI (TailwindCSS)
- Real-time statistics cards (total restaurants, risk distribution)
- Interactive Plotly visualizations:
  - Pie chart for risk distribution
  - Bar charts for regional and cuisine type analysis
  - Gauge chart for average risk level
- Responsive design for mobile and desktop
- Multiple pages: Home, Dashboard, Prediction Form, About
- Error handling pages (404, 500)
- Startup script `run_dashboard.py` for easy deployment
- Integrated API endpoints for data fetching

**8. Full Data Pipeline** (`src/data_pipeline.py`) - Grace Mandiangu
- Complete end-to-end data processing orchestration
- 5-stage pipeline: Ingestion → Validation → Cleaning → Transformation → Output
- Configurable via JSON configuration file (`pipeline_config.json`)
- Automated data quality validation with business rules
- Advanced data cleaning with multiple strategies:
  - Missing values handling (drop, mean, median, mode)
  - Outlier detection (IQR and Z-score methods)
  - Text normalization and standardization
- Data transformation and feature engineering:
  - Staff categorization (Très petit, Petit, Moyen, Grand)
  - Risk categorization (Aucun, Faible, Moyen, Élevé)
  - Derived features creation
- Multi-format output (CSV, JSON)
- Comprehensive reporting with statistics and quality metrics
- Startup script `run_pipeline.py` with CLI interface
- Enhanced `data_ingest.py` with schema validation and encoding detection
- Enhanced `data_cleaner.py` with advanced cleaning methods

**9. Automated Testing & Documentation** (`tests/`, `TESTING.md`) - Grace Mandiangu
- Complete pytest-based testing framework
- 95%+ code coverage across all modules
- Test suites for all components:
  - `test_data_ingest.py` - Data ingestion tests (15+ tests)
  - `test_data_cleaner.py` - Data cleaning tests (18+ tests)
  - `test_probability_model.py` - Model tests (20+ tests)
  - `test_api.py` - API endpoint tests (17+ tests)
  - `test_regulation_adapter.py` - Regulation tests (12+ tests)
- Interactive test runner (`run_tests.py`) with menu
- Pytest configuration (`pytest.ini`) with coverage reports
- Comprehensive testing documentation (`TESTING.md`)
- Requirements file (`requirements.txt`) with all dependencies
- HTML coverage reports with detailed analysis
- CI/CD ready with automated test execution

### Current Project Structure
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
- Expand automated test coverage (pytest)
- Add real-time data integration with MAPAQ API

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

### Starting the API - Grace Mandiangu

```bash
# Using the startup script (recommended)
python run_api.py

# Or directly
cd src
python api.py
```

### Starting the Interactive Dashboard - Grace Mandiangu

```bash
# Using the startup script (recommended)
python run_dashboard.py

# Or directly
cd dashboard
python app.py
```

**Dashboard accessible on:** `http://localhost:8080`

**Pages disponibles:**
- `/` - Page d'accueil avec présentation
- `/dashboard` - Dashboard avec visualisations Plotly interactives
- `/predict-form` - Formulaire de prédiction
- `/about` - À propos du projet et technologies

### API Request with Inspection Date

```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine_type": "Sushi",
    "staff_count": 10,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Montreal",
    "inspection_date": "2023-06-15"
  }'
```

### API Request with Detailed Explanation (NEW - Grace Mandiangu)

```bash
curl -X POST http://localhost:5000/predict/explain \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine_type": "Sushi",
    "staff_count": 10,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Montreal"
  }'
```

**Response includes:**
- Risk prediction with probabilities
- Contributing factors analysis
- Impact assessment for each factor
- Automated recommendations
- Confidence interpretation

**See `API_EXAMPLES.md` for complete API documentation and more examples.**

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

### Running the Full Data Pipeline - Grace Mandiangu

```bash
# Using the CLI script (recommended)
python run_pipeline.py data/raw/restaurants.csv -o processed_data

# With custom configuration
python run_pipeline.py data/raw/restaurants.csv -c pipeline_config.json

# Check pipeline status
python run_pipeline.py --status
```

**Pipeline stages:**
1. **Ingestion** - Load raw CSV data
2. **Validation** - Check business rules and data quality
3. **Cleaning** - Remove duplicates, handle missing values
4. **Transformation** - Create features, categorize data
5. **Output** - Save processed data (CSV/JSON) + generate report

**Output files:**
- `data/processed/processed_data.csv` - Cleaned data
- `data/processed/processed_data.json` - JSON format
- `data/reports/processed_data_report.json` - Quality report

### Using Enhanced Model Features (v3) - Grace Mandiangu

```python
import pandas as pd
from src.probability_model import ConditionalProbabilityEngine

# Initialize engine
engine = ConditionalProbabilityEngine()

# 1. Model Calibration with Historical Data
training_data = pd.DataFrame({
    'cuisine_type': ['Sushi', 'Fast Food', 'Fine Dining', ...],
    'staff_count': [10, 15, 8, ...],
    'infractions_history': [2, 1, 0, ...],
    'kitchen_size': [35.0, 50.0, 40.0, ...],
    'region': ['Montreal', 'Quebec', 'Laval', ...],
    'actual_risk_level': ['High', 'Medium', 'Low', ...]
})

metrics = engine.calibrate_model(training_data)
print(f"Model Accuracy: {metrics['accuracy']:.2%}")
print(f"F1-Score: {metrics['f1_macro']:.2%}")

# 2. Cross-Validation
cv_results = engine.cross_validate(training_data, n_folds=5)
print(f"CV Accuracy: {cv_results['mean_accuracy']:.2%} ± {cv_results['std_accuracy']:.2%}")

# 3. Prediction with Confidence Intervals
result = engine.predict_with_confidence(
    cuisine_type="Sushi",
    staff_count=10,
    infractions_history=2,
    kitchen_size=35.0,
    region="Montreal"
)
print(f"Prediction: {result['predicted_risk']}")
print(f"Confidence: {result['confidence_level']} ({result['confidence_score']:.2%})")

# 4. Sensitivity Analysis
sensitivity = engine.sensitivity_analysis(
    cuisine_type="Sushi",
    staff_count=10,
    infractions_history=2,
    kitchen_size=35.0,
    region="Montreal"
)
print("Impact of staff variations on High risk:")
for key, probs in sensitivity['staff_sensitivity'].items():
    print(f"  {key}: {probs['High']:.2%}")

# 5. Save/Load Calibrated Model
engine.save_model('data/calibrated_model.pkl')
# Later...
new_engine = ConditionalProbabilityEngine()
new_engine.load_model('data/calibrated_model.pkl')

# 6. Run Comprehensive Tests
# python test_enhanced_model.py
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

### Running Automated Tests - Grace Mandiangu

```bash
# Using the interactive test runner (recommended)
python run_tests.py

# Run all tests
python run_tests.py --all

# Run with coverage report
python run_tests.py --coverage

# Run specific test suite
python run_tests.py --file=test_probability_model.py

# Using pytest directly
pytest tests/ -v
pytest --cov=src --cov-report=html
```

**Test Coverage:**
- ✅ Data Ingestion: 95%+ coverage
- ✅ Data Cleaning: 95%+ coverage
- ✅ Probability Model: 96%+ coverage
- ✅ API Endpoints: 95%+ coverage
- ✅ Regulation Adapter: 95%+ coverage

**See `TESTING.md` for complete testing documentation.**

---

**Author:** Grace Mandiangu  
**Last Updated:** December 2, 2025