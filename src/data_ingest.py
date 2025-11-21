"""
Module d'ingestion des données MAPAQ.

Ce module gère le téléchargement et l'importation des données
d'inspection des restaurants depuis les sources publiques du MAPAQ.
"""

import pandas as pd
import requests
from pathlib import Path
from typing import Optional, Dict
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MAPAQDataIngestor:
    """Classe pour l'ingestion des données MAPAQ."""
    
    def __init__(self, data_dir: str = "data/raw"):
        """
        Initialise l'ingesteur de données.
        
        Args:
            data_dir: Répertoire où sauvegarder les données brutes
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Ingesteur initialisé - Répertoire: {self.data_dir}")
    
    def load_csv(self, filepath: str, **kwargs) -> pd.DataFrame:
        """
        Charge un fichier CSV.
        
        Args:
            filepath: Chemin du fichier CSV
            **kwargs: Arguments supplémentaires pour pd.read_csv
            
        Returns:
            DataFrame contenant les données
        """
        logger.info(f"Chargement du fichier: {filepath}")
        df = pd.read_csv(filepath, encoding='utf-8-sig', **kwargs)
        logger.info(f"Données chargées: {len(df)} lignes, {len(df.columns)} colonnes")
        return df
    
    def download_from_url(self, url: str, output_filename: str) -> Optional[Path]:
        """
        Télécharge un fichier depuis une URL.
        
        Args:
            url: URL du fichier à télécharger
            output_filename: Nom du fichier de sortie
            
        Returns:
            Chemin du fichier téléchargé ou None en cas d'erreur
        """
        try:
            logger.info(f"Téléchargement depuis: {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            output_path = self.data_dir / output_filename
            with open(output_path, 'wb') as f:
                f.write(response.content)
            
            logger.info(f"Fichier sauvegardé: {output_path}")
            return output_path
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement: {e}")
            return None
    
    def get_data_info(self, df: pd.DataFrame) -> Dict:
        """
        Obtient des informations sur un dataset.
        
        Args:
            df: DataFrame à analyser
            
        Returns:
            Dictionnaire contenant les informations
        """
        return {
            'nombre_lignes': len(df),
            'nombre_colonnes': len(df.columns),
            'colonnes': list(df.columns),
            'valeurs_manquantes': df.isnull().sum().to_dict()
        }


if __name__ == "__main__":
    ingestor = MAPAQDataIngestor()
    print("Module d'ingestion MAPAQ prêt.")
