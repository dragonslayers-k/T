import json
import unittest

from scripts.infer_effect_interpretations import (
    extract_named_effect_definitions,
    normalize_effect_name,
    parse,
)


class NamedEffectInterpretationTests(unittest.TestCase):
    def test_extracts_marker_definitions_and_multiline_status(self):
        raw = json.dumps(
            "▶ 디스히어로 : 마법 발동 후 적의 첫 번째 히어로 능력을 제거한다.<br>"
            "★ 거대화 상태 : 레벨+3, AP×2 / HP×2<br>"
            "※ 운명의퍼즐<br>"
            "1. 상태 적용시 AP를 1 증가시킨다.<br>"
            "2. 상태 해제시 원래대로 돌아간다."
        )
        rows = extract_named_effect_definitions("c1", "테스트 유닛", raw)
        by_name = {x["effect_name"]: x for x in rows}
        self.assertEqual(set(by_name), {"디스히어로", "거대화 상태", "운명의퍼즐"})
        self.assertIn("AP×2", by_name["거대화 상태"]["definition_text"])
        self.assertIn("1. 상태 적용시", by_name["운명의퍼즐"]["definition_text"])
        self.assertEqual(by_name["디스히어로"]["verification_status"], "source_text_extracted")

    def test_named_effect_extractor_rejects_count_date_example_and_prose_labels(self):
        raw = json.dumps(
            "▶ 0개 : 효과없음<br>"
            "▶ 1장 : 카드 한 장<br>"
            "▶ 1~2 레벨 : 하급 상태<br>"
            "▶ 2014-06-19 12 : 공지사항<br>"
            "▶ EX) 아군 필드 유닛1이 빛속성이면 : 조건 예시<br>"
            "▶ 해당 유닛은 소환시 하급 상태가 부여됩니다 : 설명<br>"
            "★ 거대화 상태 : 레벨+3, AP×2 / HP×2<br>"
            "▶ 1차강화능력 : 핸드에서 소각장으로 버리면 무소울 1 생성"
        )
        rows = extract_named_effect_definitions("c2", "테스트 카드", raw)
        self.assertEqual(
            {row["effect_name"] for row in rows},
            {"거대화 상태", "1차강화능력"},
        )

    def test_low_confidence_reference_and_metadata_patterns_are_preserved(self):
        cases = [
            ("2006-09-21 리콜전 [하이딩어택] 효과입니다.", "historical_card_effect_reference"),
            ("FM 콜로세움 이벤트 특별보상 카드입니다.", "event_or_acquisition_metadata"),
            ("LP는 랜드포인트를 뜻하며, 지형을 올릴 수 있는 포인트입니다.", "card_glossary_metadata"),
            ("라(EP3)와 상성 효과", "matchup_effect_reference_candidate"),
            ("강한돌진공격", "named_ability_reference_candidate"),
            ("4~5 : 악령퇴치자A", "numeric_range_reference_candidate"),
            ("묘지가 0이면 발동안함.", "effect_activation_requirement"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(parse(raw)["classification"], expected)

    def test_unclosed_lore_fragment_is_not_a_low_confidence_effect(self):
        raw = "[자신들을 지옥의 상인이라 얘기하던 그 무리를 처음에는 우리 모두 믿지 못하였다. 그러나 그들이 건네는 무기들은 그 하나하나가 놀라운 것들뿐이었다."
        result = parse(raw)
        self.assertEqual(result["classification"], "flavor_or_lore")
        self.assertFalse(any(op.get("executable") for op in result["operations"]))

    def test_named_effect_reference_resolves_to_source_definition(self):
        definitions = {
            normalize_effect_name("디스히어로"): [
                {"definition_id": 17, "source_card_id": "c1",
                 "definition_text": "마법 발동 후 적의 첫 번째 히어로 능력을 제거한다."}
            ]
        }
        result = parse("디스히어로", known_named_effects=definitions)
        self.assertEqual(result["classification"], "named_effect_reference")
        self.assertEqual(result["operations"][0]["definitionIds"], [17])
        self.assertEqual(result["operations"][0]["definitionCardIds"], ["c1"])
        self.assertFalse(result["operations"][0]["executable"])

    def test_named_status_formula_is_structured_but_non_executable(self):
        definitions = {
            normalize_effect_name("거대화 상태"): [
                {"definition_id": 18, "source_card_id": "c2",
                 "definition_text": "레벨+3, AP×2 / HP×2"}
            ]
        }
        result = parse("거대화 상태 : 레벨+3, AP×2 / HP×2", known_named_effects=definitions)
        self.assertEqual(result["classification"], "named_status_definition")
        kinds = [x["kind"] for x in result["operations"]]
        self.assertIn("modify_level", kinds)
        self.assertEqual(kinds.count("multiply_stat"), 2)
        self.assertTrue(all(x.get("executable") is False for x in result["operations"]))

    def test_empty_and_whitespace_only_text_is_not_a_low_confidence_effect(self):
        for raw in ("", " ", chr(10), " " + chr(10) + chr(9)):
            with self.subTest(raw=raw):
                result = parse(raw)
                self.assertEqual(result["classification"], "empty_source_text")
                self.assertEqual(result["confidence"], "not_applicable")
                self.assertFalse(any(op.get("executable") for op in result["operations"]))

    def test_known_unparsed_categories_are_preserved(self):
        cases = [
            ("무속성 이벤트 마법은 이벤트 마법으로 취급됩니다.", "card_type_treatment_rule"),
            ("아군 핸드 수가 동일하면 효과없음.", "conditional_no_effect"),
            ("1~2레벨 - 머슈룸맨", "level_tier_mapping"),
            ("1장 초과로 구입하시는 경우 구입에 오류가 납니다.", "administrative_or_shop_note"),
            ("[오래된 전쟁과 영웅에 대한 이야기로 구성된 풍미 문구이며 실제 효과가 아닌 배경 설명입니다.]", "flavor_or_lore"),
            (".", "source_placeholder"),
            ("…", "punctuation_artifact"),
            ("", "empty_source_text"),
            ("\n", "empty_source_text"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                self.assertEqual(parse(raw)["classification"], expected)


if __name__ == "__main__":
    unittest.main()
