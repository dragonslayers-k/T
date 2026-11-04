#!/usr/bin/env python3
"""Compare semantic-review backlog with an explicit immutable audit baseline.

This reports movement only. A lower count is not semantic verification; each
resolution still needs source evidence and (where applicable) an engine test.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path

METRICS = {
    "effect_interpretation_low_confidence": "effect_interpretation_low_confidence",
    "name_only_skill_rules": "inferred_skill_name_only_rows",
    "hybrid_soul_payment_rules": "soul_mapping_review",
    "special_soul_payment_rules": "soul_semantic_review",
    "manual_rule_conflicts": "manual_rule_conflict_count",
}

def current_counts(report: dict) -> dict:
    pending = report.get("semantic_review_pending") or {}
    return {
        "effect_interpretation_low_confidence": int(
            pending.get("effect_interpretation_low_confidence",
                       report.get("effect_interpretation_low_confidence", 0)) or 0),
        "name_only_skill_rules": int(
            pending.get("name_only_skill_rules",
                       report.get("inferred_skill_name_only_rows", 0)) or 0),
        "hybrid_soul_payment_rules": int(
            pending.get("hybrid_soul_payment_rules",
                       report.get("soul_mapping_review", 0)) or 0),
        "special_soul_payment_rules": int(
            pending.get("special_soul_payment_rules",
                       report.get("soul_semantic_review", 0)) or 0),
        "manual_rule_conflicts": int(report.get("manual_rule_conflict_count", 0) or 0),
    }

def build_progress(report: dict, baseline: dict) -> dict:
    before = baseline["counts"]
    after = current_counts(report)
    metrics = {}
    for key in METRICS:
        old, new = int(before[key]), int(after[key])
        metrics[key] = {
            "baseline": old,
            "current": new,
            "resolved_count_delta": old - new,
            "status": "reduced" if new < old else "unchanged" if new == old else "increased",
        }
    reduced = sum(1 for x in metrics.values() if x["status"] == "reduced")
    increased = sum(1 for x in metrics.values() if x["status"] == "increased")
    return {
        "baseline_name": baseline.get("baseline_name"),
        "baseline_run": baseline.get("baseline_run"),
        "baseline_commit": baseline.get("baseline_commit"),
        "current_semantic_coverage_pass": bool(report.get("semantic_coverage_pass")),
        "current_semantic_completeness_pass": bool(report.get("semantic_completeness_pass")),
        "current_engine_verification_complete": bool(report.get("engine_verification_complete")),
        "metrics": metrics,
        "metrics_reduced": reduced,
        "metrics_increased": increased,
        "overall_status": "regression" if increased else "progress" if reduced else "no_change",
        "interpretation": (
            "Counts changed; inspect every resolution against source evidence."
            if reduced or increased else
            "No backlog reduction from the immutable baseline. This audit is structural verification, not semantic progress."
        ),
        "safety": "Count reduction alone never promotes a rule to verified or executable.",
    }

def main() -> None:
    p = argparse.ArgumentParser()
    p.add_argument("--report", type=Path, required=True)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--out", type=Path, required=True)
    a = p.parse_args()
    report = json.loads(a.report.read_text(encoding="utf-8"))
    baseline = json.loads(a.baseline.read_text(encoding="utf-8"))
    result = build_progress(report, baseline)
    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
