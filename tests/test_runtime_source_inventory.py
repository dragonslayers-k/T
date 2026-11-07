import json
import sqlite3
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from runtime_source_inventory import inspect_db


class RuntimeSourceInventoryFieldTests(unittest.TestCase):
    def test_earn_soul_list_is_reported_under_its_exact_firestore_field_name(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "db29-mini.sqlite"
            db = sqlite3.connect(path)
            db.executescript("""
                CREATE TABLE cards(
                    card_id TEXT PRIMARY KEY, name TEXT, card_type TEXT,
                    attribute TEXT, raw_payload_json TEXT
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
            """)
            db.execute(
                "INSERT INTO cards VALUES(?,?,?,?,?)",
                ("land-1", "구름도시", "지형", "빛", json.dumps({"ID":"land-1"}))
            )
            db.executemany(
                "INSERT INTO card_fields VALUES(?,?,?,?,?,?)",
                [
                    (1,"land-1","RequireLP",'"01"',"1","enum_decoded"),
                    (2,"land-1","RequireSoul",'"71018101"',"71018101","enum_decoded"),
                    (3,"land-1","EarnSoulList",'"8201"',"8201","enum_decoded"),
                    (4,"land-1","MuSoul",'"2"',"2","enum_decoded"),
                ],
            )
            db.execute(
                "INSERT INTO card_costs VALUES(?,?,?,?,?,?,?,?,?)",
                ("land-1","71018101",json.dumps({"known":True,"colors":{"light":1,"neutral":1}}),
                 1,1,1,0,0,"enum_decoded")
            )
            db.commit()
            db.close()

            result = inspect_db(path)
            presence = result["costs"]["sourceFieldPresenceByType"]
            self.assertEqual(presence["RequireLP"], {"지형":1})
            self.assertEqual(presence["RequireSoul"], {"지형":1})
            self.assertEqual(presence["EarnSoulList"], {"지형":1})
            self.assertNotIn("EarnSoul", presence)
            self.assertEqual(result["runtimeStatSourceFields"]["EarnSoulList"], 1)
            self.assertEqual(result["landEarnSoulListValues"], {'"8201"':1})
            self.assertEqual(result["landProductionPairs"][0]["earnSoulList"], "8201")


if __name__ == "__main__":
    unittest.main()
