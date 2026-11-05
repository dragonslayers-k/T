import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-skill2-source-evidence-summary-2026-11-05.json"

class Skill2SourceEvidenceSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_candidate_counts_reconcile(self):
        s = self.data["summary"]
        self.assertEqual(s["candidate_rows"], 377)
        self.assertEqual(s["distinct_card_ids"], 377)
        self.assertEqual(s["rule_groups"], 8)
        self.assertEqual(s["additional_text_rows"], 368)
        self.assertEqual(s["additional_text_references"], 368)
        self.assertEqual(s["card_text_only_rows"], 1)
        self.assertEqual(s["card_text_references"], 7)
        self.assertEqual(s["missing_card_local_excerpt_rows"], 8)
        self.assertEqual(368 + 1 + 8, 377)

    def test_group_counts_reconcile_without_double_counting(self):
        groups = self.data["groups"]
        s = self.data["summary"]
        self.assertEqual(len(groups), s["rule_groups"])
        self.assertEqual(sum(x["rows"] for x in groups), s["candidate_rows"])
        self.assertEqual(sum(x["additional_text_rows"] for x in groups), s["additional_text_rows"])
        self.assertEqual(sum(x["card_text_only_rows"] for x in groups), s["card_text_only_rows"])
        self.assertEqual(sum(x["missing_rows"] for x in groups), s["missing_card_local_excerpt_rows"])
        self.assertTrue(all(x["distinct_additional_text_variants"] >= 1 for x in groups))

    def test_non_authoritative_and_missing_rows_remain_excluded(self):
        card_text_only = self.data["card_text_only_record"]
        self.assertEqual(card_text_only["card_id"], "6082340724")
        self.assertEqual(card_text_only["disposition"], "exclude_from_skill2_effect_evidence")
        missing = self.data["missing_records"]
        self.assertEqual(len(missing), 8)
        self.assertEqual(len({x["card_id"] for x in missing}), 8)
        self.assertEqual(sum(x["skill2"] == "기선제압" for x in missing), 5)
        self.assertEqual(sum(x["skill2"] == "헌신방어" for x in missing), 3)

    def test_exact_additional_text_variants_reconcile_to_observed_rows(self):
        groups = self.data["source_text_variants"]
        s = self.data["summary"]
        self.assertEqual(len(groups), s["rule_groups"])
        observed_rows = 0
        for group in groups:
            self.assertTrue(group["variants"])
            texts = [variant["text"] for variant in group["variants"]]
            self.assertTrue(all(isinstance(text, str) and text for text in texts))
            # Preserve source wording as distinct evidence; do not normalize or merge variants.
            self.assertEqual(len(texts), len(set(texts)))
            observed_rows += sum(variant["count"] for variant in group["variants"])
            self.assertEqual(group["semantic_status"], "pending_engine_test")
            self.assertTrue(group["review_gates"])
        self.assertEqual(observed_rows, s["additional_text_rows"])

    def test_no_inferred_skill2_mapping_is_promoted(self):
        policy = self.data["policy"]
        self.assertEqual(policy["mapping_status"], "inferred")
        self.assertTrue(policy["no_runtime_promotion"])
        s = self.data["summary"]
        self.assertEqual(s["source_card_verified_rows"], 0)
        self.assertEqual(s["executable_rows"], 0)

    def test_db29_remains_immutable(self):
        b = self.data["baseline"]
        self.assertEqual(b["db_release"], "fm1-carddb-29")
        self.assertTrue(b["immutable"])
        self.assertFalse(b["db30_issued"])
        self.assertFalse(b["main_merge"])

if __name__ == "__main__":
    unittest.main()
