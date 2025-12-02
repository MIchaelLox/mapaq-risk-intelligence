"""
Module de calcul de probabilités conditionnelles pour la prédiction de risque sanitaire.

Conditional Probability Engine v3 - Moteur avancé de probabilités bayésiennes pour
calculer le risque sanitaire des restaurants basé sur plusieurs facteurs.

Fonctionnalités v3 (Enhanced - Grace Mandiangu):
- Calcul de probabilités conditionnelles P(A|B) à partir de données historiques
- Théorème de Bayes pour inférence probabiliste
- Probabilités jointes pour événements multiples
- Apprentissage automatique des probabilités par type de cuisine
- Matrice de probabilités conditionnelles
- Ajustements temporels basés sur les réglementations
- Prédiction multi-facteurs (cuisine, staff, infractions, taille, région)
- Calibration du modèle avec données historiques (NEW)
- Validation croisée et métriques de performance (NEW)
- Analyse de sensibilité des facteurs (NEW)
- Persistance et chargement du modèle (NEW)
- Intervalles de confiance pour les prédictions (NEW)

Author: Grace Mandiangu
Date: December 1, 2025
"""

import numpy as np
import pandas as pd
from typing import Dict, Tuple, Optional, List
from datetime import datetime
import logging
import json
import pickle
from pathlib import Path
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix
from sklearn.model_selection import cross_val_score

try:
    from regulation_adapter import RegulationAdapter
    REGULATION_ADAPTER_AVAILABLE = True
