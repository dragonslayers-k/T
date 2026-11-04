import unittest
from scripts.infer_unmapped_skills import extract_definitions, operations_from_text
from scripts.infer_effect_interpretations import parse
from scripts.import_community_skill_reference import extract_skill_definitions
from scripts.infer_unmapped_skills import infer_one
import sqlite3, json, tempfile
from pathlib import Path

class EffectReviewQueueTests(unittest.TestCase):
    def test_duplicate_low_confidence_text_is_grouped_with_all_card_sources(self):
        from scripts.build_gap_reports import build_effect_review_queue
        rows = [
            {"card_id":"c1","name":"카드A","card_type":"마법","clause_index":0,
             "segment_text":"▶ 조건에 따라 발동.\n",
             "source_detail_url":"https://example.test/c1",
             "interpretation_json":json.dumps({"classification":"effect_activation_requirement","confidence":"low","inferenceMethod":"test"})},
            {"card_id":"c2","name":"카드B","card_type":"마법","clause_index":1,
             "segment_text":"조건에 따라 발동.",
             "source_detail_url":"https://example.test/c2",
             "interpretation_json":json.dumps({"classification":"effect_activation_requirement","confidence":"low","inferenceMethod":"test"})}
        ]
        queue = build_effect_review_queue(rows)
        self.assertEqual(len(queue), 1)
        self.assertEqual(queue[0]["occurrences"], 2)
        self.assertEqual({x["card_id"] for x in queue[0]["cards"]}, {"c1","c2"})
        # Grouping must not erase the original per-card wording or source URLs.
        self.assertEqual(
            set(queue[0]["source_text_variants"]),
            {"▶ 조건에 따라 발동.", "조건에 따라 발동."},
        )
        self.assertEqual(
            {x["url"] for x in queue[0]["cards"]},
            {"https://example.test/c1", "https://example.test/c2"},
        )
        self.assertEqual(queue[0]["review_status"], "pending_manual_semantic_review")
        self.assertEqual(queue[0]["classification_variants"], ["effect_activation_requirement"])
        self.assertFalse(queue[0]["classification_conflict"])
        self.assertFalse(queue[0]["confidence_conflict"])

    def test_review_queue_keeps_each_cards_raw_textbase_and_textextra_context(self):
        from scripts.build_gap_reports import build_effect_review_queue
        rows = [
            {"card_id":"c1","name":"카드A","card_type":"마법","clause_index":0,
             "segment_text":"효과 조각","source_detail_url":"https://example.test/c1",
             "interpretation_json":json.dumps({"classification":"effect_candidate","confidence":"low"})},
            {"card_id":"c2","name":"카드B","card_type":"유닛","clause_index":1,
             "segment_text":"효과 조각","source_detail_url":"https://example.test/c2",
             "interpretation_json":json.dumps({"classification":"effect_candidate","confidence":"low"})}
        ]
        source_context = {
            "c1": {
                "source_card_url":"https://example.test/c1",
                "TextBase":{"source_key_present":True,"source_value":"  원문 TextBase A\n"},
                "TextExtra":{"source_key_present":True,"source_value":"원문 TextExtra A"}
            },
            "c2": {
                "source_card_url":"https://example.test/c2",
                "TextBase":{"source_key_present":True,"source_value":""},
                "TextExtra":{"source_key_present":False,"source_value":None}
            }
        }
        queue = build_effect_review_queue(rows, source_context)
        self.assertEqual(len(queue), 1)
        by_id = {row["card_id"]:row for row in queue[0]["cards"]}
        self.assertEqual(by_id["c1"]["source_text_fields"]["TextBase"]["source_value"], "  원문 TextBase A\n")
        self.assertEqual(by_id["c1"]["source_text_fields"]["TextExtra"]["source_value"], "원문 TextExtra A")
        self.assertTrue(by_id["c2"]["source_text_fields"]["TextBase"]["source_key_present"])
        self.assertEqual(by_id["c2"]["source_text_fields"]["TextBase"]["source_value"], "")
        self.assertFalse(by_id["c2"]["source_text_fields"]["TextExtra"]["source_key_present"])
        self.assertEqual(by_id["c2"]["source_text_fields"]["TextExtra"]["source_value"], None)
        self.assertEqual(by_id["c2"]["source_card_url"], "https://example.test/c2")

    def test_same_text_keeps_conflicting_interpretation_variants_visible(self):
        from scripts.build_gap_reports import build_effect_review_queue
        rows = [
            {"card_id":"c1","name":"카드A","card_type":"마법","clause_index":0,
             "segment_text":"효과 문구",
             "interpretation_json":json.dumps({"classification":"effect_operation","confidence":"medium"})},
            {"card_id":"c2","name":"카드B","card_type":"마법","clause_index":1,
             "segment_text":"효과 문구",
             "interpretation_json":json.dumps({"classification":"effect_activation_requirement","confidence":"low"})}
        ]
        queue = build_effect_review_queue(rows)
        self.assertEqual(len(queue), 1)
        self.assertEqual(set(queue[0]["classification_variants"]),
                         {"effect_operation","effect_activation_requirement"})
        self.assertEqual(set(queue[0]["confidence_variants"]), {"medium","low"})
        self.assertTrue(queue[0]["classification_conflict"])
        self.assertTrue(queue[0]["confidence_conflict"])
        self.assertEqual(queue[0]["classification"], "mixed")
        self.assertEqual(queue[0]["confidence"], "low")


