import json
import unittest
from pathlib import Path


REPORT = Path(__file__).resolve().parents[1] / "data/reviews/fm1-skill2-tactical-initiative-adjudication-2026-11-06.json"


class TacticalInitiativeAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(REPORT.read_text(encoding="utf-8"))

    def test_candidate_rows_reconcile_without_promoting_mappings(self):
        scope = self.data["scope"]
        self.assertEqual(scope["candidate_rows"], 181)
        self.assertEqual(scope["distinct_card_ids"], 181)
        self.assertEqual(scope["additional_text_effect_rows"], 175)
        self.assertEqual(scope["card_text_only_rows"], 1)
        self.assertEqual(scope["missing_card_local_excerpt_rows"], 5)
        self.assertEqual(sum(x["count"] for x in self.data["variants"]), 175)
        policy = self.data["policy"]
        self.assertTrue(policy["all_card_mappings_remain_inferred"])
        self.assertTrue(policy["no_source_card_verified_promotion"])
        self.assertTrue(policy["no_executable_promotion"])

    def test_six_exact_source_variants_and_semantic_boundaries_are_preserved(self):
        variants = {x["key"]: x for x in self.data["variants"]}
        self.assertEqual(len(variants), 6)
        self.assertEqual(variants["ambiguous_level_order"]["count"], 133)
        self.assertEqual(variants["explicit_inclusive_level_threshold"]["count"], 18)
        self.assertEqual(variants["ambiguous_level_order_ap_damage_scope"]["count"], 16)
        self.assertEqual(variants["explicit_inclusive_short_form"]["count"], 6)
        self.assertEqual(variants["strict_lower_level"]["count"], 1)
        self.assertEqual(variants["explicit_inclusive_enum_abbreviation"]["count"], 1)
        self.assertNotEqual(
            variants["strict_lower_level"]["disposition"],
            variants["explicit_inclusive_level_threshold"]["disposition"],
        )
        self.assertIn("AP로 인한 데미지", variants["ambiguous_level_order_ap_damage_scope"]["text"])

    def test_non_effect_and_missing_source_rows_remain_excluded_or_pending(self):
        exclusions = self.data["exclusions"]
        self.assertEqual(exclusions["card_text_only"][0]["card_id"], "6082340724")
        self.assertEqual(len(exclusions["missing_card_local_excerpt"]), 5)
        self.assertTrue(all(x["source_card_url"].startswith("https://fmlunatic.com/card/") for x in exclusions["missing_card_local_excerpt"]))


if __name__ == "__main__":
    unittest.main()
