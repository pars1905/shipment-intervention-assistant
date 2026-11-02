import json
import sys
from app import recommend, create_task

NOW = "2026-01-10T12:00:00Z"
orders = [
    {"id": "S-101", "eta": "2026-01-10T08:00:00Z"},
    {"id": "S-102", "eta": "2026-01-11T08:00:00Z"},
    {"id": "S-103", "eta": "2026-01-13T08:00:00Z"},
]
warehouse = {"S-101": {"status": "ready"}, "S-102": {"status": "delayed"}, "S-103": {"status": "ready"}}
carrier = {
    "S-101": {"status": "exception", "scanned_at": "2026-01-09T10:00:00Z"},
    "S-102": {"status": "normal", "scanned_at": "2026-01-10T10:00:00Z"},
    "S-103": {"status": "normal", "scanned_at": "2026-01-10T10:00:00Z"},
}

if __name__ == "__main__":
    ranked = recommend(orders, warehouse, carrier, NOW)
    print(json.dumps({"recommendations": ranked}, indent=2))
    if "--ai" in sys.argv:
        from ai_explain import explain
        print(explain("shipment intervention", ranked))
    print(json.dumps({"approved_task": create_task(ranked[0], True, {})}, indent=2))
