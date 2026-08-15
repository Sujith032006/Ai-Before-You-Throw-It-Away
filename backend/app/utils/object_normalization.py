import logging
from typing import Dict, Any

logger = logging.getLogger(__name__)

def derive_confidence_level(score: float) -> str:
    if score >= 0.85:
        return "high"
    elif score >= 0.65:
        return "medium"
    elif score >= 0.40:
        return "low"
    return "unknown"

def normalize_object_name(raw_name: str) -> Dict[str, str]:
    """
    Standardizes equivalent physical object names.
    NEVER converts an unknown or unsupported item into a reuse class!
    """
    clean = raw_name.lower().strip().replace("-", "_").replace(" ", "_")

    # Safe equivalencies
    mappings = {
        "cell_phone": ("smartphone", "Smartphone"),
        "mobile_phone": ("smartphone", "Smartphone"),
        "phone": ("smartphone", "Smartphone"),
        "dining_table": ("table", "Table"),
        "desk": ("table", "Desk / Table"),
        "computer_keyboard": ("keyboard", "Keyboard"),
        "computer_monitor": ("monitor", "Monitor / Screen"),
        "tv": ("monitor", "Monitor / Screen"),
        "backpack": ("backpack", "Backpack"),
        "handbag": ("bag", "Bag / Handbag"),
        "suitcase": ("bag", "Luggage / Bag"),
        "cardboard_container": ("cardboard_box", "Cardboard Box"),
        "shipping_box": ("cardboard_box", "Cardboard Box"),
        "aluminum_can": ("tin_can", "Tin Can / Aluminum Can"),
        "metal_can": ("tin_can", "Tin Can"),
        "glass_vase": ("glass_jar", "Glass Jar / Vase"),
    }

    if clean in mappings:
        n, d = mappings[clean]
        return {"object_name": n, "display_name": d}

    # Default clean format
    display = clean.replace("_", " ").title()
    return {"object_name": clean, "display_name": display}
