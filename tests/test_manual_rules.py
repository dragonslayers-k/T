import importlib.util
import json
import sqlite3
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "import_manual_rules.py"
CATALOGUE = ROOT / "data" / "rules" / "fm1-skill-catalog-v1.json"
SPEC = importlib.util.spec_from_file_location("import_manual_rules", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


class ManualSkillCatalogueTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.catalogue = MODULE.load_catalog(CATALOGUE)

    def test_contains_27_manual_baseline_skills(self):
        manual = [x for x in self.catalogue["rules"] if x["authority"] == "manual"]
        skill_manual = [x for x in manual if x["source"]["member"] == "specialability.htm"]
        global_manual = [x for x in manual if x["source"]["member"] != "specialability.htm"]
        self.assertEqual(len(skill_manual), 27)
        self.assertEqual(len(global_manual), 15)
        self.assertEqual(len(manual), 42)



    def test_global_gameplay_catalogue_preserves_soul_cost_coin_and_manual_conflict(self):
        global_rules = [x for x in self.catalogue["rules"] if x["source"]["member"] != "specialability.htm"]
        by_id = {x["id"]: x for x in global_rules}
        self.assertIn("unit_neutral_soul_maintenance", by_id)
        self.assertIn("coin_single_roll_shared", by_id)
        conflict = by_id["terrain_placement_limit_conflict"]
        self.assertEqual(conflict["verificationStatus"], "manual_conflict")
        self.assertFalse(conflict["playableByDefault"])
        self.assertEqual(len(conflict["sourceConflicts"]), 2)
        self.assertEqual(by_id["unit_neutral_soul_summon"]["ruleDefinition"]["sourceSymbol"], "MU")

    def test_every_manual_rule_has_complete_structured_definition_and_provenance(self):
        manual = [x for x in self.catalogue["rules"] if x["authority"] == "manual"]
        for rule in manual:
            with self.subTest(rule=rule["id"]):
                definition = rule.get("ruleDefinition")
                self.assertIsInstance(definition, dict)
                self.assertTrue(definition.get("kind"))
                self.assertTrue(rule.get("source", {}).get("member"))
                self.assertTrue(rule.get("source", {}).get("section"))
                self.assertTrue(rule.get("exceptions") is not None)
                self.assertEqual(rule.get("implementationStatus"), "pending_engine_test")

    def test_legacy_definition_mirror_matches_structured_rule_definition(self):
        manual = [x for x in self.catalogue["rules"] if x["authority"] == "manual"]
        for rule in manual:
            with self.subTest(rule=rule["id"]):
                self.assertEqual(rule.get("definition"), rule.get("ruleDefinition"))

    def test_all_2017_community_entries_are_non_executable(self):
        community = [x for x in self.catalogue["rules"] if x["authority"] == "community"]
        self.assertGreaterEqual(len(community), 35)
        self.assertTrue(all(x["playableByDefault"] is False for x in community))
        self.assertTrue(all(x["verificationStatus"] == "community_documented_candidate" for x in community))

    def test_manual_and_community_aliases_do_not_collide(self):
        expected = {}
        for rule in self.catalogue["rules"]:
            for alias in [rule["name"], *rule["aliases"]]:
                key = MODULE.norm(alias)
                self.assertTrue(key)
                previous = expected.get(key)
                self.assertTrue(previous is None or previous == rule["id"])
                expected[key] = rule["id"]
        self.assertEqual(set(expected), set(self.catalogue["aliases"]))
        self.assertTrue(all(
            self.catalogue["aliases"][key]["id"] == rule_id
            for key, rule_id in expected.items()
        ))

    def test_sources_are_tiered_and_versioned(self):
        data=self.catalogue["data"]
        self.assertEqual(data["sourcePriority"][:2], ["Manual.zip", "community_reference"])
        self.assertEqual(data["manualArchive"]["member"], "specialability.htm")
        self.assertEqual(data["communitySources"][0]["publishedDate"], "2017-01-30")

    def test_database_mapping_preserves_unmapped_skill_two(self):
        db=sqlite3.connect(":memory:")
        db.execute("PRAGMA foreign_keys=ON")
        db.executescript("""
          CREATE TABLE cards(card_id TEXT PRIMARY KEY);
          CREATE TABLE card_fields(field_id INTEGER PRIMARY KEY,card_id TEXT,field_key TEXT,source_value_json TEXT,normalized_value TEXT);
          INSERT INTO cards VALUES('unit-1'),('unit-2'),('unit-3'),('unit-4');
          INSERT INTO card_fields VALUES
            (1,'unit-1','Skill1','243','방어무시'),
            (2,'unit-2','Skill1','82','기술봉쇄'),
            (3,'unit-3','Skill1','602','주문봉쇄'),
            (4,'unit-4','Skill2','175','헌신방어');
        """)
        result=MODULE.import_rules(db,self.catalogue)
        rows=db.execute("SELECT source_name,rule_id,mapping_status FROM card_rule_mappings").fetchall()
        self.assertIn(("방어무시","defense_bypass","manual_verified"),rows)
        self.assertIn(("기술봉쇄","ability_seal","manual_verified"),rows)
        self.assertIn(("주문봉쇄","spell_suppression","manual_verified"),rows)
        self.assertIn(("헌신방어",None,"unmapped"),rows)
        self.assertEqual(result["manualRuleCount"],42)
        self.assertEqual(result["manualSkillRuleCount"],27)
        self.assertEqual(result["manualGlobalRuleCount"],15)
        self.assertEqual(result["communityCandidateRuleCount"],41)
        self.assertEqual(result["playableCommunityCandidates"],0)
        self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
        db.close()


if __name__ == "__main__":
    unittest.main()
