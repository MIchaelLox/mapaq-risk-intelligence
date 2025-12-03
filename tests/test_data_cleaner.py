"""
Tests automatisés pour le module data_cleaner.py

Suite de tests pytest pour valider les fonctionnalités de nettoyage de données.

Author: Grace Mandiangu
Date: December 2, 2025
"""

import pytest
import pandas as pd
import numpy as np
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from data_cleaner import DataCleaner


class TestDataCleaner:
    """Tests pour la classe DataCleaner."""
    
    @pytest.fixture
    def cleaner(self):
        """Fixture pour créer une instance de DataCleaner."""
        return DataCleaner()
    
    @pytest.fixture
    def sample_dirty_data(self):
        """Fixture pour créer des données sales de test."""
        data = {
            'Nom Etablissement': ['  Restaurant A  ', 'Restaurant B', 'Restaurant A', 'Restaurant C'],
            'Type Cuisine': ['Sushi', 'Italian', 'Sushi', 'Fast Food'],
            'Nombre Employés': [10, 15, 10, None],
            'Infractions': [2, 0, 2, 1],
            'Taille Cuisine': [35.5, 50.0, 35.5, 25.0]
        }
        return pd.DataFrame(data)
    
    def test_cleaner_initialization(self, cleaner):
        """Test l'initialisation du cleaner."""
        assert cleaner is not None
        assert isinstance(cleaner, DataCleaner)
    
    def test_clean_dataset_basic(self, cleaner, sample_dirty_data):
        """Test le nettoyage basique d'un dataset."""
        cleaned_df, report = cleaner.clean_dataset(sample_dirty_data)
        
        assert cleaned_df is not None
        assert isinstance(cleaned_df, pd.DataFrame)
        assert 'cleaning_report' in report
    
    def test_normalize_column_names(self, cleaner, sample_dirty_data):
        """Test la normalisation des noms de colonnes."""
        cleaned_df, _ = cleaner.clean_dataset(sample_dirty_data)
        
        # Vérifier que les colonnes sont normalisées (snake_case)
        for col in cleaned_df.columns:
            assert ' ' not in col  # Pas d'espaces
            assert col.islower() or '_' in col  # Minuscules ou snake_case
    
    def test_remove_duplicates(self, cleaner, sample_dirty_data):
        """Test la suppression des doublons."""
        initial_count = len(sample_dirty_data)
        cleaned_df, report = cleaner.clean_dataset(sample_dirty_data)
        
        # Il devrait y avoir moins de lignes (doublons supprimés)
        assert len(cleaned_df) <= initial_count
        assert 'duplicates_removed' in report['cleaning_report']
    
    def test_handle_missing_values_drop(self, cleaner, sample_dirty_data):
        """Test la gestion des valeurs manquantes avec stratégie 'drop'."""
        cleaned_df = cleaner.handle_missing_values(sample_dirty_data, strategy='drop')
        
        # Aucune valeur manquante ne devrait rester
        assert cleaned_df.isnull().sum().sum() == 0
    
    def test_handle_missing_values_mean(self, cleaner):
        """Test la gestion des valeurs manquantes avec stratégie 'mean'."""
        data = pd.DataFrame({
            'col1': [1, 2, None, 4, 5],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        
        cleaned_df = cleaner.handle_missing_values(data, strategy='mean')
        
        # La valeur manquante devrait être remplacée par la moyenne
        assert cleaned_df['col1'].isnull().sum() == 0
    
    def test_handle_missing_values_median(self, cleaner):
        """Test la gestion des valeurs manquantes avec stratégie 'median'."""
        data = pd.DataFrame({
            'col1': [1, 2, None, 4, 100],
            'col2': ['a', 'b', 'c', 'd', 'e']
        })
        
        cleaned_df = cleaner.handle_missing_values(data, strategy='median')
        
        assert cleaned_df['col1'].isnull().sum() == 0
    
    def test_handle_missing_values_mode(self, cleaner):
        """Test la gestion des valeurs manquantes avec stratégie 'mode'."""
        data = pd.DataFrame({
            'col1': ['A', 'A', None, 'B', 'A'],
            'col2': [1, 2, 3, 4, 5]
        })
        
        cleaned_df = cleaner.handle_missing_values(data, strategy='mode')
        
        assert cleaned_df['col1'].isnull().sum() == 0
    
    def test_normalize_text_columns(self, cleaner):
        """Test la normalisation des colonnes textuelles."""
        data = pd.DataFrame({
            'name': ['  RESTAURANT A  ', 'restaurant b', 'Restaurant C  '],
            'city': ['MONTREAL', 'quebec', '  Laval  ']
        })
        
        cleaned_df = cleaner.normalize_text_columns(data, columns=['name', 'city'])
        
        # Vérifier que le texte est normalisé
        assert cleaned_df['name'].iloc[0] == 'restaurant a'
        assert cleaned_df['city'].iloc[0] == 'montreal'
        assert '  ' not in cleaned_df['name'].iloc[0]  # Pas d'espaces multiples
    
    def test_detect_outliers_iqr(self, cleaner):
        """Test la détection d'outliers avec méthode IQR."""
        data = pd.DataFrame({
            'values': [1, 2, 3, 4, 5, 6, 7, 8, 9, 100]  # 100 est un outlier
        })
        
        outliers = cleaner.detect_outliers(data, 'values', method='iqr')
        
        assert outliers.sum() > 0  # Au moins un outlier détecté
        assert outliers.iloc[-1] == True  # Le dernier (100) devrait être un outlier
    
    def test_detect_outliers_zscore(self, cleaner):
        """Test la détection d'outliers avec méthode Z-score."""
        data = pd.DataFrame({
            'values': [10, 12, 11, 13, 12, 11, 10, 100]  # 100 est un outlier
        })
        
        outliers = cleaner.detect_outliers(data, 'values', method='zscore')
        
        assert outliers.sum() > 0
        assert outliers.iloc[-1] == True
    
    def test_get_data_quality_report(self, cleaner, sample_dirty_data):
        """Test la génération du rapport de qualité."""
        report = cleaner.get_data_quality_report(sample_dirty_data)
        
        assert 'total_rows' in report
        assert 'total_columns' in report
        assert 'missing_values' in report
        assert 'duplicate_rows' in report
        assert 'data_types' in report
        assert 'memory_usage' in report
        
        assert report['total_rows'] == len(sample_dirty_data)
        assert report['total_columns'] == len(sample_dirty_data.columns)
    
    def test_empty_dataframe_cleaning(self, cleaner):
        """Test le nettoyage d'un DataFrame vide."""
        empty_df = pd.DataFrame()
        cleaned_df, report = cleaner.clean_dataset(empty_df)
        
        assert len(cleaned_df) == 0
        assert 'cleaning_report' in report
    
    def test_all_null_rows_removal(self, cleaner):
        """Test la suppression des lignes entièrement nulles."""
        data = pd.DataFrame({
            'col1': [1, None, 3],
            'col2': [4, None, 6],
            'col3': [7, None, 9]
        })
        
        cleaned_df, _ = cleaner.clean_dataset(data)
        
        # La ligne du milieu (tout null) devrait être supprimée
        assert len(cleaned_df) < len(data)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