class EffectReviewOnlyReportTests(unittest.TestCase):
    def test_effects_only_report_exports_raw_card_text_context_without_full_audit(self):
        from scripts.build_gap_reports import build_effect_review_report
        with tempfile.TemporaryDirectory() as temp_dir:
            root=Path(temp_dir)
            db_path=root/"review.sqlite"
            out_dir=root/"report"
            db=sqlite3.connect(db_path)
            db.executescript("""
            CREATE TABLE cards(
              card_id TEXT PRIMARY KEY,name TEXT,card_type TEXT,source_card_url TEXT,raw_payload_json TEXT
            );
            CREATE TABLE card_effect_clauses(
              clause_id INTEGER PRIMARY KEY,card_id TEXT,clause_index INTEGER,segment_text TEXT
            );
            CREATE TABLE card_effect_interpretations(
              clause_id INTEGER PRIMARY KEY,card_id TEXT,source_detail_url TEXT,
              interpretation_json TEXT,verification_status TEXT,confidence TEXT
            );
            """)
            payload={"TextBase":"원문 TextBase\n그대로","TextExtra":""}
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",(
                "c1","테스트카드","마법","https://fmlunatic.com/card/c1",
                json.dumps(payload,ensure_ascii=False)
            ))
            db.execute("INSERT INTO card_effect_clauses VALUES(1,'c1',0,'저신뢰 효과 조각')")
            db.execute("INSERT INTO card_effect_interpretations VALUES(1,'c1',?,?,?,?)",(
                "https://fmlunatic.com/card/c1",
                json.dumps({"classification":"unparsed_effect_text","confidence":"low","semantic_review_status":"pending"},ensure_ascii=False),
                "inferred","low"
            ))
            db.commit()
            db.close()
            summary=build_effect_review_report(db_path,out_dir)
            queue=[json.loads(line) for line in (out_dir/"effect-review-queue.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(summary["low_confidence_rows"],1)
            self.assertEqual(summary["unique_text_patterns"],1)
            self.assertEqual(summary["semantic_review_pending_rows"],1)
            self.assertEqual(summary["semantic_review_pending_patterns"],1)
            pending_queue=[json.loads(line) for line in (out_dir/"semantic-review-pending-queue.jsonl").read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(pending_queue),1)
            pending_card=pending_queue[0]["cards"][0]
            self.assertEqual(pending_card["source_text_fields"]["TextBase"]["source_value"],"원문 TextBase\n그대로")
            self.assertEqual(len(queue),1)
            card=queue[0]["cards"][0]
            self.assertEqual(card["source_text_fields"]["TextBase"]["source_value"],"원문 TextBase\n그대로")
            self.assertTrue(card["source_text_fields"]["TextBase"]["source_key_present"])
            self.assertTrue(card["source_text_fields"]["TextExtra"]["source_key_present"])
            self.assertEqual(card["source_text_fields"]["TextExtra"]["source_value"],"")
            self.assertEqual(card["source_card_url"],"https://fmlunatic.com/card/c1")
            self.assertFalse((out_dir/"gap-report-summary.json").exists())
class SoulCostGapStatusTests(unittest.TestCase):
    def test_hybrid_and_special_review_reasons_are_both_preserved(self):
        from scripts.build_gap_reports import cost_interpretation_status
        self.assertEqual(
            cost_interpretation_status(1, 1),
            "hybrid_and_special_identity_preserved_pending_rule",
        )

    def test_individual_review_statuses_remain_distinct(self):
        from scripts.build_gap_reports import cost_interpretation_status
        self.assertEqual(cost_interpretation_status(1, 0), "hybrid_identity_preserved_pending_rule")
        self.assertEqual(cost_interpretation_status(0, 1), "special_identity_preserved_pending_rule")
        self.assertEqual(cost_interpretation_status(0, 0), "unresolved")


class EffectGapRegressionTests(unittest.TestCase):
    def test_status_condition_target_note_is_not_unparsed_effect(self):
        parsed = parse("▶ 에카마엘상태의 조건 대상이 됩니다.")
        self.assertEqual(parsed["classification"], "state_condition_target_reference")
        self.assertEqual(parsed["confidence"], "medium")
        self.assertTrue(all(op.get("executable") is False for op in parsed["operations"]))

    def test_episode_scope_note_is_metadata(self):
        parsed = parse("※ 농민은 에피소드 농민만 해당됩니다.(어드벤스 신규발매 농민N은 포함되지 않습니다.)")
        self.assertEqual(parsed["classification"], "reference_or_metadata")
        self.assertEqual(parsed["confidence"], "not_applicable")

    def test_decorated_unit_list_heading_is_not_unparsed(self):
        parsed = parse("▶ 유닛 목록.")
        self.assertEqual(parsed["classification"], "section_heading")

    def test_activation_only_clause_is_structured_as_a_gate(self):
        parsed = parse("▶ 필드 유닛이 2장 이상일 경우에는 1,2 모두 불속성이여야 발동.")
        self.assertEqual(parsed["classification"], "effect_activation_requirement")
        self.assertTrue(all(op.get("executable") is False for op in parsed["operations"]))

    def test_dishero_label_is_reference_metadata(self):
        parsed = parse("◇ 디스히어로 카드")
        self.assertEqual(parsed["classification"], "reference_or_metadata")
        self.assertEqual(parsed["confidence"], "not_applicable")

    def test_event_acquisition_note_is_metadata(self):
        parsed = parse("밀짚모자 카드는 09 SUMMER BIG EVENT 를 통해 얻으실 수 있는 이벤트 카드 입니다.")
        self.assertEqual(parsed["classification"], "reference_or_metadata")

    def test_legacy_three_stat_vector_is_structured_but_non_executable(self):
        parsed = parse("AP3 이하 적군 유니트는 =0/-2/0")
        op = next(x for x in parsed["operations"] if x["kind"] == "set_combat_stats_vector")
        self.assertEqual(op["values"], ["=0", "-2", "0"])
        self.assertFalse(op["executable"])

    def test_catalogue_item_stat_vector_is_not_executable_effect(self):
        parsed = parse("★ 체인플레이트 ●●○○, +1 / +2 / +1")
        self.assertTrue(any(x["kind"] == "combat_stat_vector_reference" for x in parsed["operations"]))
        self.assertFalse(any(x.get("executable") is True for x in parsed["operations"]))

    def test_defense_convert_positive_negative_dp_marks_are_structured(self):
        parsed = parse("방어변환 : AP 1 이상 공격시, 상대를 공격한 후 상대의 DP 양수,음수기호를 변환시킨다.")
        self.assertEqual(parsed["confidence"], "medium")
        self.assertTrue(any(
            op.get("kind") == "modify_stat_marks" and op.get("stat") == "dp"
            and op.get("operation") == "reverse_sign" and op.get("executable") is False
            for op in parsed["operations"]
        ))


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
    def test_inferred_operations_are_never_executable_before_rule_validation(self):
        ops = operations_from_text("공격시 적 유닛 AP-2, HP+1 및 코인 -C5로 변경한다.")
        self.assertTrue(ops)
        self.assertTrue(all(op.get("executable") is False for op in ops))

    def test_coin_operation_retains_formula(self):
        ops=operations_from_text("공격시 적 유닛의 체력 코인을 -C5로 영구 변경한다.")
        self.assertTrue(any(x["kind"]=="modify_coin" for x in ops))


    def test_unmapped_skill_rule_is_inserted_and_attached_to_cards(self):
        db=sqlite3.connect(":memory:")
        db.executescript("""
        CREATE TABLE cards(card_id TEXT PRIMARY KEY,name TEXT,source_card_url TEXT);
        CREATE TABLE card_texts(text_id INTEGER PRIMARY KEY,card_id TEXT,text_type TEXT,plain_text TEXT,source_text TEXT);
        CREATE TABLE card_rule_mappings(
          card_id TEXT,source_field TEXT,source_enum_value TEXT,source_name TEXT,rule_id TEXT,
          mapping_status TEXT,confidence TEXT,evidence_references_json TEXT,
          PRIMARY KEY(card_id,source_field));
        CREATE TABLE skill_enum_inventory(
          source_field TEXT,source_enum_value TEXT,source_name TEXT,card_count INTEGER,
          mapped_card_count INTEGER,manual_verified_card_count INTEGER,
          community_candidate_card_count INTEGER,mapping_status TEXT,rule_id TEXT,
          PRIMARY KEY(source_field,source_enum_value,source_name));
        CREATE TABLE game_rule_catalog(
          rule_id TEXT PRIMARY KEY,rule_family TEXT NOT NULL,canonical_name TEXT NOT NULL,
          aliases_json TEXT NOT NULL,definition_json TEXT NOT NULL,source_authority TEXT NOT NULL,
          confidence TEXT NOT NULL,verification_status TEXT NOT NULL,implementation_status TEXT NOT NULL,
          source_references_json TEXT NOT NULL,source_conflicts_json TEXT NOT NULL,
          playable_by_default INTEGER NOT NULL DEFAULT 0,catalogue_version INTEGER NOT NULL);
        INSERT INTO cards VALUES('c1','테스트1','https://fmlunatic.com/card/c1');
        INSERT INTO cards VALUES('c2','테스트2','https://fmlunatic.com/card/c2');
        INSERT INTO card_texts VALUES(1,'c1','card_text','각인의결계' || char(10) || char(10) || ': 방어시 AP/DP/HP 중 가장 높은 수치를 영구히 3 감소시킨다.','');
        INSERT INTO card_texts VALUES(2,'c2','card_text','각인의결계' || char(10) || char(10) || ': 방어시 AP/DP/HP 중 가장 높은 수치를 영구히 3 감소시킨다.','');
        INSERT INTO card_rule_mappings VALUES('c1','Skill1','500','각인의결계',NULL,'unmapped','unreviewed','[]');
        INSERT INTO card_rule_mappings VALUES('c2','Skill1','500','각인의결계',NULL,'unmapped','unreviewed','[]');
        INSERT INTO skill_enum_inventory VALUES('Skill1','500','각인의결계',2,0,0,0,'unmapped',NULL);
        """)
        result=infer_one(db,"Skill1","500","각인의결계",2)
        self.assertEqual(result["mappedCardRows"],2)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM game_rule_catalog").fetchone()[0],1)
        self.assertEqual(db.execute("SELECT COUNT(*) FROM card_rule_mappings WHERE mapping_status='inferred' AND rule_id IS NOT NULL").fetchone()[0],2)
        self.assertEqual(db.execute("SELECT mapping_status FROM skill_enum_inventory").fetchone()[0],"inferred")
        definition=json.loads(db.execute("SELECT definition_json FROM game_rule_catalog").fetchone()[0])
        self.assertIn("가장 높은 수치",definition["rawEffectText"])
        db.close()

class CommunityReferenceTests(unittest.TestCase):
    def test_split_line_community_skill_heading(self):
        page="\n".join(["각인의결계", "", ": 방어시 상대 유닛 AP/DP/HP 중 가장 높은 수치를 3 감소시킨다.", "다른 기술: 별도 정의"])
        found=extract_skill_definitions(page,{"각인의결계":"각인의결계"})
        self.assertTrue(found.get("각인의결계"))
        self.assertIn("가장 높은 수치를 3 감소",found["각인의결계"][0])

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

    def test_compound_stat_selector_effect(self):
        result=parse("각인의결계: 방어시 상대 유닛 AP/DP/HP 중 가장 높은 수치를 영구히 3 감소시킨다.")
        self.assertTrue(any(x["kind"]=="modify_selected_combat_stat" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_generic_action_verb_effect(self):
        result=parse("적 유닛의 다음 공격을 1회 무효화한다.")
        self.assertTrue(any(x["kind"]=="generic_effect_operation" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_direct_hp_attack_rule(self):
        result=parse("상대의 DP를 무시하고 HP를 직접공격한다.")
        op=next(x for x in result["operations"] if x["kind"]=="direct_hp_damage")
        self.assertTrue(op["ignoresDefenderDP"])
        self.assertEqual(result["confidence"],"medium")

    def test_attack_with_ap_and_dp_formula(self):
        result=parse("상대를 공격시 자신의 AP에 DP를 더해 공격.")
        self.assertTrue(any(x["kind"]=="attack_with_ap_and_dp" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_dp_decrease_qualitative_rule(self):
        result=parse("AP1 이상으로 공격시 상대의 DP도 깎는다.")
        op=next(x for x in result["operations"] if x["kind"]=="modify_stat" and x.get("stat")=="dp")
        self.assertEqual(op["direction"],"decrease")
        self.assertIsNone(op["value"])

    def test_special_skill_to_normal_conversion(self):
        result=parse("AP1 이상으로 공격시 상대의 특수기술이 일반기술로 바뀐다.")
        self.assertTrue(any(x["kind"]=="modify_skill" and x.get("operation")=="replace_special_with_normal" for x in result["operations"]))

    def test_consecutive_attack_formula(self):
        result=parse("AP1 이상으로 공격시 AP 1 감소후 x2 의 AP로 공격한다.")
        self.assertTrue(any(x["kind"]=="sequential_attack_formula" for x in result["operations"]))

    def test_faq_note_is_not_effect(self):
        result=parse('자세한 사항은 FAQ에서 "랭크 카드 안내" 로 검색해 보세요.')
        self.assertEqual(result["classification"],"reference_or_metadata")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_conditional_card_reference_branch(self):
        result=parse("1 ~ 3레벨: 마법개구리.")
        self.assertEqual(result["confidence"],"medium")
        self.assertTrue(any(x["kind"]=="conditional_branch_reference" for x in result["operations"]))

    def test_time_digit_attack_formula(self):
        result=parse("AP1이상으로 공격시, Turn의 1의 자리수로 상대를 공격한다.")
        self.assertTrue(any(x["kind"]=="dynamic_attack_formula" for x in result["operations"]))

    def test_dp_sign_reversal(self):
        result=parse("AP1 이상으로 공격시 상대의 DP기호가 반대로 변환된다.")
        self.assertTrue(any(x["kind"]=="modify_stat_marks" and x.get("operation")=="reverse_sign" for x in result["operations"]))

    def test_enemy_dp_to_self_hp_formula(self):
        result=parse("AP1이상으로 공격시, 적군 DP만큼 자신 HP증가.")
        self.assertTrue(any(x["kind"]=="modify_stat" and x.get("stat")=="hp" for x in result["operations"]))

    def test_rank_profile_note_is_not_effect(self):
        result=parse("수집랭커 유니크는 수집랭커 1레벨 이상의 유저분만 구매가 가능합니다.")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_explanatory_example_is_not_effect(self):
        result=parse("ex) 해당 마법과 관련 있는 스페셜 유닛이 필드에 있는 경우 ②번 효과가 발동.")
        self.assertEqual(result["confidence"],"not_applicable")


    def test_appended_flavor_text_is_separated_from_effect_rule(self):
        result=parse("적 필드 유닛 전체 HP=적 핸드 수, AP=아군핸드 수. [믿을 수 없겠지만 모아지쿠이에 의해 처음 그 선이 그어졌을 때]")
        self.assertIn("모아지쿠이",result["flavorText"])
        self.assertIn("아군핸드 수",result["rawText"])
        formulas=[x for x in result["operations"] if x["kind"]=="set_stat_formula"]
        self.assertEqual({x["stat"] for x in formulas},{"hp","ap"})
        self.assertEqual(result["confidence"],"medium")

    def test_derived_stat_formula_is_structured(self):
        result=parse("적 필드 유닛 전체의 AP/HP를 아군 필드 유닛 수로 나눈다.")
        self.assertTrue(any(x["kind"]=="divide_stat_by_expression" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_disabled_state_is_named_and_preserved(self):
        result=parse("적군 맨 뒤의 유닛은 행동불능 상태가 된다. [힘만 믿고 설치다니 가소롭구나]")
        self.assertTrue(any(x["kind"]=="apply_or_change_named_status" for x in result["operations"]))
        self.assertIn("행동불능",result["rawText"])
        self.assertEqual(result["confidence"],"medium")

    def test_bracketed_status_label_is_reference_not_unparsed_text(self):
        result=parse("[영혼지배]상태")
        self.assertEqual(result["classification"],"named_status_reference")
        self.assertEqual(result["operations"][0]["statusName"],"영혼지배")

    def test_element_card_pair_is_reference_not_effect(self):
        result=parse("금-유리가면")
        self.assertEqual(result["classification"],"card_reference_list")
        self.assertEqual(result["operations"][0]["cardName"],"유리가면")

    def test_source_placeholder_is_not_a_low_confidence_effect(self):
        result=parse(".")
        self.assertEqual(result["classification"],"source_placeholder")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_ellipsis_is_a_punctuation_artifact(self):
        result=parse("…")
        self.assertEqual(result["classification"],"punctuation_artifact")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_item_buildup_lore_is_reference_metadata(self):
        result=parse("아이템빌드업(우산준비) [스토리 설명]")
        self.assertEqual(result["classification"],"reference_or_metadata")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_card_progression_arrow_is_reference(self):
        result=parse("악령의알 -> 슬레지어 -> 고스트로드")
        self.assertEqual(result["classification"],"card_progression_reference")
        self.assertEqual(result["operations"][0]["stages"],["악령의알","슬레지어","고스트로드"])

    def test_element_card_mapping_is_reference(self):
        result=parse("암흑 : 데스네이션.")
        self.assertEqual(result["classification"],"card_reference_list")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_rarity_and_category_values_are_references(self):
        result=parse("언커먼, 커먼 : +3")
        self.assertEqual(result["classification"],"rarity_or_category_reference")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_no_effect_clause_is_a_conditional_gate(self):
        result=parse("6턴 이상 or 0턴 - 효과 없음.")
        self.assertTrue(any(x["kind"]=="suppress_effect_when_condition" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_hybrid_status_heading_with_colon_is_reference(self):
        result=parse("[용의위압] 상태 :")
        self.assertEqual(result["classification"],"named_status_reference")

    def test_divide_by_field_space_rule(self):
        result=parse("적 필드 유닛 1,2의 공체를 적 필드 빈공간 수로 나눔.")
        self.assertTrue(any(x["kind"]=="divide_stat_by_expression" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_copy_stat_value_between_two_units(self):
        result=parse("적 필드 유닛 1의 AP는 적 필드 유닛 2의 DP와 동일해지고, 적 필드 유닛 2의 AP는 적 필드 유닛 1의 DP와 동일해진다.")
        self.assertTrue(any(x["kind"]=="copy_stat_value" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_zero_multiplier_stat_effect(self):
        result=parse("적군 야수유닛 전체의 AP를 *0 로 만든다.")
        self.assertTrue(any(x["kind"]=="multiply_stat" and x["multiplier"]==0 for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_stat_technique_becomes_another_technique(self):
        result=parse("적군 유닛의 특수기술이 일반기술로 된다.")
        self.assertTrue(any(x["kind"]=="modify_skill" for x in result["operations"]))
        self.assertEqual(result["confidence"],"medium")

    def test_named_status_effect_is_captured_without_executable_claim(self):
        result=parse("공격시 적 유닛에게 빙결 상태를 부여한다.")
        self.assertTrue(any(x["kind"]=="apply_or_change_named_status" for x in result["operations"]))
        self.assertFalse(any(x.get("executable") is True for x in result["operations"]))

    def test_legacy_trigger_receive_attack(self):
        result=parse("공격을 받을 때 상대에게 피해를 되돌려준다.")
        self.assertIn("on_receive_attack",result["triggers"])

    def test_legacy_move_and_disable_verbs_are_typed(self):
        result=parse("적 유닛을 소각장으로 보내고 특수기술을 봉인한다.")
        op=next(x for x in result["operations"] if x["kind"]=="generic_effect_operation")
        self.assertIn("move_or_select",op["actionCandidates"])
        self.assertIn("remove_or_disable",op["actionCandidates"])

    def test_leading_diamond_marker_does_not_break_skill_link(self):
        result=parse("◇디스히어로",{"디스히어로":"rule_dis_hero"})
        self.assertEqual(result["classification"],"ability_name_reference")
        self.assertEqual(result["operations"][0]["ruleId"],"rule_dis_hero")
        self.assertEqual(result["rawText"],"◇디스히어로")

    def test_known_card_name_pair_is_reference_not_unparsed_effect(self):
        result=parse("공녀의기사 : 와일드엘리펀",known_cards={
            "공녀의기사":["card-a"],"와일드엘리펀":["card-b"]})
        self.assertEqual(result["classification"],"card_reference_list")
        self.assertEqual(result["operations"][0]["entries"][0]["cardIds"],["card-a"])
        self.assertFalse(result["operations"][0]["executable"])

    def test_source_metadata_marker_is_not_counted_as_effect_and_raw_text_is_preserved(self):
        result=parse("▶ 해당 지형은 매직랜드입니다.")
        self.assertEqual(result["classification"],"reference_or_metadata")
        self.assertEqual(result["confidence"],"not_applicable")
        self.assertEqual(result["rawText"],"▶ 해당 지형은 매직랜드입니다.")

    def test_terrain_activation_order_is_retained_as_non_executable_rule_candidate(self):
        result=parse("▶ 매직랜드는 백필드에 다수 존재하더라도 맨 앞의 매직랜드만 발동합니다.")
        self.assertEqual(result["classification"],"terrain_activation_rule_candidate")
        self.assertEqual(result["confidence"],"medium")
        self.assertFalse(result["operations"][0]["executable"])

    def test_activation_requirement_is_structured_not_low_confidence(self):
        result=parse("▶ 아군 필드 유닛 1이상 필요")
        self.assertEqual(result["classification"],"effect_activation_requirement")
        self.assertEqual(result["confidence"],"medium")
        self.assertFalse(result["operations"][0]["executable"])

    def test_failed_condition_is_structured_as_branch(self):
        result=parse("▶ 실패시 : 적 필드에 3레벨 이하 마법이 존재하지 않을시")
        self.assertEqual(result["classification"],"conditional_branch_reference")
        self.assertEqual(result["confidence"],"medium")

    def test_status_duration_text_is_preserved_as_candidate(self):
        result=parse("빈공간:제물상태-1턴")
        self.assertEqual(result["classification"],"status_duration_change_candidate")
        self.assertEqual(result["operations"][0]["turnDelta"],-1)
        self.assertFalse(result["operations"][0]["executable"])

    def test_known_card_stat_label_is_not_treated_as_effect(self):
        result=parse("탈렌티움 : +3 / 0 / +3",known_cards={"탈렌티움":["card-x"]})
        self.assertEqual(result["classification"],"card_stat_profile_reference")
        self.assertEqual(result["operations"][0]["cardIds"],["card-x"])

    def test_exact_known_card_name_is_a_reference(self):
        result=parse("와일드엘리펀",known_cards={"와일드엘리펀":["card-b"]})
        self.assertEqual(result["classification"],"card_name_reference")
        self.assertEqual(result["operations"][0]["cardIds"],["card-b"])

    def test_hand_space_activation_restriction_is_not_unparsed(self):
        result=parse("▶ 핸드 빈공간이 없을 경우 의문공격은 발동하지 않습니다.")
        self.assertEqual(result["classification"],"effect_activation_requirement")
        self.assertEqual(result["confidence"],"medium")

    def test_field_space_count_branch_is_structured(self):
        result=parse("아군 필드 빈공간 수가 1 : 유닛1")
        self.assertEqual(result["classification"],"conditional_branch_reference")
        self.assertEqual(result["confidence"],"medium")

    def test_quoted_status_label_is_reference(self):
        result=parse('☆"영혼각인" 상태')
        self.assertEqual(result["classification"],"named_status_reference")
        self.assertEqual(result["confidence"],"medium")

    def test_exclusive_effect_selection_is_structured(self):
        result=parse("▶ ①과 ②중 조건에 맞는 하나의 효과만 발동. 관련 스페셜은 에피소드 카드도 포함.")
        self.assertEqual(result["classification"],"effect_selection_rule_candidate")
        self.assertEqual(result["confidence"],"medium")

    def test_hand_space_activation_restriction_is_not_unparsed(self):
        result=parse("▶ 핸드 빈공간이 없을 경우 의문공격은 발동하지 않습니다.")
        self.assertEqual(result["classification"],"effect_activation_requirement")
        self.assertEqual(result["confidence"],"medium")

    def test_field_space_count_branch_is_structured(self):
        result=parse("아군 필드 빈공간 수가 1 : 유닛1")
        self.assertEqual(result["classification"],"conditional_branch_reference")
        self.assertEqual(result["confidence"],"medium")

    def test_quoted_status_label_is_reference(self):
        result=parse('☆"영혼각인" 상태')
        self.assertEqual(result["classification"],"named_status_reference")
        self.assertEqual(result["confidence"],"medium")

    def test_exclusive_effect_selection_is_structured(self):
        result=parse("▶ ①과 ②중 조건에 맞는 하나의 효과만 발동. 관련 스페셜은 에피소드 카드도 포함.")
        self.assertEqual(result["classification"],"effect_selection_rule_candidate")
        self.assertEqual(result["confidence"],"medium")

    def test_legacy_event_note_is_not_an_effect(self):
        result=parse("※ 2009년 여름 대박 부스터 이벤트 카드.")
        self.assertEqual(result["classification"],"reference_or_metadata")
        self.assertEqual(result["confidence"],"not_applicable")

    def test_status_duration_with_trailing_period_is_candidate(self):
        result=parse("빈공간 : 상태 -1턴.")
        self.assertEqual(result["classification"],"status_duration_change_candidate")
        self.assertEqual(result["operations"][0]["turnDelta"],-1)

if __name__=="__main__":
    unittest.main()


class LegacyLowConfidenceEffectRegressionTests(unittest.TestCase):
    def test_compact_ap_hp_multipliers_are_structured(self):
        parsed=parse("아군 필드 유닛 중 자신의 이름수와 레벨이 일치하는 유닛은 APX2,HPX2")
        self.assertEqual({x.get("stat") for x in parsed["operations"] if x["kind"]=="multiply_stat"},{"ap","hp"})
        self.assertTrue(all(x.get("executable") is False for x in parsed["operations"]))

    def test_card_name_count_combat_stat_shorthand_is_preserved(self):
        parsed=parse("아군 유닛 전체 각각의 카드이름수가 공/체가 된다.")
        self.assertTrue(any(x["kind"]=="set_combat_stats_from_expression" for x in parsed["operations"]))

    def test_multiple_stats_becoming_one_are_structured(self):
        parsed=parse("아군 적군 레벨 이상은 AP와 HP가 1로 변한다.")
        self.assertTrue(any(x["kind"]=="set_multiple_stats_from_rule" for x in parsed["operations"]))

    def test_mirrored_card_levels_are_structured(self):
        parsed=parse("아군 적군 필드 유닛 카드의 레벨이 좌우대칭으로 바뀐다.")
        self.assertTrue(any(x["kind"]=="mirror_or_swap_card_levels" for x in parsed["operations"]), msg=json.dumps(parsed,ensure_ascii=False))

    def test_granted_named_attack_skill_is_structured(self):
        parsed=parse("아군 유닛 전체는 저주공격기술을 가진다.")
        self.assertTrue(any(x["kind"]=="grant_or_reference_skill" for x in parsed["operations"]))

    def test_administrative_purchase_notice_is_not_an_effect(self):
        parsed=parse("1장 초과로 구입하시는 경우 구입에 오류가 납니다. 번거로우시더라도 1장씩 구입을 부탁드립니다.")
        self.assertEqual(parsed["classification"],"administrative_or_shop_note")
        self.assertEqual(parsed["confidence"],"not_applicable")

    def test_faq_and_maintenance_notes_are_not_effects(self):
        parsed=parse("- 자세한 내용 및 조건은 FAQ 검색.")
        self.assertEqual(parsed["confidence"],"not_applicable")

    def test_damage_spelling_variant_is_captured(self):
        parsed=parse("예상밖의습격 : 적 유닛에게 단계별 대미지를 준다.")
        self.assertTrue(any(x["kind"]=="deal_damage" for x in parsed["operations"]))

    def test_card_category_treatment_is_structured(self):
        parsed=parse("무속성 이벤트 마법은 이벤트 마법으로 취급됩니다.")
        self.assertTrue(any(x["kind"]=="card_category_treatment_rule" for x in parsed["operations"]))
