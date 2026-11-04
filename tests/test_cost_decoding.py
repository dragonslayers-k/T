import unittest

from scripts.decode_soul_costs import run
from scripts.build_gap_reports import build_soul_semantic_review_queue
from scripts.soul_costs import parse_require_soul


class RequireSoulTests(unittest.TestCase):
    def test_pure_tokens_use_iron_as_canonical_metal_key(self):
        parsed = parse_require_soul("5102")
        self.assertTrue(parsed["known"])
        self.assertEqual(parsed["colors"]["iron"], 2)
        self.assertNotIn("metal", parsed["colors"])

    def test_hybrid_tokens_are_candidate_mapping_not_cross_validated(self):
        parsed = parse_require_soul("5301")
        self.assertTrue(parsed["known"])
        self.assertTrue(parsed["mapping_review"])
        self.assertEqual(parsed["colors"]["iron"], 1)
        self.assertEqual(parsed["colors"]["light"], 1)
        self.assertEqual(parsed["tokens"][0]["status"], "hybrid_identity_preserved_pending_rule")
        self.assertEqual(parsed["tokens"][0]["inference"], "hybrid_color_pair_payment_rule_unverified")

    def test_ncs_and_bonus_are_separate_semantic_review_tokens(self):
        parsed = parse_require_soul("82018302")
        self.assertTrue(parsed["known"])
        self.assertTrue(parsed["semantic_review"])
        self.assertEqual(parsed["colors"]["ncs"], 1)
        self.assertEqual(parsed["colors"]["bonus"], 2)
        self.assertEqual(parsed["colors"]["neutral"], 0)
        self.assertEqual(parsed["tokens"][0]["status"], "special_identity_preserved_pending_rule")
        self.assertEqual(parsed["tokens"][1]["status"], "special_identity_preserved_pending_rule")

    def test_korean_text_cost(self):
        p = parse_require_soul("숲 2, 물 1")
        self.assertTrue(p["known"])
        self.assertEqual(p["colors"]["forest"], 2)
        self.assertEqual(p["colors"]["water"], 1)

    def test_english_text_cost_is_case_insensitive(self):
        p = parse_require_soul("Forest 2, WATER 1, nCs 3, Bonus 1")
        self.assertTrue(p["known"])
        self.assertEqual(p["colors"]["forest"], 2)
        self.assertEqual(p["colors"]["water"], 1)
        self.assertEqual(p["colors"]["ncs"], 3)
        self.assertEqual(p["colors"]["bonus"], 1)


    def test_manual_neutral_soul_phrase_is_decoded(self):
        for raw in ("무속성 2", "무속성 소울 2", "2 무속성", "2 무속성 소울"):
            with self.subTest(raw=raw):
                parsed = parse_require_soul(raw)
                self.assertTrue(parsed["known"], parsed)
                self.assertEqual(parsed["colors"]["neutral"], 2)
                self.assertEqual(parsed["tokens"][0]["status"], "text_decoded")

    def test_unknown_text_cost_is_not_partially_accepted(self):
        p = parse_require_soul("숲 2, 미지의소울 1")
        self.assertFalse(p["known"])

    def test_only_explicit_zero_none_token_means_no_cost(self):
        self.assertTrue(parse_require_soul("0100")["known"])
        self.assertFalse(parse_require_soul("0101")["known"])
        self.assertFalse(parse_require_soul("")["known"])

    def test_numeric_tokens_with_copy_separators_are_decoded(self):
        p = parse_require_soul("5102, 4101 + 7101")
        self.assertTrue(p["known"])
        self.assertEqual(p["source_format"], "numeric_enum")
        self.assertEqual(p["colors"]["iron"], 2)
        self.assertEqual(p["colors"]["forest"], 1)
        self.assertEqual(p["colors"]["light"], 1)

    def test_unknown_code_stays_unresolved(self):
        parsed = parse_require_soul("9901")
        self.assertFalse(parsed["known"])
        self.assertEqual(parsed["error_reason"], "unsupported_token_99")
        self.assertEqual(parsed["colors"]["neutral"], 0)

    def test_actual_source_card_url_is_preserved(self):
        result = run([{
            "card_id": "card-1",
            "raw_payload": {"Name": "샘플", "RequireSoul": "8101"},
            "source_card_url": "https://fmlunatic.com/card/actual-card-id",
        }])
        self.assertEqual(result["decoded"][0]["sourceCardUrl"], "https://fmlunatic.com/card/actual-card-id")

    def test_url_is_not_fabricated_when_source_value_is_missing(self):
        result = run([{
            "card_id": "card-1",
            "raw_payload": {"Name": "샘플", "NumID": 12345, "RequireSoul": "8101"},
        }])
        self.assertIsNone(result["decoded"][0]["sourceCardUrl"])

    def test_zero_reference_costs_are_not_claimed_as_successful_validation(self):
        result = run([{
            "card_id": "card-1",
            "raw_payload": {"RequireSoul": "8101"},
        }])
        self.assertEqual(result["validatedKnownCosts"], 0)
        self.assertEqual(result["validationStatus"], "not_available_no_reference_costs")

    def test_available_reference_costs_are_compared(self):
        result = run([{
            "card_id": "card-1",
            "raw_payload": {"RequireSoul": "5102"},
            "cost": {"iron": 2},
            "costKnown": True,
        }])
        self.assertEqual(result["validatedKnownCosts"], 1)
        self.assertEqual(result["validationStatus"], "matched_reference_rows")
        self.assertEqual(result["knownCostMismatches"], [])


    def test_soul_semantic_review_queue_preserves_every_occurrence(self):
        rows = [
            {"card_id":"100","name":"A","card_type":"유닛","source_card_url":"https://example.test/100",
             "source_text":"43017101","mapping_review":1,"semantic_review":0,
             "ordinal":0,"raw_token":"4301","code":43,"count":1,"symbol":"hybrid",
             "normalized_color":"forest+light","parse_status":"hybrid_identity_preserved_pending_rule"},
            {"card_id":"100","name":"A","card_type":"유닛","source_card_url":"https://example.test/100",
             "source_text":"43017101","mapping_review":1,"semantic_review":0,
             "ordinal":1,"raw_token":"4301","code":43,"count":1,"symbol":"hybrid",
             "normalized_color":"forest+light","parse_status":"hybrid_identity_preserved_pending_rule"},
            {"card_id":"200","name":"B","card_type":"마법","source_card_url":"https://example.test/200",
             "source_text":"4301","mapping_review":1,"semantic_review":0,
             "ordinal":0,"raw_token":"4301","code":43,"count":1,"symbol":"hybrid",
             "normalized_color":"forest+light","parse_status":"hybrid_identity_preserved_pending_rule"},
        ]
        result = build_soul_semantic_review_queue(rows)
        self.assertEqual(result["pending_card_rows"], 2)
        self.assertEqual(result["token_rows"], 3)
        group = result["groups"][0]
        self.assertEqual(group["card_count"], 2)
        self.assertEqual(len(group["occurrences"]), 3)
        self.assertFalse(group["executable"])

    def test_soul_semantic_review_queue_separates_hybrid_and_special(self):
        rows = [
            {"card_id":"1","mapping_review":1,"semantic_review":0,"code":43,
             "normalized_color":"forest+light","parse_status":"hybrid_identity_preserved_pending_rule"},
            {"card_id":"2","mapping_review":0,"semantic_review":1,"code":82,
             "normalized_color":"ncs","parse_status":"special_identity_preserved_pending_rule"},
        ]
        result = build_soul_semantic_review_queue(rows)
        reasons = {g["code"]:g["review_reasons"] for g in result["groups"]}
        self.assertEqual(reasons[43], ["hybrid_payment_rule_unverified"])
        self.assertEqual(reasons[82], ["special_soul_payment_rule_unverified"])


if __name__ == "__main__":
    unittest.main()
