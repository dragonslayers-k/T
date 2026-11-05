import json
import unittest
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-soul-source-cooccurrence-probe-2026-11-05.json"

class SoulSourceCooccurrenceProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_source_inventory_reconciles_all_831_cards_and_842_tokens(self):
        s = self.data["summary"]
        self.assertEqual(s["unique_pending_cards"], 831)
        self.assertEqual(s["token_rows"], 842)
        self.assertEqual(s["groups"], 16)
        self.assertEqual(s["source_rows_matched"], 842)
        self.assertEqual(s["source_rows_missing"], 0)
        self.assertEqual(sum(x["card_rows"] for x in self.data["groups"]), 842)

    def test_ncs_and_bonus_are_separate_and_cooccurrence_is_not_semantics(self):
        groups = {x["code"]: x for x in self.data["groups"]}
        self.assertEqual(groups[82]["symbol"], "NCS")
        self.assertEqual(groups[82]["card_rows"], 351)
        self.assertEqual(groups[82]["cooccurrence"], {"neutral": 285, "none": 66})
        self.assertEqual(groups[83]["symbol"], "BONUS")
        self.assertEqual(groups[83]["card_rows"], 439)
        self.assertEqual(groups[83]["types"], {"unit": 403, "item": 36})
        self.assertTrue(self.data["policy"]["observed_cooccurrence_is_not_payment_rule_verification"])

    def test_hybrid_codes_remain_fourteen_distinct_identities(self):
        hybrids = [x for x in self.data["groups"] if x["code"] not in (82, 83)]
        self.assertEqual(len(hybrids), 14)
        self.assertEqual(sum(x["card_rows"] for x in hybrids), 52)
        self.assertTrue(all(x["symbol"] and x["card_rows"] > 0 for x in hybrids))
        self.assertTrue(self.data["policy"]["hybrid_pair_not_flattened"])

    def test_source_examples_keep_original_require_soul_and_icon_locators(self):
        samples = {x["card_id"]: x for x in self.data["sample_rows"]}
        self.assertEqual(samples["10021024687"]["raw_require_soul"], "820181018301")
        self.assertEqual(samples["10020324677"]["token_icon"], "/ncs.webp")
        self.assertEqual(samples["10021724688"]["token_icon"], "/bonus.webp")
        self.assertEqual(samples["13030626729"]["token_icon"], "/dark_earth.webp")

    def test_no_payment_rule_is_promoted_and_db29_is_immutable(self):
        self.assertTrue(self.data["policy"]["manual_MU_rule_not_applied_to_NCS_or_BONUS"])
        self.assertTrue(self.data["policy"]["no_runtime_promotion"])
        self.assertEqual(self.data["baseline"]["db_release"], "fm1-carddb-29")
        self.assertTrue(self.data["baseline"]["immutable"])
        self.assertFalse(self.data["baseline"]["db30_issued"])
        self.assertFalse(self.data["baseline"]["main_merge"])

if __name__ == "__main__":
    unittest.main()
