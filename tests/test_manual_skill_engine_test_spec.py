import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / "data" / "rules" / "fm1-skill-catalog-v1.json"
SPEC = ROOT / "data" / "reviews" / "fm1-manual-skill-engine-test-spec-2026-11-05.json"


class ManualSkillEngineTestSpecTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalog = json.loads(CATALOG.read_text(encoding="utf-8"))
        cls.spec = json.loads(SPEC.read_text(encoding="utf-8"))

    def test_all_27_manual_skills_are_covered_once(self):
        source = {rule["id"]: rule for rule in self.catalog["manualRules"]}
        target = {rule["rule_id"]: rule for rule in self.spec["rules"]}
        self.assertEqual(len(source), 27)
        self.assertEqual(len(target), 27)
        self.assertEqual(set(source), set(target))

    def test_structured_definition_and_source_provenance_are_preserved(self):
        source = {rule["id"]: rule for rule in self.catalog["manualRules"]}
        for item in self.spec["rules"]:
            with self.subTest(rule=item["rule_id"]):
                rule = source[item["rule_id"]]
                self.assertEqual(item["skill_name_exact"], rule["name"])
                self.assertEqual(item["source"], rule["source"])
                self.assertEqual(item["trigger"], rule.get("trigger"))
                self.assertEqual(item["conditions"], rule.get("conditions"))
                self.assertEqual(item["effect"], rule.get("effect"))
                self.assertEqual(
                    item["rule_definition"],
                    rule.get("ruleDefinition") or rule.get("definition"),
                )

    def test_test_prompts_are_non_executable_until_engine_validation(self):
        for item in self.spec["rules"]:
            with self.subTest(rule=item["rule_id"]):
                self.assertFalse(item["test_design"]["executable"])
                self.assertEqual(len(item["test_design"]["cases"]), 4)
                self.assertTrue(all(
                    case["status"] == "design_only"
                    for case in item["test_design"]["cases"]
                ))
                self.assertIsNone(item["card_source_matching"]["card_id"])
                self.assertEqual(
                    item["card_source_matching"]["status"],
                    "pending_db29_raw_inventory",
                )

    def test_baseline_guardrails_remain_explicit(self):
        self.assertEqual(self.spec["baseline"]["db_release"], "DB29")
        self.assertTrue(self.spec["baseline"]["immutable"])
        self.assertFalse(self.spec["baseline"]["db30_issued"])
        self.assertFalse(self.spec["baseline"]["main_merge"])
        self.assertEqual(self.spec["summary"]["executable_rules"], 0)


if __name__ == "__main__":
    unittest.main()
