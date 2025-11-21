"""
Module de nettoyage et normalisation des données MAPAQ.

Author: Grace Mandiangu
Date: November 21, 2025
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


if __name__ == "__main__":
    cleaner = DataCleaner()
    print("Module de nettoyage MAPAQ prêt.")
