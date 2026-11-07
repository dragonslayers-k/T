import json
import tempfile
import unittest
from pathlib import Path

from scripts.effect_pattern_audit import analyze, split_clause_candidates
from scripts.build_gap_reports import classify_cost_review
from scripts.build_gap_reports import expand_cost_token_review_rows
from scripts.build_gap_reports import write_jsonl_rows
from scripts.soul_costs import parse_require_soul


class EffectPatternAuditTests(unittest.TestCase):
    def test_multi_label_stat_and_timing_candidates(self):
        parsed = analyze("자신보다 높거나 같은 레벨을 공격시 자신의 AP+1.")
        self.assertIn("stat_ap", parsed["topic_candidates"])
        self.assertIn("on_attack", parsed["trigger_candidates"])
        self.assertIn("self", parsed["actor_candidates"])
        self.assertEqual(parsed["number_candidates"], ["+1"])

    def test_direct_hp_attack_and_dp_candidate(self):
        parsed = analyze("상대의 DP를 무시하고 HP를 직접공격한다.")
        self.assertIn("direct_hp_attack", parsed["topic_candidates"])
        self.assertIn("dp_bypass", parsed["topic_candidates"])
        self.assertIn("stat_dp", parsed["topic_candidates"])
        self.assertIn("stat_hp", parsed["topic_candidates"])

    def test_attack_defense_window_is_candidate_not_verified(self):
        parsed = analyze("발동시점 : 공격/방어. 아군 유닛 전체에게 AP+2.")
        self.assertIn("attack_or_defense_window", parsed["trigger_candidates"])
        self.assertIn("friendly", parsed["actor_candidates"])
        self.assertIn("stat_modify", parsed["operation_candidates"])
        self.assertEqual(parsed.get("verification_status"), None)

    def test_invalid_is_not_an_effect_candidate(self):
        parsed = analyze("invalid")
        self.assertEqual(parsed["topic_candidates"], ["non_effect_or_invalid"])
        self.assertEqual(parsed["number_candidates"], [])
        self.assertEqual(parsed["special_token_candidates"], [])

    def test_unclassified_remains_candidate(self):
        parsed = analyze("이 문구는 사전의 표현과 다릅니다.")
        self.assertEqual(parsed["topic_candidates"], ["unclassified_candidate"])
        self.assertEqual(parsed["source_text_class_candidate"], "effect_text_candidate")

    def test_bracket_only_flavor_is_separated_but_not_deleted(self):
        parsed = analyze("[마을 사람들은 전설을 이야기했다.]")
        self.assertEqual(parsed["source_text_class_candidate"], "flavor_only_candidate")
        self.assertEqual(parsed["topic_candidates"], ["non_effect_or_invalid"])

    def test_reference_note_is_not_auto_promoted_to_effect(self):
        parsed = analyze("▶ 해당 카드는 상점에서 판매불가입니다.")
        self.assertEqual(parsed["source_text_class_candidate"], "reference_or_rule_note_candidate")
        self.assertIn("rule_note", parsed["topic_candidates"])

    def test_destroy_trigger_candidate_is_explicit(self):
        parsed = analyze("자이언트킬링 : 자신 파괴시, 상대 유닛도 파괴.")
        self.assertIn("on_destroy_or_death", parsed["topic_candidates"])

    def test_card_reference_candidate_is_separate(self):
        parsed = analyze("상성카드 : 트라이던트")
        self.assertIn("card_reference", parsed["topic_candidates"])

    def test_clause_candidate_spans_reconstruct_source_exactly(self):
        text = "아군 AP+1.\n\n※ 적 HP-2\n다음 효과"
        clauses = split_clause_candidates(text)
        self.assertEqual("".join(item["text"] for item in clauses), text)
        for item in clauses:
            self.assertEqual(text[item["start_char"]:item["end_char"]], item["text"])
        separators = [item for item in clauses if item["segment_type"] == "separator"]
        self.assertEqual([item["text"] for item in separators], ["\n"])
        self.assertTrue(all(not item["topic_candidates"] for item in separators))

    def test_clause_candidate_spans_preserve_leading_and_trailing_whitespace(self):
        text = "\n  AP+1  \n"
        clauses = split_clause_candidates(text)
        self.assertEqual("".join(item["text"] for item in clauses), text)
        self.assertEqual(clauses[0]["segment_type"], "separator")
        self.assertEqual(text[clauses[-1]["start_char"]:clauses[-1]["end_char"]], clauses[-1]["text"])

    def test_numeric_percent_is_preserved_as_text(self):
        parsed = analyze("공격시 AP+2 및 25% 추가 피해")
        self.assertIn("stat_ap", parsed["topic_candidates"])
        self.assertIn("damage", parsed["topic_candidates"])
        self.assertEqual(parsed["number_candidates"], ["+2", "25%"])


