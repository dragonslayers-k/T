import json, unittest
from collections import Counter
from pathlib import Path
DATA=Path(__file__).resolve().parents[1]/"data/reviews/fm1-skill2-strong-devoted-defense-adjudication-2026-11-06.json"
class StrongDevotedDefenseAdjudicationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.data=json.loads(DATA.read_text(encoding="utf-8"))
 def test_all_28_candidates_have_unique_card_local_effect_evidence(self):
  d=self.data; cards=d["cards"]
  self.assertEqual(len(cards),28); self.assertEqual(len({x["card_id"] for x in cards}),28)
  self.assertEqual(d["summary"]["candidate_rows"],28); self.assertEqual(d["summary"]["additional_text_rows"],28)
  self.assertTrue(all(x["evidence_type"]=="additional_text" and x["source_excerpt"] for x in cards))
 def test_two_wording_variants_reconcile_21_and_7(self):
  variants=self.data["source_text_variants"]
  self.assertEqual([x["count"] for x in variants],[21,7])
  observed=Counter(x["source_excerpt"] for x in self.data["cards"])
  self.assertEqual(dict(observed),{x["text"]:x["count"] for x in variants})
  self.assertEqual(len(observed),2)
 def test_all_candidates_remain_inferred_and_non_executable(self):
  self.assertTrue(all(x["mapping_status"]=="inferred" and not x["executable"] for x in self.data["cards"]))
  self.assertEqual(self.data["summary"]["source_card_verified_rows"],0)
  self.assertEqual(self.data["summary"]["executable_rows"],0)
  self.assertEqual(self.data["rule_hypothesis"]["status"],"candidate_only_not_adjudicated")
 def test_db29_immutable_and_no_db30(self):
  b=self.data["baseline"]; self.assertEqual(b["db_release"],"fm1-carddb-29")
  self.assertTrue(b["immutable"]); self.assertFalse(b["db30_issued"]); self.assertFalse(b["main_merge"])
if __name__=="__main__": unittest.main()
