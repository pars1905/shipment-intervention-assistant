import json
import unittest
from pathlib import Path
from datetime import datetime
from evaluate import evaluate


class EvaluationTests(unittest.TestCase):
    def test_balanced_cases_and_confusion_counts(self):
        cases = json.loads((Path(__file__).parent / "data" / "shipments_100.json").read_text())
        result = evaluate(cases)
        self.assertEqual(result["examples"], 100)
        self.assertEqual({v["total"] for v in result["by_scenario"].values()}, {25})
        self.assertEqual(sum(result["confusion"].values()), 100)
        self.assertGreater(result["confusion"]["fp"], 0)
        self.assertGreater(result["confusion"]["fn"], 0)
        for case in cases:
            if case["scenario"] == "overdue":
                self.assertLess(datetime.fromisoformat(case["order"]["eta"].replace("Z", "+00:00")),
                                datetime.fromisoformat(case["now"].replace("Z", "+00:00")))


if __name__ == "__main__":
    unittest.main()
