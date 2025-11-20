from datetime import date

from src.regulation_adapter import RegulationAdapter


def test_regulation_adjustment_changes_value():
    adapter = RegulationAdapter()
    base = 0.5

    before = adapter.adjust_probability(base, date(2010, 1, 1))
    mid = adapter.adjust_probability(base, date(2017, 1, 1))
    after = adapter.adjust_probability(base, date(2023, 1, 1))

    # Before early_year: should be lower or equal
    assert before <= base
    # Between years: should be unchanged
    assert mid == base
    # After strict_year: should be higher or equal
    assert after >= base

    for value in (before, mid, after):
        assert 0.0 <= value <= 1.0