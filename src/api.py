"""
Module API REST pour les prédictions de risque sanitaire.

Expose l'endpoint /predict pour obtenir des prédictions de risque
basées sur les caractéristiques d'un restaurant.

Author: Grace Mandiangu
Date: November 24, 2025
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
        "region": "Montreal"
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
            region=region
        )
        
        # Obtenir le niveau de risque prédit
        risk_level, confidence = prediction_engine.predict_risk_level(
            cuisine_type=cuisine_type,
            staff_count=staff_count,
            infractions_history=infractions_history,
            kitchen_size=kitchen_size,
            region=region
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
                'region': region
            },
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
                risk_level, confidence = prediction_engine.predict_risk_level(
                    cuisine_type=restaurant['cuisine_type'],
                    staff_count=int(restaurant['staff_count']),
                    infractions_history=int(restaurant['infractions_history']),
                    kitchen_size=float(restaurant['kitchen_size']),
                    region=restaurant['region']
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
