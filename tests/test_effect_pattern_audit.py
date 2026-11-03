import unittest

from scripts.effect_pattern_audit import analyze


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

    def test_numeric_percent_is_preserved_as_text(self):
        parsed = analyze("공격시 AP+2 및 25% 추가 피해")
        self.assertIn("stat_ap", parsed["topic_candidates"])
        self.assertIn("damage", parsed["topic_candidates"])
        self.assertEqual(parsed["number_candidates"], ["+2", "25%"])


if __name__ == "__main__":
    unittest.main()
