"""
Script de test pour les fonctionnalités avancées du modèle de probabilités v3.

Teste les nouvelles fonctionnalités:
- Calibration du modèle
- Validation croisée
- Analyse de sensibilité
- Prédiction avec confiance
- Sauvegarde/chargement du modèle

Author: Grace Mandiangu
Date: December 1, 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
import sys
import os

# Ajouter le répertoire src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.probability_model import ConditionalProbabilityEngine


def print_section(title):
    """Affiche un titre de section."""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70 + "\n")


def generate_sample_data(n_samples=100):
    """Génère des données d'exemple pour les tests."""
    np.random.seed(42)
    
    cuisines = ['Sushi', 'Fast Food', 'Fine Dining', 'Bakery', 'BBQ']
    regions = ['Montreal', 'Quebec', 'Laval', 'Gatineau']
    risk_levels = ['Low', 'Medium', 'High']
    
    data = {
        'cuisine_type': np.random.choice(cuisines, n_samples),
        'staff_count': np.random.randint(1, 50, n_samples),
        'infractions_history': np.random.randint(0, 5, n_samples),
        'kitchen_size': np.random.uniform(10, 100, n_samples),
        'region': np.random.choice(regions, n_samples),
        'actual_risk_level': np.random.choice(risk_levels, n_samples)
    }
    
    return pd.DataFrame(data)


def test_model_calibration():
    """Test 1: Calibration du modèle."""
    print_section("TEST 1: CALIBRATION DU MODÈLE")
    
    engine = ConditionalProbabilityEngine()
    training_data = generate_sample_data(150)
    
    print(f"📊 Données d'entraînement: {len(training_data)} échantillons")
    print(f"   Distribution des risques:")
    print(training_data['actual_risk_level'].value_counts())
    
    print("\n🔧 Calibration en cours...")
    metrics = engine.calibrate_model(training_data)
    
    print(f"\n✅ Métriques de calibration:")
    print(f"   • Accuracy:  {metrics['accuracy']:.2%}")
    print(f"   • Precision: {metrics['precision_macro']:.2%}")
    print(f"   • Recall:    {metrics['recall_macro']:.2%}")
    print(f"   • F1-Score:  {metrics['f1_macro']:.2%}")
    
    print(f"\n📈 Matrice de confusion:")
    conf_matrix = metrics['confusion_matrix']
    print("              Low    Medium    High")
    for i, level in enumerate(['Low', 'Medium', 'High']):
        print(f"   {level:8s}  {conf_matrix[i]}")


def test_cross_validation():
    """Test 2: Validation croisée."""
    print_section("TEST 2: VALIDATION CROISÉE")
    
    engine = ConditionalProbabilityEngine()
    data = generate_sample_data(200)
    
    print(f"📊 Données de validation: {len(data)} échantillons")
    print(f"🔄 Validation croisée avec 5 folds...")
    
    results = engine.cross_validate(data, n_folds=5)
    
    print(f"\n✅ Résultats de validation croisée:")
    print(f"   • Accuracy moyenne: {results['mean_accuracy']:.2%}")
    print(f"   • Écart-type:       {results['std_accuracy']:.2%}")
    print(f"\n   Scores par fold:")
    for i, score in enumerate(results['fold_scores'], 1):
        print(f"      Fold {i}: {score:.2%}")


def test_sensitivity_analysis():
    """Test 3: Analyse de sensibilité."""
    print_section("TEST 3: ANALYSE DE SENSIBILITÉ")
    
    engine = ConditionalProbabilityEngine()
    
    print("🔍 Analyse de sensibilité pour un restaurant Sushi")
    print("   Paramètres de base:")
    print("   • Type: Sushi")
    print("   • Staff: 10 employés")
    print("   • Infractions: 2")
    print("   • Cuisine: 35 m²")
    print("   • Région: Montreal")
    
    sensitivity = engine.sensitivity_analysis(
        cuisine_type="Sushi",
        staff_count=10,
        infractions_history=2,
        kitchen_size=35.0,
        region="Montreal"
    )
    
    print(f"\n📊 Prédiction de base:")
    base = sensitivity['base_prediction']
    print(f"   Low: {base['Low']:.2%}, Medium: {base['Medium']:.2%}, High: {base['High']:.2%}")
    
    print(f"\n👥 Sensibilité au nombre d'employés:")
    for key, probs in sensitivity['staff_sensitivity'].items():
        staff_num = key.split('_')[1]
        print(f"   {staff_num:3s} employés → High risk: {probs['High']:.2%}")
    
    print(f"\n⚠️  Sensibilité aux infractions:")
    for key, probs in sensitivity['infractions_sensitivity'].items():
        infr_num = key.split('_')[1]
        print(f"   {infr_num} infractions → High risk: {probs['High']:.2%}")


