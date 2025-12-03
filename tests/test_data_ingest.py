"""
Tests automatisés pour le module data_ingest.py

Suite de tests pytest pour valider les fonctionnalités d'ingestion de données.

Author: Grace Mandiangu
Date: December 2, 2025
"""

import pytest
import pandas as pd
import sys
import os
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_ingest import MAPAQDataIngestor


class TestMAPAQDataIngestor:
    """Tests pour la classe MAPAQDataIngestor."""
    
    @pytest.fixture
    def ingestor(self):
        """Fixture pour créer une instance de MAPAQDataIngestor."""
        return MAPAQDataIngestor()
    
    @pytest.fixture
    def sample_csv_data(self, tmp_path):
        """Fixture pour créer un fichier CSV de test."""
        csv_file = tmp_path / "test_data.csv"
        data = {
            'nom_etablissement': ['Restaurant A', 'Restaurant B', 'Restaurant C'],
            'adresse': ['123 Rue A', '456 Rue B', '789 Rue C'],
            'ville': ['Montreal', 'Quebec', 'Laval'],
            'type_cuisine': ['Sushi', 'Italian', 'Fast Food'],
            'nombre_employes': [10, 15, 8],
            'infractions': [2, 0, 1]
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False, encoding='utf-8')
        return csv_file
    
    def test_ingestor_initialization(self, ingestor):
        """Test l'initialisation de l'ingestor."""
        assert ingestor is not None
        assert isinstance(ingestor, MAPAQDataIngestor)
    
    def test_load_csv_success(self, ingestor, sample_csv_data):
        """Test le chargement réussi d'un fichier CSV."""
        df = ingestor.load_csv(str(sample_csv_data))
        
        assert df is not None
        assert isinstance(df, pd.DataFrame)
        assert len(df) == 3
        assert 'nom_etablissement' in df.columns
        assert 'type_cuisine' in df.columns
    
    def test_load_csv_file_not_found(self, ingestor):
        """Test le chargement d'un fichier inexistant."""
        with pytest.raises(FileNotFoundError):
            ingestor.load_csv('fichier_inexistant.csv')
    
    def test_get_data_info(self, ingestor, sample_csv_data):
        """Test la récupération des informations sur les données."""
        df = ingestor.load_csv(str(sample_csv_data))
        info = ingestor.get_data_info(df)
        
        assert 'nombre_lignes' in info
        assert 'nombre_colonnes' in info
        assert 'colonnes' in info
        assert 'valeurs_manquantes' in info
        
        assert info['nombre_lignes'] == 3
        assert info['nombre_colonnes'] == 6
        assert len(info['colonnes']) == 6
    
    def test_validate_schema_success(self, ingestor, sample_csv_data):
        """Test la validation de schéma réussie."""
        df = ingestor.load_csv(str(sample_csv_data))
        required_columns = ['nom_etablissement', 'type_cuisine', 'ville']
        
        result = ingestor.validate_schema(df, required_columns)
        
        assert result['valid'] == True
        assert result['missing_columns'] == []
    
    def test_validate_schema_missing_columns(self, ingestor, sample_csv_data):
        """Test la validation de schéma avec colonnes manquantes."""
        df = ingestor.load_csv(str(sample_csv_data))
        required_columns = ['nom_etablissement', 'colonne_inexistante', 'autre_colonne']
        
        result = ingestor.validate_schema(df, required_columns)
        
        assert result['valid'] == False
        assert len(result['missing_columns']) == 2
        assert 'colonne_inexistante' in result['missing_columns']
    
    def test_detect_encoding(self, ingestor, sample_csv_data):
        """Test la détection d'encodage."""
        encoding = ingestor.detect_encoding(str(sample_csv_data))
        
        assert encoding is not None
        assert isinstance(encoding, str)
        assert encoding in ['utf-8', 'latin-1', 'iso-8859-1', 'cp1252']
    
    def test_empty_dataframe(self, ingestor):
        """Test avec un DataFrame vide."""
        df = pd.DataFrame()
        info = ingestor.get_data_info(df)
        
        assert info['nombre_lignes'] == 0
        assert info['nombre_colonnes'] == 0
    
    def test_dataframe_with_missing_values(self, ingestor, tmp_path):
        """Test avec des valeurs manquantes."""
        csv_file = tmp_path / "test_missing.csv"
        data = {
            'col1': [1, 2, None, 4],
            'col2': ['a', None, 'c', 'd'],
            'col3': [None, None, None, None]
        }
        df = pd.DataFrame(data)
        df.to_csv(csv_file, index=False)
        
        loaded_df = ingestor.load_csv(str(csv_file))
        info = ingestor.get_data_info(loaded_df)
        
        assert info['valeurs_manquantes']['col1'] > 0
        assert info['valeurs_manquantes']['col2'] > 0
        assert info['valeurs_manquantes']['col3'] == 4


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
