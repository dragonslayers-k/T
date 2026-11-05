import json, unittest
from collections import Counter
from pathlib import Path
DATA=Path(__file__).resolve().parents[1]/"data/reviews/fm1-skill2-wrath-adjudication-2026-11-06.json"
class WrathAdjudicationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.data=json.loads(DATA.read_text(encoding="utf-8"))
 def test_all_20_candidates_have_unique_card_local_effect_evidence(self):
  d=self.data; cards=d["cards"]
  self.assertEqual(len(cards),20); self.assertEqual(len({x["card_id"] for x in cards}),20)
  self.assertEqual(d["summary"]["candidate_rows"],20); self.assertEqual(d["summary"]["additional_text_rows"],20)
  self.assertTrue(all(x["evidence_type"]=="additional_text" and x["source_excerpt"] for x in cards))
  self.assertEqual(Counter(x["card_type"] for x in cards),{"유닛":18,"아이템":2})
 def test_two_exact_wording_variants_reconcile_19_and_1(self):
  variants=self.data["source_text_variants"]
  self.assertEqual([x["count"] for x in variants],[19,1])
  observed=Counter(x["source_excerpt"] for x in self.data["cards"])
  self.assertEqual(dict(observed),{x["text"]:x["count"] for x in variants})
  self.assertEqual(len(observed),2)
 def test_item_cards_are_not_silently_treated_as_unit_mappings(self):
  items={x["card_id"] for x in self.data["cards"] if x["card_type"]=="아이템"}
  self.assertEqual(items,{"5060240558","9071541045"})
  self.assertTrue(self.data["policy"]["item_skill2_is_not_automatically_unit_skill2"])
  self.assertIn("item_host_scope",{x["id"] for x in self.data["semantic_questions"]})
 def test_all_candidates_remain_inferred_and_non_executable(self):
  self.assertTrue(all(x["mapping_status"]=="inferred" and not x["executable"] for x in self.data["cards"]))
  self.assertEqual(self.data["summary"]["source_card_verified_rows"],0)
  self.assertEqual(self.data["summary"]["executable_rows"],0)
  self.assertEqual(self.data["rule_hypothesis"]["status"],"candidate_only_not_adjudicated")
 def test_db29_immutable_and_no_db30(self):
  b=self.data["baseline"]; self.assertEqual(b["db_release"],"fm1-carddb-29")
  self.assertTrue(b["immutable"]); self.assertFalse(b["db30_issued"]); self.assertFalse(b["main_merge"])
if __name__=="__main__": unittest.main()
