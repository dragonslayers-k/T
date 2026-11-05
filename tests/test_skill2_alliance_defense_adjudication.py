import json, unittest
from collections import Counter
from pathlib import Path
DATA=Path(__file__).resolve().parents[1]/"data/reviews/fm1-skill2-alliance-defense-adjudication-2026-11-06.json"
class AllianceDefenseAdjudicationTests(unittest.TestCase):
 @classmethod
 def setUpClass(cls): cls.data=json.loads(DATA.read_text(encoding="utf-8"))
 def test_all_44_candidates_have_unique_card_local_effect_evidence(self):
  d=self.data; cards=d["cards"]
  self.assertEqual(len(cards),44); self.assertEqual(len({x["card_id"] for x in cards}),44)
  self.assertEqual(d["summary"]["candidate_rows"],44); self.assertEqual(d["summary"]["additional_text_rows"],44)
  self.assertTrue(all(x["evidence_type"]=="additional_text" and x["source_excerpt"] for x in cards))
 def test_exact_three_variants_and_counts_reconcile(self):
  variants=d=self.data["source_text_variants"]
  self.assertEqual([x["count"] for x in variants],[40,2,2])
  observed=Counter(x["source_excerpt"] for x in self.data["cards"])
  expected={x["text"]:x["count"] for x in variants}
  self.assertEqual(dict(observed),expected)
  self.assertEqual(len(observed),3)
 def test_variant_with_explicit_friendly_scope_is_not_normalized_away(self):
  explicit=[x for x in self.data["cards"] if x["variant_id"]=="alliance_v3"]
  self.assertEqual({x["card_id"] for x in explicit},{"14110527683","14110527686"})
  self.assertTrue(all("아군 필드" in x["source_excerpt"] for x in explicit))
 def test_no_card_mapping_is_promoted_or_executable(self):
  self.assertTrue(all(x["mapping_status"]=="inferred" and not x["executable"] for x in self.data["cards"]))
  self.assertEqual(self.data["summary"]["source_card_verified_rows"],0)
  self.assertEqual(self.data["summary"]["executable_rows"],0)
  self.assertEqual(self.data["rule_hypothesis"]["status"],"candidate_only_not_adjudicated")
 def test_db29_immutable_and_no_db30(self):
  b=self.data["baseline"]; self.assertEqual(b["db_release"],"fm1-carddb-29")
  self.assertTrue(b["immutable"]); self.assertFalse(b["db30_issued"]); self.assertFalse(b["main_merge"])
if __name__=="__main__": unittest.main()