except ImportError:
    REGULATION_ADAPTER_AVAILABLE = False
    logging.warning("RegulationAdapter non disponible, ajustements temporels désactivés")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ConditionalProbabilityEngine:
    """
    Moteur de probabilités conditionnelles v2 pour la prédiction de risque.
    
    Utilise le théorème de Bayes et l'inférence probabiliste pour calculer P(Risque | Features).
    
    Méthodes principales:
    - calculate_risk_probability: Calcule les probabilités de risque pour un restaurant
    - predict_risk_level: Prédit le niveau de risque le plus probable
    - calculate_conditional_probability: Calcule P(A|B) à partir de données
    - calculate_bayes_theorem: Applique le théorème de Bayes
    - calculate_joint_probability: Calcule P(A ∩ B ∩ C...)
    - learn_cuisine_probabilities: Apprend les probabilités à partir de données
    - get_probability_matrix: Génère une matrice de probabilités conditionnelles
    - update_priors: Met à jour les probabilités a priori
    """
    
    def __init__(self, enable_temporal_adjustment: bool = True):
        """Initialise le moteur de probabilités.
        
        Args:
            enable_temporal_adjustment: Active les ajustements temporels basés sur les réglementations
        """
        
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
        
        # Initialiser l'adaptateur de réglementations
        self.regulation_adapter = None
        self.temporal_adjustment_enabled = False
        
        if enable_temporal_adjustment and REGULATION_ADAPTER_AVAILABLE:
            try:
                self.regulation_adapter = RegulationAdapter()
                self.temporal_adjustment_enabled = True
                logger.info("Ajustements temporels activés")
            except Exception as e:
                logger.warning(f"Impossible d'initialiser RegulationAdapter: {str(e)}")
        
        logger.info("ConditionalProbabilityEngine v2 initialisé")
    
    def calculate_risk_probability(
        self,
        cuisine_type: str,
        staff_count: int,
        infractions_history: int,
        kitchen_size: float,
        region: str,
        inspection_date: Optional[datetime] = None
    ) -> Dict[str, float]:
        """
        Calcule les probabilités de risque conditionnelles.
        
        Args:
            cuisine_type: Type de cuisine du restaurant
            staff_count: Nombre d'employés
            infractions_history: Nombre d'infractions passées
            kitchen_size: Taille de la cuisine en m²
            region: Région géographique
            inspection_date: Date de l'inspection (optionnel, défaut: aujourd'hui)
            
        Returns:
            Dictionnaire avec les probabilités pour chaque niveau de risque
        """
        if inspection_date is None:
            inspection_date = datetime.now()
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
        
        # Appliquer les ajustements temporels si activés
        if self.temporal_adjustment_enabled and self.regulation_adapter:
            final_probs = self.regulation_adapter.adjust_risk_probabilities(
                final_probs,
                inspection_date
            )
            logger.info(f"Probabilités après ajustement temporel: {final_probs}")
        else:
            logger.info(f"Probabilités calculées: {final_probs}")
        
        return final_probs
    
    def predict_risk_level(
        self,
        cuisine_type: str,
        staff_count: int,
        infractions_history: int,
        kitchen_size: float,
        region: str,
        inspection_date: Optional[datetime] = None
    ) -> Tuple[str, float]:
        """
        Prédit le niveau de risque le plus probable.
        
        Args:
            cuisine_type: Type de cuisine du restaurant
            staff_count: Nombre d'employés
            infractions_history: Nombre d'infractions passées
            kitchen_size: Taille de la cuisine en m²
            region: Région géographique
            inspection_date: Date de l'inspection (optionnel, défaut: aujourd'hui)
        
        Returns:
            Tuple (niveau_de_risque, probabilité)
        """
        probs = self.calculate_risk_probability(
            cuisine_type,
            staff_count,
            infractions_history,
            kitchen_size,
            region,
            inspection_date
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
        data: pd.DataFrame,
        column_a: str = 'risk_level',
        column_b: str = 'cuisine_type'
    ) -> float:
        """
        Calcule P(A|B) = P(A ∩ B) / P(B) à partir de données historiques.
        
        Args:
            event_a: Événement A (ex: 'High')
            event_b: Événement B (ex: 'Sushi')
            data: DataFrame contenant les données historiques
            column_a: Nom de la colonne pour l'événement A
            column_b: Nom de la colonne pour l'événement B
            
        Returns:
            Probabilité conditionnelle P(A|B)
        """
        if data.empty:
            logger.warning("DataFrame vide, impossible de calculer P(A|B)")
            return 0.0
        
        if column_a not in data.columns or column_b not in data.columns:
            logger.error(f"Colonnes manquantes: {column_a} ou {column_b}")
            return 0.0
        
        # P(B) - Probabilité de l'événement B
        count_b = len(data[data[column_b] == event_b])
        if count_b == 0:
            logger.warning(f"Aucune occurrence de {event_b} dans {column_b}")
            return 0.0
        
        prob_b = count_b / len(data)
        
        # P(A ∩ B) - Probabilité de A et B simultanément
        count_a_and_b = len(data[(data[column_a] == event_a) & (data[column_b] == event_b)])
        prob_a_and_b = count_a_and_b / len(data)
        
        # P(A|B) = P(A ∩ B) / P(B)
        prob_a_given_b = prob_a_and_b / prob_b
        
        logger.info(f"P({event_a}|{event_b}) = {prob_a_given_b:.4f}")
        logger.debug(f"P({event_b}) = {prob_b:.4f}, P({event_a} ∩ {event_b}) = {prob_a_and_b:.4f}")
        
        return prob_a_given_b
    
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
    
    def learn_cuisine_probabilities(self, data: pd.DataFrame) -> None:
        """
        Apprend les probabilités conditionnelles par type de cuisine à partir de données historiques.
        
        Args:
            data: DataFrame avec colonnes 'cuisine_type' et 'risk_level'
        """
        if 'cuisine_type' not in data.columns or 'risk_level' not in data.columns:
            logger.error("Colonnes 'cuisine_type' et 'risk_level' requises")
            return
        
        # Grouper par type de cuisine
        cuisine_types = data['cuisine_type'].unique()
        
        for cuisine in cuisine_types:
            cuisine_data = data[data['cuisine_type'] == cuisine]
            total = len(cuisine_data)
            
            if total > 0:
                self.cuisine_risk_probs[cuisine] = {
                    'Low': len(cuisine_data[cuisine_data['risk_level'] == 'Low']) / total,
                    'Medium': len(cuisine_data[cuisine_data['risk_level'] == 'Medium']) / total,
                    'High': len(cuisine_data[cuisine_data['risk_level'] == 'High']) / total
                }
                logger.info(f"Probabilités apprises pour {cuisine}: {self.cuisine_risk_probs[cuisine]}")
    
    def calculate_joint_probability(
        self,
        events: Dict[str, str],
        data: pd.DataFrame
    ) -> float:
        """
        Calcule la probabilité jointe P(A ∩ B ∩ C ...) pour plusieurs événements.
        
        Args:
            events: Dictionnaire {colonne: valeur} des événements
            data: DataFrame contenant les données historiques
            
        Returns:
            Probabilité jointe des événements
        """
        if data.empty:
            logger.warning("DataFrame vide")
            return 0.0
        
        # Filtrer les données pour tous les événements
        filtered_data = data.copy()
        for column, value in events.items():
            if column not in data.columns:
                logger.error(f"Colonne {column} manquante")
                return 0.0
            filtered_data = filtered_data[filtered_data[column] == value]
        
        # Probabilité jointe
        joint_prob = len(filtered_data) / len(data)
        
        logger.info(f"P({events}) = {joint_prob:.4f}")
        return joint_prob
    
    def calculate_bayes_theorem(
        self,
        hypothesis: str,
        evidence: str,
        data: pd.DataFrame,
        hypothesis_col: str = 'risk_level',
        evidence_col: str = 'cuisine_type'
    ) -> float:
        """
        Applique le théorème de Bayes: P(H|E) = P(E|H) * P(H) / P(E).
        
        Args:
            hypothesis: Hypothèse (ex: 'High')
            evidence: Évidence observée (ex: 'Sushi')
            data: DataFrame avec données historiques
            hypothesis_col: Colonne de l'hypothèse
            evidence_col: Colonne de l'évidence
            
        Returns:
            Probabilité a posteriori P(H|E)
        """
        # P(H) - Probabilité a priori de l'hypothèse
        count_h = len(data[data[hypothesis_col] == hypothesis])
        prob_h = count_h / len(data) if len(data) > 0 else 0.0
        
        # P(E) - Probabilité de l'évidence
        count_e = len(data[data[evidence_col] == evidence])
        prob_e = count_e / len(data) if len(data) > 0 else 0.0
        
        if prob_e == 0:
            logger.warning(f"P({evidence}) = 0, impossible de calculer P(H|E)")
            return 0.0
        
        # P(E|H) - Vraisemblance
        data_h = data[data[hypothesis_col] == hypothesis]
        count_e_given_h = len(data_h[data_h[evidence_col] == evidence])
        prob_e_given_h = count_e_given_h / count_h if count_h > 0 else 0.0
        
        # Théorème de Bayes: P(H|E) = P(E|H) * P(H) / P(E)
        prob_h_given_e = (prob_e_given_h * prob_h) / prob_e
        
        logger.info(f"Théorème de Bayes: P({hypothesis}|{evidence}) = {prob_h_given_e:.4f}")
        logger.debug(f"P(H)={prob_h:.4f}, P(E)={prob_e:.4f}, P(E|H)={prob_e_given_h:.4f}")
        
        return prob_h_given_e
    
    def get_probability_matrix(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Génère une matrice de probabilités conditionnelles P(Risk|Cuisine).
        
        Args:
            data: DataFrame avec colonnes 'cuisine_type' et 'risk_level'
            
        Returns:
            DataFrame avec matrice de probabilités
        """
        if 'cuisine_type' not in data.columns or 'risk_level' not in data.columns:
            logger.error("Colonnes requises manquantes")
            return pd.DataFrame()
        
        # Créer une table de contingence
        contingency_table = pd.crosstab(
            data['cuisine_type'],
            data['risk_level'],
            normalize='index'
        )
        
        logger.info("Matrice de probabilités conditionnelles générée")
        return contingency_table
    
    def calibrate_model(self, training_data: pd.DataFrame) -> Dict:
        """
        Calibre le modèle avec des données d'entraînement historiques.
        
        Args:
            training_data: DataFrame avec colonnes requises pour l'entraînement
            
        Returns:
            Dictionnaire avec métriques de calibration
        
        Author: Grace Mandiangu (v3 Enhancement)
        """
        logger.info("Début de la calibration du modèle...")
        
        required_cols = ['cuisine_type', 'staff_count', 'infractions_history', 
                        'kitchen_size', 'region', 'actual_risk_level']
        
        if not all(col in training_data.columns for col in required_cols):
            logger.error(f"Colonnes requises manquantes: {required_cols}")
            return {}
        
        # Apprendre les probabilités à partir des données
        self.learn_cuisine_probabilities(training_data.rename(
            columns={'actual_risk_level': 'risk_level'}
        ))
        
        # Calculer les prédictions
        predictions = []
        actuals = []
        
        for _, row in training_data.iterrows():
            predicted_level, _ = self.predict_risk_level(
                cuisine_type=row['cuisine_type'],
                staff_count=int(row['staff_count']),
                infractions_history=int(row['infractions_history']),
                kitchen_size=float(row['kitchen_size']),
                region=row['region']
            )
            predictions.append(predicted_level)
            actuals.append(row['actual_risk_level'])
        
        # Calculer les métriques
        metrics = {
            'accuracy': accuracy_score(actuals, predictions),
            'precision_macro': precision_score(actuals, predictions, average='macro', zero_division=0),
            'recall_macro': recall_score(actuals, predictions, average='macro', zero_division=0),
            'f1_macro': f1_score(actuals, predictions, average='macro', zero_division=0),
            'confusion_matrix': confusion_matrix(actuals, predictions, labels=['Low', 'Medium', 'High']).tolist(),
            'training_samples': len(training_data)
        }
        
        logger.info(f"Calibration terminée - Accuracy: {metrics['accuracy']:.2%}")
        return metrics
    
    def cross_validate(self, data: pd.DataFrame, n_folds: int = 5) -> Dict:
        """
        Effectue une validation croisée du modèle.
        
        Args:
            data: DataFrame avec données de validation
            n_folds: Nombre de folds pour la validation croisée
            
        Returns:
            Dictionnaire avec résultats de validation
        
        Author: Grace Mandiangu (v3 Enhancement)
        """
        logger.info(f"Validation croisée avec {n_folds} folds...")
        
        from sklearn.model_selection import KFold
        
        kf = KFold(n_splits=n_folds, shuffle=True, random_state=42)
        fold_scores = []
        
        for fold, (train_idx, test_idx) in enumerate(kf.split(data), 1):
            train_data = data.iloc[train_idx]
            test_data = data.iloc[test_idx]
            
            # Calibrer sur le fold d'entraînement
            self.calibrate_model(train_data)
            
            # Tester sur le fold de test
            predictions = []
            actuals = []
            
            for _, row in test_data.iterrows():
                pred, _ = self.predict_risk_level(
                    cuisine_type=row['cuisine_type'],
                    staff_count=int(row['staff_count']),
                    infractions_history=int(row['infractions_history']),
                    kitchen_size=float(row['kitchen_size']),
                    region=row['region']
                )
                predictions.append(pred)
                actuals.append(row['actual_risk_level'])
            
            fold_accuracy = accuracy_score(actuals, predictions)
            fold_scores.append(fold_accuracy)
            logger.info(f"Fold {fold}: Accuracy = {fold_accuracy:.2%}")
        
        results = {
            'mean_accuracy': np.mean(fold_scores),
            'std_accuracy': np.std(fold_scores),
            'fold_scores': fold_scores,
            'n_folds': n_folds
        }
        
        logger.info(f"Validation croisée terminée - Accuracy moyenne: {results['mean_accuracy']:.2%} ± {results['std_accuracy']:.2%}")
        return results
    
    def sensitivity_analysis(
        self,
        cuisine_type: str,
        staff_count: int,
        infractions_history: int,
        kitchen_size: float,
        region: str
    ) -> Dict:
        """
        Analyse la sensibilité des prédictions aux différents facteurs.
        
        Args:
            cuisine_type, staff_count, infractions_history, kitchen_size, region: Paramètres de base
            
        Returns:
            Dictionnaire avec analyse de sensibilité pour chaque facteur
        
        Author: Grace Mandiangu (v3 Enhancement)
        """
        logger.info("Analyse de sensibilité des facteurs...")
        
        base_probs = self.calculate_risk_probability(
            cuisine_type, staff_count, infractions_history, kitchen_size, region
        )
        
        sensitivity = {
            'base_prediction': base_probs,
            'staff_sensitivity': {},
            'infractions_sensitivity': {},
            'kitchen_sensitivity': {}
        }
        
        # Sensibilité au nombre d'employés
        for staff_variation in [-5, -2, 0, 2, 5]:
            new_staff = max(1, staff_count + staff_variation)
            probs = self.calculate_risk_probability(
                cuisine_type, new_staff, infractions_history, kitchen_size, region
            )
            sensitivity['staff_sensitivity'][f'staff_{new_staff}'] = probs
        
        # Sensibilité aux infractions
        for infraction_variation in [-1, 0, 1, 2]:
            new_infractions = max(0, infractions_history + infraction_variation)
            probs = self.calculate_risk_probability(
                cuisine_type, staff_count, new_infractions, kitchen_size, region
            )
            sensitivity['infractions_sensitivity'][f'infractions_{new_infractions}'] = probs
        
        # Sensibilité à la taille de cuisine
        for kitchen_variation in [-10, -5, 0, 5, 10]:
            new_kitchen = max(5, kitchen_size + kitchen_variation)
            probs = self.calculate_risk_probability(
                cuisine_type, staff_count, infractions_history, new_kitchen, region
            )
            sensitivity['kitchen_sensitivity'][f'kitchen_{new_kitchen}'] = probs
        
        logger.info("Analyse de sensibilité terminée")
        return sensitivity
    
    def predict_with_confidence(
        self,
        cuisine_type: str,
        staff_count: int,
        infractions_history: int,
        kitchen_size: float,
        region: str,
        inspection_date: Optional[datetime] = None
    ) -> Dict:
        """
        Prédit le niveau de risque avec intervalle de confiance.
        
        Args:
            cuisine_type, staff_count, infractions_history, kitchen_size, region: Paramètres
            inspection_date: Date d'inspection optionnelle
            
        Returns:
            Dictionnaire avec prédiction, probabilités et intervalle de confiance
        
        Author: Grace Mandiangu (v3 Enhancement)
        """
        probs = self.calculate_risk_probability(
            cuisine_type, staff_count, infractions_history, kitchen_size, region, inspection_date
        )
        
        risk_level = max(probs, key=probs.get)
        probability = probs[risk_level]
        
        # Calculer l'intervalle de confiance (basé sur l'entropie)
        entropy = -sum(p * np.log2(p + 1e-10) for p in probs.values())
        max_entropy = np.log2(3)  # Pour 3 classes
        confidence_score = 1 - (entropy / max_entropy)
        
        # Déterminer le niveau de confiance
        if confidence_score >= 0.8:
            confidence_level = "Très élevée"
        elif confidence_score >= 0.6:
            confidence_level = "Élevée"
        elif confidence_score >= 0.4:
            confidence_level = "Moyenne"
        else:
            confidence_level = "Faible"
        
        result = {
            'predicted_risk': risk_level,
            'probability': probability,
            'all_probabilities': probs,
            'confidence_score': confidence_score,
            'confidence_level': confidence_level,
            'entropy': entropy
        }
        
        logger.info(f"Prédiction: {risk_level} ({probability:.2%}) - Confiance: {confidence_level} ({confidence_score:.2%})")
        return result
    
    def save_model(self, filepath: str) -> bool:
        """
        Sauvegarde le modèle calibré dans un fichier.
        
        Args:
            filepath: Chemin du fichier de sauvegarde
            
        Returns:
            True si sauvegardé avec succès
        
        Author: Grace Mandiangu (v3 Enhancement)
        """
        try:
            model_data = {
                'prior_risk': self.prior_risk,
                'cuisine_risk_probs': self.cuisine_risk_probs,
                'staff_thresholds': self.staff_thresholds,
                'infraction_weights': self.infraction_weights,
                'temporal_adjustment_enabled': self.temporal_adjustment_enabled,
                'version': '3.0',
                'saved_date': datetime.now().isoformat()
            }
            
            with open(filepath, 'wb') as f:
                pickle.dump(model_data, f)
            
            logger.info(f"Modèle sauvegardé: {filepath}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return False
    
    def load_model(self, filepath: str) -> bool:
        """
        Charge un modèle calibré depuis un fichier.
        
        Args:
            filepath: Chemin du fichier à charger
            
        Returns:
            True si chargé avec succès
        
        Author: Grace Mandiangu (v3 Enhancement)
        """
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            self.prior_risk = model_data['prior_risk']
            self.cuisine_risk_probs = model_data['cuisine_risk_probs']
            self.staff_thresholds = model_data['staff_thresholds']
            self.infraction_weights = model_data['infraction_weights']
            
            logger.info(f"Modèle chargé: {filepath} (version {model_data.get('version', 'unknown')})")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors du chargement: {str(e)}")
            return False
    
    def get_model_summary(self) -> Dict:
        """
        Retourne un résumé des paramètres du modèle.
        
        Returns:
            Dictionnaire avec résumé du modèle
        
        Author: Grace Mandiangu (v3 Enhancement)
        """
        return {
            'version': '3.0',
            'prior_risk_distribution': self.prior_risk,
            'cuisine_types_supported': list(self.cuisine_risk_probs.keys()),
            'temporal_adjustment': self.temporal_adjustment_enabled,
            'staff_thresholds': self.staff_thresholds,
            'infraction_weights': self.infraction_weights
        }


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
