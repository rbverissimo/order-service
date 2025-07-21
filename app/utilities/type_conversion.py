from typing import Any
from decimal import Decimal

def convert_decimal_into_serializable_str(obj: Any) -> Any:
    if isinstance(obj, Decimal):
        return str(obj)
    elif isinstance(obj, dict):
        return {k: convert_decimal_into_serializable_str(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_decimal_into_serializable_str(elem) for elem in obj]
    elif isinstance(obj, (int, bool)):
        return obj
    else:
        return str(obj)