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
    candidate = {}
    runtime = {}
    inference = []
    fallback = False
    neutral_upkeep = 0
    mu_crosswalk_inferred = False

    def add(target, key, amount):
        target[key] = target.get(key, 0) + amount

    tokens = parsed.get("tokens") or []
    for token in tokens:
        status = token.get("status")
        amount = max(0, int(token.get("count") or 0))
        code = token.get("code")
        color = token.get("normalized_color")
        if status == "no_cost" or amount == 0:
            continue

        if code in {11, 21, 31, 41, 51, 61, 71} and color in {
            "dark", "fire", "water", "forest", "iron", "earth", "light"
        }:
            add(candidate, color, amount)
            add(runtime, "metal" if color == "iron" else color, amount)
        elif code == 81 or (code is None and color == "neutral" and status == "text_decoded"):
            # MU(81) is the inferred crosswalk to the Manual's colorless bead.
            # The rule is direct; icon identity still needs visual verification.
            add(candidate, "neutral", amount)
            add(runtime, "neutral", amount)
            mu_crosswalk_inferred = True
            inference.append("mu_81_manual_neutral_bead_crosswalk_inferred")
            if card.get("card_type") == "유닛":
                neutral_upkeep += amount
        elif code == 82 or color == "ncs":
            add(candidate, "ncs", amount)
            # Preserve source identity. This generic payment is a tagged
            # playability fallback, not a claim that NCS means neutral.
            add(runtime, "neutral", amount)
            inference.append("ncs_requiresoul_semantics_unverified_generic_fallback")
            fallback = True
        elif code == 83 or color == "bonus":
            add(candidate, "bonus", amount)
            add(runtime, "neutral", amount)
            inference.append("bonus_requiresoul_semantics_unverified_generic_fallback")
            fallback = True
        elif status == "hybrid_payment_unverified" or (isinstance(color, str) and "+" in color):
            add(candidate, "hybrid:" + str(color), amount)
            # A pair icon is one source token. Do not charge both colors until
            # the payment choice (both vs either) is independently proven.
            add(runtime, "neutral", amount)
            inference.append("hybrid_payment_semantics_unverified_generic_fallback")
            fallback = True
        elif color in {"dark", "fire", "water", "forest", "iron", "earth", "light"}:
            add(candidate, color, amount)
            add(runtime, "metal" if color == "iron" else color, amount)
        elif color == "neutral":
            add(candidate, "neutral", amount)
            add(runtime, "neutral", amount)
            if card.get("card_type") == "유닛":
                neutral_upkeep += amount
            mu_crosswalk_inferred = True
            inference.append("text_neutral_bead_upkeep_crosswalk_inferred")
        else:
            add(candidate, str(color or "unknown"), amount)
            add(runtime, "neutral", amount)
            inference.append("unknown_source_token_generic_payable_fallback")
            fallback = True

    if not parsed.get("known") and not tokens:
        add(runtime, "neutral", 1)
        inference.append("missing_or_invalid_source_cost_conservative_payable_fallback")
        fallback = True

    if not runtime:
        if parsed.get("known"):
            runtime = {"neutral": 0}
        else:
            runtime = {"neutral": 1}
            inference.append("missing_source_cost_conservative_payable_fallback")
            fallback = True

    allowed = {"dark", "fire", "water", "forest", "metal", "earth", "light", "neutral"}
    for key, value in runtime.items():
        if key not in allowed or not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid runtime cost for {card.get('card_id')}: {key}={value}")

    source_review = bool(
        (cost_row and (cost_row.get("mapping_review") or cost_row.get("semantic_review")))
        or fallback
    )
    status = "fallback_payable" if fallback else (
        "implemented_inferred" if mu_crosswalk_inferred or source_review else "implemented_verified"
    )
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
        "sourceTokens": tokens,
        "candidateCost": candidate,
        "runtimeCost": runtime,
        "runtimeCostStatus": status,
        "runtimeCostInference": sorted(set(inference)),
        "runtimeUpkeepCost": {"neutral": neutral_upkeep},
        "runtimeUpkeepStatus": "mu_81_manual_neutral_crosswalk_inferred" if neutral_upkeep else "zero_upkeep",
        "playable": True
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
        cards = [dict(r) for r in db.execute("SELECT card_id,name,card_type,attribute FROM cards ORDER BY card_id")]
        costs = {r["card_id"]: dict(r) for r in db.execute("SELECT * FROM card_costs")}
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
        ({"card_id":"a","name":"dark","card_type":"유닛"}, {"source_text":"1101","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"dark":1}, "implemented_verified", 0),
        ({"card_id":"b","name":"mu","card_type":"유닛"}, {"source_text":"8102","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"neutral":2}, "implemented_inferred", 2),
        ({"card_id":"c","name":"ncs","card_type":"유닛"}, {"source_text":"8201","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {"neutral":1}, "fallback_payable", 0),
        ({"card_id":"d","name":"bonus","card_type":"아이템"}, {"source_text":"8301","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {"neutral":1}, "fallback_payable", 0),
        ({"card_id":"e","name":"hybrid","card_type":"유닛"}, {"source_text":"1201","mapping_review":1,"semantic_review":0,"verification_status":"mapping_review"}, {"neutral":1}, "fallback_payable", 0),
        ({"card_id":"f","name":"mixed","card_type":"유닛"}, {"source_text":"810182018301","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {"neutral":3}, "fallback_payable", 1),
        ({"card_id":"g","name":"no-cost","card_type":"마법"}, {"source_text":"0100","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"neutral":0}, "implemented_verified", 0),
        ({"card_id":"h","name":"unknown","card_type":"유닛"}, {"source_text":"9901","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {"neutral":1}, "fallback_payable", 0),
        ({"card_id":"i","name":"missing-cost","card_type":"마법"}, None, {"neutral":1}, "fallback_payable", 0)
    ]
    for card, row, expected, status, upkeep in cases:
        result = profile_for_card(card, row)
        assert result["runtimeCost"] == expected, (result, expected)
        assert result["runtimeCostStatus"] == status, (result, status)
        assert result["runtimeUpkeepCost"] == {"neutral": upkeep}, result
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
