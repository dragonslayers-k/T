import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RULE = ROOT / "data/reviews/fm1-disenchant-shared-rule-v1.json"
REVIEW = ROOT / "data/reviews/fm1-carddb-29-semantic-review-reference-adjudication-2026-11-04.json"

class DisenchantSharedRuleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rule = json.loads(RULE.read_text(encoding="utf-8"))
        cls.review = json.loads(REVIEW.read_text(encoding="utf-8"))
        cls.rows = [r for r in cls.review["records"]
                    if r["classification"] == "named_effect_reference_candidate"]

    def test_shared_rule_links_all_23_distinct_evidence_cards(self):
        self.assertEqual(self.rule["supporting_reference_rows"], 23)
        self.assertEqual(len(self.rule["supporting_card_ids"]), 23)
        self.assertEqual(len({x["card_id"] for x in self.rule["supporting_card_ids"]}), 23)
        self.assertEqual(len(self.rows), 23)
        self.assertTrue(all(
            r["external_reference_review"]["structured_candidate"]["shared_rule_id"] == self.rule["rule_id"]
            for r in self.rows
        ))

    def test_twenty_one_attribute_named_cards_map_to_exact_ids_within_evidence_rows(self):
        groups = self.rule["disenchant_card_names_by_attribute"]
        self.assertEqual(len(groups), 7)
        self.assertEqual({g["attribute"] for g in groups},
                         {"암흑", "불", "물", "숲", "금속", "대지", "빛"})
        items = [x for g in groups for x in g["items"]]
        self.assertEqual(len(items), 21)
        self.assertEqual(len({x["name"] for x in items}), 21)
        self.assertTrue(all(x["card_id"] for x in items))
        self.assertTrue(all(x["match_status"] == "exact_card_name_match_within_23_evidence_rows" for x in items))

    def test_supporting_rows_not_in_typed_list_remain_separate(self):
        extra = self.rule["supporting_cards_not_in_named_type_list"]
        self.assertEqual({x["name"] for x in extra}, {"칠색조의가호", "시스카이"})
        self.assertEqual(len(extra), 2)

    def test_source_text_is_preserved_and_execution_remains_blocked(self):
        self.assertEqual(self.rule["source_authority"], "DB29 original card TextExtra")
        self.assertIn("인첸트 발동 페이즈", self.rule["source_definition"])
        self.assertFalse(self.rule["engine_verified"])
        self.assertFalse(self.rule["executable"])
        self.assertEqual(self.rule["runtime_status"], "non_executable")
        self.assertEqual(len(self.rows), 23)
        for row in self.rows:
            extra = row["source_card"]["TextExtra"]["source_value"]
            self.assertIn(self.rule["source_definition"], extra)
            self.assertEqual(row["review_status"], "pending_manual_semantic_review")
            self.assertEqual(row["runtime_status"], "non_executable")
            self.assertEqual(row["external_reference_review"]["runtime_status"], "non_executable")

    def test_full_text_variants_and_card_specific_notes_are_not_collapsed(self):
        variants = {r["source_card"]["TextExtra"]["source_value"] for r in self.rows}
        self.assertEqual(len(variants), self.rule["source_text_variant_count"])
        self.assertGreater(len(self.rule["card_specific_auxiliary_notes"]), 0)
        self.assertIn("원문", self.rule["original_text_policy"])

if __name__ == "__main__":
    unittest.main()
