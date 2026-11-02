"""Evaluate shipment triage against labeled synthetic scenarios."""
import json
from pathlib import Path
from app import recommend


def evaluate(cases):
    tp = fp = fn = tn = 0
    buckets = {}
    for case in cases:
        predicted = recommend([case["order"]], case["warehouse"], case["carrier"], case["now"])[0]["intervene"]
        actual = case["late"]
        tp += predicted and actual
        fp += predicted and not actual
        fn += not predicted and actual
        tn += not predicted and not actual
        bucket = buckets.setdefault(case["scenario"], {"total": 0, "correct": 0})
        bucket["total"] += 1
        bucket["correct"] += predicted == actual
    return {"examples": len(cases), "precision": round(tp / (tp + fp), 3) if tp + fp else None,
            "recall": round(tp / (tp + fn), 3) if tp + fn else None,
            "confusion": {"tp": tp, "fp": fp, "fn": fn, "tn": tn},
            "by_scenario": {name: {**count, "rate": round(count["correct"] / count["total"], 3)}
                            for name, count in sorted(buckets.items())}}


if __name__ == "__main__":
    cases = json.loads((Path(__file__).parent / "data" / "shipments_100.json").read_text())
    print(json.dumps(evaluate(cases), indent=2))
