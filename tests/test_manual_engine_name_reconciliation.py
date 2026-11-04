import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REPORT = ROOT / "data" / "reviews" / "fm1-manual-engine-name-reconciliation-2026-11-05.json"


class ManualEngineNameReconciliationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_db29_guardrails_are_preserved(self):
        baseline = self.report["baseline"]
        self.assertEqual(baseline["db_release"], "DB29")
        self.assertTrue(baseline["immutable"])
        self.assertFalse(baseline["db30_issued"])
        self.assertFalse(baseline["main_merge"])

    def test_manual_inventory_and_engine_allowlist_counts(self):
        summary = self.report["summary"]
        self.assertEqual(summary["manual_rules"], 27)
        self.assertEqual(summary["engine_keyword_entries"], 27)
        self.assertEqual(summary["exact_name_match"], 19)
        self.assertEqual(summary["label_differences"], 8)
        self.assertEqual(summary["missing_engine_keywords"], 0)
        self.assertEqual(len(self.report["records"]), 27)

    def test_all_name_differences_remain_explicit_and_non_automatic(self):
        differences = [
            row for row in self.report["records"]
            if row["label_status"] == "name_difference_needs_adjudication"
        ]
        self.assertEqual(len(differences), 8)
        for row in differences:
            with self.subTest(rule=row["rule_id"]):
                self.assertNotEqual(row["manual_canonical_name"], row["engine_whitelist_name"])
                self.assertIn("Do not auto-alias", row["mapping_policy"])

    def test_whitelist_presence_is_not_mistaken_for_runtime_verification(self):
        for row in self.report["records"]:
            with self.subTest(rule=row["rule_id"]):
                self.assertTrue(row["engine_keyword_present"])
                self.assertIn("only a normalization gate", self.report["findings"])


if __name__ == "__main__":
    unittest.main()