class CostReviewClassificationTests(unittest.TestCase):
    def row(self, **updates):
        value = {
            "card_type": "유닛",
            "soul_known": 1,
            "mapping_review": 0,
            "semantic_review": 0,
            "lp_known": 1,
        }
        value.update(updates)
        return value

    def test_hybrid_cost_is_pending_mapping_not_playable(self):
        status, dimensions = classify_cost_review(
            self.row(mapping_review=1),
            [{"symbol": "DARK_FIRE", "normalized_color": "dark+fire"}],
        )
        self.assertEqual(status, "hybrid_mapping_review_pending")
        self.assertEqual(dimensions, ["hybrid_mapping_review_pending"])

    def test_bonus_cost_is_never_labelled_flexible_neutral(self):
        status, dimensions = classify_cost_review(
            self.row(semantic_review=1),
            [{"symbol": "BONUS", "normalized_color": "bonus"}],
        )
        self.assertEqual(status, "bonus_semantics_unverified")
        self.assertEqual(dimensions, ["bonus_semantics_unverified"])

    def test_ncs_semantic_review_stays_distinct_from_bonus(self):
        status, dimensions = classify_cost_review(
            self.row(semantic_review=1),
            [{"symbol": "NCS", "normalized_color": "ncs"}],
        )
        self.assertEqual(status, "ncs_semantics_unverified")
        self.assertEqual(dimensions, ["ncs_semantics_unverified"])

    def test_unidentified_semantic_review_is_not_guessed(self):
        status, dimensions = classify_cost_review(
            self.row(semantic_review=1), []
        )
        self.assertEqual(status, "semantic_review_unclassified")
        self.assertEqual(dimensions, ["semantic_review_unclassified"])

    def test_source_unknown_cost_is_separate_from_semantic_review(self):
        status, dimensions = classify_cost_review(
            self.row(soul_known=0), []
        )
        self.assertEqual(status, "source_cost_unresolved")
        self.assertEqual(dimensions, ["source_cost_unresolved"])

    def test_land_lp_review_is_reported_separately(self):
        status, dimensions = classify_cost_review(
            self.row(card_type="지형", lp_known=0), []
        )
        self.assertEqual(status, "land_lp_unresolved")
        self.assertEqual(dimensions, ["land_lp_unresolved"])

    def test_multiple_review_dimensions_are_preserved(self):
        status, dimensions = classify_cost_review(
            self.row(mapping_review=1, semantic_review=1),
            [{"symbol": "BONUS", "normalized_color": "bonus"}],
        )
        self.assertEqual(status, "multiple_review_dimensions")
        self.assertEqual(
            dimensions,
            ["hybrid_mapping_review_pending", "bonus_semantics_unverified"],
        )

    def test_verified_cost_has_no_pending_dimensions(self):
        status, dimensions = classify_cost_review(self.row(), [])
        self.assertEqual(status, "verified")
        self.assertEqual(dimensions, [])


class SoulCostParserReviewTests(unittest.TestCase):
    def test_ncs_is_separate_and_remains_semantic_review(self):
        parsed = parse_require_soul("8201")
        self.assertTrue(parsed["known"])
        self.assertEqual(parsed["colors"]["ncs"], 1)
        self.assertEqual(parsed["colors"]["bonus"], 0)
        self.assertEqual(parsed["colors"]["neutral"], 0)
        self.assertTrue(parsed["semantic_review"])
        self.assertEqual(parsed["tokens"][0]["status"], "semantic_review")
        self.assertEqual(parsed["tokens"][0]["inference"], "ncs_requiresoul_semantics_unverified")

    def test_bonus_is_separate_and_remains_semantic_review(self):
        parsed = parse_require_soul("8301")
        self.assertTrue(parsed["known"], "token parsing is distinct from playable-cost approval")
        self.assertEqual(parsed["colors"]["bonus"], 1)
        self.assertEqual(parsed["colors"]["ncs"], 0)
        self.assertEqual(parsed["colors"]["neutral"], 0)
        self.assertTrue(parsed["semantic_review"])
        self.assertEqual(parsed["tokens"][0]["status"], "semantic_review")
        self.assertEqual(parsed["tokens"][0]["inference"], "bonus_semantics_unverified")

    def test_hybrid_token_preserves_component_candidates_without_costing_both_colors(self):
        parsed = parse_require_soul("1301")
        self.assertTrue(parsed["known"], "token parsing is distinct from playable-cost approval")
        self.assertEqual(parsed["colors"]["dark"], 0)
        self.assertEqual(parsed["colors"]["fire"], 0)
        self.assertEqual(parsed["tokens"][0]["components"], ["dark", "fire"])
        self.assertTrue(parsed["mapping_review"])
        self.assertFalse(parsed["semantic_review"])
        self.assertEqual(parsed["tokens"][0]["status"], "hybrid_payment_unverified")


