"""
Script de démarrage de l'API REST MAPAQ Risk Intelligence.

Ce script initialise et démarre le serveur Flask pour exposer
les endpoints de prédiction de risque sanitaire.

Author: Grace Mandiangu
Date: November 28, 2025
"""

import sys
import os
import logging
from pathlib import Path

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.api import app

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Affiche la bannière de démarrage."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        🧬 MAPAQ RISK INTELLIGENCE API                        ║
    ║                                                              ║
    ║        Prédiction de risque sanitaire pour restaurants      ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    📡 Endpoints disponibles:
    
    • GET  /health              - Vérification de santé
    • POST /predict             - Prédiction de risque simple
    • POST /predict/batch       - Prédictions multiples
    • POST /predict/explain     - Prédiction avec explication
    
    🔧 Configuration:
    • Host: 0.0.0.0
    • Port: 5000
    • Mode: Development
    
    👤 Développé par: Grace Mandiangu
    📅 Version: 1.0
    
    ═══════════════════════════════════════════════════════════════
    """
    print(banner)


def check_dependencies():
    """Vérifie que toutes les dépendances sont installées."""
    required_modules = ['flask', 'pandas', 'numpy']
    missing = []
    
    for module in required_modules:
        try:
            __import__(module)
        except ImportError:
            missing.append(module)
    
    if missing:
        logger.error(f"Modules manquants: {', '.join(missing)}")
        logger.error("Installez-les avec: pip install " + " ".join(missing))
        return False
    
    return True


def main():
    """Fonction principale de démarrage."""
    try:
        print_banner()
        
        # Vérifier les dépendances
        logger.info("Vérification des dépendances...")
        if not check_dependencies():
            sys.exit(1)
        
        logger.info("✅ Toutes les dépendances sont installées")
        
        # Vérifier que les répertoires nécessaires existent
        data_dir = Path("data")
        if not data_dir.exists():
            logger.warning("⚠️  Répertoire 'data' manquant, création...")
            data_dir.mkdir(parents=True)
        
        # Démarrer le serveur
        logger.info("🚀 Démarrage du serveur API...")
        logger.info("📍 API accessible sur: http://localhost:5000")
        logger.info("📖 Documentation: Voir README.md pour exemples d'utilisation")
        logger.info("")
        logger.info("Appuyez sur CTRL+C pour arrêter le serveur")
        logger.info("═" * 63)
        
        # Lancer l'application Flask
        app.run(
            host='0.0.0.0',
            port=5000,
            debug=True,
            use_reloader=True
        )
    
    except KeyboardInterrupt:
        logger.info("\n\n🛑 Arrêt du serveur demandé par l'utilisateur")
        logger.info("👋 Au revoir!")
        sys.exit(0)
    
    except Exception as e:
        logger.error(f"❌ Erreur lors du démarrage: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
