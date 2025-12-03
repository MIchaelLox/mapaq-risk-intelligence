"""
Tests automatisés pour le module probability_model.py

Suite de tests pytest pour valider le moteur de probabilités conditionnelles.

Author: Grace Mandiangu
Date: December 2, 2025
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from probability_model import ConditionalProbabilityEngine


class TestConditionalProbabilityEngine:
    """Tests pour la classe ConditionalProbabilityEngine."""
    
    @pytest.fixture
    def engine(self):
        """Fixture pour créer une instance du moteur."""
        return ConditionalProbabilityEngine(enable_temporal_adjustment=False)
    
    @pytest.fixture
    def sample_training_data(self):
        """Fixture pour créer des données d'entraînement."""
        np.random.seed(42)
        data = {
            'cuisine_type': ['Sushi'] * 30 + ['Fast Food'] * 30 + ['Fine Dining'] * 30,
            'staff_count': np.random.randint(1, 50, 90),
            'infractions_history': np.random.randint(0, 5, 90),
            'kitchen_size': np.random.uniform(10, 100, 90),
            'region': np.random.choice(['Montreal', 'Quebec', 'Laval'], 90),
            'actual_risk_level': np.random.choice(['Low', 'Medium', 'High'], 90)
        }
        return pd.DataFrame(data)
    
    def test_engine_initialization(self, engine):
        """Test l'initialisation du moteur."""
        assert engine is not None
        assert isinstance(engine, ConditionalProbabilityEngine)
        assert hasattr(engine, 'prior_risk')
        assert hasattr(engine, 'cuisine_risk_probs')
    
    def test_calculate_risk_probability(self, engine):
        """Test le calcul des probabilités de risque."""
        probs = engine.calculate_risk_probability(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        
        assert isinstance(probs, dict)
        assert 'Low' in probs
        assert 'Medium' in probs
        assert 'High' in probs
        
        # Les probabilités doivent sommer à 1
        total = sum(probs.values())
        assert abs(total - 1.0) < 0.001
        
        # Chaque probabilité doit être entre 0 et 1
        for prob in probs.values():
            assert 0 <= prob <= 1
    
    def test_predict_risk_level(self, engine):
        """Test la prédiction du niveau de risque."""
        risk_level, confidence = engine.predict_risk_level(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        
        assert risk_level in ['Low', 'Medium', 'High']
        assert 0 <= confidence <= 1
    
    def test_different_cuisine_types(self, engine):
        """Test avec différents types de cuisine."""
        cuisines = ['Sushi', 'Fast Food', 'Fine Dining', 'Bakery', 'BBQ']
        
        for cuisine in cuisines:
            probs = engine.calculate_risk_probability(
                cuisine_type=cuisine,
                staff_count=10,
                infractions_history=1,
                kitchen_size=30.0,
                region='Montreal'
            )
            
            assert isinstance(probs, dict)
            assert abs(sum(probs.values()) - 1.0) < 0.001
    
    def test_staff_factor_impact(self, engine):
        """Test l'impact du nombre d'employés."""
        # Petit staff
        probs_small = engine.calculate_risk_probability(
            cuisine_type='Sushi',
            staff_count=3,
            infractions_history=1,
            kitchen_size=30.0,
            region='Montreal'
        )
        
        # Grand staff
        probs_large = engine.calculate_risk_probability(
            cuisine_type='Sushi',
            staff_count=25,
            infractions_history=1,
            kitchen_size=30.0,
            region='Montreal'
        )
        
        # Les probabilités devraient être différentes
        assert probs_small != probs_large
    
    def test_infractions_impact(self, engine):
        """Test l'impact des infractions."""
        # Aucune infraction
        probs_none = engine.calculate_risk_probability(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=0,
            kitchen_size=30.0,
            region='Montreal'
        )
        
        # Plusieurs infractions
        probs_many = engine.calculate_risk_probability(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=4,
            kitchen_size=30.0,
            region='Montreal'
        )
        
        # Le risque élevé devrait augmenter avec les infractions
        assert probs_many['High'] > probs_none['High']
    
    def test_calibrate_model(self, engine, sample_training_data):
        """Test la calibration du modèle."""
        metrics = engine.calibrate_model(sample_training_data)
        
        assert 'accuracy' in metrics
        assert 'precision_macro' in metrics
        assert 'recall_macro' in metrics
        assert 'f1_macro' in metrics
        assert 'confusion_matrix' in metrics
        
        assert 0 <= metrics['accuracy'] <= 1
    
    def test_predict_with_confidence(self, engine):
        """Test la prédiction avec confiance."""
        result = engine.predict_with_confidence(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        
        assert 'predicted_risk' in result
        assert 'probability' in result
        assert 'confidence_score' in result
        assert 'confidence_level' in result
        assert 'all_probabilities' in result
        
        assert result['predicted_risk'] in ['Low', 'Medium', 'High']
        assert 0 <= result['confidence_score'] <= 1
        assert result['confidence_level'] in ['Très élevée', 'Élevée', 'Moyenne', 'Faible']
    
    def test_sensitivity_analysis(self, engine):
        """Test l'analyse de sensibilité."""
        sensitivity = engine.sensitivity_analysis(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        
        assert 'base_prediction' in sensitivity
        assert 'staff_sensitivity' in sensitivity
        assert 'infractions_sensitivity' in sensitivity
        assert 'kitchen_sensitivity' in sensitivity
        
        # Vérifier que les variations sont présentes
        assert len(sensitivity['staff_sensitivity']) > 0
        assert len(sensitivity['infractions_sensitivity']) > 0
    
    def test_model_summary(self, engine):
        """Test le résumé du modèle."""
        summary = engine.get_model_summary()
        
        assert 'version' in summary
        assert 'prior_risk_distribution' in summary
        assert 'cuisine_types_supported' in summary
        assert 'temporal_adjustment' in summary
        
        assert summary['version'] == '3.0'
        assert isinstance(summary['cuisine_types_supported'], list)
    
    def test_save_and_load_model(self, engine, tmp_path):
        """Test la sauvegarde et le chargement du modèle."""
        model_path = tmp_path / "test_model.pkl"
        
        # Sauvegarder
        success = engine.save_model(str(model_path))
        assert success == True
        assert model_path.exists()
        
        # Charger
        new_engine = ConditionalProbabilityEngine()
        success = new_engine.load_model(str(model_path))
        assert success == True
        
        # Vérifier que les prédictions sont identiques
        pred1, prob1 = engine.predict_risk_level(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        
        pred2, prob2 = new_engine.predict_risk_level(
            cuisine_type='Sushi',
            staff_count=10,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        
        assert pred1 == pred2
        assert abs(prob1 - prob2) < 0.001
    
    def test_invalid_inputs(self, engine):
        """Test avec des entrées invalides."""
        # Staff count négatif devrait quand même fonctionner (géré en interne)
        probs = engine.calculate_risk_probability(
            cuisine_type='Sushi',
            staff_count=-5,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        assert isinstance(probs, dict)
    
    def test_unknown_cuisine_type(self, engine):
        """Test avec un type de cuisine inconnu."""
        probs = engine.calculate_risk_probability(
            cuisine_type='Unknown Cuisine',
            staff_count=10,
            infractions_history=2,
            kitchen_size=35.0,
            region='Montreal'
        )
        
        # Devrait utiliser les probabilités par défaut
        assert isinstance(probs, dict)
        assert abs(sum(probs.values()) - 1.0) < 0.001


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
