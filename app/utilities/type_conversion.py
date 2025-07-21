from typing import Any
from decimal import Decimal

def convert_decimal_into_float(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return float(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_into_float(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_into_float(elem) for elem in obj]
    else:
        return obj