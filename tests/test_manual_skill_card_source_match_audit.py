import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.audit_manual_skill_card_source_matches import audit


class ManualSkillCardSourceMatchAuditTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.db_path = self.root / "db29.sqlite"
        self.catalog_path = self.root / "catalog.json"
        self._make_db()
        rules = [
            {"id": "normal_attack", "name": "일반공격", "aliases": ["일반공격", "일반공격기술"], "authority": "manual"},
            {"id": "defense_bypass", "name": "방어무시", "aliases": ["방어무시", "방어무시기술"], "authority": "manual"},
        ]
        rules.extend({"id": f"unused_{i}", "name": f"unused skill {i}", "aliases": [], "authority": "manual"} for i in range(25))
        self.catalog_path.write_text(json.dumps({"manualRules": rules}, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        self.tmp.cleanup()

    def _make_db(self):
        db = sqlite3.connect(self.db_path)
        db.executescript("""
            CREATE TABLE cards(card_id TEXT PRIMARY KEY,name TEXT,source_card_url TEXT);
            CREATE TABLE card_fields(card_id TEXT,field_key TEXT,source_value_json TEXT,normalized_value TEXT);
        """)
        db.executemany("INSERT INTO cards VALUES(?,?,?)", [
            ("1001", "기본공격유닛", "https://fmlunatic.com/card/1001"),
            ("1002", "방어무시유닛", "https://fmlunatic.com/card/1002"),
            ("1003", "별도문구유닛", "https://fmlunatic.com/card/1003"),
            ("1004", "문구누락유닛", "https://fmlunatic.com/card/1004"),
        ])
        db.executemany("INSERT INTO card_fields VALUES(?,?,?,?)", [
            ("1001", "Skill1", '"일반공격기술"', "일반공격기술"),
            ("1002", "Skill1", '"방어무시"', "방어무시"),
            ("1003", "Skill1", '"방어무시기술"', "방어무시기술"),
            ("1004", "Skill1", '"방어무시"', "방어무시"),
            ("1001", "TextBase", '"기본 카드 설명"', "기본 카드 설명"),
            ("1001", "TextExtra", '"<b>추가 원문</b>"', "<b>추가 원문</b>"),
            ("1002", "TextBase", '"카드 설명만 있음"', "카드 설명만 있음"),
            ("1002", "TextExtra", '""', ""),
        ])
        db.commit()
        db.close()

    def test_exact_canonical_and_catalog_alias_match_preserve_source_rows(self):
        report = audit(self.db_path, self.catalog_path)
        self.assertEqual(report["summary"]["manual_rule_count"], 27)
        self.assertEqual(report["summary"]["rules_with_exact_card_rows"], 2)
        normal = report["rules"][0]["matched_card_rows"][0]
        self.assertEqual(normal["card_id"], "1001")
        self.assertEqual(normal["source_value"], "일반공격기술")
        self.assertEqual(normal["match_type"], "catalog_alias_match")
        self.assertEqual(normal["source_card_url"], "https://fmlunatic.com/card/1001")
        self.assertEqual(normal["source_text_fields"]["TextExtra"], "<b>추가 원문</b>")
        self.assertEqual(normal["text_evidence_type"], "additional_text")

    def test_substring_or_similar_name_is_not_a_match(self):
        report = audit(self.db_path, self.catalog_path)
        normal = report["rules"][0]
        self.assertEqual([row["card_id"] for row in normal["matched_card_rows"]], ["1001"])
        self.assertNotIn("1003", [row["card_id"] for row in normal["matched_card_rows"]])

    def test_card_text_only_and_missing_text_are_distinguished(self):
        report = audit(self.db_path, self.catalog_path)
        defense = report["rules"][1]
        self.assertEqual([row["card_id"] for row in defense["matched_card_rows"]], ["1002", "1004"])
        self.assertEqual([row["text_evidence_type"] for row in defense["matched_card_rows"]],
                         ["card_text_only", "missing"])
        self.assertEqual(defense["text_evidence_summary"], {
            "additional_text_rows": 0, "card_text_only_rows": 1, "missing_text_rows": 1
        })
        self.assertEqual(report["summary"]["rows_with_additional_text"], 1)
        self.assertEqual(report["summary"]["rows_with_card_text_only"], 1)
        self.assertEqual(report["summary"]["rows_missing_both_text_fields"], 1)

    def test_source_text_is_context_not_skill_semantic_approval(self):
        report = audit(self.db_path, self.catalog_path)
        self.assertTrue(report["policy"]["text_presence_is_not_skill_semantic_approval"])
        self.assertEqual(report["summary"]["runtime_executable_rules"], 0)
        self.assertTrue(all(row["runtime_promotion"] == "not_authorized" for row in report["rules"]))
        self.assertTrue(report["baseline"]["immutable"])
        self.assertFalse(report["baseline"]["db30_issued"])
        self.assertFalse(report["baseline"]["main_merge"])

    def test_audit_is_pinned_to_db29(self):
        with self.assertRaises(ValueError):
            audit(self.db_path, self.catalog_path, "fm1-carddb-30")


if __name__ == "__main__":
    unittest.main()
