import unittest
from scripts.infer_unmapped_skills import extract_definitions, operations_from_text
from scripts.infer_effect_interpretations import parse

class SkillExtractionTests(unittest.TestCase):
    def test_split_skill_heading_and_body(self):
        text="각인의결계\n\n: 방어시 상대 유닛 AP/DP/HP 중 가장 높은 수치를 영구히 3 감소시킨다."
        rows=extract_definitions("각인의결계",text)
        self.assertTrue(rows)
        self.assertIn("가장 높은 수치",rows[0]["body"])
    def test_alias_with_next_line_body(self):
        text="구원자의인장\n\n자신 파괴시 아군 핸드필드 유닛 전체 공방체 +1"
        rows=extract_definitions("구원자의인정",text)
        self.assertTrue(rows)
        self.assertIn("공방체 +1",rows[0]["body"])
    def test_coin_operation_retains_formula(self):
        ops=operations_from_text("공격시 적 유닛의 체력 코인을 -C5로 영구 변경한다.")
        self.assertTrue(any(x["kind"]=="modify_coin" for x in ops))

class EffectInterpretationTests(unittest.TestCase):
    def test_grouped_stats(self):
        result=parse("아군 필드 유닛 전체의 공방체를 영구히 1 증가시킨다.")
        self.assertEqual(result["confidence"],"medium")
        self.assertTrue(any(x["kind"]=="modify_combat_stats" for x in result["operations"]))
    def test_coin_effect(self):
        result=parse("공격시 아군 유닛의 +코인 수치를 1 증가시킨다.")
        self.assertTrue(any(x["kind"]=="modify_coin" for x in result["operations"]))
    def test_transform_effect(self):
        result=parse("3턴마다 다음 단계 유닛으로 성장한다.")
        self.assertTrue(any(x["kind"]=="transform_or_move_card" for x in result["operations"]))
    def test_metadata_classification(self):
        result=parse("1차 강화 유닛 특징")
        self.assertEqual(result["classification"],"reference_or_metadata")
        self.assertEqual(result["confidence"],"not_applicable")
    def test_catalogue_reference(self):
        result=parse("기선제압",{"기선제압":"skill_first_strike"})
        self.assertEqual(result["classification"],"ability_name_reference")
        self.assertEqual(result["operations"][0]["ruleId"],"skill_first_strike")

if __name__=="__main__":
    unittest.main()
