from src.probability_model import RestaurantFeatures, RiskModel


def test_probability_in_range():
    model = RiskModel()
    features = RestaurantFeatures(
        theme="Sushi",
        staff_count=10,
        infractions_history=2,
        kitchen_size=30.0,
        region="Montreal",
    )
    p = model.predict_probability(features)
    assert 0.0 <= p <= 1.0


def test_category_valid():
    model = RiskModel()
    for prob in [0.1, 0.5, 0.9]:
        level = model.categorize(prob)
        assert level in {"Low", "Medium", "High"}