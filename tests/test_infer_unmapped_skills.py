import unittest

from scripts.infer_unmapped_skills import card_specific_evidence, extract_definitions, operations_from_text
from scripts.import_community_skill_reference import merge_evidence_references


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

    def test_card_specific_evidence_never_leaks_sibling_card_excerpts(self):
        refs = [
            {"cardId":"card-a","url":"https://example.test/a","effectText":"A rule"},
            {"cardId":"card-b","url":"https://example.test/b","effectText":"B rule"},
            {"cardId":"card-a","url":"https://example.test/a","effectText":"A variant"},
        ]
        selected = card_specific_evidence(refs,"card-a")
        self.assertEqual([x["effectText"] for x in selected],["A rule","A variant"])
        self.assertTrue(all(x["cardId"]=="card-a" for x in selected))

    def test_community_evidence_merge_preserves_card_local_provenance(self):
        existing = json.dumps([{"kind":"card_text_inference","cardId":"card-a","evidenceCount":1}])
        source = {"kind":"community_reference","url":"https://example.test/community","title":"Community"}
        merged = json.loads(merge_evidence_references(existing,source))
        self.assertEqual(len(merged),2)
        self.assertEqual(merged[0]["kind"],"card_text_inference")
        self.assertEqual(merged[1]["kind"],"community_reference")
        merged_again = json.loads(merge_evidence_references(json.dumps(merged),source))
        self.assertEqual(len(merged_again),2)

    def test_skill_grant_flavor_text_is_not_misread_as_effect_definition(self):
        rows = extract_definitions(
            "기선제압",
            "기선제압 기술부여 [비슐로의 주인이자 시대의 마왕이 지녔던 비늘이다.]"
        )
        self.assertEqual(rows, [])

    def test_real_skill_effect_with_trailing_flavor_is_preserved(self):
        rows = extract_definitions(
            "기선제압",
            "기선제압: 적군이 아군보다 이하 레벨일 경우 데미지를 1 덜 받는다. [방패의 전설]"
        )
        self.assertEqual(len(rows), 1)
        self.assertIn("데미지를 1 덜 받는다", rows[0]["body"])

    def test_stat_operations_are_structured_without_becoming_executable(self):
        ops = operations_from_text("아군 AP+2, DP-1")
        self.assertIn({"kind": "modify_stat", "stat": "ap", "operator": "+", "value": 2, "executable": False}, ops)
        self.assertIn({"kind": "modify_stat", "stat": "dp", "operator": "-", "value": 1, "executable": False}, ops)
        self.assertTrue(all(x.get("executable") is not True for x in ops))


if __name__ == "__main__":
    unittest.main()
