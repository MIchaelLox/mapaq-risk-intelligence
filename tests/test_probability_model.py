from src.probability_model import compute_conditional_probabilities

def test_probabilities_between_0_and_1():
   probs = compute_conditional_probabilities()
   assert all(0.0 <= p <= 1.0 for p in probs.values())
