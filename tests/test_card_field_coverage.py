import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.build_gap_reports import build


class CardFieldCoverageTests(unittest.TestCase):
    def test_absent_field_is_not_inferred_from_other_cards(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            db_path = root / "sample.sqlite"
            db = sqlite3.connect(db_path)
            db.executescript("""
                PRAGMA foreign_keys=ON;
                CREATE TABLE cards(
                    card_id TEXT PRIMARY KEY, name TEXT, card_type TEXT, raw_payload_json TEXT, source_card_url TEXT
                );
                CREATE TABLE card_fields(
                    field_id INTEGER PRIMARY KEY, card_id TEXT, field_key TEXT,
                    source_value_json TEXT, normalized_value TEXT, verification_status TEXT
                );
                CREATE TABLE card_costs(
                    card_id TEXT PRIMARY KEY, source_text TEXT, soul_json TEXT,
                    lp_value REAL, lp_known INTEGER, soul_known INTEGER,
                    mapping_review INTEGER, semantic_review INTEGER, verification_status TEXT
                );
                CREATE TABLE card_soul_cost_tokens(
                    card_id TEXT, ordinal INTEGER, raw_token TEXT, code INTEGER, count INTEGER,
                    symbol TEXT, normalized_color TEXT, parse_status TEXT
                );
                CREATE TABLE card_rule_mappings(
                    card_id TEXT, source_field TEXT, source_enum_value TEXT, source_name TEXT,
                    mapping_status TEXT, rule_id TEXT, confidence TEXT, evidence_references_json TEXT
                );
                CREATE TABLE card_effect_clauses(
                    clause_id INTEGER PRIMARY KEY, card_id TEXT, clause_index INTEGER, segment_text TEXT
                );
                CREATE TABLE card_effect_interpretations(
                    clause_id INTEGER, card_id TEXT, interpretation_json TEXT,
                    verification_status TEXT, confidence TEXT, source_detail_url TEXT
                );
            """)
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",
                       ("c1", "카드1", "유닛", json.dumps({"Name": "카드1", "Skill1": 12}, ensure_ascii=False), "https://fmlunatic.com/card/c1"))
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",
                       ("c2", "카드2", "유닛", json.dumps({"Name": "카드2"}, ensure_ascii=False), "https://fmlunatic.com/card/c2"))
            db.executemany("INSERT INTO card_fields VALUES(?,?,?,?,?,?)", [
                (1, "c1", "Name", json.dumps("카드1", ensure_ascii=False), "카드1", "extracted"),
                (2, "c1", "Skill1", "12", "12", "extracted"),
                (3, "c2", "Name", json.dumps("카드2", ensure_ascii=False), "카드2", "extracted"),
            ])
            db.executemany("INSERT INTO card_costs VALUES(?,?,?,?,?,?,?,?,?)", [
                ("c1", "0100", "{}", 0, 1, 1, 0, 0, "extracted"),
                ("c2", "0100", "{}", 0, 1, 1, 0, 0, "extracted"),
            ])
            db.commit()
            db.close()

            summary = build(db_path, root / "out")
            self.assertEqual(summary["field_status_counts"].get("missing_on_card", 0), 0)
            self.assertEqual(summary["field_status_counts"].get("source_absent_confirmed", 0), 1)
            self.assertEqual(summary["source_payload_mismatches"], 0)

            check = sqlite3.connect(db_path)
            status = check.execute(
                "SELECT coverage_status FROM card_field_coverage WHERE card_id='c2' AND field_key='Skill1'"
            ).fetchone()[0]
            check.close()
            self.assertEqual(status, "source_absent_confirmed")


if __name__ == "__main__":
    unittest.main()
