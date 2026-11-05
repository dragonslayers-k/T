import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-carddb-29-semantic-review-adjudication-overlay-2026-11-05.json"

class SemanticReviewAdjudicationOverlayTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_41_patterns_and_54_occurrences_reconcile(self):
        s = self.data["summary"]
        records = self.data["records"]
        self.assertEqual(s["unique_patterns"], 41)
        self.assertEqual(len({x["pattern_id"] for x in records}), 41)
        self.assertEqual(s["occurrences"], 54)
        self.assertEqual(len(records), 54)
        self.assertEqual(s["source_context_resolved_patterns"], 39)
        self.assertEqual(s["source_context_resolved_occurrences"], 52)
        self.assertEqual(s["pending_patterns"], 2)
        self.assertEqual(s["pending_occurrences"], 2)

    def test_adjudication_group_counts_match_pass3(self):
        groups = {g["id"]: g for g in self.data["summary"]["groups"]}
        expected = {
            "shared_disenchant_rule_reference": (22, 23),
            "named_area_hero_counter_reference": (7, 7),
            "card_pool_reference": (2, 8),
            "summon_profile_reference": (2, 8),
            "named_card_variant_reference": (2, 2),
            "condition_branch_profile_context": (4, 4),
            "opaque_source_annotation_pending": (1, 1),
            "incomplete_source_fragment_pending": (1, 1),
        }
        self.assertEqual(set(groups), set(expected))
        for key, (patterns, occurrences) in expected.items():
            self.assertEqual(groups[key]["patterns"], patterns)
            self.assertEqual(groups[key]["occurrences"], occurrences)

    def test_only_cwda_and_trailing_sang_remain_unresolved(self):
        unresolved = [x for x in self.data["records"] if x["context_status"].startswith("pending_")]
        self.assertEqual({x["pattern_id"] for x in unresolved}, {"f41dfd55352a6ebd", "3c2d6ddb4a94f1f3"})
        self.assertEqual({x["source_card"]["card_id"] for x in unresolved}, {"13010233113", "9071541048"})

    def test_all_occurrences_remain_non_executable(self):
        self.assertEqual(self.data["summary"]["runtime_executable_occurrences"], 0)
        self.assertTrue(self.data["policy"]["context_resolution_is_not_runtime_semantic_completion"])
        self.assertTrue(all(x["runtime_status"] == "non_executable" for x in self.data["records"]))

    def test_source_locator_and_db29_immutability(self):
        for row in self.data["records"]:
            self.assertTrue(row["source_card"]["card_id"])
            self.assertTrue(row["source_card"]["source_detail_url"].startswith("https://fmlunatic.com/card/"))
        b = self.data["baseline"]
        self.assertEqual(b["db_release"], "fm1-carddb-29")
        self.assertTrue(b["immutable"])
        self.assertFalse(b["db30_issued"])
        self.assertFalse(b["main_merge"])

if __name__ == "__main__":
    unittest.main()
