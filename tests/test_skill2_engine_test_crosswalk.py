import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-skill2-engine-test-crosswalk-2026-11-05.json"

class Skill2EngineTestCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_all_eight_catalog_rules_have_a_passing_engine_test(self):
        self.assertEqual(self.data["summary"]["catalog_rule_count"], 8)
        self.assertEqual(self.data["summary"]["positive_rule_tests"], 8)
        self.assertEqual(len(self.data["rules"]), 8)
        self.assertEqual(len({x["rule_id"] for x in self.data["rules"]}), 8)
        self.assertEqual(self.data["summary"]["engine_test_status"], "passed_in_actions_208")
        self.assertEqual(self.data["engine_evidence"]["workflow_run_number"], 208)
        self.assertEqual(self.data["engine_evidence"]["workflow_conclusion"], "success")

    def test_boundary_and_fail_closed_tests_are_preserved(self):
        self.assertEqual(len(self.data["boundary_tests"]), 5)
        self.assertEqual(len(self.data["fail_closed_tests"]), 3)
        self.assertTrue(any("inferred card mappings" in x for x in self.data["fail_closed_tests"]))

    def test_engine_pass_does_not_promote_db29_card_mappings(self):
        s = self.data["summary"]
        self.assertEqual(s["db29_skill2_candidate_rows"], 377)
        self.assertEqual(s["db29_rows_with_additional_text"], 368)
        self.assertEqual(s["db29_card_text_only_rows"], 1)
        self.assertEqual(s["db29_rows_missing_excerpt"], 8)
        self.assertEqual(s["db29_source_card_verified_rows"], 0)
        self.assertEqual(s["db29_executable_rows"], 0)
        self.assertTrue(self.data["policy"]["handler_test_pass_is_not_card_mapping_promotion"])

    def test_db29_remains_immutable(self):
        b = self.data["baseline"]
        self.assertEqual(b["db_release"], "fm1-carddb-29")
        self.assertTrue(b["immutable"])
        self.assertFalse(b["db30_issued"])
        self.assertFalse(b["main_merge"])

if __name__ == "__main__":
    unittest.main()
