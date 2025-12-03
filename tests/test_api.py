"""
Tests automatisés pour le module api.py

Suite de tests pytest pour valider l'API REST.

Author: Grace Mandiangu
Date: December 2, 2025
"""

import pytest
import json
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from api import app


class TestAPI:
    """Tests pour l'API REST."""
    
    @pytest.fixture
    def client(self):
        """Fixture pour créer un client de test Flask."""
        app.config['TESTING'] = True
        with app.test_client() as client:
            yield client
    
    @pytest.fixture
    def valid_prediction_data(self):
        """Fixture pour des données de prédiction valides."""
        return {
            'cuisine_type': 'Sushi',
            'staff_count': 10,
            'infractions_history': 2,
            'kitchen_size': 35.0,
            'region': 'Montreal'
        }
    
    def test_health_endpoint(self, client):
        """Test l'endpoint /health."""
        response = client.get('/health')
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'status' in data
        assert data['status'] == 'ok'
        assert 'service' in data
        assert 'version' in data
    
    def test_predict_endpoint_success(self, client, valid_prediction_data):
        """Test l'endpoint /predict avec des données valides."""
        response = client.post(
            '/predict',
            data=json.dumps(valid_prediction_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'prediction' in data
        assert 'risk_level' in data['prediction']
        assert 'confidence' in data['prediction']
        assert 'probabilities' in data['prediction']
        
        # Vérifier les niveaux de risque
        assert data['prediction']['risk_level'] in ['Low', 'Medium', 'High']
        
        # Vérifier les probabilités
        probs = data['prediction']['probabilities']
        assert 'Low' in probs
        assert 'Medium' in probs
        assert 'High' in probs
    
    def test_predict_endpoint_missing_fields(self, client):
        """Test /predict avec des champs manquants."""
        incomplete_data = {
            'cuisine_type': 'Sushi',
            'staff_count': 10
            # Champs manquants
        }
        
        response = client.post(
            '/predict',
            data=json.dumps(incomplete_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        
        assert 'error' in data
        assert 'missing_fields' in data
    
    def test_predict_endpoint_invalid_data_types(self, client):
        """Test /predict avec des types de données invalides."""
        invalid_data = {
            'cuisine_type': 'Sushi',
            'staff_count': 'invalid',  # Devrait être un nombre
            'infractions_history': 2,
            'kitchen_size': 35.0,
            'region': 'Montreal'
        }
        
        response = client.post(
            '/predict',
            data=json.dumps(invalid_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_endpoint_negative_values(self, client):
        """Test /predict avec des valeurs négatives."""
        negative_data = {
            'cuisine_type': 'Sushi',
            'staff_count': -10,  # Négatif
            'infractions_history': 2,
            'kitchen_size': 35.0,
            'region': 'Montreal'
        }
        
        response = client.post(
            '/predict',
            data=json.dumps(negative_data),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_endpoint_with_inspection_date(self, client, valid_prediction_data):
        """Test /predict avec une date d'inspection."""
        data_with_date = valid_prediction_data.copy()
        data_with_date['inspection_date'] = '2023-06-15'
        
        response = client.post(
            '/predict',
            data=json.dumps(data_with_date),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'prediction' in data
    
    def test_predict_endpoint_invalid_date_format(self, client, valid_prediction_data):
        """Test /predict avec un format de date invalide."""
        data_with_bad_date = valid_prediction_data.copy()
        data_with_bad_date['inspection_date'] = '15/06/2023'  # Format invalide
        
        response = client.post(
            '/predict',
            data=json.dumps(data_with_bad_date),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_batch_endpoint(self, client, valid_prediction_data):
        """Test l'endpoint /predict/batch."""
        batch_data = {
            'restaurants': [
                valid_prediction_data,
                {
                    'cuisine_type': 'Fast Food',
                    'staff_count': 15,
                    'infractions_history': 1,
                    'kitchen_size': 50.0,
                    'region': 'Quebec'
                }
            ]
        }
        
        response = client.post(
            '/predict/batch',
            data=json.dumps(batch_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'predictions' in data
        assert 'total' in data
        assert len(data['predictions']) == 2
        assert data['total'] == 2
    
    def test_predict_batch_missing_restaurants_field(self, client):
        """Test /predict/batch sans le champ 'restaurants'."""
        response = client.post(
            '/predict/batch',
            data=json.dumps({}),
            content_type='application/json'
        )
        
        assert response.status_code == 400
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_predict_explain_endpoint(self, client, valid_prediction_data):
        """Test l'endpoint /predict/explain."""
        response = client.post(
            '/predict/explain',
            data=json.dumps(valid_prediction_data),
            content_type='application/json'
        )
        
        assert response.status_code == 200
        data = json.loads(response.data)
        
        assert 'prediction' in data
        assert 'explanation' in data
        
        explanation = data['explanation']
        assert 'contributing_factors' in explanation
        assert 'recommendations' in explanation
        assert 'summary' in explanation
    
    def test_404_error_handler(self, client):
        """Test le gestionnaire d'erreur 404."""
        response = client.get('/nonexistent_endpoint')
        
        assert response.status_code == 404
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_405_error_handler(self, client):
        """Test le gestionnaire d'erreur 405 (méthode non autorisée)."""
        response = client.get('/predict')  # GET au lieu de POST
        
        assert response.status_code == 405
        data = json.loads(response.data)
        assert 'error' in data
    
    def test_different_cuisine_types(self, client):
        """Test avec différents types de cuisine."""
        cuisines = ['Sushi', 'Fast Food', 'Fine Dining', 'Bakery', 'BBQ']
        
        for cuisine in cuisines:
            data = {
                'cuisine_type': cuisine,
                'staff_count': 10,
                'infractions_history': 1,
                'kitchen_size': 30.0,
                'region': 'Montreal'
            }
            
            response = client.post(
                '/predict',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200
    
    def test_different_regions(self, client):
        """Test avec différentes régions."""
        regions = ['Montreal', 'Quebec', 'Laval', 'Gatineau']
        
        for region in regions:
            data = {
                'cuisine_type': 'Sushi',
                'staff_count': 10,
                'infractions_history': 1,
                'kitchen_size': 30.0,
                'region': region
            }
            
            response = client.post(
                '/predict',
                data=json.dumps(data),
                content_type='application/json'
            )
            
            assert response.status_code == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
