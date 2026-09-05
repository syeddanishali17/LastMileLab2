"""Input-only capacity feedback. These are not planning run KPIs."""

from math import ceil
from typing import Any


def capacity_preview(demands: list[Any], vans: int, capacity: int) -> dict[str, Any]:
    valid = bool(demands) and all(type(value) is int and value > 0 for value in demands)
    valid = valid and vans > 0 and capacity > 0
    if not valid:
        return {"valid": False, "can_generate": False}
    total = sum(demands)
    largest = max(demands)
    fleet = vans * capacity
    return {
        "valid": True,
        "largest": largest,
        "total": total,
        "fleet": fleet,
        "spare": fleet - total,
        "minimum_vans": ceil(total / capacity),
        "order_ok": largest <= capacity,
        "fleet_ok": total <= fleet,
        "can_generate": largest <= capacity and total <= fleet,
    }
