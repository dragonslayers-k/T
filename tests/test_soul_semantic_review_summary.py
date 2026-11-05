import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-soul-semantic-review-summary-2026-11-05.json"

class SoulSemanticReviewSummaryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_pending_card_and_token_counts_reconcile(self):
        s = self.data["summary"]
        self.assertEqual(s["pending_card_rows"], 831)
        self.assertEqual(s["token_rows"], 842)
        self.assertEqual(s["groups"], 16)
        self.assertEqual(sum(g["card_rows"] for g in self.data["groups"]), 831)
        self.assertEqual(sum(g["token_rows"] for g in self.data["groups"]), 842)

    def test_hybrid_ncs_and_bonus_remain_separate(self):
        groups = self.data["groups"]
        hybrid = [g for g in groups if g["code"] not in (82, 83)]
        ncs = next(g for g in groups if g["code"] == 82)
        bonus = next(g for g in groups if g["code"] == 83)
        self.assertEqual(len(hybrid), 14)
        self.assertEqual(sum(g["card_rows"] for g in hybrid), 52)
        self.assertEqual(ncs["symbol"], "NCS")
        self.assertEqual(ncs["card_rows"], 351)
        self.assertEqual(bonus["symbol"], "BONUS")
        self.assertEqual(bonus["card_rows"], 439)
        self.assertNotEqual(ncs["candidate_color_mapping"], bonus["candidate_color_mapping"])

    def test_no_payment_semantics_are_promoted(self):
        self.assertEqual(self.data["summary"]["source_verified_rows"], 0)
        self.assertEqual(self.data["summary"]["executable_rows"], 0)
        self.assertTrue(self.data["policy"]["hybrid_identity_must_not_be_flattened_to_single_color"])
        self.assertTrue(self.data["policy"]["ncs_and_bonus_must_remain_distinct"])
        self.assertTrue(self.data["policy"]["token_parsing_is_not_payment_rule_verification"])
        self.assertTrue(all(g["status"].endswith("_pending_rule") for g in self.data["groups"]))

    def test_db29_remains_immutable(self):
        b = self.data["baseline"]
        self.assertEqual(b["db_release"], "fm1-carddb-29")
        self.assertTrue(b["immutable"])
        self.assertFalse(b["db30_issued"])
        self.assertFalse(b["main_merge"])

if __name__ == "__main__":
    unittest.main()
