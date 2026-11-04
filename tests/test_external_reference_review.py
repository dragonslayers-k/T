import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/reviews/fm1-reference-source-registry-2026-11-04.json"
REVIEW = ROOT / "data/reviews/fm1-carddb-29-semantic-review-reference-adjudication-2026-11-04.json"

class ExternalReferenceReviewTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.registry = json.loads(REGISTRY.read_text(encoding="utf-8"))
        cls.review = json.loads(REVIEW.read_text(encoding="utf-8"))

    def test_all_pending_rows_and_source_text_are_preserved(self):
        summary = self.review["summary"]
        self.assertEqual(summary["input_rows"], 54)
        self.assertEqual(summary["distinct_card_ids"], 54)
        self.assertTrue(summary["records_with_original_text_preserved"])
        self.assertEqual(len(self.review["records"]), 54)

    def test_every_candidate_remains_non_executable(self):
        self.assertTrue(self.review["summary"]["all_non_executable"])
        self.assertTrue(all(r["external_reference_review"]["runtime_status"] == "non_executable" for r in self.review["records"]))

    def test_disenchant_definition_is_card_local_and_not_engine_verified(self):
        rows = [r for r in self.review["records"] if r["classification"] == "named_effect_reference_candidate"]
        self.assertEqual(len(rows), 23)
        self.assertTrue(all(r["external_reference_review"]["structured_candidate"]["engine_verified"] is False for r in rows))
        self.assertTrue(all("인첸트 발동 페이즈" in r["external_reference_review"]["structured_candidate"]["source_definition"] for r in rows))

    def test_area_counter_name_mismatches_are_not_silently_merged(self):
        rows = [r for r in self.review["records"] if r["classification"] == "named_area_counter_reference_candidate"]
        self.assertEqual(len(rows), 7)
        mismatches = [r for r in rows if r["external_reference_review"]["structured_candidate"]["label_mismatch"]]
        matches = [r for r in rows if not r["external_reference_review"]["structured_candidate"]["label_mismatch"]]
        self.assertEqual(len(mismatches), 6)
        self.assertEqual(len(matches), 1)
        self.assertTrue(all(r["external_reference_review"]["structured_candidate"]["counter_label_in_TextBase"] and
                            r["external_reference_review"]["structured_candidate"]["counter_label_in_TextExtra"] for r in rows))

    def test_naver_reference_is_registered_but_not_claimed_as_read(self):
        source = next(s for s in self.registry["sources"] if s["id"] == "jlplace_original_fanma_guide")
        self.assertEqual(source["status"], "not_retrieved_robots_or_access_block")
        self.assertFalse(self.review["summary"]["naver_post_body_retrieved"])

    def test_community_sources_are_supplemental(self):
        policy = self.registry["authority_policy"]
        self.assertTrue(policy["community_sources_are_supplemental"])
        self.assertTrue(policy["community_sources_cannot_alone_set_executable"])
        self.assertTrue(policy["fantasy_masters_1_and_2_must_not_be_conflated"])

if __name__ == "__main__":
    unittest.main()


    def test_inven_reference_cross_checks_item_names_but_does_not_override_card_text(self):
        source = next(s for s in self.registry["sources"] if s["id"] == "inven_fm1_skill_reference_2017")
        self.assertEqual(source["published_at"], "2017-01-30")
        self.assertIn("코스튬체인지", " ".join(source["facts_observed"]))
        rows = [r for r in self.review["records"]
                if r["external_reference_review"]["structured_candidate"].get("kind") == "named_card_reference_list"
                and r["external_reference_review"]["structured_candidate"].get("names") == [
                    "블러드본랜스","루비소드","레드아이스링","네추럴링","생명의물약","번개의모래","그리핀석상"]]
        self.assertEqual(len(rows), 7)
        for row in rows:
            extra = row["source_card"]["TextExtra"]["source_value"]
            self.assertIn("아이템 미장착한", extra)
            cross = [x for x in row["external_reference_review"]["secondary_source_assessment"]
                     if x.get("source_id") == "inven_fm1_skill_reference_2017"]
            self.assertEqual(len(cross), 1)
            self.assertIn("조건", cross[0]["discrepancy"])
            self.assertEqual(row["external_reference_review"]["runtime_status"], "non_executable")

    def test_naver_capture_is_not_claimed_as_transcribed(self):
        source = next(s for s in self.registry["sources"] if s["id"] == "jlplace_original_fanma_guide")
        capture = source["attached_capture"]
        self.assertEqual(capture["image_dimensions_px"]["width"], 65)
        self.assertEqual(capture["extraction_status"], "no_rules_or_values_extracted")
        self.assertFalse(self.review["summary"]["naver_post_body_retrieved"])

    def test_summon_profile_community_context_does_not_claim_pool_verification(self):
        rows = [r for r in self.review["records"]
                if r["external_reference_review"]["structured_candidate"].get("kind") == "summoned_unit_profile"]
        self.assertGreaterEqual(len(rows), 8)
        for row in rows:
            cross = [x for x in row["external_reference_review"]["secondary_source_assessment"]
                     if x.get("source_id") == "inven_fm1_skill_reference_2017"]
            self.assertEqual(len(cross), 1)
            self.assertIn("검증", cross[0]["limitation"])
            self.assertEqual(row["external_reference_review"]["runtime_status"], "non_executable")
