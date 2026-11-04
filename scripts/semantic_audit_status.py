"""Separate structural semantic coverage from verified semantic completion."""

def evaluate_semantic_status(report):
    """Return coverage/completion gates and explicit pending-review counts."""
    coverage_pass = bool(
        report.get("field_coverage_complete")
        and report.get("soul_cost_needs_review", 0) == 0
        and report.get("soul_cost_tokens", 0) > 0
        and report.get("skill_unmapped_rows", 0) == 0
        and report.get("skill_inventory_unmapped_values", 0) == 0
        and report.get("unmapped_skill_card_rows_after_inference", 0) == 0
        and report.get("effect_interpretation_rows") == report.get("effect_clause_rows")
        and report.get("effect_interpretation_missing", 0) == 0
    )
    pending = {
        "field_applicability_category_pairs": int(report.get("field_coverage_applicability_candidate_pairs", 0)),
        "effect_interpretation_low_confidence": int(report.get("effect_interpretation_low_confidence", 0)),
        "effect_semantic_review_pending": int(report.get("effect_semantic_review_pending", 0)),
        "name_only_skill_rules": int(report.get("inferred_skill_name_only_rows", 0)),
        "hybrid_soul_payment_rules": int(report.get("soul_mapping_review", 0)),
        "special_soul_payment_rules": int(report.get("soul_semantic_review", 0)),
    }
    semantic_complete = coverage_pass and not any(pending.values())
    engine_pending = int(report.get("manual_rule_engine_test_pending", 0))
    return {
        "semantic_coverage_pass": coverage_pass,
        "semantic_completeness_pass": semantic_complete,
        "semantic_review_pending": pending,
        "engine_verification_pending": engine_pending,
        "engine_verification_complete": engine_pending == 0,
    }
