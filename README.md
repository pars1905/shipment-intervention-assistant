# Shipment Intervention Assistant

A standalone Python prototype that joins mock order, warehouse, and carrier records, ranks shipments for an operations team, and creates a mock follow-up task only after explicit approval. It has no third-party Python dependencies.

**Scenario:** An operations lead asks which orders need intervention today. Three mock systems expose orders, warehouse readiness, and carrier scans. The assistant joins them by order ID, calculates a deterministic risk score, explains its evidence, and creates a follow-up task only after human approval.

From the repository root, run `python3 demo.py`, `python3 -m unittest discover -v`, and `python3 evaluate.py`. No packages or credentials are required.

To try an optional model-written reviewer explanation, set `OPENAI_API_KEY` and `OPENAI_MODEL` in your shell and run `python3 demo.py --ai`. The model receives structured recommendations and cannot create tasks. This API path has been tested with a mocked response, not a live key. API usage may incur charges.

## Design

An overdue ETA adds 3 points; an ETA within 24 hours adds 1. A delayed warehouse adds 2. A carrier exception adds 2; no scan for at least 24 hours adds 1. A score of at least 3 is flagged. Missing carrier data is shown as missing, never presented as a confirmed exception. The rule thresholds are illustrative and should be calibrated with real operational data.

The `recommend` function returns structured evidence. The `create_task` function requires an explicit approval flag and refuses duplicate open tasks. In a real integration, map the mock dictionaries to authenticated ERP/WMS/carrier APIs, enforce user permissions, persist an audit trail, and measure against historical late deliveries.

## Evaluation

`data/shipments_100.json` has 100 generated synthetic examples: 25 each with overdue ETAs, warehouse delays, carrier exceptions, and apparently normal signals. Some delayed warehouse or exception cases arrive on time; some apparently normal cases arrive late. These labels were assigned by the scenario generator, **not** from real shipment history. `python3 evaluate.py` reports precision, recall, a confusion matrix, and per-scenario accuracy. Use these numbers to find weaknesses in the rule, not as a claim of operational performance.

## Honest CV wording

“Built a Python shipment triage prototype joining mock order, warehouse, and carrier data; added explainable risk scoring, human-approved task creation, and evaluation on 100 synthetic cases.” Include metrics only with the synthetic-data qualifier.
