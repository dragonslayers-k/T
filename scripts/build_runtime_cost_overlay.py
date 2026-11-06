#!/usr/bin/env python3
"""Build a separate, playable runtime-cost overlay from DB29 source values."""
import argparse
import hashlib
import json
import sqlite3
from collections import Counter
from pathlib import Path

from soul_costs import parse_require_soul


def profile_for_card(card, cost_row):
    raw = cost_row["source_text"] if cost_row else None
    parsed = parse_require_soul(raw)
    colors = parsed.get("colors") or {}
    runtime = {}
    inference = []
    fallback = False

    for source_color, raw_amount in colors.items():
        amount = int(raw_amount or 0)
        if amount < 0:
            fallback = True
            continue
        if source_color == "ncs":
            runtime["neutral"] = runtime.get("neutral", 0) + amount
        elif source_color == "bonus":
            # Inferred: BONUS is a separate one-time generic requirement.
            # Keep its identity separate from NCS so it does not inherit
            # Manual's unit-only recurring NCS upkeep rule.
            runtime["bonus"] = runtime.get("bonus", 0) + amount
            inference.append("bonus_generic_one_time_payment")
        elif source_color == "iron":
            runtime["metal"] = runtime.get("metal", 0) + amount
        else:
            runtime[source_color] = runtime.get(source_color, 0) + amount

    for token in parsed.get("tokens") or []:
        status = token.get("status")
        if status == "inferred_hybrid_both_colors":
            inference.append("hybrid_requires_both_component_colors")
        elif status == "manual_review":
            amount = max(1, int(token.get("amount") or 1))
            runtime["neutral"] = runtime.get("neutral", 0) + amount
            inference.append("unknown_token_conservative_payable_fallback")
            fallback = True

    if not parsed.get("known") and not any(t.get("status") == "manual_review" for t in parsed.get("tokens", [])):
        runtime["neutral"] = runtime.get("neutral", 0) + 1
        inference.append("missing_or_invalid_source_cost_conservative_payable_fallback")
        fallback = True

    if not runtime:
        if parsed.get("known"):
            runtime = {"neutral": 0}  # Explicit source no-cost token.
        else:
            runtime = {"neutral": 1}
            inference.append("missing_source_cost_conservative_payable_fallback")
            fallback = True

    for key, value in runtime.items():
        if not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid runtime cost for {card.get('card_id')}: {key}={value}")

    status = "fallback_payable" if fallback else ("implemented_inferred" if inference else "implemented_verified")
    return {
        "cardId": str(card["card_id"]),
        "name": str(card.get("name") or ""),
        "cardType": str(card.get("card_type") or ""),
        "attribute": str(card.get("attribute") or ""),
        "sourceRequireSoul": raw,
        "sourceParseKnown": bool(parsed.get("known")),
        "sourceMappingReview": bool(cost_row and cost_row.get("mapping_review")),
        "sourceSemanticReview": bool(cost_row and cost_row.get("semantic_review")),
        "sourceVerificationStatus": str(cost_row.get("verification_status") or "missing") if cost_row else "missing",
        "sourceTokens": parsed.get("tokens") or [],
        "runtimeCost": runtime,
        "runtimeCostStatus": status,
        "runtimeCostInference": sorted(set(inference)),
        "playable": True,
        "upkeepPolicy": {
            "neutral": "manual_unit_only_upkeep",
            "bonus": "one_time_only_no_upkeep_inference"
        }
    }


def build_overlay(db_path):
    digest = hashlib.sha256()
    with db_path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    db = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise RuntimeError(f"DB29 SQLite integrity_check failed: {integrity}")
        cards = db.execute("SELECT card_id,name,card_type,attribute FROM cards ORDER BY card_id").fetchall()
        costs = {r["card_id"]: r for r in db.execute("SELECT * FROM card_costs")}
        profiles = [profile_for_card(card, costs.get(card["card_id"])) for card in cards]
        ids = [p["cardId"] for p in profiles]
        if len(profiles) != 15350 or len(set(ids)) != len(ids):
            raise RuntimeError(f"Runtime overlay population mismatch: {len(profiles)} cards / {len(set(ids))} unique IDs")
        statuses = Counter(p["runtimeCostStatus"] for p in profiles)
        token_counts = Counter()
        for profile in profiles:
            for token in profile["sourceTokens"]:
                token_counts[str(token.get("status") or "unknown")] += 1
        return {
            "schemaVersion": 1,
            "sourceReleaseTag": "fm1-carddb-29",
            "sourceDbSha256": digest.hexdigest(),
            "sourceCardCount": len(cards),
            "runtimeProfileCount": len(profiles),
            "playableProfileCount": sum(1 for p in profiles if p["playable"]),
            "runtimeCostStatusCounts": dict(statuses),
            "sourceTokenStatusCounts": dict(token_counts),
            "policy": {
                "sourceValuesImmutable": True,
                "sourceReviewSeparateFromPlayability": True,
                "ncsPayment": "any-colored-or-neutral-soul; unit-only-recurring-upkeep",
                "bonusPayment": "generic-any-generated-soul-once; no-recurring-upkeep-inference",
                "hybridPayment": "all-component-colors-required-inference",
                "unknownCost": "conservative-payable-neutral-fallback",
                "db29Modified": False,
                "db30Published": False
            },
            "cards": profiles
        }
    finally:
        db.close()


def self_test():
    cases = [
        ({"card_id":"a","name":"dark","card_type":"유닛"}, {"source_text":"1101","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"dark":1}, "implemented_verified"),
        ({"card_id":"b","name":"ncs","card_type":"유닛"}, {"source_text":"8201","mapping_review":0,"semantic_review":0,"verification_status":"manual_semantics_verified"}, {"neutral":1}, "implemented_verified"),
        ({"card_id":"c","name":"bonus","card_type":"아이템"}, {"source_text":"11018301","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {"dark":1,"bonus":1}, "implemented_inferred"),
        ({"card_id":"d","name":"hybrid","card_type":"유닛"}, {"source_text":"1201","mapping_review":1,"semantic_review":0,"verification_status":"mapping_review"}, {"dark":1,"earth":1}, "implemented_inferred"),
        ({"card_id":"e","name":"no-cost","card_type":"마법"}, {"source_text":"0100","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"neutral":0}, "implemented_verified"),
        ({"card_id":"f","name":"unknown","card_type":"유닛"}, {"source_text":"9901","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {"neutral":1}, "fallback_payable")
    ]
    for card, row, expected, status in cases:
        result = profile_for_card(card, row)
        assert result["runtimeCost"] == expected, (result, expected)
        assert result["runtimeCostStatus"] == status, (result, status)
        assert result["playable"] is True
    print("runtime cost overlay self-test: PASS")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    if not args.db or not args.output:
        parser.error("--db and --output are required unless --self-test is used")
    result = build_overlay(args.db)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("sourceReleaseTag","sourceDbSha256","sourceCardCount","runtimeProfileCount","playableProfileCount","runtimeCostStatusCounts","sourceTokenStatusCounts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
