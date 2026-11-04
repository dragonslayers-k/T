import unittest

from scripts.build_gap_reports import build_skill2_execution_review_rows


class Skill2ExecutionReviewTests(unittest.TestCase):
    def test_review_joins_exact_skill2_rows_and_keeps_evidence_pending(self):
        rules = [
            {"name":"홀리오오라","trigger":"incoming_unit_attack_damage_calculation","effect":{"operation":"prevent_damage"}},
            {"name":"격노","trigger":"after_defending_unit_receives_hp_damage","effect":{"operation":"gain_ap"}},
        ]
        rows = [
            {"card_id":"card-a","name":"두랄의기사","source_card_url":"https://example.test/a",
             "source_field":"Skill2","source_name":"홀리오오라","mapping_status":"inferred",
             "evidence_references_json":'[{"kind":"card_text_inference","evidenceCount":1,"references":[{"cardId":"card-a","effectText":"방어시 피해를 받지 않는다."}]}]'},
            {"card_id":"card-b","name":"헬블레이드","source_card_url":"https://example.test/b",
             "source_field":"Skill2","source_name":"격노","mapping_status":"inferred",
             "evidence_references_json":'[{"kind":"card_text_evidence_missing","evidenceCount":0,"references":[]}]'},
            {"card_id":"card-c","name":"무관","source_card_url":"https://example.test/c",
             "source_field":"Skill1","source_name":"홀리오오라","mapping_status":"inferred",
             "evidence_references_json":"[]"},
        ]
        result = build_skill2_execution_review_rows(rows,rules)
        self.assertEqual(len(result),2)
        by_name={x["source_name"]:x for x in result}
        self.assertEqual(by_name["홀리오오라"]["verification_status"],
                         "card_source_excerpt_available_pending_semantic_review")
        self.assertEqual(by_name["홀리오오라"]["execution_rule"]["effect"]["operation"],"prevent_damage")
        self.assertEqual(by_name["격노"]["verification_status"],"card_source_excerpt_missing")
        self.assertFalse(any(x["verification_status"]=="source_card_verified" for x in result))


if __name__=="__main__":
    unittest.main()
