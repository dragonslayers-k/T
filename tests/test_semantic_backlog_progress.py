import unittest
from scripts.semantic_backlog_progress import build_progress

class SemanticBacklogProgressTests(unittest.TestCase):
    def setUp(self):
        self.baseline = {"baseline_name":"#432","baseline_run":432,"baseline_commit":"abc",
            "counts":{"effect_interpretation_low_confidence":206,"name_only_skill_rules":26,
            "hybrid_soul_payment_rules":52,"special_soul_payment_rules":779,"manual_rule_conflicts":1}}
    def report(self):
        return {"semantic_review_pending":{"effect_interpretation_low_confidence":206,
            "name_only_skill_rules":26,"hybrid_soul_payment_rules":52,
            "special_soul_payment_rules":779},"manual_rule_conflict_count":1,
            "semantic_coverage_pass":True,"semantic_completeness_pass":False,
            "engine_verification_complete":False}
    def test_unchanged_backlog_is_explicitly_no_change(self):
        result=build_progress(self.report(),self.baseline)
        self.assertEqual(result["overall_status"],"no_change")
        self.assertEqual(result["metrics_reduced"],0)
        self.assertEqual(result["metrics"]["special_soul_payment_rules"]["resolved_count_delta"],0)
    def test_only_actual_count_reduction_is_reported_as_progress(self):
        report=self.report()
        report["semantic_review_pending"]["effect_interpretation_low_confidence"]=190
        result=build_progress(report,self.baseline)
        self.assertEqual(result["overall_status"],"progress")
        self.assertEqual(result["metrics"]["effect_interpretation_low_confidence"]["resolved_count_delta"],16)
        self.assertEqual(result["metrics_reduced"],1)
    def test_increased_backlog_is_regression_even_if_another_metric_falls(self):
        report=self.report()
        report["semantic_review_pending"]["effect_interpretation_low_confidence"]=200
        report["semantic_review_pending"]["special_soul_payment_rules"]=800
        result=build_progress(report,self.baseline)
        self.assertEqual(result["overall_status"],"regression")
        self.assertEqual(result["metrics_increased"],1)
    def test_pending_counts_fall_back_to_audit_report_fields(self):
        report={"effect_interpretation_low_confidence":205,"inferred_skill_name_only_rows":26,
            "soul_mapping_review":52,"soul_semantic_review":779,"manual_rule_conflict_count":1}
        result=build_progress(report,self.baseline)
        self.assertEqual(result["metrics"]["effect_interpretation_low_confidence"]["status"],"reduced")

if __name__ == "__main__":
    unittest.main()
