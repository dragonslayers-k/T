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
        self.assertEqual(len(manual), 27)
        self.assertEqual({x["source"]["member"] for x in manual}, {"specialability.htm"})

    def test_all_2017_community_entries_are_non_executable(self):
        community = [x for x in self.catalogue["rules"] if x["authority"] == "community"]
        self.assertGreaterEqual(len(community), 35)
        self.assertTrue(all(x["playableByDefault"] is False for x in community))
        self.assertTrue(all(x["verificationStatus"] == "community_documented_candidate" for x in community))

    def test_manual_and_community_aliases_do_not_collide(self):
        self.assertEqual(len(self.catalogue["aliases"]), sum(
            len(set([x["name"], *x["aliases"]])) for x in self.catalogue["rules"]
        ) - sum(
            max(0, len([x for x in [r["name"], *r["aliases"]]]) -
                len(set([r["name"], *r["aliases"]])))
            for r in self.catalogue["rules"]
        ) - self._duplicate_alias_discount())

    def _duplicate_alias_discount(self):
        # Aliases may repeat within the same rule only if the importer normalizes them;
        # no alias may resolve to two different rule IDs.
        total = 0
        for rule in self.catalogue["rules"]:
            values=[MODULE.norm(rule["name"]), *[MODULE.norm(x) for x in rule["aliases"]]]
            total += len(values)-len(set(values))
        return total

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
        self.assertEqual(result["manualRuleCount"],27)
        self.assertEqual(result["communityCandidateRuleCount"],41)
        self.assertEqual(result["playableCommunityCandidates"],0)
        self.assertEqual(db.execute("PRAGMA foreign_key_check").fetchall(),[])
        db.close()


if __name__ == "__main__":
    unittest.main()
