import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-global-gameplay-engine-test-crosswalk-2026-11-05.json"

class GlobalGameplayEngineTestCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_all_fifteen_manual_global_rules_are_accounted_for(self):
        self.assertEqual(self.data["summary"]["global_rule_count"], 15)
        self.assertEqual(len(self.data["rules"]), 15)
        self.assertEqual(len({x["rule_id"] for x in self.data["rules"]}), 15)

    def test_fourteen_rules_have_test_evidence_and_one_gap_is_explicit(self):
        rules = self.data["rules"]
        covered = [x for x in rules if x["tests"]]
        missing = [x for x in rules if not x["tests"]]
        self.assertEqual(len(covered), 14)
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0]["rule_id"], "opponent_concession_win")
        self.assertEqual(self.data["summary"]["rules_without_engine_test_evidence"], 1)

    def test_manual_terrain_conflict_is_not_resolved_by_engine_behavior(self):
        rule = next(x for x in self.data["rules"] if x["rule_id"] == "terrain_placement_limit_conflict")
        self.assertEqual(rule["coverage_status"], "engine_behavior_tested_source_conflict_unresolved")
        self.assertIn("conflict", rule["source_conflict"])
        self.assertIn("not source resolution", rule["source_conflict"])

    def test_test_coverage_does_not_promote_runtime_rules(self):
        self.assertEqual(self.data["summary"]["runtime_rule_promotions"], 0)
        self.assertTrue(self.data["policy"]["test_presence_is_not_complete_semantic_verification"])
        self.assertTrue(self.data["policy"]["unverified_NCS_BONUS_and_hybrid_rules_not_promoted"])

    def test_db29_remains_immutable(self):
        b = self.data["baseline"]
        self.assertEqual(b["db_release"], "fm1-carddb-29")
        self.assertTrue(b["immutable"])
        self.assertFalse(b["db30_issued"])
        self.assertFalse(b["main_merge"])

if __name__ == "__main__":
    unittest.main()
