"""
Script de test pour le Conditional Probability Engine v2.

Démontre les nouvelles fonctionnalités avancées de calcul de probabilités
conditionnelles, théorème de Bayes, et apprentissage à partir de données.

Author: Grace Mandiangu
Date: November 27, 2025
"""

import pandas as pd
import numpy as np
from datetime import datetime
from src.probability_model import ConditionalProbabilityEngine

def create_sample_historical_data():
    """Crée un dataset d'exemple pour les tests."""
    np.random.seed(42)
    
    data = {
        'restaurant_id': range(1, 101),
        'cuisine_type': np.random.choice(
            ['Sushi', 'Italian', 'Fast Food', 'BBQ', 'Fine Dining', 'Bakery'],
            100
        ),
        'staff_count': np.random.randint(3, 25, 100),
        'infractions_history': np.random.randint(0, 5, 100),
        'kitchen_size': np.random.uniform(15, 80, 100),
        'region': np.random.choice(['Montreal', 'Quebec', 'Laval', 'Gatineau'], 100),
        'risk_level': np.random.choice(['Low', 'Medium', 'High'], 100, p=[0.6, 0.3, 0.1])
    }
    
    return pd.DataFrame(data)


def test_conditional_probability():
    """Test du calcul de probabilités conditionnelles P(A|B)."""
    print("\n" + "="*70)
    print("TEST 1: PROBABILITÉS CONDITIONNELLES P(A|B)")
    print("="*70)
    
    engine = ConditionalProbabilityEngine()
    data = create_sample_historical_data()
    
    # Calculer P(High Risk | Sushi)
    prob = engine.calculate_conditional_probability(
        event_a='High',
        event_b='Sushi',
        data=data,
        column_a='risk_level',
        column_b='cuisine_type'
    )
    
    print(f"\n📊 P(High Risk | Sushi) = {prob:.2%}")
    
    # Calculer P(Low Risk | Fine Dining)
    prob2 = engine.calculate_conditional_probability(
        event_a='Low',
        event_b='Fine Dining',
        data=data,
        column_a='risk_level',
        column_b='cuisine_type'
    )
    
    print(f"📊 P(Low Risk | Fine Dining) = {prob2:.2%}")
    
    # Calculer P(Medium Risk | Montreal)
    prob3 = engine.calculate_conditional_probability(
        event_a='Medium',
        event_b='Montreal',
        data=data,
        column_a='risk_level',
        column_b='region'
    )
    
    print(f"📊 P(Medium Risk | Montreal) = {prob3:.2%}")


def test_bayes_theorem():
    """Test du théorème de Bayes."""
    print("\n" + "="*70)
    print("TEST 2: THÉORÈME DE BAYES")
    print("="*70)
    
    engine = ConditionalProbabilityEngine()
    data = create_sample_historical_data()
    
    # Appliquer le théorème de Bayes
    posterior = engine.calculate_bayes_theorem(
        hypothesis='High',
        evidence='Sushi',
        data=data,
        hypothesis_col='risk_level',
        evidence_col='cuisine_type'
    )
    
    print(f"\n🎯 P(High Risk | Sushi) via Bayes = {posterior:.2%}")
    
    # Autre exemple
    posterior2 = engine.calculate_bayes_theorem(
        hypothesis='Low',
        evidence='Bakery',
        data=data,
        hypothesis_col='risk_level',
        evidence_col='cuisine_type'
    )
    
    print(f"🎯 P(Low Risk | Bakery) via Bayes = {posterior2:.2%}")


def test_joint_probability():
    """Test des probabilités jointes."""
    print("\n" + "="*70)
    print("TEST 3: PROBABILITÉS JOINTES P(A ∩ B ∩ C)")
    print("="*70)
    
    engine = ConditionalProbabilityEngine()
    data = create_sample_historical_data()
    
    # Probabilité jointe de plusieurs événements
    joint_prob = engine.calculate_joint_probability(
        events={
            'cuisine_type': 'Sushi',
            'risk_level': 'High',
            'region': 'Montreal'
        },
        data=data
    )
    
    print(f"\n🔗 P(Sushi ∩ High Risk ∩ Montreal) = {joint_prob:.2%}")
    
    # Autre exemple
    joint_prob2 = engine.calculate_joint_probability(
        events={
            'cuisine_type': 'Fine Dining',
            'risk_level': 'Low',
            'region': 'Quebec'
        },
        data=data
    )
    
    print(f"🔗 P(Fine Dining ∩ Low Risk ∩ Quebec) = {joint_prob2:.2%}")


