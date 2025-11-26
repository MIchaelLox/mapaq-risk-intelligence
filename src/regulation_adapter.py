"""
Module d'adaptation temporelle des réglementations pour l'ajustement du risque.

Temporal Regulation Weighting - Applique des pondérations temporelles basées
sur les changements réglementaires effectifs pour ajuster les scores de risque.

Author: Grace Mandiangu
Date: November 25, 2025
"""

import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Tuple
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class RegulationAdapter:
    """
    Adaptateur de réglementations temporelles pour ajuster les scores de risque.
    
    Charge les réglementations depuis regulations.json et applique des pondérations
    temporelles basées sur les dates effectives des changements réglementaires.
    """
    
    def __init__(self, regulations_path: Optional[str] = None):
        """
        Initialise l'adaptateur de réglementations.
        
        Args:
            regulations_path: Chemin vers le fichier regulations.json
        """
        if regulations_path is None:
            # Chemin par défaut relatif au module
            base_path = Path(__file__).parent.parent
            regulations_path = base_path / "data" / "regulations.json"
        
        self.regulations_path = Path(regulations_path)
        self.regulations: List[Dict] = []
        self.metadata: Dict = {}
        
        self._load_regulations()
        logger.info(f"RegulationAdapter initialisé avec {len(self.regulations)} réglementations")
    
    def _load_regulations(self) -> None:
        """Charge les réglementations depuis le fichier JSON."""
        try:
            with open(self.regulations_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                self.regulations = data.get('regulations', [])
                self.metadata = data.get('metadata', {})
            
            # Convertir les dates en objets datetime
            for reg in self.regulations:
                reg['effective_date_obj'] = datetime.strptime(
                    reg['effective_date'], 
                    '%Y-%m-%d'
                )
            
            logger.info(f"Chargé {len(self.regulations)} réglementations depuis {self.regulations_path}")
        
        except FileNotFoundError:
            logger.error(f"Fichier de réglementations non trouvé: {self.regulations_path}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Erreur de parsing JSON: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Erreur lors du chargement des réglementations: {str(e)}")
            raise
    
    def get_applicable_regulations(
        self, 
        inspection_date: datetime
    ) -> List[Dict]:
        """
        Retourne les réglementations applicables à une date d'inspection donnée.
        
        Args:
            inspection_date: Date de l'inspection
            
        Returns:
            Liste des réglementations applicables
        """
        applicable = [
            reg for reg in self.regulations 
            if reg['effective_date_obj'] <= inspection_date
        ]
        
        logger.debug(f"{len(applicable)} réglementations applicables pour {inspection_date}")
        return applicable
    
    def calculate_temporal_weight(
        self, 
        inspection_date: datetime,
        base_risk_score: float
    ) -> Tuple[float, List[Dict]]:
        """
        Calcule le poids temporel basé sur les réglementations applicables.
        
        Args:
            inspection_date: Date de l'inspection
            base_risk_score: Score de risque de base (0-1)
            
        Returns:
            Tuple (score_ajusté, réglementations_appliquées)
        """
        applicable_regs = self.get_applicable_regulations(inspection_date)
        
        if not applicable_regs:
            logger.info("Aucune réglementation applicable, score non modifié")
            return base_risk_score, []
        
        # Calculer le poids cumulatif
        cumulative_weight = 1.0
        applied_regulations = []
        
        for reg in applicable_regs:
            impact_weight = reg.get('impact_weight', 1.0)
            cumulative_weight *= impact_weight
            
            applied_regulations.append({
                'id': reg['id'],
                'name': reg['name'],
                'effective_date': reg['effective_date'],
                'impact_weight': impact_weight
            })
        
        # Appliquer le poids au score de base
        adjusted_score = base_risk_score * cumulative_weight
        
        # Normaliser pour rester dans [0, 1]
        adjusted_score = min(max(adjusted_score, 0.0), 1.0)
        
        logger.info(
            f"Score ajusté: {base_risk_score:.4f} -> {adjusted_score:.4f} "
            f"(poids cumulatif: {cumulative_weight:.4f})"
        )
        
        return adjusted_score, applied_regulations
    
    def adjust_risk_probabilities(
        self,
        probabilities: Dict[str, float],
        inspection_date: datetime
    ) -> Dict[str, float]:
        """
        Ajuste les probabilités de risque en fonction des réglementations temporelles.
        
        Args:
            probabilities: Dictionnaire {'Low': p1, 'Medium': p2, 'High': p3}
            inspection_date: Date de l'inspection
            
        Returns:
            Dictionnaire de probabilités ajustées
        """
        applicable_regs = self.get_applicable_regulations(inspection_date)
        
        if not applicable_regs:
            return probabilities
        
        # Calculer le facteur d'ajustement moyen
        avg_impact = sum(reg['impact_weight'] for reg in applicable_regs) / len(applicable_regs)
        
        # Ajuster les probabilités
        # Si impact > 1.0, augmenter le risque (déplacer vers High)
        # Si impact < 1.0, diminuer le risque (déplacer vers Low)
        
        adjusted_probs = probabilities.copy()
        
        if avg_impact > 1.0:
            # Augmenter le risque
            shift_factor = (avg_impact - 1.0) * 0.5  # Facteur de déplacement
            
            adjusted_probs['High'] = probabilities['High'] + shift_factor * probabilities['Medium']
            adjusted_probs['Medium'] = probabilities['Medium'] * (1 - shift_factor)
            adjusted_probs['Low'] = probabilities['Low'] * (1 - shift_factor * 0.5)
        
        elif avg_impact < 1.0:
            # Diminuer le risque
            shift_factor = (1.0 - avg_impact) * 0.5
            
            adjusted_probs['Low'] = probabilities['Low'] + shift_factor * probabilities['Medium']
            adjusted_probs['Medium'] = probabilities['Medium'] * (1 - shift_factor)
            adjusted_probs['High'] = probabilities['High'] * (1 - shift_factor * 0.5)
        
        # Normaliser pour garantir que la somme = 1
        total = sum(adjusted_probs.values())
        adjusted_probs = {k: v/total for k, v in adjusted_probs.items()}
        
        logger.info(f"Probabilités ajustées avec impact moyen: {avg_impact:.4f}")
        
        return adjusted_probs
    
    def get_regulation_timeline(self) -> List[Dict]:
        """
        Retourne la chronologie complète des réglementations.
        
        Returns:
            Liste triée des réglementations par date effective
        """
        timeline = sorted(
            self.regulations,
            key=lambda x: x['effective_date_obj']
        )
        
        return [
            {
                'id': reg['id'],
                'name': reg['name'],
                'effective_date': reg['effective_date'],
                'description': reg.get('description', ''),
                'impact_weight': reg.get('impact_weight', 1.0)
            }
            for reg in timeline
        ]
    
    def get_regulation_by_id(self, regulation_id: str) -> Optional[Dict]:
        """
        Retourne une réglementation spécifique par son ID.
        
        Args:
            regulation_id: ID de la réglementation
            
        Returns:
            Dictionnaire de la réglementation ou None
        """
        for reg in self.regulations:
            if reg['id'] == regulation_id:
                return {
                    'id': reg['id'],
                    'name': reg['name'],
                    'effective_date': reg['effective_date'],
                    'description': reg.get('description', ''),
                    'impact_weight': reg.get('impact_weight', 1.0)
                }
        
        return None
    
    def add_regulation(
        self,
        regulation_id: str,
        name: str,
        effective_date: str,
        description: str,
        impact_weight: float
    ) -> bool:
        """
        Ajoute une nouvelle réglementation.
        
        Args:
            regulation_id: ID unique de la réglementation
            name: Nom de la réglementation
            effective_date: Date effective (format: YYYY-MM-DD)
            description: Description de la réglementation
            impact_weight: Poids d'impact (multiplicateur)
            
        Returns:
            True si ajouté avec succès, False sinon
        """
        try:
            # Vérifier si l'ID existe déjà
            if any(reg['id'] == regulation_id for reg in self.regulations):
                logger.warning(f"Réglementation {regulation_id} existe déjà")
                return False
            
            # Valider la date
            effective_date_obj = datetime.strptime(effective_date, '%Y-%m-%d')
            
            # Créer la nouvelle réglementation
            new_regulation = {
                'id': regulation_id,
                'name': name,
                'effective_date': effective_date,
                'effective_date_obj': effective_date_obj,
                'description': description,
                'impact_weight': impact_weight
            }
            
            self.regulations.append(new_regulation)
            logger.info(f"Réglementation {regulation_id} ajoutée avec succès")
            
            return True
        
        except ValueError as e:
            logger.error(f"Erreur de format de date: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Erreur lors de l'ajout de la réglementation: {str(e)}")
            return False
    
    def save_regulations(self) -> bool:
        """
        Sauvegarde les réglementations dans le fichier JSON.
        
        Returns:
            True si sauvegardé avec succès, False sinon
        """
        try:
            # Préparer les données pour la sauvegarde
            regulations_data = []
            for reg in self.regulations:
                reg_copy = reg.copy()
                # Retirer l'objet datetime avant la sérialisation
                reg_copy.pop('effective_date_obj', None)
                regulations_data.append(reg_copy)
            
            data = {
                'regulations': regulations_data,
                'metadata': {
                    **self.metadata,
                    'last_updated': datetime.now().strftime('%Y-%m-%d')
                }
            }
            
            with open(self.regulations_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            logger.info(f"Réglementations sauvegardées dans {self.regulations_path}")
            return True
        
        except Exception as e:
            logger.error(f"Erreur lors de la sauvegarde: {str(e)}")
            return False


if __name__ == "__main__":
    # Test du module
    adapter = RegulationAdapter()
    
    # Test 1: Obtenir les réglementations applicables
    inspection_date = datetime(2023, 6, 1)
    applicable = adapter.get_applicable_regulations(inspection_date)
    print(f"\nRéglementations applicables au {inspection_date.date()}:")
    for reg in applicable:
        print(f"  - {reg['name']} (impact: {reg['impact_weight']})")
    
    # Test 2: Calculer le poids temporel
    base_score = 0.65
    adjusted_score, applied = adapter.calculate_temporal_weight(inspection_date, base_score)
    print(f"\nScore de base: {base_score:.4f}")
    print(f"Score ajusté: {adjusted_score:.4f}")
    
    # Test 3: Ajuster les probabilités
    probabilities = {'Low': 0.30, 'Medium': 0.50, 'High': 0.20}
    adjusted_probs = adapter.adjust_risk_probabilities(probabilities, inspection_date)
    print(f"\nProbabilités originales: {probabilities}")
    print(f"Probabilités ajustées: {adjusted_probs}")
    
    # Test 4: Chronologie des réglementations
    timeline = adapter.get_regulation_timeline()
    print(f"\nChronologie des réglementations:")
    for reg in timeline:
        print(f"  {reg['effective_date']}: {reg['name']}")
