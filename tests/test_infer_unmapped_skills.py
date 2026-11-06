import unittest

from scripts.infer_unmapped_skills import extract_definitions, operations_from_text


class SkillDefinitionExtractionTests(unittest.TestCase):
    def test_inline_definition(self):
        rows = extract_definitions("후폭풍", "후폭풍: 공격받은 뒤 상대에게 피해를 돌려준다.")
        self.assertEqual(len(rows), 1)
        self.assertIn("상대에게 피해", rows[0]["body"])

    def test_split_heading_and_decorated_body(self):
        rows = extract_definitions("네이처드레인", "네이처 드레인\n▶ 물속성 유닛을 공격하면 HP를 2 회복한다.")
        self.assertEqual(len(rows), 1)
        self.assertIn("물속성 유닛", rows[0]["body"])

    def test_html_breaks_and_entities(self):
        rows = extract_definitions("각인의결계", "각인의결계<br/>아군 AP+2 &amp; DP+1")
        self.assertEqual(len(rows), 1)
        self.assertIn("아군 AP+2", rows[0]["body"])

    def test_html_breaks_separate_preceding_text_from_skill_heading(self):
        rows = extract_definitions(
            "후폭풍",
            "설명 문장<BR /><b>후폭풍</b><br/>▶ 공격받은 뒤 상대에게 피해를 돌려준다."
        )
        self.assertEqual(len(rows), 1)
        self.assertIn("피해를 돌려준다", rows[0]["body"])

    def test_stat_operations_are_structured_without_becoming_executable(self):
        ops = operations_from_text("아군 AP+2, DP-1")
        self.assertIn({"kind": "modify_stat", "stat": "ap", "operator": "+", "value": 2}, ops)
        self.assertIn({"kind": "modify_stat", "stat": "dp", "operator": "-", "value": 1}, ops)
        self.assertTrue(all(x.get("executable") is not True for x in ops))


if __name__ == "__main__":
    unittest.main()
