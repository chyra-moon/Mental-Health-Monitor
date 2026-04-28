from datetime import date, datetime
from decimal import Decimal
from typing import Any


def to_jsonable(value: Any) -> Any:
    """Convert common non-JSON Python/NumPy values to JSON-serializable values."""
    try:
        import numpy as np

        if isinstance(value, np.generic):
            return value.item()
        if isinstance(value, np.ndarray):
            return [to_jsonable(item) for item in value.tolist()]
    except ImportError:
        pass

    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, dict):
        return {str(key): to_jsonable(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [to_jsonable(item) for item in value]

    return value
