import unittest

from scripts.effect_pattern_audit import analyze


class EffectPatternAuditTests(unittest.TestCase):
    def test_multi_label_stat_and_timing_candidates(self):
        topics, numbers, tokens = analyze("자신보다 높거나 같은 레벨을 공격시 자신의 AP+1.")
        self.assertIn("stat_ap", topics)
        self.assertIn("timing", topics)
        self.assertEqual(numbers, ["1"])
        self.assertEqual(tokens, [])

    def test_direct_hp_attack_and_dp_candidate(self):
        topics, _, _ = analyze("상대의 DP를 무시하고 HP를 직접공격한다.")
        self.assertIn("direct_hp_attack", topics)
        self.assertIn("dp_bypass", topics)
        self.assertIn("stat_dp", topics)
        self.assertIn("stat_hp", topics)

    def test_invalid_is_not_an_effect_candidate(self):
        topics, numbers, tokens = analyze("invalid")
        self.assertEqual(topics, ["non_effect_or_invalid"])
        self.assertEqual(numbers, [])
        self.assertEqual(tokens, [])

    def test_unclassified_remains_candidate(self):
        topics, _, _ = analyze("이 문구는 사전의 표현과 다릅니다.")
        self.assertEqual(topics, ["unclassified_candidate"])

    def test_numeric_percent_is_preserved_as_text(self):
        topics, numbers, _ = analyze("공격시 AP+2 및 25% 추가 피해")
        self.assertIn("stat_ap", topics)
        self.assertIn("damage", topics)
        self.assertEqual(numbers, ["+2", "25%"])


if __name__ == "__main__":
    unittest.main()
