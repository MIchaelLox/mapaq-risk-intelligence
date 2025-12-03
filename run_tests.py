"""
Script d'exécution des tests automatisés pour MAPAQ Risk Intelligence.

Ce script permet d'exécuter la suite complète de tests avec différentes options.

Author: Grace Mandiangu
Date: December 2, 2025
"""

import sys
import os
import subprocess
from pathlib import Path


def print_banner():
    """Affiche la bannière du script de tests."""
    banner = """
╔══════════════════════════════════════════════════════════════════╗
║                                                                  ║
║         🧪 MAPAQ RISK INTELLIGENCE - TEST SUITE 🧪              ║
║                                                                  ║
║              Automated Testing Framework                         ║
║              Author: Grace Mandiangu                             ║
║                                                                  ║
╚══════════════════════════════════════════════════════════════════╝
"""
    print(banner)


def check_pytest_installed():
    """Vérifie si pytest est installé."""
    try:
        import pytest
        print(f"✅ pytest version {pytest.__version__} détecté")
        return True
    except ImportError:
        print("❌ pytest n'est pas installé!")
        print("\n💡 Installation requise:")
        print("   pip install -r requirements.txt")
        return False


def run_all_tests():
    """Exécute tous les tests."""
    print("\n" + "="*70)
    print("  EXÉCUTION DE TOUS LES TESTS")
    print("="*70 + "\n")
    
    cmd = ["pytest", "tests/", "-v", "--cov=src", "--cov-report=term-missing"]
    result = subprocess.run(cmd)
    return result.returncode


def run_unit_tests():
    """Exécute uniquement les tests unitaires."""
    print("\n" + "="*70)
    print("  EXÉCUTION DES TESTS UNITAIRES")
    print("="*70 + "\n")
    
    cmd = ["pytest", "tests/", "-v", "-m", "unit"]
    result = subprocess.run(cmd)
    return result.returncode


def run_integration_tests():
    """Exécute uniquement les tests d'intégration."""
    print("\n" + "="*70)
    print("  EXÉCUTION DES TESTS D'INTÉGRATION")
    print("="*70 + "\n")
    
    cmd = ["pytest", "tests/", "-v", "-m", "integration"]
    result = subprocess.run(cmd)
    return result.returncode


def run_api_tests():
    """Exécute uniquement les tests de l'API."""
    print("\n" + "="*70)
    print("  EXÉCUTION DES TESTS API")
    print("="*70 + "\n")
    
    cmd = ["pytest", "tests/test_api.py", "-v"]
    result = subprocess.run(cmd)
    return result.returncode


def run_specific_test(test_file):
    """Exécute un fichier de test spécifique."""
    print(f"\n" + "="*70)
    print(f"  EXÉCUTION DE {test_file}")
    print("="*70 + "\n")
    
    cmd = ["pytest", f"tests/{test_file}", "-v"]
    result = subprocess.run(cmd)
    return result.returncode


def run_with_coverage():
    """Exécute les tests avec rapport de couverture détaillé."""
    print("\n" + "="*70)
    print("  TESTS AVEC RAPPORT DE COUVERTURE")
    print("="*70 + "\n")
    
    cmd = [
        "pytest",
        "tests/",
        "-v",
        "--cov=src",
        "--cov-report=html",
        "--cov-report=term-missing",
        "--cov-branch"
    ]
    result = subprocess.run(cmd)
    
    if result.returncode == 0:
        print("\n" + "="*70)
        print("  📊 RAPPORT DE COUVERTURE GÉNÉRÉ")
        print("="*70)
        print("\n📁 Rapport HTML disponible dans: htmlcov/index.html")
        print("💡 Ouvrez ce fichier dans votre navigateur pour voir les détails")
    
    return result.returncode


def show_menu():
    """Affiche le menu interactif."""
    print("\n" + "="*70)
    print("  MENU DES TESTS")
    print("="*70)
    print("\n  1. Exécuter tous les tests")
    print("  2. Exécuter les tests unitaires")
    print("  3. Exécuter les tests d'intégration")
    print("  4. Exécuter les tests API")
    print("  5. Exécuter un test spécifique")
    print("  6. Exécuter avec rapport de couverture")
    print("  7. Quitter")
    print("\n" + "="*70)


def main():
    """Fonction principale."""
    print_banner()
    
    # Vérifier que pytest est installé
    if not check_pytest_installed():
        sys.exit(1)
    
    # Vérifier que nous sommes dans le bon répertoire
    if not Path("tests").exists():
        print("\n❌ Erreur: Le répertoire 'tests' n'existe pas!")
        print("💡 Assurez-vous d'exécuter ce script depuis la racine du projet.")
        sys.exit(1)
    
    # Si des arguments sont fournis
    if len(sys.argv) > 1:
        option = sys.argv[1]
        
        if option == "--all":
            return run_all_tests()
        elif option == "--unit":
            return run_unit_tests()
        elif option == "--integration":
            return run_integration_tests()
        elif option == "--api":
            return run_api_tests()
        elif option == "--coverage":
            return run_with_coverage()
        elif option.startswith("--file="):
            test_file = option.split("=")[1]
            return run_specific_test(test_file)
        else:
            print(f"\n❌ Option inconnue: {option}")
            print("\n💡 Options disponibles:")
            print("   --all          : Tous les tests")
            print("   --unit         : Tests unitaires")
            print("   --integration  : Tests d'intégration")
            print("   --api          : Tests API")
            print("   --coverage     : Tests avec couverture")
            print("   --file=<nom>   : Test spécifique")
            return 1
    
    # Mode interactif
    while True:
        show_menu()
        choice = input("\n👉 Votre choix (1-7): ").strip()
        
        if choice == '1':
            run_all_tests()
        elif choice == '2':
            run_unit_tests()
        elif choice == '3':
            run_integration_tests()
        elif choice == '4':
            run_api_tests()
        elif choice == '5':
            print("\n📁 Fichiers de test disponibles:")
            test_files = list(Path("tests").glob("test_*.py"))
            for i, file in enumerate(test_files, 1):
                print(f"   {i}. {file.name}")
            
            file_choice = input("\n👉 Numéro du fichier: ").strip()
            try:
                file_idx = int(file_choice) - 1
                if 0 <= file_idx < len(test_files):
                    run_specific_test(test_files[file_idx].name)
                else:
                    print("❌ Numéro invalide!")
            except ValueError:
                print("❌ Entrée invalide!")
        elif choice == '6':
            run_with_coverage()
        elif choice == '7':
            print("\n👋 Au revoir!\n")
            break
        else:
            print("\n❌ Choix invalide! Veuillez choisir entre 1 et 7.")
        
        input("\n⏸️  Appuyez sur Entrée pour continuer...")


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print("\n\n⚠️  Interruption par l'utilisateur")
        sys.exit(0)
