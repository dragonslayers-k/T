import unittest

from scripts.semantic_audit_status import evaluate_semantic_status


class SemanticAuditStatusTests(unittest.TestCase):
    def base_report(self):
        return {
            "field_coverage_complete": True,
            "field_coverage_applicability_complete": True,
            "field_coverage_applicability_candidate_pairs": 0,
            "soul_cost_needs_review": 0,
            "soul_cost_tokens": 24166,
            "skill_unmapped_rows": 0,
            "skill_inventory_unmapped_values": 0,
            "unmapped_skill_card_rows_after_inference": 0,
            "effect_interpretation_rows": 48281,
            "effect_clause_rows": 48281,
            "effect_interpretation_missing": 0,
            "effect_interpretation_low_confidence": 0,
            "effect_semantic_review_pending": 0,
            "inferred_skill_name_only_rows": 0,
            "soul_mapping_review": 0,
            "soul_semantic_review": 0,
            "manual_rule_engine_test_pending": 0,
        }

    def test_coverage_is_not_completion_when_reviews_remain(self):
        report = self.base_report()
        report.update({
            "effect_interpretation_low_confidence": 1249,
            "effect_semantic_review_pending": 0,
            "inferred_skill_name_only_rows": 24,
            "soul_mapping_review": 52,
            "soul_semantic_review": 779,
            "manual_rule_engine_test_pending": 27,
        })
        result = evaluate_semantic_status(report)
        self.assertTrue(result["semantic_coverage_pass"])
        self.assertFalse(result["semantic_completeness_pass"])
        self.assertEqual(result["semantic_review_pending"], {
            "field_applicability_category_pairs": 0,
            "effect_interpretation_low_confidence": 1249,
            "effect_semantic_review_pending": 0,
            "name_only_skill_rules": 24,
            "hybrid_soul_payment_rules": 52,
            "special_soul_payment_rules": 779,
        })
        self.assertFalse(result["engine_verification_complete"])
        self.assertEqual(result["engine_verification_pending"], 27)

    def test_non_low_confidence_candidates_still_block_semantic_completion(self):
        report=self.base_report()
        report["effect_semantic_review_pending"]=16
        result=evaluate_semantic_status(report)
        self.assertTrue(result["semantic_coverage_pass"])
        self.assertFalse(result["semantic_completeness_pass"])
        self.assertEqual(result["semantic_review_pending"]["effect_semantic_review_pending"],16)

    def test_zero_pending_reviews_means_semantic_completion(self):
        result = evaluate_semantic_status(self.base_report())
        self.assertTrue(result["semantic_coverage_pass"])
        self.assertTrue(result["semantic_completeness_pass"])
        self.assertTrue(result["engine_verification_complete"])



    def test_unresolved_applicability_candidates_fail_semantic_coverage(self):
        report = self.base_report()
        report["field_coverage_complete"] = False
        report["field_coverage_applicability_complete"] = False
        report["field_coverage_applicability_candidate_pairs"] = 100
        result = evaluate_semantic_status(report)
        self.assertFalse(result["semantic_coverage_pass"])
        self.assertFalse(result["semantic_completeness_pass"])
        self.assertEqual(result["semantic_review_pending"]["field_applicability_category_pairs"], 100)

    def test_missing_interpretations_fail_coverage(self):
        report = self.base_report()
        report["effect_interpretation_missing"] = 1
        result = evaluate_semantic_status(report)
        self.assertFalse(result["semantic_coverage_pass"])
        self.assertFalse(result["semantic_completeness_pass"])


if __name__ == "__main__":
    unittest.main()
