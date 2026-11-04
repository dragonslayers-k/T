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


    def test_audit_432_unparsed_notes_are_reclassified_without_execution(self):
        cases = [
            ("※", "source_marker_only"),
            ("--------------------------------------------------------------------", "source_separator"),
            ("기가스XG는 종족 소속이 없고 4글자 이름의 유닛입니다.", "reference_or_metadata"),
            ("디멘션트리거는 1레벨 ~ 10레벨까지 랜덤한 레벨로 덱에 구성됩니다.", "reference_or_metadata"),
            ("상점에서 %샌드웜% 로 검색하시면 해당 카드를 확인할 수 있습니다.", "reference_or_metadata"),
            ("나눈 값의 나머지는 내림합니다.", "calculation_or_counting_rule_candidate"),
            ("일반 지형카드의 레벨은 1로 체크합니다.", "calculation_or_counting_rule_candidate"),
            ("아군 필드 마법은 소드그로잉 마법을 포함한 카드 레벨 합입니다.", "calculation_or_counting_rule_candidate"),
            ("마법 발동 실패시 후속 효과도 발동 되지 않습니다.", "target_or_resolution_rule_candidate"),
            ("적군 전체를 대상으로 하는 마법입니다.", "target_or_resolution_rule_candidate"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                self.assertEqual(result["classification"], expected)
                self.assertTrue(result["operations"])
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))


    def test_audit_435_counting_conditions_and_ability_labels(self):
        cases = [
            ("※ 동일 수에서 자신은 제외됩니다.", "counting_or_scope_rule_candidate"),
            ("※ 듀얼 카드 카운트에서 지형은 제외됩니다.(같이 발매된 다른 마법과 동일)", "counting_or_scope_rule_candidate"),
            ("▶ 지형은 1레벨로 계산", "counting_or_scope_rule_candidate"),
            ("▶ 가장 많은 속성의 카드수가 동일할 경우에는 효과가 없습니다.", "effect_activation_requirement"),
            ("▶ 1번 슬롯의 맨 위 인첸트가 대지 인첸트여야 합니다.", "effect_activation_requirement"),
            ("▶ 적 필드 카드가 2이상 이여야 발동", "effect_activation_requirement"),
            ("수호일격 공격기술 (기술방어보다 먼저발동)", "named_ability_reference_candidate"),
            ("(캐리온크로우, 패러키트, 스패로우, 만다린덕, 크레인, 데저트이글, 펠리컨).", "card_reference_list"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                self.assertEqual(result["classification"], expected)
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))

    def test_audit_435_legacy_action_verbs_are_non_executable_candidates(self):
        cases = [
            "슬롯 유닛에게 숲의보호 기술을 투여한다.",
            "적군 유닛1을 상대방 덱 위로 올린다.",
            "아군 유닛 전체는 장비능력으로 변한다.",
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                self.assertEqual(result["classification"], "effect_candidate")
                self.assertTrue(any(op.get("kind") in {
                    "generic_effect_operation",
                    "legacy_skill_grant_or_reference_candidate",
                    "legacy_card_movement_candidate",
                    "legacy_card_or_ability_transform_candidate",
                } for op in result["operations"]))
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))

    def test_audit_435_actual_legacy_effect_sentences_are_structured(self):
        cases = [
            ("아군 전체 유니트의 AP/DP/HP 를 +1 한다.", "legacy_combat_stat_operation_candidate"),
            ("적군 유닛1을 상대방 덱 위로 올린다.", "legacy_card_movement_candidate"),
            ("슬롯 유닛에게 숲의보호 기술을 투여한다.", "legacy_skill_grant_or_reference_candidate"),
            ("아군 유닛 전체는 장비능력으로 변한다.", "legacy_card_or_ability_transform_candidate"),
            ("아군 유닛 1의 킬수가 아군의 LP가 된 후 킬수=0", "generic_effect_operation"),
            ("적군 필드 유닛 전체의 AP를 0으로 만든다.", "legacy_combat_stat_operation_candidate"),
        ]
        for raw, expected_kind in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                kinds = {op.get("kind") for op in result["operations"]}
                self.assertIn(expected_kind, kinds)
                self.assertEqual(result["classification"], "effect_candidate")
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))

    def test_audit_435_passive_effect_predicates_are_structured(self):
        cases = [
            ("아군 짝수번째 유닛과 적군 홀수번째 유닛은 행동 불능이 된다.", "legacy_status_application_candidate"),
            ("아군 유닛 1의 킬수가 아군의 LP가 된 후 킬수=0", "legacy_counter_to_resource_conversion_candidate"),
            ("아군 필드 마법 유닛 수 만큼 적군 핸드 유닛에게 저주과 착용한다.", "legacy_card_movement_candidate"),
        ]
        for raw, expected_kind in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                kinds = {op.get("kind") for op in result["operations"]}
                self.assertIn(expected_kind, kinds)
                self.assertEqual(result["classification"], "effect_candidate")
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))

    def test_audit_435_ability_and_card_lists_are_not_unparsed_effects(self):
        cases = [
            ("수호일격 공격기술 (기술방어보다 먼저발동)", "named_ability_reference_candidate"),
            ("돌진공격/네이밍디펜스", "named_ability_reference_candidate"),
            ("(캐리온크로우, 패러키트, 스패로우, 만다린덕).", "card_reference_list"),
            ("무-마안석", "card_reference_list"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                self.assertEqual(result["classification"], expected)
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))


    def test_audit_437_remaining_effect_examples_get_candidate_operations(self):
        cases = [
            "적군 장비/야수 중 HP가 AP보다 높은 유닛 1을 핸드로 보낸다.",
            "아군 적군 장비 유닛에게 저주과를 착용시킨다.",
            "적군의 1번 유니트를 맨 뒷자리로 보낸다.",
            "아군 유닛 전체는 장비능력으로 변한다.",
        ]
        for raw in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                self.assertEqual(result["classification"], "effect_candidate")
                self.assertTrue(result["operations"])
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))


    def test_audit_444_card_local_annotations_are_structured_candidates(self):
        cases = [
            ("발동 후 다크파워 히어로 +1", "modify_hero_power"),
            ("발동시 아군 핸드/필드가 모두 블라토브 유닛이면 마법 대상 +1.", "modify_spell_target_count"),
            ("아군필드 금속 속성 유닛 전체 공체+1. 적군필드 유닛 전체 공체-1", "modify_combat_stats"),
            ("아군 전체 HP- 전투 필드 10개의 공간 중 양쪽 모두 비어있는 공간 수.", "formula_based_stat_change"),
            ("적 필드 카드 1의 레벨에 따라 다른 효과.", "conditional_effect_branch_reference"),
        ]
        for raw, expected_kind in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                kinds = {op.get("kind") for op in result["operations"]}
                self.assertIn(expected_kind, kinds)
                self.assertEqual(result["classification"], "effect_candidate")
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))


    def test_audit_446_remaining_effect_relations_and_conditions(self):
        cases = [
            ("레벨3 이하 아군 장비, 마법 전체는 순화능력을 갖는다.", "grant_named_ability_candidate"),
            ("아군 필드 유닛 1이 마법 유닛이면 적 필드 유닛 1의 능력에 따라 효과 발생", "conditional_effect_branch_reference"),
            ("즉, 적 필드에 암흑속성카드 2장, 불속성카드 2장이 있을 경우에는 아무 효과가 없습니다.", "suppress_effect_under_condition"),
            ("체인라이트닝 - 체인라이트닝 - 라이트닝볼트 순서로 필드에 나열됩니다.", "card_progression_reference"),
            ("피닉스의알 : 피닉스. / 티라노의알 : 티라노.", "related_card_pair_reference"),
            ("아이템/인첸트 : 소드맨 1장, 포위공격 1장.", "card_requirement_reference"),
            ("야누스가면(만능능력)○ : 야누스, 0/*/0", "named_ability_stat_reference"),
            ("얼음꽃 : +2 / ▲2 / 0", "set_combat_stats_vector"),
        ]
        for raw, expected_kind in cases:
            with self.subTest(raw=raw):
                result = parse(raw)
                kinds = {op.get("kind") for op in result["operations"]}
                self.assertIn(expected_kind, kinds)
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))


    def test_audit_454_remaining_card_local_notes_are_dispositioned_without_execution(self):
        cases = [
            ('"기가스XG"는 울티밋퓨전 마법을 사용하여 확보할 수 있습니다.', "acquisition_method_reference"),
            ("cwda!", "source_annotation_pending"),
            ("다크마레아(3카운터)", "named_area_counter_reference_candidate"),
            ("디스인첸트 카드 [모래 마법의 장막.]", "named_effect_reference_candidate"),
            ("디스인첸트 카드. [그리핀과의 사투.]", "named_effect_reference_candidate"),
            ("롯트, 장생수, 맨이터롯트N, 이모탈트리, 손드트리, 뮤턴트엔트, 에인션트엔트.", "card_reference_list"),
            ("모래형상 유닛(야수, 골렘, 돌진공격).", "named_summon_unit_profile_reference"),
            ("AP1이상으로 공격시, 상대 유닛이 장비/야수면 3턴간", "effect_condition_continuation_candidate"),
            ("발동시 이름종류수에 따라 특 별 효과가 발동한다(특이사항)", "conditional_effect_branch_reference"),
            ("블레이즈스탭, 정령의화염, 퓨리라이드, 화염의용술사, 버닝래빗, 불새의둥지, 불의노래, 퓨리파이어샷 (2015.5.6 발매기준)", "historical_release_cohort_metadata"),
            ("상", "incomplete_source_fragment"),
            ("실패시.", "conditional_branch_reference"),
            ("에네퍼브렌C", "named_card_variant_reference"),
            ("워터마레마(3카운터)", "named_area_counter_reference_candidate"),
            ("조건에 따른 이서리얼의 능력.", "conditional_unit_profile_reference"),
            ("해당카드는 하급, 중급 등 에카마엘 상태를 보유하지 않고 있습니다.★★★", "card_state_exclusion_metadata"),
        ]
        for raw, expected in cases:
            with self.subTest(raw=raw):
                result = parse(raw, known_cards={"에네퍼브렌":["14022627282"]})
                self.assertEqual(result["classification"], expected)
                self.assertTrue(result["operations"])
                self.assertFalse(any(op.get("executable") is True for op in result["operations"]))

    def test_audit_454_named_area_counter_retains_counter_and_name(self):
        result=parse("포레스마레마(3카운터)")
        op=result["operations"][0]
        self.assertEqual(op["areaName"],"포레스마레마")
        self.assertEqual(op["counterCount"],3)

    def test_audit_454_split_attack_condition_keeps_actor_target_and_duration(self):
        result=parse("AP1이상으로 공격시, 상대 유닛이 장비/야수면 3턴간")
        op=result["operations"][0]
        self.assertEqual(result["triggers"],["on_attack"])
        self.assertEqual(op["minimumAttackStat"],1)
        self.assertEqual(op["targetTypeAnyOf"],["장비","야수"])
        self.assertEqual(op["durationTurns"],3)

    def test_audit_454_release_cohort_parses_as_metadata_not_effect(self):
        result=parse("블레이즈스탭, 정령의화염, 퓨리라이드, 화염의용술사, 버닝래빗, 불새의둥지, 불의노래, 퓨리파이어샷 (2015.5.6 발매기준)")
        op=result["operations"][0]
        self.assertEqual(op["asOfDate"],"2015-5-6")
        self.assertEqual(len(op["cardNames"]),8)
        self.assertEqual(result["confidence"],"not_applicable")

    def test_audit_454_variant_reference_requires_known_base_card(self):
        without_base=parse("에네퍼브렌C")
        with_base=parse("에네퍼브렌C",known_cards={"에네퍼브렌":["14022627282"]})
        self.assertNotEqual(without_base["classification"],"named_card_variant_reference")
        self.assertEqual(with_base["classification"],"named_card_variant_reference")


if __name__ == "__main__":
    unittest.main()
