"""
Tests unitaires pour le module regulation_adapter.

Author: Grace Mandiangu
Date: November 25, 2025
"""

import pytest
import sys
from pathlib import Path
from datetime import datetime

# Ajouter le répertoire src au path
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from regulation_adapter import RegulationAdapter


class TestRegulationAdapter:
    """Tests pour la classe RegulationAdapter."""
    
    @pytest.fixture
    def adapter(self):
        """Fixture pour créer une instance de RegulationAdapter."""
        return RegulationAdapter()
    
    def test_initialization(self, adapter):
        """Test l'initialisation de l'adaptateur."""
        assert adapter is not None
        assert len(adapter.regulations) > 0
        assert adapter.metadata is not None
    
    def test_load_regulations(self, adapter):
        """Test le chargement des réglementations."""
        assert len(adapter.regulations) >= 3
        
        # Vérifier que les dates ont été converties
        for reg in adapter.regulations:
            assert 'effective_date_obj' in reg
            assert isinstance(reg['effective_date_obj'], datetime)
    
    def test_get_applicable_regulations_before_all(self, adapter):
        """Test avec une date avant toutes les réglementations."""
        inspection_date = datetime(2019, 1, 1)
        applicable = adapter.get_applicable_regulations(inspection_date)
        
        assert len(applicable) == 0
    
    def test_get_applicable_regulations_after_first(self, adapter):
        """Test avec une date après la première réglementation."""
        inspection_date = datetime(2020, 6, 1)
        applicable = adapter.get_applicable_regulations(inspection_date)
        
        assert len(applicable) >= 1
        assert all(reg['effective_date_obj'] <= inspection_date for reg in applicable)
    
    def test_get_applicable_regulations_current(self, adapter):
        """Test avec la date actuelle."""
        inspection_date = datetime.now()
        applicable = adapter.get_applicable_regulations(inspection_date)
        
        # Toutes les réglementations devraient être applicables
        assert len(applicable) == len(adapter.regulations)
    
    def test_calculate_temporal_weight_no_regulations(self, adapter):
        """Test le calcul de poids sans réglementations applicables."""
        inspection_date = datetime(2019, 1, 1)
        base_score = 0.65
        
        adjusted_score, applied = adapter.calculate_temporal_weight(
            inspection_date, 
            base_score
        )
        
        assert adjusted_score == base_score
        assert len(applied) == 0
    
    def test_calculate_temporal_weight_with_regulations(self, adapter):
        """Test le calcul de poids avec réglementations applicables."""
        inspection_date = datetime(2023, 6, 1)
        base_score = 0.50
        
        adjusted_score, applied = adapter.calculate_temporal_weight(
            inspection_date, 
            base_score
        )
        
        assert adjusted_score != base_score
        assert len(applied) > 0
        assert 0.0 <= adjusted_score <= 1.0
    
    def test_calculate_temporal_weight_bounds(self, adapter):
        """Test que le score ajusté reste dans les limites [0, 1]."""
        inspection_date = datetime.now()
        
        # Test avec score très bas
        adjusted_low, _ = adapter.calculate_temporal_weight(inspection_date, 0.01)
        assert 0.0 <= adjusted_low <= 1.0
        
        # Test avec score très haut
        adjusted_high, _ = adapter.calculate_temporal_weight(inspection_date, 0.99)
        assert 0.0 <= adjusted_high <= 1.0
    
    def test_adjust_risk_probabilities_no_regulations(self, adapter):
        """Test l'ajustement des probabilités sans réglementations."""
        inspection_date = datetime(2019, 1, 1)
        probabilities = {'Low': 0.30, 'Medium': 0.50, 'High': 0.20}
        
        adjusted = adapter.adjust_risk_probabilities(probabilities, inspection_date)
        
        assert adjusted == probabilities
    
    def test_adjust_risk_probabilities_with_regulations(self, adapter):
        """Test l'ajustement des probabilités avec réglementations."""
        inspection_date = datetime(2023, 6, 1)
        probabilities = {'Low': 0.30, 'Medium': 0.50, 'High': 0.20}
        
        adjusted = adapter.adjust_risk_probabilities(probabilities, inspection_date)
        
        # Vérifier que les probabilités ont changé
        assert adjusted != probabilities
        
        # Vérifier que la somme = 1
        assert abs(sum(adjusted.values()) - 1.0) < 0.0001
        
        # Vérifier que toutes les probabilités sont positives
        assert all(p >= 0 for p in adjusted.values())
    
    def test_get_regulation_timeline(self, adapter):
        """Test l'obtention de la chronologie des réglementations."""
        timeline = adapter.get_regulation_timeline()
        
        assert len(timeline) == len(adapter.regulations)
        
        # Vérifier que c'est trié par date
        dates = [datetime.strptime(reg['effective_date'], '%Y-%m-%d') for reg in timeline]
        assert dates == sorted(dates)
    
    def test_get_regulation_by_id_exists(self, adapter):
        """Test la récupération d'une réglementation existante."""
        # Utiliser le premier ID disponible
        first_reg_id = adapter.regulations[0]['id']
        
        regulation = adapter.get_regulation_by_id(first_reg_id)
        
        assert regulation is not None
        assert regulation['id'] == first_reg_id
        assert 'name' in regulation
        assert 'effective_date' in regulation
    
    def test_get_regulation_by_id_not_exists(self, adapter):
        """Test la récupération d'une réglementation inexistante."""
        regulation = adapter.get_regulation_by_id('NON-EXISTENT-ID')
        
        assert regulation is None
    
    def test_add_regulation_success(self, adapter):
        """Test l'ajout d'une nouvelle réglementation."""
        initial_count = len(adapter.regulations)
        
        success = adapter.add_regulation(
            regulation_id='TEST-001',
            name='Test Regulation',
            effective_date='2024-01-01',
            description='Test description',
            impact_weight=1.25
        )
        
        assert success is True
        assert len(adapter.regulations) == initial_count + 1
        
        # Vérifier que la réglementation a été ajoutée
        added_reg = adapter.get_regulation_by_id('TEST-001')
        assert added_reg is not None
        assert added_reg['name'] == 'Test Regulation'
    
    def test_add_regulation_duplicate_id(self, adapter):
        """Test l'ajout d'une réglementation avec ID dupliqué."""
        # Utiliser un ID existant
        existing_id = adapter.regulations[0]['id']
        
        success = adapter.add_regulation(
            regulation_id=existing_id,
            name='Duplicate',
            effective_date='2024-01-01',
            description='Should fail',
            impact_weight=1.0
        )
        
        assert success is False
    
    def test_add_regulation_invalid_date(self, adapter):
        """Test l'ajout d'une réglementation avec date invalide."""
        success = adapter.add_regulation(
            regulation_id='TEST-002',
            name='Invalid Date',
            effective_date='invalid-date',
            description='Should fail',
            impact_weight=1.0
        )
        
        assert success is False
    
    def test_impact_weight_increases_risk(self, adapter):
        """Test que impact_weight > 1.0 augmente le risque."""
        # Créer une réglementation temporaire avec impact élevé
        adapter.add_regulation(
            regulation_id='HIGH-IMPACT',
            name='High Impact Regulation',
            effective_date='2020-01-01',
            description='High impact test',
            impact_weight=1.5
        )
        
        inspection_date = datetime(2024, 1, 1)
        base_score = 0.50
        
        adjusted_score, _ = adapter.calculate_temporal_weight(
            inspection_date, 
            base_score
        )
        
        # Le score devrait augmenter
        assert adjusted_score > base_score
    
    def test_probability_sum_always_one(self, adapter):
        """Test que la somme des probabilités ajustées est toujours 1."""
        inspection_date = datetime(2023, 6, 1)
        
        test_cases = [
            {'Low': 0.60, 'Medium': 0.30, 'High': 0.10},
            {'Low': 0.20, 'Medium': 0.50, 'High': 0.30},
            {'Low': 0.33, 'Medium': 0.33, 'High': 0.34},
        ]
        
        for probs in test_cases:
            adjusted = adapter.adjust_risk_probabilities(probs, inspection_date)
            total = sum(adjusted.values())
            assert abs(total - 1.0) < 0.0001, f"Sum is {total}, expected 1.0"


if __name__ == "__main__":
    pytest.main([__file__, '-v'])
