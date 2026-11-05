import json, unittest
from collections import Counter
from pathlib import Path

DATA = Path(__file__).resolve().parents[1] / "data/reviews/fm1-skill2-devoted-defense-adjudication-2026-11-06.json"

class DevotedDefenseAdjudicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.data = json.loads(DATA.read_text(encoding="utf-8"))

    def test_candidate_and_evidence_counts_reconcile(self):
        summary = self.data["summary"]
        cards = self.data["cards"]
        missing = self.data["missing_records"]
        self.assertEqual(len(cards), 63)
        self.assertEqual(len(missing), 3)
        self.assertEqual(summary["candidate_rows"], 66)
        self.assertEqual(len(cards) + len(missing), 66)
        self.assertEqual(len({x["card_id"] for x in cards + missing}), 66)
        self.assertEqual(sum(x["count"] for x in self.data["source_text_variants"]), 63)
        observed = Counter(x["source_excerpt"] for x in cards)
        expected = {x["text"]: x["count"] for x in self.data["source_text_variants"]}
        self.assertEqual(dict(observed), expected)

    def test_exact_source_variants_are_preserved_without_normalization(self):
        variants = self.data["source_text_variants"]
        self.assertEqual(len(variants), 6)
        self.assertEqual([x["count"] for x in variants], [45, 12, 3, 1, 1, 1])
        self.assertEqual(len({x["text"] for x in variants}), 6)
        observed = {x["source_excerpt"] for x in self.data["cards"]}
        self.assertEqual(observed, {x["text"] for x in variants})
        self.assertTrue(all(x["normalization"] == "none_exact_source_preserved" for x in variants))

    def test_missing_card_ids_are_explicit_and_not_borrowed(self):
        self.assertEqual(
            {x["card_id"] for x in self.data["missing_records"]},
            {"14031227302", "16110228578", "16112328609"},
        )
        self.assertTrue(all(x["evidence_type"] == "missing_card_local_excerpt" for x in self.data["missing_records"]))
        self.assertTrue(all(not x.get("source_excerpt") for x in self.data["missing_records"]))

    def test_card_text_is_not_mixed_into_effect_evidence(self):
        self.assertTrue(all(x["evidence_type"] == "additional_text" for x in self.data["cards"]))
        self.assertNotIn("기술부여", "\n".join(x["source_excerpt"] for x in self.data["cards"]))

    def test_no_mapping_or_runtime_promotion(self):
        rows = self.data["cards"] + self.data["missing_records"]
        self.assertTrue(all(x["mapping_status"] == "inferred" and not x["executable"] for x in rows))
        self.assertEqual(self.data["summary"]["source_card_verified_rows"], 0)
        self.assertEqual(self.data["summary"]["executable_rows"], 0)
        self.assertEqual(self.data["rule_hypothesis"]["status"], "candidate_only_not_adjudicated")

    def test_db29_remains_immutable(self):
        baseline = self.data["baseline"]
        self.assertEqual(baseline["db_release"], "fm1-carddb-29")
        self.assertTrue(baseline["immutable"])
        self.assertFalse(baseline["db30_issued"])
        self.assertFalse(baseline["main_merge"])

if __name__ == "__main__":
    unittest.main()
