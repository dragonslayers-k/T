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

    def test_unresolved_queue_contains_raw_text_and_source_fields_for_card_level_review(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "db29-review.sqlite"
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
            raw = {
                "RequireSoul":"8201", "EarnSoulList":"", "MuSoul":0, "Skill1":51, "Skill2":129,
                "TextBase":"NCS source text base",
                "TextExtra":"NCS source text extra / resource conversion"
            }
            db.execute("INSERT INTO cards VALUES(?,?,?,?,?)",
                       ("unit-ncs-1","NCS test unit","유닛","빛",json.dumps(raw,ensure_ascii=False)))
            db.execute("INSERT INTO card_costs VALUES(?,?,?,?,?,?,?,?,?)",
                       ("unit-ncs-1","8201",json.dumps({
                           "known":True,"semantic_review":True,"mapping_review":False,
                           "colors":{"ncs":1},
                           "tokens":[{"code":82,"count":1,"normalized_color":"ncs","status":"semantic_review"}]
                       }),None,0,1,0,1,"semantic_review"))
            db.commit()
            db.close()

            result = inspect_db(path)
            item = result["reviewQueue"][0]
            self.assertEqual(item["sourceFields"]["RequireSoul"], "8201")
            self.assertEqual(item["sourceFields"]["Skill1"], 51)
            self.assertEqual(item["sourceFields"]["Skill2"], 129)
            self.assertEqual(item["sourceTexts"]["TextBase"], "NCS source text base")
            self.assertEqual(item["sourceTexts"]["TextExtra"], "NCS source text extra / resource conversion")


if __name__ == "__main__":
    unittest.main()