def test_learning_from_data():
    """Test de l'apprentissage des probabilités à partir de données."""
    print("\n" + "="*70)
    print("TEST 4: APPRENTISSAGE À PARTIR DE DONNÉES")
    print("="*70)
    
    engine = ConditionalProbabilityEngine()
    data = create_sample_historical_data()
    
    print("\n📚 Probabilités initiales (hardcodées):")
    print(f"Sushi: {engine.cuisine_risk_probs.get('Sushi', 'N/A')}")
    
    # Apprendre les probabilités à partir des données
    engine.learn_cuisine_probabilities(data)
    
    print("\n📚 Probabilités apprises des données:")
    for cuisine in ['Sushi', 'Italian', 'Fast Food', 'BBQ', 'Fine Dining', 'Bakery']:
        if cuisine in engine.cuisine_risk_probs:
            probs = engine.cuisine_risk_probs[cuisine]
            print(f"{cuisine:15} -> Low: {probs['Low']:.2%}, "
                  f"Medium: {probs['Medium']:.2%}, High: {probs['High']:.2%}")


def test_probability_matrix():
    """Test de la génération de matrice de probabilités."""
    print("\n" + "="*70)
    print("TEST 5: MATRICE DE PROBABILITÉS CONDITIONNELLES")
    print("="*70)
    
    engine = ConditionalProbabilityEngine()
    data = create_sample_historical_data()
    
    # Générer la matrice de probabilités
    prob_matrix = engine.get_probability_matrix(data)
    
    print("\n📊 Matrice P(Risk Level | Cuisine Type):")
    print(prob_matrix.round(3))


def test_update_priors():
    """Test de la mise à jour des probabilités a priori."""
    print("\n" + "="*70)
    print("TEST 6: MISE À JOUR DES PROBABILITÉS A PRIORI")
    print("="*70)
    
    engine = ConditionalProbabilityEngine()
    data = create_sample_historical_data()
    
    print("\n📈 Probabilités a priori initiales:")
    print(f"Low: {engine.prior_risk['Low']:.2%}, "
          f"Medium: {engine.prior_risk['Medium']:.2%}, "
          f"High: {engine.prior_risk['High']:.2%}")
    
    # Mettre à jour avec les nouvelles données
    engine.update_priors(data)
    
    print("\n📈 Probabilités a priori après mise à jour:")
    print(f"Low: {engine.prior_risk['Low']:.2%}, "
          f"Medium: {engine.prior_risk['Medium']:.2%}, "
          f"High: {engine.prior_risk['High']:.2%}")


def test_complete_prediction():
    """Test de prédiction complète avec toutes les fonctionnalités."""
    print("\n" + "="*70)
    print("TEST 7: PRÉDICTION COMPLÈTE AVEC AJUSTEMENTS TEMPORELS")
    print("="*70)
    
    engine = ConditionalProbabilityEngine(enable_temporal_adjustment=True)
    
    # Prédiction pour un restaurant
    risk_level, confidence = engine.predict_risk_level(
        cuisine_type="Sushi",
        staff_count=12,
        infractions_history=2,
        kitchen_size=40.0,
        region="Montreal",
        inspection_date=datetime(2023, 6, 15)
    )
    
    print(f"\n🎯 Prédiction pour un restaurant Sushi à Montreal:")
    print(f"   - Niveau de risque: {risk_level}")
    print(f"   - Confiance: {confidence:.2%}")
    
    # Calculer toutes les probabilités
    probs = engine.calculate_risk_probability(
        cuisine_type="Sushi",
        staff_count=12,
        infractions_history=2,
        kitchen_size=40.0,
        region="Montreal",
        inspection_date=datetime(2023, 6, 15)
    )
    
    print(f"\n📊 Distribution des probabilités:")
    print(f"   - Low Risk: {probs['Low']:.2%}")
    print(f"   - Medium Risk: {probs['Medium']:.2%}")
    print(f"   - High Risk: {probs['High']:.2%}")


def main():
    """Fonction principale pour exécuter tous les tests."""
    print("\n" + "="*70)
    print("🧪 TESTS DU CONDITIONAL PROBABILITY ENGINE V2")
    print("Author: Grace Mandiangu")
    print("="*70)
    
    try:
        test_conditional_probability()
        test_bayes_theorem()
        test_joint_probability()
        test_learning_from_data()
        test_probability_matrix()
        test_update_priors()
        test_complete_prediction()
        
        print("\n" + "="*70)
        print("✅ TOUS LES TESTS RÉUSSIS!")
        print("="*70)
        
    except Exception as e:
        print(f"\n❌ Erreur lors des tests: {str(e)}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
