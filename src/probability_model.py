"""
Module de calcul de probabilités conditionnelles pour la prédiction de risque sanitaire.

Conditional Probability Engine v2 - Utilise les probabilités bayésiennes pour
calculer le risque sanitaire des restaurants basé sur plusieurs facteurs.

Author: Grace Mandiangu
Date: November 21, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConditionalProbabilityEngine:
    """
    Moteur de probabilités conditionnelles v2 pour la prédiction de risque.
    
    Utilise le théorème de Bayes pour calculer P(Risque | Features).
    """
    
    def __init__(self):
        """Initialise le moteur de probabilités."""
        
        # Probabilités a priori (baseline)
        self.prior_risk = {
            'Low': 0.60,      # 60% des restaurants sont à faible risque
            'Medium': 0.30,   # 30% à risque moyen
            'High': 0.10      # 10% à risque élevé
        }
        
        # Probabilités conditionnelles par type de cuisine
        self.cuisine_risk_probs = {
            'Sushi': {'Low': 0.30, 'Medium': 0.40, 'High': 0.30},
            'Fast Food': {'Low': 0.50, 'Medium': 0.35, 'High': 0.15},
            'Fine Dining': {'Low': 0.70, 'Medium': 0.25, 'High': 0.05},
            'Bakery': {'Low': 0.75, 'Medium': 0.20, 'High': 0.05},
            'BBQ': {'Low': 0.55, 'Medium': 0.30, 'High': 0.15},
            'Other': {'Low': 0.60, 'Medium': 0.30, 'High': 0.10}
        }
        
        # Seuils pour les facteurs numériques
        self.staff_thresholds = {
            'small': (0, 5),      # Petite équipe
            'medium': (6, 15),    # Équipe moyenne
            'large': (16, 100)    # Grande équipe
        }
        
        self.infraction_weights = {
            0: 0.0,    # Aucune infraction
            1: 0.15,   # 1 infraction
            2: 0.30,   # 2 infractions
            3: 0.50,   # 3 infractions
            4: 0.70,   # 4+ infractions
        }
        
        logger.info("ConditionalProbabilityEngine v2 initialisé")
    
    def calculate_risk_probability(
        self,
        cuisine_type: str,
        staff_count: int,
        infractions_history: int,
        kitchen_size: float,
        region: str
    ) -> Dict[str, float]:
        """
        Calcule les probabilités de risque conditionnelles.
        
        Args:
            cuisine_type: Type de cuisine du restaurant
            staff_count: Nombre d'employés
            infractions_history: Nombre d'infractions passées
            kitchen_size: Taille de la cuisine en m²
            region: Région géographique
            
        Returns:
            Dictionnaire avec les probabilités pour chaque niveau de risque
        """
        logger.info(f"Calcul de probabilité pour: {cuisine_type}, {staff_count} employés")
        
        # 1. Probabilité basée sur le type de cuisine
        cuisine_probs = self._get_cuisine_probability(cuisine_type)
        
        # 2. Ajustement basé sur le nombre d'employés
        staff_factor = self._calculate_staff_factor(staff_count)
        
        # 3. Ajustement basé sur l'historique d'infractions
        infraction_factor = self._calculate_infraction_factor(infractions_history)
        
        # 4. Ajustement basé sur la taille de la cuisine
        kitchen_factor = self._calculate_kitchen_factor(kitchen_size)
        
        # 5. Ajustement régional
        region_factor = self._calculate_region_factor(region)
        
        # Combiner tous les facteurs
        final_probs = {}
        for risk_level in ['Low', 'Medium', 'High']:
            # Probabilité conditionnelle combinée
            prob = cuisine_probs[risk_level]
            prob *= (1 + staff_factor)
            prob *= (1 + infraction_factor)
            prob *= (1 + kitchen_factor)
            prob *= (1 + region_factor)
            
            final_probs[risk_level] = prob
        
        # Normaliser les probabilités pour qu'elles somment à 1
        total = sum(final_probs.values())
        final_probs = {k: v/total for k, v in final_probs.items()}
        
        logger.info(f"Probabilités calculées: {final_probs}")
        
        return final_probs
    
    def predict_risk_level(
        self,
        cuisine_type: str,
        staff_count: int,
        infractions_history: int,
        kitchen_size: float,
        region: str
    ) -> Tuple[str, float]:
        """
        Prédit le niveau de risque le plus probable.
        
        Returns:
            Tuple (niveau_de_risque, probabilité)
        """
        probs = self.calculate_risk_probability(
            cuisine_type,
            staff_count,
            infractions_history,
            kitchen_size,
            region
        )
        
        # Retourner le niveau avec la probabilité maximale
        risk_level = max(probs, key=probs.get)
        probability = probs[risk_level]
        
        return risk_level, probability
    
    def _get_cuisine_probability(self, cuisine_type: str) -> Dict[str, float]:
        """Retourne les probabilités de base selon le type de cuisine."""
        cuisine_type = cuisine_type.strip().title()
        
        if cuisine_type in self.cuisine_risk_probs:
            return self.cuisine_risk_probs[cuisine_type]
        else:
            return self.cuisine_risk_probs['Other']
    
    def _calculate_staff_factor(self, staff_count: int) -> float:
        """
        Calcule le facteur d'ajustement basé sur le nombre d'employés.
        Plus d'employés = plus de risque de coordination.
        """
        if staff_count <= 5:
            return -0.10  # Réduction de risque (petite équipe)
        elif staff_count <= 15:
            return 0.0    # Neutre
        else:
            return 0.15   # Augmentation de risque (grande équipe)
    
    def _calculate_infraction_factor(self, infractions: int) -> float:
        """
        Calcule le facteur d'ajustement basé sur l'historique d'infractions.
        Plus d'infractions = risque plus élevé.
        """
        if infractions >= 4:
            infractions = 4
        
        return self.infraction_weights.get(infractions, 0.0)
    
    def _calculate_kitchen_factor(self, kitchen_size: float) -> float:
        """
        Calcule le facteur d'ajustement basé sur la taille de la cuisine.
        Grande cuisine = plus de zones à surveiller.
        """
        if kitchen_size < 20:
            return -0.05  # Petite cuisine, plus facile à gérer
        elif kitchen_size < 50:
            return 0.0    # Taille moyenne
        else:
            return 0.10   # Grande cuisine, plus complexe
    
    def _calculate_region_factor(self, region: str) -> float:
        """
        Calcule le facteur d'ajustement basé sur la région.
        Certaines régions peuvent avoir des standards différents.
        """
        region = region.strip().lower()
        
        # Facteurs régionaux (exemple)
        region_factors = {
            'montreal': 0.05,   # Zone urbaine dense
            'quebec': 0.0,      # Neutre
            'laval': 0.02,      # Légèrement plus élevé
            'gatineau': 0.0,    # Neutre
        }
        
        return region_factors.get(region, 0.0)
    
    def calculate_conditional_probability(
        self,
        event_a: str,
        event_b: str,
        data: pd.DataFrame
    ) -> float:
        """
        Calcule P(A|B) = P(A ∩ B) / P(B).
        
        Args:
            event_a: Événement A (ex: 'High Risk')
            event_b: Événement B (ex: 'Sushi')
            data: DataFrame contenant les données historiques
            
        Returns:
            Probabilité conditionnelle P(A|B)
        """
        # Cette méthode peut être étendue pour calculer des probabilités
        # conditionnelles à partir de données historiques
        pass
    
    def update_priors(self, new_data: pd.DataFrame) -> None:
        """
        Met à jour les probabilités a priori basées sur de nouvelles données.
        
        Args:
            new_data: DataFrame avec nouvelles observations
        """
        if 'risk_level' in new_data.columns:
            total = len(new_data)
            
            self.prior_risk['Low'] = len(new_data[new_data['risk_level'] == 'Low']) / total
            self.prior_risk['Medium'] = len(new_data[new_data['risk_level'] == 'Medium']) / total
            self.prior_risk['High'] = len(new_data[new_data['risk_level'] == 'High']) / total
            
            logger.info(f"Probabilités a priori mises à jour: {self.prior_risk}")


if __name__ == "__main__":
    # Test du moteur
    engine = ConditionalProbabilityEngine()
    
    # Exemple de prédiction
    risk_level, prob = engine.predict_risk_level(
        cuisine_type="Sushi",
        staff_count=10,
        infractions_history=2,
        kitchen_size=35.0,
        region="Montreal"
    )
    
    print(f"Niveau de risque prédit: {risk_level} (probabilité: {prob:.2%})")
