# 📡 Exemples d'Utilisation de l'API MAPAQ Risk Intelligence

**Author:** Grace Mandiangu  
**Date:** November 28, 2025

---

## 🚀 Démarrage de l'API

### Option 1: Script de démarrage (Recommandé)
```bash
python run_api.py
```

### Option 2: Démarrage direct
```bash
cd src
python api.py
```

L'API sera accessible sur: `http://localhost:5000`

---

## 📋 Endpoints Disponibles

### 1. GET /health - Vérification de Santé

Vérifie que l'API fonctionne correctement.

**Requête:**
```bash
curl -X GET http://localhost:5000/health
```

**Réponse:**
```json
{
  "status": "ok",
  "service": "MAPAQ Risk Intelligence API",
  "version": "1.0"
}
```

---

### 2. POST /predict - Prédiction Simple

Prédit le niveau de risque sanitaire pour un restaurant.

**Requête:**
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine_type": "Sushi",
    "staff_count": 10,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Montreal"
  }'
```

**Avec date d'inspection:**
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

**Réponse:**
```json
{
  "prediction": {
    "risk_level": "Medium",
    "confidence": 0.4523,
    "probabilities": {
      "Low": 0.3245,
      "Medium": 0.4523,
      "High": 0.2232
    }
  },
  "input": {
    "cuisine_type": "Sushi",
    "staff_count": 10,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Montreal",
    "inspection_date": "2023-06-15"
  },
  "temporal_adjustment_applied": true,
  "timestamp": "2025-11-28T19:30:45.123456"
}
```

---

### 3. POST /predict/batch - Prédictions Multiples

Prédit le risque pour plusieurs restaurants en une seule requête.

**Requête:**
```bash
curl -X POST http://localhost:5000/predict/batch \
  -H "Content-Type: application/json" \
  -d '{
    "restaurants": [
      {
        "cuisine_type": "Sushi",
        "staff_count": 10,
        "infractions_history": 2,
        "kitchen_size": 35.0,
        "region": "Montreal"
      },
      {
        "cuisine_type": "Italian",
        "staff_count": 8,
        "infractions_history": 0,
        "kitchen_size": 45.0,
        "region": "Quebec"
      },
      {
        "cuisine_type": "Fast Food",
        "staff_count": 20,
        "infractions_history": 3,
        "kitchen_size": 60.0,
        "region": "Laval"
      }
    ]
  }'
```

**Réponse:**
```json
{
  "predictions": [
    {
      "index": 0,
      "risk_level": "Medium",
      "confidence": 0.4523,
      "input": {
        "cuisine_type": "Sushi",
        "staff_count": 10,
        "infractions_history": 2,
        "kitchen_size": 35.0,
        "region": "Montreal"
      }
    },
    {
      "index": 1,
      "risk_level": "Low",
      "confidence": 0.6789,
      "input": {
        "cuisine_type": "Italian",
        "staff_count": 8,
        "infractions_history": 0,
        "kitchen_size": 45.0,
        "region": "Quebec"
      }
    },
    {
      "index": 2,
      "risk_level": "High",
      "confidence": 0.5234,
      "input": {
        "cuisine_type": "Fast Food",
        "staff_count": 20,
        "infractions_history": 3,
        "kitchen_size": 60.0,
        "region": "Laval"
      }
    }
  ],
  "total": 3,
  "timestamp": "2025-11-28T19:35:12.654321"
}
```

---

### 4. POST /predict/explain - Prédiction avec Explication (Nouveau - Grace Mandiangu)

Prédit le risque avec une explication détaillée des facteurs contributifs et des recommandations.

**Requête:**
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

**Réponse:**
```json
{
  "prediction": {
    "risk_level": "Medium",
    "confidence": 0.4523,
    "probabilities": {
      "Low": 0.3245,
      "Medium": 0.4523,
      "High": 0.2232
    }
  },
  "explanation": {
    "risk_level": "Medium",
    "confidence_interpretation": "Modérée - Prédiction incertaine",
    "contributing_factors": [
      {
        "factor": "Type de cuisine",
        "value": "Sushi",
        "impact": "élevé",
        "description": "Le type de cuisine 'Sushi' a un impact élevé sur le risque."
      },
      {
        "factor": "Nombre d'employés",
        "value": 10,
        "impact": "neutre",
        "description": "10 employés - neutre."
      },
      {
        "factor": "Historique d'infractions",
        "value": 2,
        "impact": "préoccupant",
        "description": "2 infraction(s) passée(s) - Impact préoccupant."
      },
      {
        "factor": "Taille de la cuisine",
        "value": "35.0 m²",
        "impact": "neutre",
        "description": "Cuisine de 35.0 m² - neutre."
      },
      {
        "factor": "Région",
        "value": "Montreal",
        "impact": "élevé",
        "description": "Région Montreal - Impact élevé."
      }
    ],
    "recommendations": [],
    "summary": "Le restaurant présente un risque medium avec une confiance de 45.2%."
  },
  "input": {
    "cuisine_type": "Sushi",
    "staff_count": 10,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Montreal",
    "inspection_date": null
  },
  "timestamp": "2025-11-28T19:40:33.987654"
}
```

---

## 🐍 Exemples Python

### Utilisation avec requests

```python
import requests
import json

