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
                       ("c1", "카드1", "same-display-type", json.dumps({"Name": "카드1", "Category": 2, "Skill1": 12}, ensure_ascii=False), "https://fmlunatic.com/card/c1"))
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",
                       ("c2", "카드2", "same-display-type", json.dumps({"Name": "카드2", "Category": 2}, ensure_ascii=False), "https://fmlunatic.com/card/c2"))
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",
                       ("c3", "카드3", "same-display-type", json.dumps({"Name": "카드3", "Category": 3}, ensure_ascii=False), "https://fmlunatic.com/card/c3"))
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",
                       ("c4", "카드4", "same-display-type", json.dumps({"Name": "카드4", "Category": 2, "Skill1": ""}, ensure_ascii=False), "https://fmlunatic.com/card/c4"))
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",
                       ("c5", "카드5", "same-display-type", json.dumps({"Name": "카드5", "Category": 2, "Skill1": None}, ensure_ascii=False), "https://fmlunatic.com/card/c5"))
            db.executemany("INSERT INTO card_fields VALUES(?,?,?,?,?,?)", [
                (1, "c1", "Name", json.dumps("카드1", ensure_ascii=False), "카드1", "extracted"),
                (2, "c1", "Skill1", "12", "12", "extracted"),
                (3, "c2", "Name", json.dumps("카드2", ensure_ascii=False), "카드2", "extracted"),
                (4, "c3", "Name", json.dumps("카드3", ensure_ascii=False), "카드3", "extracted"),
                (5, "c4", "Name", json.dumps("카드4", ensure_ascii=False), "카드4", "extracted"),
                (6, "c4", "Skill1", json.dumps("", ensure_ascii=False), "", "extracted"),
                (7, "c5", "Name", json.dumps("카드5", ensure_ascii=False), "카드5", "extracted"),
            ])
            db.executemany("INSERT INTO card_costs VALUES(?,?,?,?,?,?,?,?,?)", [
                ("c1", "0100", "{}", 0, 1, 1, 0, 0, "extracted"),
                ("c2", "0100", "{}", 0, 1, 1, 0, 0, "extracted"),
                ("c3", "0100", "{}", 0, 1, 1, 0, 0, "extracted"),
                ("c4", "0100", "{}", 0, 1, 1, 0, 0, "extracted"),
                ("c5", "0100", "{}", 0, 1, 1, 0, 0, "extracted"),
            ])
            db.commit()
            db.close()

            summary = build(db_path, root / "out")
            self.assertEqual(summary["field_status_counts"].get("missing_on_card", 0), 0)
            self.assertEqual(summary["field_status_counts"].get("source_absent_confirmed", 0), 2)
            self.assertEqual(summary["field_status_counts"].get("not_applicable_candidate", 0), 0)
            self.assertEqual(summary["field_applicability_counts_by_field"]["Skill1"]["applicable_source_absent"], 1)
            self.assertEqual(summary["field_applicability_counts_by_field"]["Skill1"]["not_applicable_candidate"], 1)
            self.assertEqual(summary["field_applicability_candidate_pairs"], 1)
            self.assertEqual(summary["field_applicability_candidate_cells"], 1)
            self.assertEqual(summary["field_status_counts"].get("source_empty_confirmed", 0), 1)
            self.assertEqual(summary["field_status_counts"].get("source_null_confirmed", 0), 1)
            self.assertEqual(summary["source_payload_mismatches"], 0)
            card_rows = [json.loads(line) for line in (root / "out" / "card-field-card-summary.jsonl").read_text(encoding="utf-8").splitlines()]
            c2_summary = next(row for row in card_rows if row["card_id"] == "c2")
            self.assertIn("Skill1", c2_summary["source_absent_confirmed_fields"])
            self.assertEqual(c2_summary["missing_on_card_fields"], [])
            c4_summary = next(row for row in card_rows if row["card_id"] == "c4")
            self.assertIn("Skill1", c4_summary["source_empty_confirmed_fields"])
            c5_summary = next(row for row in card_rows if row["card_id"] == "c5")
            self.assertIn("Skill1", c5_summary["source_null_confirmed_fields"])
            c3_summary = next(row for row in card_rows if row["card_id"] == "c3")
            self.assertIn("Skill1", c3_summary["not_applicable_candidate_fields"])
            self.assertIn("Skill1", c3_summary["source_absent_confirmed_fields"])
            self.assertEqual(c2_summary["source_category"], 2)
            self.assertEqual(c3_summary["source_category"], 3)
            field_summary = json.loads((root / "out" / "card-field-status-summary.json").read_text(encoding="utf-8"))
            self.assertEqual(field_summary["cards"], 5)
            self.assertEqual(field_summary["fields"], 2)
            self.assertEqual(field_summary["field_status_counts"]["Skill1"]["source_absent_confirmed"], 2)
            self.assertEqual(field_summary["field_applicability_counts"]["Skill1"]["not_applicable_candidate"], 1)
            self.assertEqual(field_summary["field_status_counts"]["Skill1"]["source_empty_confirmed"], 1)
            self.assertEqual(field_summary["field_status_counts"]["Skill1"]["source_null_confirmed"], 1)

            check = sqlite3.connect(db_path)
            status = check.execute(
                "SELECT coverage_status,applicability_status FROM card_field_coverage WHERE card_id='c2' AND field_key='Skill1'"
            ).fetchone()
            candidate = check.execute(
                "SELECT coverage_status,applicability_status FROM card_field_coverage WHERE card_id='c3' AND field_key='Skill1'"
            ).fetchone()
            check.close()
            self.assertEqual(tuple(status), ("source_absent_confirmed", "applicable_source_absent"))
            self.assertEqual(tuple(candidate), ("source_absent_confirmed", "not_applicable_candidate"))


if __name__ == "__main__":
    unittest.main()
