import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-manual-skill1-engine-test-crosswalk-2026-11-05.json"

class ManualSkill1EngineTestCrosswalkTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_all_27_manual_rule_ids_are_in_engine_test_catalogue(self):
        s = self.data["summary"]
        self.assertEqual(s["manual_rule_count"], 27)
        self.assertEqual(s["rule_ids_in_engine_test_catalogue"], 27)
        self.assertEqual(len(self.data["rules"]), 27)
        self.assertEqual(len({x["rule_id"] for x in self.data["rules"]}), 27)
        self.assertEqual(self.data["engine_evidence"]["workflow_run_number"], 208)
        self.assertEqual(self.data["engine_evidence"]["workflow_conclusion"], "success")

    def test_representative_db29_fixture_gaps_are_explicit(self):
        s = self.data["summary"]
        self.assertEqual(s["representative_db29_card_fixtures_present"], 18)
        self.assertEqual(s["representative_db29_card_fixtures_missing"], 9)
        self.assertEqual(len(self.data["missing_representative_fixtures"]), 9)
        for row in self.data["missing_representative_fixtures"]:
            self.assertTrue(row["card_id"])
            self.assertTrue(row["manual_name"])
            self.assertTrue(row["engine_name"])

    def test_manual_and_engine_labels_are_not_collapsed(self):
        differences = [x for x in self.data["rules"] if x["manual_name"] != x["engine_whitelist_name"]]
        self.assertEqual(len(differences), 8)
        self.assertTrue(self.data["policy"]["manual_and_engine_names_preserved_separately"])

    def test_every_rule_retains_exact_db29_source_locator(self):
        for row in self.data["rules"]:
            self.assertEqual(row["source_field"], "Skill1")
            self.assertTrue(row["source_card_url"].startswith("https://fmlunatic.com/card/"))
            self.assertTrue(row["exact_source_label"])
            self.assertIsNotNone(row["source_enum_value"])
            self.assertGreater(row["matched_db29_card_rows"], 0)

    def test_engine_tests_do_not_promote_db29_card_mappings(self):
        self.assertFalse(self.data["summary"]["db29_mapping_semantic_promotion_authorized"])
        self.assertTrue(self.data["policy"]["db29_card_mapping_not_promoted_by_engine_test_alone"])
        self.assertEqual(self.data["source_evidence"]["skill1_exact_label_groups"], 27)
        self.assertEqual(self.data["source_evidence"]["skill1_matched_card_rows"], 3158)

    def test_db29_remains_immutable(self):
        b = self.data["baseline"]
        self.assertEqual(b["db_release"], "fm1-carddb-29")
        self.assertTrue(b["immutable"])
        self.assertFalse(b["db30_issued"])
        self.assertFalse(b["main_merge"])

if __name__ == "__main__":
    unittest.main()
