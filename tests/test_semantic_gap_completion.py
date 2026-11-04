import unittest
from scripts.infer_unmapped_skills import extract_definitions, operations_from_text
from scripts.infer_effect_interpretations import parse
from scripts.infer_unmapped_skills import infer_one
import sqlite3, json

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