class CostTokenReviewQueueTests(unittest.TestCase):
    def test_expands_each_token_occurrence_without_collapsing_card_identity(self):
        card = {
            "card_id": "CARD-HYBRID-01",
            "name": "Hybrid Example",
            "card_type": "유닛",
            "source_text": "1302",
            "soul_known": 1,
            "mapping_review": 1,
            "semantic_review": 0,
            "lp_known": 1,
        }
        tokens = [
            {"ordinal": 0, "raw_token": "1302", "code": 13, "count": 2,
             "symbol": "DARK_FIRE", "normalized_color": "dark+fire", "parse_status": "inferred"},
            {"ordinal": 1, "raw_token": "5101", "code": 51, "count": 1,
             "symbol": "IRON", "normalized_color": "iron", "parse_status": "enum_decoded"},
        ]
        rows = expand_cost_token_review_rows([card], {card["card_id"]: tokens})
        self.assertEqual(len(rows), 2)
        self.assertEqual([row["ordinal"] for row in rows], [0, 1])
        self.assertTrue(all(row["card_id"] == "CARD-HYBRID-01" for row in rows))
        self.assertTrue(all(row["review_status"] == "hybrid_mapping_review_pending" for row in rows))
        self.assertTrue(all(row["review_dimensions"] == ["hybrid_mapping_review_pending"] for row in rows))
        self.assertEqual(rows[0]["raw_token"], "1302")
        self.assertEqual(rows[1]["raw_token"], "5101")
        self.assertEqual(rows[0]["token_review_relevance"], "direct_token_evidence")
        self.assertEqual(rows[0]["token_dimensions"], ["hybrid_mapping_review_pending"])
        self.assertEqual(rows[1]["token_review_relevance"], "context_only")
        self.assertEqual(rows[1]["token_dimensions"], [])

    def test_preserves_card_review_when_token_evidence_is_missing(self):
        card = {
            "card_id": "CARD-NO-TOKEN",
            "name": "Missing Evidence",
            "card_type": "유닛",
            "source_text": "UNKNOWN",
            "soul_known": 0,
            "mapping_review": 0,
            "semantic_review": 0,
            "lp_known": 1,
        }
        rows = expand_cost_token_review_rows([card], {})
        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["review_scope"], "card_without_token_evidence")
        self.assertEqual(rows[0]["review_status"], "source_cost_unresolved")
        self.assertIsNone(rows[0]["ordinal"])
        self.assertEqual(rows[0]["source_text"], "UNKNOWN")

    def test_bonus_and_ncs_occurrences_remain_separately_identified(self):
        card = {
            "card_id": "CARD-SPECIAL",
            "name": "Special Soul",
            "card_type": "유닛",
            "source_text": "8201;8301",
            "soul_known": 1,
            "mapping_review": 0,
            "semantic_review": 1,
            "lp_known": 1,
        }
        tokens = [
            {"ordinal": 0, "raw_token": "8201", "code": 82, "count": 1,
             "symbol": "NCS", "normalized_color": "ncs", "parse_status": "manual_semantics_verified"},
            {"ordinal": 1, "raw_token": "8301", "code": 83, "count": 1,
             "symbol": "BONUS", "normalized_color": "bonus", "parse_status": "semantic_review"},
        ]
        rows = expand_cost_token_review_rows([card], {card["card_id"]: tokens})
        self.assertEqual([row["symbol"] for row in rows], ["NCS", "BONUS"])
        self.assertTrue(all(row["review_status"] == "multiple_review_dimensions" for row in rows))
        self.assertEqual(
            rows[0]["review_dimensions"],
            ["bonus_semantics_unverified", "ncs_semantics_unverified"],
        )
        self.assertEqual([row["ordinal"] for row in rows], [0, 1])
        self.assertEqual(rows[0]["token_review_relevance"], "direct_token_evidence")
        self.assertEqual(rows[0]["token_dimensions"], ["ncs_semantics_unverified"])
        self.assertEqual(rows[1]["token_review_relevance"], "direct_token_evidence")
        self.assertEqual(rows[1]["token_dimensions"], ["bonus_semantics_unverified"])

    def test_jsonl_queue_writes_one_parseable_record_per_line(self):
        rows = [
            {"card_id": "CARD-1", "symbol": "NCS"},
            {"card_id": "CARD-2", "symbol": "BONUS"},
        ]
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "queue.jsonl"
            write_jsonl_rows(path, rows)
            lines = path.read_text(encoding="utf-8").splitlines()
        self.assertEqual(len(lines), 2)
        self.assertEqual([json.loads(line) for line in lines], rows)


if __name__ == "__main__":
    unittest.main()
