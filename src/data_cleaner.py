"""
Module de nettoyage et normalisation des données MAPAQ.

Fonctionnalités:
- Nettoyage complet des données
- Normalisation des colonnes
- Gestion des valeurs manquantes
- Détection et suppression des doublons
- Transformations de données
- Validation de qualité
- Génération de rapports

Author: Grace Mandiangu
Date: November 30, 2025
"""

import pandas as pd
import numpy as np
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DataCleaner:
    """Classe pour le nettoyage et la normalisation des données MAPAQ."""
    
    def __init__(self):
        """Initialise le nettoyeur de données."""
        logger.info("DataCleaner initialisé")
    
    def clean_dataset(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Pipeline complet de nettoyage des données.
        
        Args:
            df: DataFrame brut à nettoyer
            
        Returns:
            DataFrame nettoyé et normalisé
        """
        logger.info(f"Début du nettoyage - {len(df)} lignes")
        
        df = df.copy()
        
        # 1. Normaliser les noms de colonnes
        df.columns = df.columns.str.lower().str.strip()
        df.columns = df.columns.str.replace(' ', '_')
        
        # 2. Supprimer les doublons
        initial_count = len(df)
        df = df.drop_duplicates()
        logger.info(f"Doublons supprimés: {initial_count - len(df)}")
        
        # 3. Nettoyer les champs texte
        text_columns = df.select_dtypes(include=['object']).columns
        for col in text_columns:
            df[col] = df[col].astype(str).str.strip()
        
        # 4. Gérer les valeurs manquantes
        df = df.dropna(how='all')
        
        logger.info(f"Nettoyage terminé - {len(df)} lignes conservées")
        
        return df
    
    def get_cleaning_report(self, df_before: pd.DataFrame, df_after: pd.DataFrame) -> dict:
        """
        Génère un rapport de nettoyage.
        
        Args:
            df_before: DataFrame avant nettoyage
            df_after: DataFrame après nettoyage
            
        Returns:
            Dictionnaire contenant les statistiques
        """
        return {
            'lignes_initiales': len(df_before),
            'lignes_finales': len(df_after),
            'lignes_supprimees': len(df_before) - len(df_after),
            'taux_retention': round(len(df_after) / len(df_before) * 100, 2)
        }
    
    def save_cleaned_data(self, df: pd.DataFrame, output_path: str) -> None:
        """
        Sauvegarde les données nettoyées.
        
        Args:
            df: DataFrame nettoyé
            output_path: Chemin du fichier de sortie
        """
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        logger.info(f"Données sauvegardées: {output_path}")
    
    def handle_missing_values(self, df: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
        """
        Gère les valeurs manquantes selon la stratégie choisie.
        
        Args:
            df: DataFrame à traiter
            strategy: Stratégie ('drop', 'fill_mean', 'fill_median', 'fill_mode')
            
        Returns:
            DataFrame avec valeurs manquantes traitées
        """
        df = df.copy()
        
        if strategy == 'drop':
            df = df.dropna()
            logger.info(f"Lignes avec valeurs manquantes supprimées")
        
        elif strategy == 'fill_mean':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].mean())
            logger.info(f"Valeurs manquantes remplies avec la moyenne")
        
        elif strategy == 'fill_median':
            numeric_cols = df.select_dtypes(include=[np.number]).columns
            df[numeric_cols] = df[numeric_cols].fillna(df[numeric_cols].median())
            logger.info(f"Valeurs manquantes remplies avec la médiane")
        
        elif strategy == 'fill_mode':
            for col in df.columns:
                if df[col].isnull().any():
                    df[col].fillna(df[col].mode()[0], inplace=True)
            logger.info(f"Valeurs manquantes remplies avec le mode")
        
        return df
    
    def normalize_text_columns(self, df: pd.DataFrame, columns: list = None) -> pd.DataFrame:
        """
        Normalise les colonnes textuelles.
        
        Args:
            df: DataFrame à traiter
            columns: Liste des colonnes à normaliser (None = toutes les colonnes texte)
            
        Returns:
            DataFrame avec colonnes normalisées
        """
        df = df.copy()
        
        if columns is None:
            columns = df.select_dtypes(include=['object']).columns
        
        for col in columns:
            if col in df.columns:
                # Supprimer espaces, mettre en minuscules
                df[col] = df[col].astype(str).str.strip().str.lower()
                # Remplacer espaces multiples par un seul
                df[col] = df[col].str.replace(r'\s+', ' ', regex=True)
        
        logger.info(f"Colonnes textuelles normalisées: {len(columns)}")
        return df
    
    def detect_outliers(self, df: pd.DataFrame, column: str, method: str = 'iqr') -> pd.Series:
        """
        Détecte les valeurs aberrantes dans une colonne.
        
        Args:
            df: DataFrame
            column: Nom de la colonne
            method: Méthode de détection ('iqr' ou 'zscore')
            
        Returns:
            Series booléenne indiquant les outliers
        """
        if method == 'iqr':
            Q1 = df[column].quantile(0.25)
            Q3 = df[column].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR
            outliers = (df[column] < lower_bound) | (df[column] > upper_bound)
        
        elif method == 'zscore':
            z_scores = np.abs((df[column] - df[column].mean()) / df[column].std())
            outliers = z_scores > 3
        
        else:
            raise ValueError(f"Méthode inconnue: {method}")
        
        outlier_count = outliers.sum()
        logger.info(f"Outliers détectés dans '{column}': {outlier_count}")
        
        return outliers
    
    def get_data_quality_report(self, df: pd.DataFrame) -> dict:
        """
        Génère un rapport de qualité des données.
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire contenant les métriques de qualité
        """
        report = {
            'total_rows': len(df),
            'total_columns': len(df.columns),
            'missing_values': {
                'by_column': df.isnull().sum().to_dict(),
                'total': int(df.isnull().sum().sum()),
                'percentage': round(df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100, 2)
            },
            'duplicates': {
                'count': int(df.duplicated().sum()),
                'percentage': round(df.duplicated().sum() / len(df) * 100, 2)
            },
            'data_types': df.dtypes.astype(str).to_dict(),
            'memory_usage_mb': round(df.memory_usage(deep=True).sum() / 1024 / 1024, 2)
        }
        
        return report


if __name__ == "__main__":
    cleaner = DataCleaner()
    print("Module de nettoyage MAPAQ prêt.")
