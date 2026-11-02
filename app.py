"""Deterministic shipment triage with explicit approval for mutations."""
from datetime import datetime, timezone


def _parse(value):
    parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        raise ValueError("Timestamps must include a timezone")
    return parsed.astimezone(timezone.utc)


def recommend(orders, warehouse, carrier, now):
    """Join mock systems and rank interventions; all inputs are synthetic."""
    now = _parse(now)
    if len({o["id"] for o in orders}) != len(orders):
        raise ValueError("Duplicate order ID")
    results = []
    for order in orders:
        order_id = order["id"]
        wh = warehouse.get(order_id)
        scan = carrier.get(order_id)
        evidence, score = [], 0
        hours_to_eta = (_parse(order["eta"]) - now).total_seconds() / 3600
        if hours_to_eta < 0:
            score += 3
            evidence.append("ETA passed")
        elif hours_to_eta <= 24:
            score += 1
            evidence.append("ETA within 24 hours")
        if wh is None:
            evidence.append("Warehouse status unavailable")
        elif wh["status"] == "delayed":
            score += 2
            evidence.append("Warehouse delayed")
        if scan is None:
            evidence.append("Carrier status unavailable")
        else:
            if scan["status"] == "exception":
                score += 2
                evidence.append("Carrier exception")
            age = (now - _parse(scan["scanned_at"])).total_seconds() / 3600
            if age >= 24:
                score += 1
                evidence.append("No carrier scan for at least 24 hours")
        results.append({"order_id": order_id, "score": score,
                        "intervene": score >= 3, "evidence": evidence})
    return sorted(results, key=lambda item: (-item["score"], item["order_id"]))


def create_task(recommendation, approved, open_tasks):
    if not approved:
        raise PermissionError("Operator approval required")
    if not recommendation["intervene"]:
        raise ValueError("Only flagged shipments can receive a task")
    order_id = recommendation["order_id"]
    if order_id in open_tasks:
        return {"order_id": order_id, "status": "already_open"}
    task = {"order_id": order_id, "status": "open", "reason": recommendation["evidence"]}
    open_tasks[order_id] = task
    return task
