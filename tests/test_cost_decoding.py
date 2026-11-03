import unittest

from scripts.decode_soul_costs import run
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
        self.assertEqual(parsed["tokens"][0]["status"], "mapping_review")

    def test_ncs_and_bonus_are_separate_semantic_review_tokens(self):
        parsed = parse_require_soul("82018302")
        self.assertTrue(parsed["known"])
        self.assertTrue(parsed["semantic_review"])
        self.assertEqual(parsed["colors"]["ncs"], 1)
        self.assertEqual(parsed["colors"]["bonus"], 2)
        self.assertEqual(parsed["colors"]["neutral"], 0)

    def test_only_explicit_zero_none_token_means_no_cost(self):
        self.assertTrue(parse_require_soul("0100")["known"])
        self.assertFalse(parse_require_soul("0101")["known"])
        self.assertFalse(parse_require_soul("")["known"])

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


if __name__ == "__main__":
    unittest.main()
