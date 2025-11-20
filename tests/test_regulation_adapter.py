from datetime import datetime
from src.regulation_adapter import get_regulation_weight

def test_weight_changes_after_regulation_date():
   before = get_regulation_weight(datetime(2012, 1, 1))
   after = get_regulation_weight(datetime(2020, 1, 1))
   assert after >= before
