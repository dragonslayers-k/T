import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ECA = ROOT / "data/reviews/fm1-ecaemael-summon-profile-v1.json"
SAND = ROOT / "data/reviews/fm1-turn-derived-summon-profile-v1.json"
REVIEW = ROOT / "data/reviews/fm1-carddb-29-semantic-review-reference-adjudication-2026-11-04.json"

class SummonProfileReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.eca = json.loads(ECA.read_text(encoding="utf-8"))
        cls.sand = json.loads(SAND.read_text(encoding="utf-8"))
        cls.review = json.loads(REVIEW.read_text(encoding="utf-8"))

    def test_exactly_seven_ecaemael_cards_and_shared_source_text(self):
        self.assertEqual(self.eca["card_count"], 7)
        self.assertEqual(len(self.eca["cards"]), 7)
        self.assertEqual(len({x["card_id"] for x in self.eca["cards"]}), 7)
        self.assertEqual(len({x["text_extra"] for x in self.eca["cards"]}), 1)
        self.assertTrue(all(x["text_base"] == "" for x in self.eca["cards"]))

    def test_ecaemael_pool_rules_are_source_text_and_exceptions_remain_unresolved(self):
        pool = self.eca["structured_pool_filter"]
        self.assertEqual(pool["chapter_range_inclusive"], [1, 3])
        self.assertTrue(pool["same_level"])
        self.assertTrue(pool["same_attribute"])
        self.assertEqual(pool["selection"], "random")
        self.assertTrue(pool["include_rank_cards"])
        self.assertTrue(pool["exclude_event_grade"])
        self.assertIn("일부", pool["other_exclusions"])
        self.assertFalse(self.eca["engine_verified"])
        self.assertEqual(self.eca["runtime_status"], "non_executable")

    def test_ecaemael_parity_formula_preserves_zero_count_unknown(self):
        effect = self.eca["terrain_count_effect"]
        self.assertEqual(effect["odd_count"], {"stat": "AP", "delta": 1})
        self.assertEqual(effect["even_count"], {"stat": "HP", "delta": 1})
        self.assertEqual(effect["zero_count_behavior"], "unverified")
        self.assertIn("maximum-five", " ".join(self.eca["unresolved_engine_questions"]).lower()
                      if any("maximum-five" in x.lower() for x in self.eca["unresolved_engine_questions"]) else
                      " ".join(self.eca["unresolved_engine_questions"]).lower())

    def test_sand_shape_is_not_an_ecaemael_profile(self):
        self.assertEqual(self.sand["card_id"], "9010731883")
        self.assertEqual(self.sand["card_name"], "모래의형상화")
        self.assertEqual(self.sand["generated_unit_profile"]["soul_costs"]["colored_soul"], "턴의 일의자리수")
        self.assertEqual(self.sand["generated_unit_profile"]["soul_costs"]["neutral_soul"], "턴의 십의자리수")
        self.assertEqual(self.sand["generated_unit_profile"]["stats"], {
            "AP": "소각장 유닛수", "DP": "핸드 유닛수", "HP": "백필드 지형수"
        })
        self.assertEqual(self.sand["generated_unit_profile"]["max_level"], 10)
        self.assertFalse(self.sand["engine_verified"])
        self.assertEqual(self.sand["runtime_status"], "non_executable")

    def test_adjudication_rows_keep_pending_and_distinguish_three_summon_models(self):
        rows = self.review["records"]
        eca_rows = [r for r in rows if r.get("external_reference_review", {}).get("structured_candidate", {}).get("profile_kind") == "ecaemael_chapter_summon_profile"]
        sand_rows = [r for r in rows if r.get("external_reference_review", {}).get("structured_candidate", {}).get("profile_kind") == "turn_derived_sand_shaping_summon"]
        cond_rows = [r for r in rows if r.get("external_reference_review", {}).get("structured_candidate", {}).get("kind") == "conditional_summoned_unit_profile"]
        self.assertEqual(len(eca_rows), 7)
        self.assertEqual(len(sand_rows), 1)
        self.assertEqual(len(cond_rows), 1)
        for row in eca_rows + sand_rows + cond_rows:
            self.assertEqual(row["review_status"], "pending_manual_semantic_review")
            self.assertEqual(row["runtime_status"], "non_executable")

if __name__ == "__main__":
    unittest.main()
