"""
Script d'exemple pour le nettoyage et la normalisation des datasets MAPAQ.

Ce script démontre l'utilisation complète du pipeline de nettoyage
et de normalisation des données d'inspection des restaurants.

Author: Grace Mandiangu
Date: November 25, 2025
"""

import pandas as pd
import numpy as np
from pathlib import Path
import logging

from src.data_ingest import MAPAQDataIngestor
from src.data_cleaner import DataCleaner

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def create_sample_data():
    """
    Crée un dataset d'exemple avec des données non nettoyées.
    
    Returns:
        DataFrame avec des données brutes simulées
    """
    logger.info("Création d'un dataset d'exemple...")
    
    # Données d'exemple avec problèmes typiques
    data = {
        'Nom Restaurant': [
            '  Sushi Express  ',
            'Pizza Palace',
            'BBQ King',
            'Pizza Palace',  # Doublon
            'Café Bistro',
            '  Bakery Delight',
            'Fast Burger',
            None,  # Valeur manquante
            'Thai Garden',
            'Steakhouse Premium'
        ],
        'Adresse': [
            '123 Rue Saint-Laurent',
            '456 Av. Mont-Royal  ',
            '789 Boul. René-Lévesque',
            '456 Av. Mont-Royal',  # Doublon
            '321 Rue Sherbrooke',
            '654 Rue Sainte-Catherine  ',
            '987 Boul. Décarie',
            '111 Rue Principale',
            '222 Av. du Parc',
            '333 Rue Crescent'
        ],
        'Ville': [
            'MONTREAL',
            'montreal',
            'Montreal',
            'montreal',
            'Quebec',
            'LAVAL',
            'Montreal',
            'Gatineau',
            'Montreal',
            'Montreal'
        ],
        'Type Cuisine': [
            'Sushi',
            'Italian',
            'BBQ',
            'Italian',
            'French',
            'Bakery',
            'Fast Food',
            'Other',
            'Asian',
            'Steakhouse'
        ],
        'Nombre Employes': [
            10,
            15,
            8,
            15,
            12,
            5,
            20,
            np.nan,  # Valeur manquante
            7,
            18
        ],
        'Infractions': [
            2,
            0,
            1,
            0,
            0,
            1,
            3,
            1,
            0,
            1
        ],
        'Taille Cuisine': [
            35.5,
            50.0,
            40.0,
            50.0,
            45.5,
            25.0,
            60.0,
            30.0,
            28.5,
            55.0
        ],
        'Date Inspection': [
            '2024-01-15',
            '2024-02-20',
            '2024-03-10',
            '2024-02-20',
            '2024-04-05',
            '2024-05-12',
            '2024-06-18',
            '2024-07-22',
            '2024-08-30',
            '2024-09-15'
        ]
    }
    
    df = pd.DataFrame(data)
    logger.info(f"Dataset créé avec {len(df)} lignes et {len(df.columns)} colonnes")
    
    return df


def analyze_data_quality(df: pd.DataFrame, title: str = "Dataset"):
    """
    Analyse la qualité des données.
    
    Args:
        df: DataFrame à analyser
        title: Titre pour l'affichage
    """
    print(f"\n{'='*60}")
    print(f"ANALYSE DE QUALITÉ - {title}")
    print(f"{'='*60}")
    
    print(f"\n📊 Dimensions: {df.shape[0]} lignes × {df.shape[1]} colonnes")
    
    print(f"\n📋 Colonnes:")
    for col in df.columns:
        print(f"  - {col}")
    
    print(f"\n❌ Valeurs manquantes:")
    missing = df.isnull().sum()
    for col, count in missing.items():
        if count > 0:
            percentage = (count / len(df)) * 100
            print(f"  - {col}: {count} ({percentage:.1f}%)")
    
    print(f"\n🔄 Doublons: {df.duplicated().sum()}")
    
    print(f"\n📈 Statistiques numériques:")
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        print(df[numeric_cols].describe().round(2))


