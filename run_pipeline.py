"""
Script d'exécution du pipeline de données MAPAQ Risk Intelligence.

Ce script permet d'exécuter le pipeline complet de traitement des données
avec une interface en ligne de commande conviviale.

Author: Grace Mandiangu
Date: November 30, 2025
"""

import sys
import os
from pathlib import Path
import logging
import argparse

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.data_pipeline import DataPipeline

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Affiche la bannière du pipeline."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🔄 MAPAQ RISK INTELLIGENCE DATA PIPELINE              ║
    ║                                                              ║
    ║        Pipeline Complet de Traitement des Données           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📊 Étapes du Pipeline:
    
    1️⃣  Ingestion       - Chargement des données brutes
    2️⃣  Validation      - Vérification des règles métier
    3️⃣  Nettoyage       - Suppression doublons, normalisation
    4️⃣  Transformation  - Enrichissement et features
    5️⃣  Sauvegarde      - Export CSV/JSON + Rapport
    
    👤 Développé par: Grace Mandiangu
    📅 Version: 1.0
    
    ═══════════════════════════════════════════════════════════════
    """
    print(banner)


def parse_arguments():
    """
    Parse les arguments de la ligne de commande.
    
    Returns:
        Arguments parsés
    """
    parser = argparse.ArgumentParser(
        description='Pipeline de traitement des données MAPAQ',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'input_file',
        type=str,
        help='Chemin du fichier de données brutes (CSV)'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        default=None,
        help='Nom de base pour les fichiers de sortie (optionnel)'
    )
    
    parser.add_argument(
        '-c', '--config',
        type=str,
        default=None,
        help='Chemin du fichier de configuration JSON (optionnel)'
    )
    
    parser.add_argument(
        '--status',
        action='store_true',
        help='Afficher le statut du pipeline sans exécution'
    )
    
    return parser.parse_args()


def check_input_file(filepath: str) -> bool:
    """
    Vérifie que le fichier d'entrée existe.
    
    Args:
        filepath: Chemin du fichier
        
    Returns:
        True si le fichier existe, False sinon
    """
    if not Path(filepath).exists():
        logger.error(f"❌ Fichier introuvable: {filepath}")
        return False
    
    if not filepath.endswith('.csv'):
        logger.warning(f"⚠️  Le fichier n'est pas un CSV: {filepath}")
    
    return True


def display_pipeline_status(pipeline: DataPipeline):
    """
    Affiche le statut du pipeline.
    
    Args:
        pipeline: Instance du pipeline
    """
    status = pipeline.get_pipeline_status()
    
    print("\n📊 STATUT DU PIPELINE")
    print("=" * 60)
    
    print("\n📁 Configuration:")
    for key, value in status['config'].items():
        print(f"  • {key}: {value}")
    
    print("\n📂 Répertoires:")
    for dir_name, exists in status['directories_exist'].items():
        status_icon = "✅" if exists else "❌"
        print(f"  {status_icon} {dir_name}: {'Existe' if exists else 'Manquant'}")
    
    print("\n" + "=" * 60)


def main():
    """Fonction principale."""
    try:
        print_banner()
        
        # Parser les arguments
        args = parse_arguments()
        
        # Initialiser le pipeline
        logger.info("Initialisation du pipeline...")
        pipeline = DataPipeline(config_path=args.config)
        
        # Mode statut uniquement
        if args.status:
            display_pipeline_status(pipeline)
            return 0
        
        # Vérifier le fichier d'entrée
        if not check_input_file(args.input_file):
            return 1
        
        logger.info(f"📂 Fichier d'entrée: {args.input_file}")
        
        if args.output:
            logger.info(f"📝 Nom de sortie: {args.output}")
        
        # Exécuter le pipeline
        print("\n🚀 Démarrage du pipeline...\n")
        
        report = pipeline.run_full_pipeline(
            input_file=args.input_file,
            output_name=args.output
        )
        
        # Afficher le résumé
        print("\n" + "=" * 70)
        print("📊 RÉSUMÉ DU PIPELINE")
        print("=" * 70)
        print(f"\n⏱️  Durée: {report['pipeline_info']['duration_seconds']} secondes")
        print(f"\n📈 Flux de données:")
        print(f"  • Lignes brutes:      {report['data_flow']['raw_rows']}")
        print(f"  • Lignes validées:    {report['data_flow']['validated_rows']}")
        print(f"  • Lignes nettoyées:   {report['data_flow']['cleaned_rows']}")
        print(f"  • Lignes finales:     {report['data_flow']['final_rows']}")
        print(f"  • Taux de rétention:  {report['data_flow']['retention_rate']}%")
        
        if report['validation']['issues']:
            print(f"\n⚠️  Problèmes détectés: {len(report['validation']['issues'])}")
            for issue in report['validation']['issues'][:3]:  # Afficher max 3
                print(f"  • {issue['column']}: {issue['invalid_count']} valeurs invalides")
        
        print(f"\n✅ Pipeline terminé avec succès!")
        print(f"📁 Fichiers générés dans: data/processed/ et data/reports/")
        print("=" * 70 + "\n")
        
        return 0
    
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Pipeline interrompu par l'utilisateur")
        return 130
    
    except Exception as e:
        logger.error(f"\n❌ Erreur lors de l'exécution du pipeline: {str(e)}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
