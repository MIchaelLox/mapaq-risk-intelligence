"""
Module API REST pour les prédictions de risque sanitaire.

Expose les endpoints /predict pour obtenir des prédictions de risque
basées sur les caractéristiques d'un restaurant.

Endpoints disponibles:
- POST /predict: Prédiction simple de risque
- POST /predict/batch: Prédictions multiples
- POST /predict/explain: Prédiction avec explication détaillée
- GET /health: Vérification de santé de l'API

Author: Grace Mandiangu
Date: November 28, 2025
"""

from flask import Flask, request, jsonify
from typing import Dict, Any
import logging
from datetime import datetime

# Import du moteur de probabilités
from probability_model import ConditionalProbabilityEngine

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)

# Initialisation du moteur de prédiction
prediction_engine = ConditionalProbabilityEngine()


@app.route('/health', methods=['GET'])
def health_check():
    """
    Endpoint de vérification de santé de l'API.
    
    Returns:
        JSON avec le statut de l'API
    """
    return jsonify({
        'status': 'ok',
        'service': 'MAPAQ Risk Intelligence API',
        'version': '1.0'
    }), 200


@app.route('/predict', methods=['POST'])
def predict_risk():
    """
    Endpoint principal pour prédire le risque sanitaire d'un restaurant.
    
    Request Body (JSON):
    {
        "cuisine_type": "Sushi",
        "staff_count": 10,
        "infractions_history": 2,
        "kitchen_size": 35.0,
        "region": "Montreal",
        "inspection_date": "2023-06-15"  // Optionnel, format: YYYY-MM-DD
    }
    
    Returns:
        JSON avec la prédiction de risque
    """
    try:
        # Récupérer les données de la requête
        data = request.get_json()
        
        # Validation des données requises
        required_fields = [
            'cuisine_type',
            'staff_count',
            'infractions_history',
            'kitchen_size',
            'region'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Extraire les paramètres
        cuisine_type = data['cuisine_type']
        staff_count = int(data['staff_count'])
        infractions_history = int(data['infractions_history'])
        kitchen_size = float(data['kitchen_size'])
        region = data['region']
        
        # Paramètre optionnel: date d'inspection
        inspection_date = None
        if 'inspection_date' in data:
            try:
                inspection_date = datetime.strptime(data['inspection_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'error': 'Invalid inspection_date format',
                    'message': 'Expected format: YYYY-MM-DD'
                }), 400
        
        # Validation des valeurs
        if staff_count < 0:
            return jsonify({'error': 'staff_count must be positive'}), 400
        
        if infractions_history < 0:
            return jsonify({'error': 'infractions_history must be positive'}), 400
        
        if kitchen_size <= 0:
            return jsonify({'error': 'kitchen_size must be greater than 0'}), 400
        
        logger.info(f"Prédiction demandée pour: {cuisine_type}, {region}")
        
        # Calculer les probabilités
        probabilities = prediction_engine.calculate_risk_probability(
            cuisine_type=cuisine_type,
            staff_count=staff_count,
            infractions_history=infractions_history,
            kitchen_size=kitchen_size,
            region=region,
            inspection_date=inspection_date
        )
        
        # Obtenir le niveau de risque prédit
        risk_level, confidence = prediction_engine.predict_risk_level(
            cuisine_type=cuisine_type,
            staff_count=staff_count,
            infractions_history=infractions_history,
            kitchen_size=kitchen_size,
            region=region,
            inspection_date=inspection_date
        )
        
        # Construire la réponse
        response = {
            'prediction': {
                'risk_level': risk_level,
                'confidence': round(confidence, 4),
                'probabilities': {
                    'Low': round(probabilities['Low'], 4),
                    'Medium': round(probabilities['Medium'], 4),
                    'High': round(probabilities['High'], 4)
                }
            },
            'input': {
                'cuisine_type': cuisine_type,
                'staff_count': staff_count,
                'infractions_history': infractions_history,
                'kitchen_size': kitchen_size,
                'region': region,
                'inspection_date': inspection_date.isoformat() if inspection_date else None
            },
            'temporal_adjustment_applied': prediction_engine.temporal_adjustment_enabled,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Prédiction: {risk_level} (confiance: {confidence:.2%})")
        
        return jsonify(response), 200
    
    except ValueError as e:
        logger.error(f"Erreur de validation: {str(e)}")
        return jsonify({
            'error': 'Invalid input data',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Erreur serveur: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/predict/batch', methods=['POST'])
def predict_batch():
    """
    Endpoint pour prédire le risque de plusieurs restaurants en une seule requête.
    
    Request Body (JSON):
    {
        "restaurants": [
            {
                "cuisine_type": "Sushi",
                "staff_count": 10,
                "infractions_history": 2,
                "kitchen_size": 35.0,
                "region": "Montreal"
            },
            ...
        ]
    }
    
    Returns:
        JSON avec les prédictions pour chaque restaurant
    """
    try:
        data = request.get_json()
        
        if 'restaurants' not in data:
            return jsonify({'error': 'Missing "restaurants" field'}), 400
        
        restaurants = data['restaurants']
        
        if not isinstance(restaurants, list):
            return jsonify({'error': '"restaurants" must be a list'}), 400
        
        predictions = []
        
        for idx, restaurant in enumerate(restaurants):
            try:
                # Extraire la date d'inspection si présente
                inspection_date = None
                if 'inspection_date' in restaurant:
                    try:
                        inspection_date = datetime.strptime(restaurant['inspection_date'], '%Y-%m-%d')
                    except ValueError:
                        pass
                
                risk_level, confidence = prediction_engine.predict_risk_level(
                    cuisine_type=restaurant['cuisine_type'],
                    staff_count=int(restaurant['staff_count']),
                    infractions_history=int(restaurant['infractions_history']),
                    kitchen_size=float(restaurant['kitchen_size']),
                    region=restaurant['region'],
                    inspection_date=inspection_date
                )
                
                predictions.append({
                    'index': idx,
                    'risk_level': risk_level,
                    'confidence': round(confidence, 4),
                    'input': restaurant
                })
            
            except Exception as e:
                predictions.append({
                    'index': idx,
                    'error': str(e),
                    'input': restaurant
                })
        
        return jsonify({
            'predictions': predictions,
            'total': len(restaurants),
            'timestamp': datetime.now().isoformat()
        }), 200
    
    except Exception as e:
        logger.error(f"Erreur batch: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


@app.route('/predict/explain', methods=['POST'])
def explain_prediction():
    """
    Endpoint pour obtenir une explication détaillée de la prédiction.
    
    Request Body (JSON): Identique à /predict
    
    Returns:
        JSON avec prédiction et explication détaillée des facteurs
    """
    try:
        data = request.get_json()
        
        # Validation des données requises
        required_fields = [
            'cuisine_type',
            'staff_count',
            'infractions_history',
            'kitchen_size',
            'region'
        ]
        
        missing_fields = [field for field in required_fields if field not in data]
        if missing_fields:
            return jsonify({
                'error': 'Missing required fields',
                'missing_fields': missing_fields
            }), 400
        
        # Extraire les paramètres
        cuisine_type = data['cuisine_type']
        staff_count = int(data['staff_count'])
        infractions_history = int(data['infractions_history'])
        kitchen_size = float(data['kitchen_size'])
        region = data['region']
        
        # Paramètre optionnel: date d'inspection
        inspection_date = None
        if 'inspection_date' in data:
            try:
                inspection_date = datetime.strptime(data['inspection_date'], '%Y-%m-%d')
            except ValueError:
                return jsonify({
                    'error': 'Invalid inspection_date format',
                    'message': 'Expected format: YYYY-MM-DD'
                }), 400
        
        logger.info(f"Explication demandée pour: {cuisine_type}, {region}")
        
        # Calculer les probabilités
        probabilities = prediction_engine.calculate_risk_probability(
            cuisine_type=cuisine_type,
            staff_count=staff_count,
            infractions_history=infractions_history,
            kitchen_size=kitchen_size,
            region=region,
            inspection_date=inspection_date
        )
        
        # Obtenir le niveau de risque prédit
        risk_level, confidence = prediction_engine.predict_risk_level(
            cuisine_type=cuisine_type,
            staff_count=staff_count,
            infractions_history=infractions_history,
            kitchen_size=kitchen_size,
            region=region,
            inspection_date=inspection_date
        )
        
        # Générer l'explication détaillée
        explanation = _generate_explanation(
            cuisine_type, staff_count, infractions_history,
            kitchen_size, region, risk_level, probabilities
        )
        
        # Construire la réponse
        response = {
            'prediction': {
                'risk_level': risk_level,
                'confidence': round(confidence, 4),
                'probabilities': {
                    'Low': round(probabilities['Low'], 4),
                    'Medium': round(probabilities['Medium'], 4),
                    'High': round(probabilities['High'], 4)
                }
            },
            'explanation': explanation,
            'input': {
                'cuisine_type': cuisine_type,
                'staff_count': staff_count,
                'infractions_history': infractions_history,
                'kitchen_size': kitchen_size,
                'region': region,
                'inspection_date': inspection_date.isoformat() if inspection_date else None
            },
            'timestamp': datetime.now().isoformat()
        }
        
        return jsonify(response), 200
    
    except ValueError as e:
        logger.error(f"Erreur de validation: {str(e)}")
        return jsonify({
            'error': 'Invalid input data',
            'message': str(e)
        }), 400
    
    except Exception as e:
        logger.error(f"Erreur serveur: {str(e)}")
        return jsonify({
            'error': 'Internal server error',
            'message': str(e)
        }), 500


def _generate_explanation(
    cuisine_type: str,
    staff_count: int,
    infractions_history: int,
    kitchen_size: float,
    region: str,
    risk_level: str,
    probabilities: Dict[str, float]
) -> Dict[str, Any]:
    """
    Génère une explication détaillée de la prédiction.
    
    Returns:
        Dictionnaire avec les facteurs contributifs
    """
    factors = []
    
    # Analyse du type de cuisine
    cuisine_risk = prediction_engine._get_cuisine_probability(cuisine_type)
    cuisine_impact = "élevé" if cuisine_risk['High'] > 0.2 else "modéré" if cuisine_risk['High'] > 0.1 else "faible"
    factors.append({
        'factor': 'Type de cuisine',
        'value': cuisine_type,
        'impact': cuisine_impact,
        'description': f"Le type de cuisine '{cuisine_type}' a un impact {cuisine_impact} sur le risque."
    })
    
    # Analyse du nombre d'employés
    staff_factor = prediction_engine._calculate_staff_factor(staff_count)
    if staff_count <= 5:
        staff_impact = "positif (petite équipe)"
    elif staff_count <= 15:
        staff_impact = "neutre"
    else:
        staff_impact = "négatif (coordination complexe)"
    
    factors.append({
        'factor': 'Nombre d\'employés',
        'value': staff_count,
        'impact': staff_impact,
        'description': f"{staff_count} employés - {staff_impact}."
    })
    
    # Analyse de l'historique d'infractions
    if infractions_history == 0:
        infraction_impact = "excellent (aucune infraction)"
    elif infractions_history <= 1:
        infraction_impact = "bon"
    elif infractions_history <= 2:
        infraction_impact = "préoccupant"
    else:
        infraction_impact = "critique"
    
    factors.append({
        'factor': 'Historique d\'infractions',
        'value': infractions_history,
        'impact': infraction_impact,
        'description': f"{infractions_history} infraction(s) passée(s) - Impact {infraction_impact}."
    })
    
    # Analyse de la taille de la cuisine
    if kitchen_size < 20:
        kitchen_impact = "positif (facile à gérer)"
    elif kitchen_size < 50:
        kitchen_impact = "neutre"
    else:
        kitchen_impact = "négatif (grande surface)"
    
    factors.append({
        'factor': 'Taille de la cuisine',
        'value': f"{kitchen_size} m²",
        'impact': kitchen_impact,
        'description': f"Cuisine de {kitchen_size} m² - {kitchen_impact}."
    })
    
    # Analyse de la région
    region_factor = prediction_engine._calculate_region_factor(region)
    region_impact = "élevé" if region_factor > 0.03 else "modéré" if region_factor > 0 else "neutre"
    
    factors.append({
        'factor': 'Région',
        'value': region,
        'impact': region_impact,
        'description': f"Région {region} - Impact {region_impact}."
    })
    
    # Recommandations
    recommendations = []
    if infractions_history > 2:
        recommendations.append("Réduire le nombre d'infractions par une formation accrue du personnel.")
    if staff_count > 15:
        recommendations.append("Améliorer la coordination entre les équipes.")
    if kitchen_size > 50:
        recommendations.append("Mettre en place des zones de contrôle pour faciliter la surveillance.")
    if risk_level == 'High':
        recommendations.append("Inspection prioritaire recommandée.")
    
    return {
        'risk_level': risk_level,
        'confidence_interpretation': _interpret_confidence(probabilities[risk_level]),
        'contributing_factors': factors,
        'recommendations': recommendations,
        'summary': f"Le restaurant présente un risque {risk_level.lower()} avec une confiance de {probabilities[risk_level]:.1%}."
    }


def _interpret_confidence(confidence: float) -> str:
    """Interprète le niveau de confiance."""
    if confidence >= 0.7:
        return "Très élevée - Prédiction très fiable"
    elif confidence >= 0.5:
        return "Élevée - Prédiction fiable"
    elif confidence >= 0.4:
        return "Modérée - Prédiction incertaine"
    else:
        return "Faible - Prédiction peu fiable"


@app.errorhandler(404)
def not_found(error):
    """Gestionnaire d'erreur 404."""
    return jsonify({
        'error': 'Endpoint not found',
        'message': 'The requested endpoint does not exist'
    }), 404


@app.errorhandler(405)
def method_not_allowed(error):
    """Gestionnaire d'erreur 405."""
    return jsonify({
        'error': 'Method not allowed',
        'message': 'The HTTP method is not allowed for this endpoint'
    }), 405


if __name__ == '__main__':
    logger.info("Démarrage de l'API MAPAQ Risk Intelligence...")
    app.run(host='0.0.0.0', port=5000, debug=True)
