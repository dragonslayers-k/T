import json, unittest
from collections import Counter
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"data/reviews"
class SmallSkill2AdjudicationTests(unittest.TestCase):
 def load(self,name): return json.loads((ROOT/name).read_text(encoding="utf-8"))
 def assert_unpromoted(self,d):
  self.assertTrue(all(x["mapping_status"]=="inferred" and not x["executable"] for x in d["cards"]))
  self.assertEqual(d["summary"]["source_card_verified_rows"],0)
  self.assertEqual(d["summary"]["executable_rows"],0)
  self.assertTrue(d["baseline"]["immutable"])
  self.assertFalse(d["baseline"]["db30_issued"])
  self.assertFalse(d["baseline"]["main_merge"])
 def test_holy_aura_two_card_sources_and_distinct_wordings(self):
  d=self.load("fm1-skill2-holy-aura-adjudication-2026-11-06.json")
  self.assertEqual(len(d["cards"]),2)
  self.assertEqual({x["card_id"] for x in d["cards"]},{"11112425419","5020340530"})
  self.assertEqual(Counter(x["card_type"] for x in d["cards"]),{"유닛":1,"아이템":1})
  self.assertEqual(Counter(x["source_excerpt"] for x in d["cards"]),{x["text"]:x["count"] for x in d["source_text_variants"]})
  self.assertIn("item_host_scope",{x["id"] for x in d["semantic_questions"]})
  self.assert_unpromoted(d)
 def test_pressure_single_card_source_and_floor_questions(self):
  d=self.load("fm1-skill2-pressure-adjudication-2026-11-06.json")
  self.assertEqual(len(d["cards"]),1)
  self.assertEqual(d["cards"][0]["card_id"],"13100227071")
  self.assertIn("내림",d["cards"][0]["source_excerpt"])
  self.assertIn("floor_rounding",{x["id"] for x in d["semantic_questions"]})
  self.assert_unpromoted(d)
if __name__=="__main__": unittest.main()
