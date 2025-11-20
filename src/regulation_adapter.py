from pathlib import Path
from datetime import datetime
import json
from typing import List, Dict

ROOT_DIR = Path(__file__).resolve().parents[1]
DATA_DIR = ROOT_DIR / "data"
REG_FILE = DATA_DIR / "regulations.json"

def load_regulations() -> List[Dict]:
   with open(REG_FILE, "r", encoding="utf-8") as f:
       rules = json.load(f)
   for r in rules:
       r["effective_from"] = datetime.fromisoformat(r["effective_from"])
   rules.sort(key=lambda r: r["effective_from"])
   return rules

def get_regulation_weight(inspection_date: datetime) -> float:
   rules = load_regulations()
   weight = 1.0
   for r in rules:
       if inspection_date >= r["effective_from"]:
           weight = r["weight"]
   return weight
