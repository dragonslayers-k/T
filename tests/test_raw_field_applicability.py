import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

from scripts.audit_raw_field_applicability import audit_raw_applicability


class RawFieldApplicabilityTests(unittest.TestCase):
    def test_raw_source_presence_prevents_false_category_na(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "cards.sqlite"
            db = sqlite3.connect(db_path)
            db.execute("CREATE TABLE cards(card_id TEXT, card_type TEXT, raw_payload_json TEXT)")
            db.executemany("INSERT INTO cards VALUES(?,?,?)", [
                ("c1", "유닛", json.dumps({"Category": "유닛", "Skill2": "A"})),
                ("c2", "유닛", json.dumps({"Category": "유닛"})),
            ])
            db.commit()
            db.close()

            rows = audit_raw_applicability(db_path)
            skill2 = next(row for row in rows if row["field_key"] == "Skill2")
            self.assertEqual(skill2["raw_key_present_count"], 1)
            self.assertEqual(skill2["raw_populated_count"], 1)
            self.assertEqual(skill2["raw_applicability_status"], "raw_presence_varies_in_category")
            self.assertEqual(skill2["basis"], "immutable_cards.raw_payload_json")

    def test_null_and_empty_values_are_not_counted_as_populated(self):
        with tempfile.TemporaryDirectory() as tmp:
            db_path = Path(tmp) / "cards.sqlite"
            db = sqlite3.connect(db_path)
            db.execute("CREATE TABLE cards(card_id TEXT, card_type TEXT, raw_payload_json TEXT)")
            db.executemany("INSERT INTO cards VALUES(?,?,?)", [
                ("c1", "마법", json.dumps({"Category": "마법", "Skill2": None})),
                ("c2", "마법", json.dumps({"Category": "마법", "Skill2": "  "})),
            ])
            db.commit()
            db.close()

            rows = audit_raw_applicability(db_path)
            skill2 = next(row for row in rows if row["field_key"] == "Skill2")
            self.assertEqual(skill2["raw_key_present_count"], 2)
            self.assertEqual(skill2["raw_populated_count"], 0)
            self.assertEqual(skill2["raw_applicability_status"], "raw_present_but_empty_in_category")


if __name__ == "__main__":
    unittest.main()
