# TODO: implement data ingestion logic
from dataclasses import dataclass


NORMALIZATION_RULES = {
    "st.": "saint",
    "ste.": "sainte",
    "av.": "avenue",
}


@dataclass
class AddressGeocoder:
    """
    For now this only normalizes address strings.

    Later we can add:
      - actual geocoding (lat/lon)
      - caching of geocoding results
    """

    def normalize(self, address: str) -> str:
        normalized = address.strip().lower()
        for short, full in NORMALIZATION_RULES.items():
            normalized = normalized.replace(short, full)
        # collapse extra spaces
        return " ".join(normalized.split())