def clean_and_normalize_pipeline():
    """
    Pipeline complet de nettoyage et normalisation.
    """
    print("\n" + "="*80)
    print("🧹 PIPELINE DE NETTOYAGE ET NORMALISATION DES DONNÉES MAPAQ")
    print("="*80)
    
    # 1. Créer des données d'exemple
    print("\n📥 ÉTAPE 1: Création des données d'exemple")
    df_raw = create_sample_data()
    
    # Analyser les données brutes
    analyze_data_quality(df_raw, "DONNÉES BRUTES")
    
    # 2. Initialiser le nettoyeur
    print("\n🔧 ÉTAPE 2: Initialisation du DataCleaner")
    cleaner = DataCleaner()
    
    # 3. Nettoyer les données
    print("\n🧹 ÉTAPE 3: Nettoyage des données")
    df_clean = cleaner.clean_dataset(df_raw)
    
    # Analyser les données nettoyées
    analyze_data_quality(df_clean, "DONNÉES NETTOYÉES")
    
    # 4. Générer un rapport de nettoyage
    print("\n📊 ÉTAPE 4: Rapport de nettoyage")
    report = cleaner.get_cleaning_report(df_raw, df_clean)
    
    print(f"\n{'='*60}")
    print("RAPPORT DE NETTOYAGE")
    print(f"{'='*60}")
    print(f"Lignes initiales:    {report['lignes_initiales']}")
    print(f"Lignes finales:      {report['lignes_finales']}")
    print(f"Lignes supprimées:   {report['lignes_supprimees']}")
    print(f"Taux de rétention:   {report['taux_retention']}%")
    
    # 5. Normalisation avancée
    print("\n🔄 ÉTAPE 5: Normalisation avancée")
    df_normalized = advanced_normalization(df_clean)
    
    # 6. Sauvegarder les données nettoyées
    print("\n💾 ÉTAPE 6: Sauvegarde des données")
    output_dir = Path("data/cleaned")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    output_path = output_dir / "restaurants_cleaned.csv"
    cleaner.save_cleaned_data(df_normalized, str(output_path))
    
    print(f"\n✅ Données nettoyées sauvegardées: {output_path}")
    
    # 7. Afficher un aperçu final
    print("\n👀 APERÇU DES DONNÉES FINALES:")
    print(df_normalized.head(10).to_string())
    
    return df_normalized


def advanced_normalization(df: pd.DataFrame) -> pd.DataFrame:
    """
    Normalisation avancée des données.
    
    Args:
        df: DataFrame à normaliser
        
    Returns:
        DataFrame normalisé
    """
    df = df.copy()
    
    # Normaliser les noms de villes
    if 'ville' in df.columns:
        df['ville'] = df['ville'].str.upper().str.strip()
        logger.info("Villes normalisées en majuscules")
    
    # Normaliser les types de cuisine
    if 'type_cuisine' in df.columns:
        df['type_cuisine'] = df['type_cuisine'].str.title().str.strip()
        logger.info("Types de cuisine normalisés")
    
    # Convertir les dates
    if 'date_inspection' in df.columns:
        df['date_inspection'] = pd.to_datetime(df['date_inspection'])
        logger.info("Dates converties en format datetime")
    
    # Remplir les valeurs manquantes numériques
    numeric_cols = df.select_dtypes(include=[np.number]).columns
    for col in numeric_cols:
        if df[col].isnull().any():
            median_val = df[col].median()
            df[col].fillna(median_val, inplace=True)
            logger.info(f"Valeurs manquantes de '{col}' remplies avec la médiane: {median_val}")
    
    # Créer des colonnes dérivées
    if 'nombre_employes' in df.columns:
        df['categorie_taille'] = pd.cut(
            df['nombre_employes'],
            bins=[0, 5, 15, 100],
            labels=['Petit', 'Moyen', 'Grand']
        )
        logger.info("Colonne 'categorie_taille' créée")
    
    if 'infractions' in df.columns:
        df['niveau_conformite'] = df['infractions'].apply(
            lambda x: 'Excellent' if x == 0 else 'Bon' if x <= 1 else 'À améliorer'
        )
        logger.info("Colonne 'niveau_conformite' créée")
    
    return df


def main():
    """Fonction principale."""
    try:
        # Exécuter le pipeline complet
        df_final = clean_and_normalize_pipeline()
        
        print("\n" + "="*80)
        print("✅ PIPELINE TERMINÉ AVEC SUCCÈS!")
        print("="*80)
        print(f"\nDataset final: {len(df_final)} lignes × {len(df_final.columns)} colonnes")
        print(f"Fichier sauvegardé: data/cleaned/restaurants_cleaned.csv")
        
    except Exception as e:
        logger.error(f"Erreur lors de l'exécution: {str(e)}")
        raise


if __name__ == "__main__":
    main()
