"""
Application Dashboard Interactif pour MAPAQ Risk Intelligence.

Dashboard Flask pour visualiser les prédictions de risque sanitaire
et les statistiques des restaurants.

Author: Grace Mandiangu
Date: November 24, 2025
"""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

# Ajouter le dossier parent au path pour importer les modules src
sys.path.append(str(Path(__file__).parent.parent))

from src.probability_model import ConditionalProbabilityEngine
from src.data_cleaner import DataCleaner
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialisation de l'application Flask
app = Flask(__name__)
app.config['SECRET_KEY'] = 'mapaq-risk-intelligence-2025'

# Initialisation du moteur de prédiction
prediction_engine = ConditionalProbabilityEngine()
data_cleaner = DataCleaner()


@app.route('/')
def index():
    """
    Page d'accueil du dashboard.
    
    Returns:
        Template HTML de la page principale
    """
    return render_template('index.html')


@app.route('/dashboard')
def dashboard():
    """
    Page principale du dashboard avec visualisations.
    
    Returns:
        Template HTML du dashboard
    """
    return render_template('dashboard.html')


@app.route('/predict-form')
def predict_form():
    """
    Page avec formulaire de prédiction.
    
    Returns:
        Template HTML du formulaire
    """
    return render_template('predict_form.html')


@app.route('/api/predict', methods=['POST'])
def api_predict():
    """
    API endpoint pour les prédictions depuis le dashboard.
    
    Returns:
        JSON avec la prédiction
    """
    try:
        data = request.get_json()
        
        # Validation des données
        required_fields = ['cuisine_type', 'staff_count', 'infractions_history', 
                          'kitchen_size', 'region']
        
        for field in required_fields:
            if field not in data:
                return jsonify({'error': f'Missing field: {field}'}), 400
        
        # Calculer la prédiction
        probabilities = prediction_engine.calculate_risk_probability(
            cuisine_type=data['cuisine_type'],
            staff_count=int(data['staff_count']),
            infractions_history=int(data['infractions_history']),
            kitchen_size=float(data['kitchen_size']),
            region=data['region']
        )
        
        risk_level, confidence = prediction_engine.predict_risk_level(
            cuisine_type=data['cuisine_type'],
            staff_count=int(data['staff_count']),
            infractions_history=int(data['infractions_history']),
            kitchen_size=float(data['kitchen_size']),
            region=data['region']
        )
        
        # Déterminer la couleur selon le niveau de risque
        risk_colors = {
            'Low': '#10b981',      # Vert
            'Medium': '#f59e0b',   # Orange
            'High': '#ef4444'      # Rouge
        }
        
        response = {
            'success': True,
            'prediction': {
                'risk_level': risk_level,
                'confidence': round(confidence * 100, 2),
                'color': risk_colors[risk_level],
                'probabilities': {
                    'Low': round(probabilities['Low'] * 100, 2),
                    'Medium': round(probabilities['Medium'] * 100, 2),
                    'High': round(probabilities['High'] * 100, 2)
                }
            },
            'input': data
        }
        
        logger.info(f"Prédiction dashboard: {risk_level} ({confidence:.2%})")
        
        return jsonify(response), 200
    
    except Exception as e:
        logger.error(f"Erreur prédiction dashboard: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/statistics')
def api_statistics():
    """
    Endpoint pour obtenir des statistiques globales.
    
    Returns:
        JSON avec les statistiques
    """
    # Statistiques exemple (à remplacer par de vraies données)
    stats = {
        'total_restaurants': 1250,
        'risk_distribution': {
            'Low': 750,
            'Medium': 375,
            'High': 125
        },
        'by_region': {
            'Montreal': 450,
            'Quebec': 320,
            'Laval': 280,
            'Gatineau': 200
        },
        'by_cuisine': {
            'Fast Food': 320,
            'Sushi': 180,
            'Fine Dining': 150,
            'BBQ': 140,
            'Bakery': 210,
            'Other': 250
        }
    }
    
    return jsonify(stats), 200


@app.route('/about')
def about():
    """
    Page à propos du projet.
    
    Returns:
        Template HTML de la page à propos
    """
    return render_template('about.html')


@app.errorhandler(404)
def page_not_found(e):
    """Gestionnaire d'erreur 404."""
    return render_template('404.html'), 404


@app.errorhandler(500)
def internal_error(e):
    """Gestionnaire d'erreur 500."""
    return render_template('500.html'), 500


if __name__ == '__main__':
    logger.info("Démarrage du Dashboard MAPAQ Risk Intelligence...")
    app.run(host='0.0.0.0', port=8080, debug=True)