# URL de base de l'API
BASE_URL = "http://localhost:5000"

# 1. Vérifier la santé de l'API
response = requests.get(f"{BASE_URL}/health")
print("Health Check:", response.json())

# 2. Prédiction simple
data = {
    "cuisine_type": "Sushi",
    "staff_count": 10,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Montreal"
}

response = requests.post(f"{BASE_URL}/predict", json=data)
result = response.json()
print(f"Risque prédit: {result['prediction']['risk_level']}")
print(f"Confiance: {result['prediction']['confidence']:.2%}")

# 3. Prédiction avec explication
response = requests.post(f"{BASE_URL}/predict/explain", json=data)
result = response.json()
print("\nExplication:")
print(result['explanation']['summary'])
for factor in result['explanation']['contributing_factors']:
    print(f"  - {factor['factor']}: {factor['impact']}")

# 4. Prédictions multiples
batch_data = {
    "restaurants": [
        {
            "cuisine_type": "Sushi",
            "staff_count": 10,
            "infractions_history": 2,
            "kitchen_size": 35.0,
            "region": "Montreal"
        },
        {
            "cuisine_type": "Italian",
            "staff_count": 8,
            "infractions_history": 0,
            "kitchen_size": 45.0,
            "region": "Quebec"
        }
    ]
}

response = requests.post(f"{BASE_URL}/predict/batch", json=batch_data)
results = response.json()
print(f"\nPrédictions pour {results['total']} restaurants:")
for pred in results['predictions']:
    print(f"  Restaurant {pred['index']}: {pred['risk_level']}")
```

---

## 🔧 Gestion des Erreurs

### Champs Manquants
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine_type": "Sushi"
  }'
```

**Réponse (400):**
```json
{
  "error": "Missing required fields",
  "missing_fields": [
    "staff_count",
    "infractions_history",
    "kitchen_size",
    "region"
  ]
}
```

### Valeurs Invalides
```bash
curl -X POST http://localhost:5000/predict \
  -H "Content-Type: application/json" \
  -d '{
    "cuisine_type": "Sushi",
    "staff_count": -5,
    "infractions_history": 2,
    "kitchen_size": 35.0,
    "region": "Montreal"
  }'
```

**Réponse (400):**
```json
{
  "error": "staff_count must be positive"
}
```

### Endpoint Inexistant
```bash
curl -X GET http://localhost:5000/invalid
```

**Réponse (404):**
```json
{
  "error": "Endpoint not found",
  "message": "The requested endpoint does not exist"
}
```

---

## 📊 Paramètres de Requête

### Champs Requis

| Champ | Type | Description | Exemple |
|-------|------|-------------|---------|
| `cuisine_type` | string | Type de cuisine du restaurant | "Sushi", "Italian", "Fast Food" |
| `staff_count` | integer | Nombre d'employés (≥ 0) | 10 |
| `infractions_history` | integer | Nombre d'infractions passées (≥ 0) | 2 |
| `kitchen_size` | float | Taille de la cuisine en m² (> 0) | 35.0 |
| `region` | string | Région géographique | "Montreal", "Quebec", "Laval" |

### Champs Optionnels

| Champ | Type | Description | Format | Exemple |
|-------|------|-------------|--------|---------|
| `inspection_date` | string | Date de l'inspection | YYYY-MM-DD | "2023-06-15" |

---

## 🎯 Niveaux de Risque

| Niveau | Description | Probabilité |
|--------|-------------|-------------|
| **Low** | Risque faible - Restaurant conforme | P(Low) > 0.5 |
| **Medium** | Risque moyen - Surveillance recommandée | 0.3 < P(Medium) < 0.5 |
| **High** | Risque élevé - Inspection prioritaire | P(High) > 0.3 |

---

## 💡 Conseils d'Utilisation

1. **Toujours vérifier `/health`** avant d'utiliser l'API
2. **Utiliser `/predict/explain`** pour comprendre les prédictions
3. **Utiliser `/predict/batch`** pour traiter plusieurs restaurants efficacement
4. **Inclure `inspection_date`** pour des ajustements temporels précis
5. **Gérer les erreurs** avec des try-catch appropriés

---

## 🔐 Sécurité (À Implémenter)

Pour une utilisation en production, considérez:
- Authentification par token (JWT)
- Rate limiting
- HTTPS obligatoire
- Validation stricte des entrées
- Logging des requêtes

---

**Développé par:** Grace Mandiangu  
**Projet:** MAPAQ Risk Intelligence  
**Version API:** 1.0  
**Dernière mise à jour:** November 28, 2025
