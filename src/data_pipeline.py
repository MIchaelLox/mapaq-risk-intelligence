"""
Module de pipeline de données complet pour MAPAQ Risk Intelligence.

Ce module orchestre l'ensemble du flux de traitement des données:
1. Ingestion des données brutes
2. Validation et nettoyage
3. Transformation et enrichissement
4. Sauvegarde des données traitées
5. Génération de rapports

Author: Grace Mandiangu
Date: November 30, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import logging
import json
from datetime import datetime

from data_ingest import MAPAQDataIngestor
from data_cleaner import DataCleaner
from probability_model import ConditionalProbabilityEngine

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class DataPipeline:
    """
    Pipeline complet de traitement des données MAPAQ.
    
    Gère l'ensemble du flux depuis l'ingestion jusqu'à la préparation
    des données pour le modèle de prédiction.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialise le pipeline de données.
        
        Args:
            config_path: Chemin vers le fichier de configuration JSON
        """
        self.config = self._load_config(config_path)
        self.ingestor = MAPAQDataIngestor(self.config['raw_data_dir'])
        self.cleaner = DataCleaner()
        self.engine = ConditionalProbabilityEngine()
        
        # Créer les répertoires nécessaires
        Path(self.config['cleaned_data_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['processed_data_dir']).mkdir(parents=True, exist_ok=True)
        Path(self.config['reports_dir']).mkdir(parents=True, exist_ok=True)
        
        logger.info("Pipeline de données initialisé")
    
    def _load_config(self, config_path: Optional[str]) -> Dict:
        """
        Charge la configuration du pipeline.
        
        Args:
            config_path: Chemin vers le fichier de configuration
            
        Returns:
            Dictionnaire de configuration
        """
        default_config = {
            'raw_data_dir': 'data/raw',
            'cleaned_data_dir': 'data/cleaned',
            'processed_data_dir': 'data/processed',
            'reports_dir': 'data/reports',
            'required_columns': [
                'nom_etablissement',
                'adresse',
                'ville',
                'type_cuisine',
                'nombre_employes',
                'infractions'
            ],
            'validation_rules': {
                'nombre_employes': {'min': 0, 'max': 500},
                'infractions': {'min': 0, 'max': 100}
            }
        }
        
        if config_path and Path(config_path).exists():
            with open(config_path, 'r', encoding='utf-8') as f:
                user_config = json.load(f)
                default_config.update(user_config)
        
        return default_config
    
    def run_full_pipeline(self, input_file: str, output_name: str = None) -> Dict:
        """
        Exécute le pipeline complet de traitement des données.
        
        Args:
            input_file: Chemin du fichier de données brutes
            output_name: Nom de base pour les fichiers de sortie
            
        Returns:
            Dictionnaire contenant les statistiques du pipeline
        """
        logger.info("=" * 70)
        logger.info("DÉMARRAGE DU PIPELINE DE DONNÉES COMPLET")
        logger.info("=" * 70)
        
        start_time = datetime.now()
        
        if output_name is None:
            output_name = f"processed_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Étape 1: Ingestion
        logger.info("\n[ÉTAPE 1/5] Ingestion des données...")
        df_raw = self._ingest_data(input_file)
        
        # Étape 2: Validation
        logger.info("\n[ÉTAPE 2/5] Validation des données...")
        df_validated, validation_report = self._validate_data(df_raw)
        
        # Étape 3: Nettoyage
        logger.info("\n[ÉTAPE 3/5] Nettoyage des données...")
        df_cleaned = self._clean_data(df_validated)
        
        # Étape 4: Transformation et enrichissement
        logger.info("\n[ÉTAPE 4/5] Transformation et enrichissement...")
        df_processed = self._transform_data(df_cleaned)
        
        # Étape 5: Sauvegarde et rapport
        logger.info("\n[ÉTAPE 5/5] Sauvegarde et génération du rapport...")
        self._save_outputs(df_processed, output_name)
        
        # Générer le rapport final
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        final_report = self._generate_final_report(
            df_raw, df_validated, df_cleaned, df_processed,
            validation_report, duration
        )
        
        # Sauvegarder le rapport
        report_path = Path(self.config['reports_dir']) / f"{output_name}_report.json"
        with open(report_path, 'w', encoding='utf-8') as f:
            json.dump(final_report, f, indent=2, ensure_ascii=False)
        
        logger.info(f"\n✅ Pipeline terminé avec succès en {duration:.2f} secondes")
        logger.info(f"📊 Rapport sauvegardé: {report_path}")
        logger.info("=" * 70)
        
        return final_report
    
    def _ingest_data(self, input_file: str) -> pd.DataFrame:
        """
        Ingère les données depuis un fichier.
        
        Args:
            input_file: Chemin du fichier source
            
        Returns:
            DataFrame contenant les données brutes
        """
        df = self.ingestor.load_csv(input_file)
        logger.info(f"✓ Données ingérées: {len(df)} lignes, {len(df.columns)} colonnes")
        return df
    
    def _validate_data(self, df: pd.DataFrame) -> Tuple[pd.DataFrame, Dict]:
        """
        Valide les données selon les règles définies.
        
        Args:
            df: DataFrame à valider
            
        Returns:
            Tuple (DataFrame validé, rapport de validation)
        """
        df_valid = df.copy()
        report = {
            'total_rows': len(df),
            'issues': [],
            'warnings': []
        }
        
        # Vérifier les colonnes requises
        missing_cols = set(self.config['required_columns']) - set(df.columns)
        if missing_cols:
            report['warnings'].append(f"Colonnes manquantes: {missing_cols}")
            logger.warning(f"⚠️  Colonnes manquantes: {missing_cols}")
        
        # Valider les valeurs numériques
        for col, rules in self.config['validation_rules'].items():
            if col in df.columns:
                invalid_mask = (
                    (df[col] < rules['min']) | 
                    (df[col] > rules['max'])
                )
                invalid_count = invalid_mask.sum()
                
                if invalid_count > 0:
                    report['issues'].append({
                        'column': col,
                        'invalid_count': int(invalid_count),
                        'rule': f"Valeurs hors limites [{rules['min']}, {rules['max']}]"
                    })
                    logger.warning(f"⚠️  {col}: {invalid_count} valeurs invalides")
                    
                    # Filtrer les lignes invalides
                    df_valid = df_valid[~invalid_mask]
        
        report['valid_rows'] = len(df_valid)
        report['removed_rows'] = len(df) - len(df_valid)
        
        logger.info(f"✓ Validation terminée: {report['valid_rows']}/{report['total_rows']} lignes valides")
        
        return df_valid, report
    
    def _clean_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Nettoie les données.
        
        Args:
            df: DataFrame à nettoyer
            
        Returns:
            DataFrame nettoyé
        """
        df_before = df.copy()
        df_cleaned = self.cleaner.clean_dataset(df)
        
        cleaning_report = self.cleaner.get_cleaning_report(df_before, df_cleaned)
        logger.info(f"✓ Nettoyage: {cleaning_report['taux_retention']}% de rétention")
        
        return df_cleaned
    
    def _transform_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Transforme et enrichit les données.
        
        Args:
            df: DataFrame à transformer
            
        Returns:
            DataFrame transformé
        """
        df_transformed = df.copy()
        
        # 1. Normaliser les noms de colonnes
        column_mapping = {
            'nom_etablissement': 'restaurant_name',
            'type_cuisine': 'cuisine_type',
            'nombre_employes': 'staff_count',
            'infractions': 'infractions_history',
            'taille_cuisine': 'kitchen_size',
            'region': 'region'
        }
        
        for old_col, new_col in column_mapping.items():
            if old_col in df_transformed.columns:
                df_transformed.rename(columns={old_col: new_col}, inplace=True)
        
        # 2. Créer des features dérivées
        if 'staff_count' in df_transformed.columns:
            df_transformed['staff_category'] = pd.cut(
                df_transformed['staff_count'],
                bins=[0, 5, 15, 50, float('inf')],
                labels=['Très petit', 'Petit', 'Moyen', 'Grand']
            )
        
        if 'infractions_history' in df_transformed.columns:
            df_transformed['risk_category'] = pd.cut(
                df_transformed['infractions_history'],
                bins=[-1, 0, 2, 5, float('inf')],
                labels=['Aucun', 'Faible', 'Moyen', 'Élevé']
            )
        
        # 3. Ajouter des métadonnées
        df_transformed['processed_date'] = datetime.now().strftime('%Y-%m-%d')
        df_transformed['pipeline_version'] = '1.0'
        
        logger.info(f"✓ Transformation: {len(df_transformed.columns)} colonnes finales")
        
        return df_transformed
    
    def _save_outputs(self, df: pd.DataFrame, output_name: str) -> None:
        """
        Sauvegarde les données traitées.
        
        Args:
            df: DataFrame à sauvegarder
            output_name: Nom de base pour les fichiers
        """
        # Sauvegarder en CSV
        csv_path = Path(self.config['processed_data_dir']) / f"{output_name}.csv"
        df.to_csv(csv_path, index=False, encoding='utf-8-sig')
        logger.info(f"✓ CSV sauvegardé: {csv_path}")
        
        # Sauvegarder en JSON
        json_path = Path(self.config['processed_data_dir']) / f"{output_name}.json"
        df.to_json(json_path, orient='records', force_ascii=False, indent=2)
        logger.info(f"✓ JSON sauvegardé: {json_path}")
    
    def _generate_final_report(
        self,
        df_raw: pd.DataFrame,
        df_validated: pd.DataFrame,
        df_cleaned: pd.DataFrame,
        df_processed: pd.DataFrame,
        validation_report: Dict,
        duration: float
    ) -> Dict:
        """
        Génère le rapport final du pipeline.
        
        Args:
            df_raw: DataFrame brut
            df_validated: DataFrame validé
            df_cleaned: DataFrame nettoyé
            df_processed: DataFrame final
            validation_report: Rapport de validation
            duration: Durée d'exécution en secondes
            
        Returns:
            Dictionnaire contenant le rapport complet
        """
        report = {
            'pipeline_info': {
                'version': '1.0',
                'author': 'Grace Mandiangu',
                'execution_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                'duration_seconds': round(duration, 2)
            },
            'data_flow': {
                'raw_rows': len(df_raw),
                'validated_rows': len(df_validated),
                'cleaned_rows': len(df_cleaned),
                'final_rows': len(df_processed),
                'total_loss': len(df_raw) - len(df_processed),
                'retention_rate': round(len(df_processed) / len(df_raw) * 100, 2)
            },
            'validation': validation_report,
            'final_schema': {
                'columns': list(df_processed.columns),
                'dtypes': {col: str(dtype) for col, dtype in df_processed.dtypes.items()}
            },
            'statistics': {
                'missing_values': df_processed.isnull().sum().to_dict(),
                'numeric_summary': df_processed.describe().to_dict() if len(df_processed.select_dtypes(include=[np.number]).columns) > 0 else {}
            }
        }
        
        return report
    
    def get_pipeline_status(self) -> Dict:
        """
        Obtient le statut actuel du pipeline.
        
        Returns:
            Dictionnaire contenant les informations de statut
        """
        return {
            'config': self.config,
            'directories_exist': {
                'raw': Path(self.config['raw_data_dir']).exists(),
                'cleaned': Path(self.config['cleaned_data_dir']).exists(),
                'processed': Path(self.config['processed_data_dir']).exists(),
                'reports': Path(self.config['reports_dir']).exists()
            }
        }


if __name__ == "__main__":
    # Exemple d'utilisation
    pipeline = DataPipeline()
    print("Pipeline de données MAPAQ prêt.")
    print(f"Configuration: {pipeline.config}")
