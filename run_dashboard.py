"""
Script de démarrage du Dashboard Interactif MAPAQ Risk Intelligence.

Ce script initialise et démarre le serveur Flask pour le dashboard
avec visualisations interactives et statistiques en temps réel.

Author: Grace Mandiangu
Date: November 28, 2025
"""

import sys
import os
import logging
from pathlib import Path

# Ajouter le répertoire dashboard au path
dashboard_dir = os.path.join(os.path.dirname(__file__), 'dashboard')
sys.path.insert(0, dashboard_dir)

from dashboard.app import app

# Configuration du logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def print_banner():
    """Affiche la bannière de démarrage du dashboard."""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║        📊 MAPAQ RISK INTELLIGENCE DASHBOARD                 ║
    ║                                                              ║
    ║        Dashboard Interactif avec Visualisations             ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    
    🌐 Pages disponibles:
    
    • GET  /                    - Page d'accueil
    • GET  /dashboard           - Dashboard avec graphiques
    • GET  /predict-form        - Formulaire de prédiction
    • GET  /about               - À propos du projet
    • POST /api/predict         - API de prédiction
    • GET  /api/statistics      - Statistiques globales
    
    📊 Visualisations:
    • Graphique circulaire - Distribution des risques
    • Graphique en barres - Restaurants par région
    • Graphique en barres - Types de cuisine
    • Jauge - Niveau de risque moyen
    
    🔧 Configuration:
    • Host: 0.0.0.0
    • Port: 8080
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


def check_templates():
    """Vérifie que les templates HTML existent."""
    templates_dir = Path("dashboard/templates")
    required_templates = [
        'index.html',
        'dashboard.html',
        'predict_form.html',
        'about.html',
        '404.html',
        '500.html'
    ]
    
    missing = []
    for template in required_templates:
        if not (templates_dir / template).exists():
            missing.append(template)
    
    if missing:
        logger.warning(f"⚠️  Templates manquants: {', '.join(missing)}")
        logger.warning("Certaines pages pourraient ne pas fonctionner correctement")
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
        
        # Vérifier les templates
        logger.info("Vérification des templates...")
        if check_templates():
            logger.info("✅ Tous les templates sont présents")
        
        # Vérifier que les répertoires nécessaires existent
        data_dir = Path("data")
        if not data_dir.exists():
            logger.warning("⚠️  Répertoire 'data' manquant, création...")
            data_dir.mkdir(parents=True)
        
        # Démarrer le serveur
        logger.info("🚀 Démarrage du serveur Dashboard...")
        logger.info("📍 Dashboard accessible sur: http://localhost:8080")
        logger.info("📖 Pages:")
        logger.info("   • Accueil:    http://localhost:8080/")
        logger.info("   • Dashboard:  http://localhost:8080/dashboard")
        logger.info("   • Prédiction: http://localhost:8080/predict-form")
        logger.info("   • À propos:   http://localhost:8080/about")
        logger.info("")
        logger.info("Appuyez sur CTRL+C pour arrêter le serveur")
        logger.info("═" * 63)
        
        # Lancer l'application Flask
        app.run(
            host='0.0.0.0',
            port=8080,
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
