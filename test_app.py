import unittest
from app import recommend, create_task


class LogisticsTests(unittest.TestCase):
    def setUp(self):
        self.now = "2026-01-10T12:00:00Z"

    def test_overdue_is_flagged_without_carrier_claim(self):
        item = recommend([{"id": "A", "eta": "2026-01-10T11:00:00Z"}], {}, {}, self.now)[0]
        self.assertTrue(item["intervene"])
        self.assertIn("Carrier status unavailable", item["evidence"])
        self.assertNotIn("Carrier exception", item["evidence"])

    def test_approval_and_idempotence(self):
        item = recommend([{"id": "A", "eta": "2026-01-10T11:00:00Z"}], {}, {}, self.now)[0]
        tasks = {}
        with self.assertRaises(PermissionError):
            create_task(item, False, tasks)
        self.assertFalse(tasks)
        create_task(item, True, tasks)
        self.assertEqual(create_task(item, True, tasks)["status"], "already_open")

    def test_rejects_duplicate_orders(self):
        with self.assertRaises(ValueError):
            recommend([{"id": "A"}, {"id": "A"}], {}, {}, self.now)

    def test_only_boolean_true_counts_as_approval(self):
        item = recommend([{"id": "A", "eta": "2026-01-10T11:00:00Z"}], {}, {}, self.now)[0]
        tasks = {}
        for value in ("false", "no", 1):
            with self.subTest(value=value):
                with self.assertRaises(PermissionError):
                    create_task(item, value, tasks)
        self.assertFalse(tasks)

    def test_future_scan_is_reported_not_treated_as_fresh(self):
        order = {"id": "A", "eta": "2026-01-13T12:00:00Z"}
        scan = {"A": {"status": "normal", "scanned_at": "2026-01-13T12:00:00Z"}}
        item = recommend([order], {"A": {"status": "ready"}}, scan, self.now)[0]
        self.assertIn("Carrier scan timestamp is in the future", item["evidence"])


if __name__ == "__main__":
    unittest.main()
