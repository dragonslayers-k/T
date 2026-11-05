import json
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REVIEWS = ROOT / "data" / "reviews"


def load_review(name):
    return json.loads((REVIEWS / name).read_text(encoding="utf-8"))


class StructuredSemanticEnrichmentTests(unittest.TestCase):
    def assert_pending_non_executable(self, record):
        self.assertEqual(record.get("semantic_review_status"), "pending")
        self.assertEqual(record.get("runtime_status"), "non_executable")

    def test_all_enrichments_are_bound_to_immutable_db29(self):
        documents = [
            load_review("fm1-carddb-29-area-counter-structured-review-2026-11-05.json"),
            load_review("fm1-carddb-29-disenchant-definition-enrichment-2026-11-05.json"),
            load_review("fm1-carddb-29-eka-mael-profile-enrichment-2026-11-05.json"),
        ]
        for document in documents:
            self.assertEqual(document["source_db_release"], "fm1-carddb-29")
            self.assertTrue(document["immutable_baseline"])
            policy = document["policy"]
            self.assertTrue(policy["db29_immutable"])
            self.assertFalse(policy["db30_issued"])
            self.assertFalse(policy["merge_to_main_authorized"] if "merge_to_main_authorized" in policy else policy["merge_to_main"])
        external = load_review("fm1-external-card-and-magic-order-claims-2026-11-05.json")
        self.assertEqual(external["immutable_baseline"], "DB29")
        self.assertEqual(external["ruleset"].split(";")[0], "FM1")
        self.assertTrue(external["policy"]["db29_immutable"])
        self.assertFalse(external["policy"]["db30_issued"])
        self.assertFalse(external["policy"]["main_merge"])

    def test_area_counter_records_preserve_card_local_source_and_label_mismatches(self):
        data = load_review("fm1-carddb-29-area-counter-structured-review-2026-11-05.json")
        records = data["records"]
        self.assertEqual(data["summary"]["records"], 7)
        self.assertEqual(len(records), 7)
        self.assertEqual(sum(bool(x["label_mismatch"]) for x in records), 6)
        self.assertEqual(sum(not x["label_mismatch"] for x in records), 1)
        self.assertFalse(data["common_rule"]["executable"])
        for record in records:
            self.assertTrue(record["card_id"])
            self.assertTrue(record["TextBase"]["source_key_present"])
            self.assertTrue(record["TextExtra"]["source_key_present"])
            self.assertIn("아군 남은 LP가 1 이상", record["TextExtra"]["source_value"])
            self.assertEqual(record["lp_condition"], 1)
            self.assertEqual(record["lp_cost"], 1)
            self.assertTrue(record["terrain_from"])
            self.assertTrue(record["terrain_to"])
            self.assertEqual(record["evidence_status"], "card_local_text_observed")
            self.assert_pending_non_executable(record)

    def test_disenchant_shared_definition_is_source_observed_but_not_executable(self):
        data = load_review("fm1-carddb-29-disenchant-definition-enrichment-2026-11-05.json")
        records = data["records"]
        self.assertEqual(len(data["shared_definitions"]), 1)
        self.assertEqual(len(records), 23)
        definition = data["shared_definitions"][0]
        excerpt = definition["source_excerpt"]
        self.assertIn("인첸트 발동 페이즈", excerpt)
        self.assertIn("첫번째 인첸트부터 순서대로", excerpt)
        self.assertFalse(definition["normalized_semantics"]["unresolved"]["runtime_executable"])
        for record in records:
            self.assertEqual(record["linked_definition_id"], definition["definition_id"])
            self.assertTrue(record["source_detail_url"].startswith("https://fmlunatic.com/card/"))
            self.assertTrue(record["original_TextExtra"]["source_key_present"])
            self.assertIn("디스인첸트 카드", record["original_TextExtra"]["source_value"])
            self.assertEqual(record["evidence_status"], "observed_in_DB29_TextExtra")
            self.assert_pending_non_executable(record)

    def test_eka_mael_profile_keeps_random_pool_exclusions_and_pending_gate(self):
        data = load_review("fm1-carddb-29-eka-mael-profile-enrichment-2026-11-05.json")
        records = data["records"]
        self.assertEqual(len(records), 7)
        profile = data["normalized_semantics"]
        pool = profile["summon_pool"]
        self.assertEqual(pool["source"], "1~3 chapter units")
        self.assertIn("same level", pool["matching"])
        self.assertIn("same attribute", pool["matching"])
        self.assertTrue(pool["random_selection"])
        self.assertTrue(pool["includes_rank_cards"])
        self.assertTrue(pool["excludes_event_grade"])
        self.assertIn("some cards are excluded", profile["scaling"]["exception"])
        self.assertFalse(data["unresolved"]["runtime_executable"])
        for record in records:
            self.assertTrue(record["source_detail_url"].startswith("https://fmlunatic.com/card/"))
            self.assertTrue(record["original_TextExtra"]["source_key_present"])
            self.assertIn("에카마엘 지형", record["original_TextExtra"]["source_value"])
            self.assert_pending_non_executable(record)

    def test_external_community_claims_remain_supplemental_and_non_executable(self):
        data = load_review("fm1-external-card-and-magic-order-claims-2026-11-05.json")
        self.assertTrue(data["claims"])
        for claim in data["claims"]:
            self.assertEqual(claim["evidence_status"], "community_claim")
            self.assertEqual(claim["runtime_status"], "non_executable")
            self.assertIn(claim.get("id_match_status"), (None, "pending_card_id_match"))
            self.assertTrue(claim["source"]["url"])
        self.assertEqual(data["policy"]["ruleset"], "FM1; historical version uncertain unless noted")
        self.assertFalse(data["policy"]["main_merge"])


if __name__ == "__main__":
    unittest.main()