def test_confidence_prediction():
    """Test 4: Prédiction avec confiance."""
    print_section("TEST 4: PRÉDICTION AVEC CONFIANCE")
    
    engine = ConditionalProbabilityEngine()
    
    test_cases = [
        {
            'name': 'Restaurant à faible risque',
            'cuisine_type': 'Fine Dining',
            'staff_count': 8,
            'infractions_history': 0,
            'kitchen_size': 40.0,
            'region': 'Quebec'
        },
        {
            'name': 'Restaurant à risque élevé',
            'cuisine_type': 'Sushi',
            'staff_count': 25,
            'infractions_history': 4,
            'kitchen_size': 80.0,
            'region': 'Montreal'
        },
        {
            'name': 'Restaurant incertain',
            'cuisine_type': 'BBQ',
            'staff_count': 12,
            'infractions_history': 2,
            'kitchen_size': 50.0,
            'region': 'Laval'
        }
    ]
    
    for case in test_cases:
        print(f"\n🍽️  {case['name']}")
        print(f"   Type: {case['cuisine_type']}, Staff: {case['staff_count']}, Infractions: {case['infractions_history']}")
        
        result = engine.predict_with_confidence(
            cuisine_type=case['cuisine_type'],
            staff_count=case['staff_count'],
            infractions_history=case['infractions_history'],
            kitchen_size=case['kitchen_size'],
            region=case['region']
        )
        
        print(f"\n   ✅ Prédiction: {result['predicted_risk']} ({result['probability']:.2%})")
        print(f"   🎯 Confiance: {result['confidence_level']} ({result['confidence_score']:.2%})")
        print(f"   📊 Distribution:")
        for level, prob in result['all_probabilities'].items():
            bar = '█' * int(prob * 50)
            print(f"      {level:8s} {prob:.2%} {bar}")


def test_model_persistence():
    """Test 5: Sauvegarde et chargement du modèle."""
    print_section("TEST 5: PERSISTANCE DU MODÈLE")
    
    # Créer et calibrer un modèle
    engine1 = ConditionalProbabilityEngine()
    training_data = generate_sample_data(100)
    engine1.calibrate_model(training_data)
    
    print("💾 Sauvegarde du modèle calibré...")
    model_path = "data/calibrated_model.pkl"
    os.makedirs("data", exist_ok=True)
    success = engine1.save_model(model_path)
    
    if success:
        print(f"   ✅ Modèle sauvegardé: {model_path}")
    
    # Charger le modèle dans une nouvelle instance
    print("\n📂 Chargement du modèle...")
    engine2 = ConditionalProbabilityEngine()
    success = engine2.load_model(model_path)
    
    if success:
        print(f"   ✅ Modèle chargé avec succès")
    
    # Vérifier que les prédictions sont identiques
    print("\n🔍 Vérification de la cohérence...")
    
    pred1, prob1 = engine1.predict_risk_level(
        cuisine_type="Sushi",
        staff_count=10,
        infractions_history=2,
        kitchen_size=35.0,
        region="Montreal"
    )
    
    pred2, prob2 = engine2.predict_risk_level(
        cuisine_type="Sushi",
        staff_count=10,
        infractions_history=2,
        kitchen_size=35.0,
        region="Montreal"
    )
    
    if pred1 == pred2 and abs(prob1 - prob2) < 0.001:
        print(f"   ✅ Prédictions identiques: {pred1} ({prob1:.2%})")
    else:
        print(f"   ❌ Différence détectée!")


def test_model_summary():
    """Test 6: Résumé du modèle."""
    print_section("TEST 6: RÉSUMÉ DU MODÈLE")
    
    engine = ConditionalProbabilityEngine()
    summary = engine.get_model_summary()
    
    print("📋 Résumé du modèle:")
    print(f"   • Version: {summary['version']}")
    print(f"   • Ajustement temporel: {summary['temporal_adjustment']}")
    print(f"\n   • Types de cuisine supportés:")
    for cuisine in summary['cuisine_types_supported']:
        print(f"      - {cuisine}")
    
    print(f"\n   • Distribution a priori:")
    for level, prob in summary['prior_risk_distribution'].items():
        print(f"      {level:8s}: {prob:.2%}")


def main():
    """Fonction principale."""
    print("\n" + "╔" + "═" * 68 + "╗")
    print("║" + " " * 68 + "║")
    print("║" + "  🧪 TEST DU MODÈLE DE PROBABILITÉS CONDITIONNELLES v3".center(68) + "║")
    print("║" + "  Enhanced Conditional Probability Model".center(68) + "║")
    print("║" + " " * 68 + "║")
    print("╚" + "═" * 68 + "╝")
    
    print("\n👤 Développé par: Grace Mandiangu")
    print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    try:
        test_model_calibration()
        test_cross_validation()
        test_sensitivity_analysis()
        test_confidence_prediction()
        test_model_persistence()
        test_model_summary()
        
        print_section("✅ TOUS LES TESTS TERMINÉS AVEC SUCCÈS")
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
