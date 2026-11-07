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
    blocked = False
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
            # Preserve source identity; no payment rule is inferred.
            inference.append("ncs_requiresoul_semantics_unverified_blocked")
            blocked = True
        elif code == 83 or color == "bonus":
            add(candidate, "bonus", amount)
            inference.append("bonus_requiresoul_semantics_unverified_blocked")
            blocked = True
        elif status == "hybrid_payment_unverified" or (isinstance(color, str) and "+" in color):
            add(candidate, "hybrid:" + str(color), amount)
            # A pair icon is one source token; payment is blocked until its
            # both-vs-either semantics are established from authoritative rules.
            inference.append("hybrid_payment_semantics_unverified_blocked")
            blocked = True
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
            inference.append("unknown_source_token_blocked")
            blocked = True

    source_review = bool(
        (cost_row and (cost_row.get("mapping_review") or cost_row.get("semantic_review")))
        or parsed.get("mapping_review") or parsed.get("semantic_review")
    )
    if not parsed.get("known") or source_review:
        blocked = True
        inference.append("unresolved-requiresoul-cost-blocked")

    if not runtime and not blocked:
        runtime = {"neutral": 0}
    if blocked:
        runtime = {}

    allowed = {"dark", "fire", "water", "forest", "metal", "earth", "light", "neutral"}
    for key, value in runtime.items():
        if key not in allowed or not isinstance(value, int) or value < 0:
            raise ValueError(f"Invalid runtime cost for {card.get('card_id')}: {key}={value}")

    status = "semantic_review_blocked" if blocked else (
        "implemented_inferred" if mu_crosswalk_inferred else "implemented_verified"
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
        "runtimeCostKnown": not blocked,
        "runtimeCostStatus": status,
        "runtimeCostInference": sorted(set(inference)),
        "runtimeUpkeepCost": {"neutral": neutral_upkeep},
        "runtimeUpkeepStatus": "mu_81_manual_neutral_crosswalk_inferred" if neutral_upkeep else "zero_upkeep",
        "playable": not blocked
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
                "sourceReviewBlocksPlayability": True,
                "ncsPayment": "blocked-until-source-semantics-verified",
                "bonusPayment": "blocked-until-source-semantics-verified",
                "hybridPayment": "blocked-until-both-vs-either-payment-is-verified",
                "unknownCost": "blocked-no-generic-neutral-fallback",
                "db29Modified": False,
                "db30Published": False
            },
            "cards": profiles
        }
    finally:
        db.close()


def self_test():
    cases = [
        ({"card_id":"a","name":"dark","card_type":"유닛"}, {"source_text":"1101","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"dark":1}, "implemented_verified", 0, True),
        ({"card_id":"b","name":"mu","card_type":"유닛"}, {"source_text":"8102","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"neutral":2}, "implemented_inferred", 2, True),
        ({"card_id":"c","name":"ncs","card_type":"유닛"}, {"source_text":"8201","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {}, "semantic_review_blocked", 0, False),
        ({"card_id":"d","name":"bonus","card_type":"아이템"}, {"source_text":"8301","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {}, "semantic_review_blocked", 0, False),
        ({"card_id":"e","name":"hybrid","card_type":"유닛"}, {"source_text":"1201","mapping_review":1,"semantic_review":0,"verification_status":"mapping_review"}, {}, "semantic_review_blocked", 0, False),
        ({"card_id":"f","name":"mixed","card_type":"유닛"}, {"source_text":"810182018301","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {}, "semantic_review_blocked", 1, False),
        ({"card_id":"g","name":"no-cost","card_type":"마법"}, {"source_text":"0100","mapping_review":0,"semantic_review":0,"verification_status":"enum_decoded"}, {"neutral":0}, "implemented_verified", 0, True),
        ({"card_id":"h","name":"unknown","card_type":"유닛"}, {"source_text":"9901","mapping_review":0,"semantic_review":1,"verification_status":"semantic_review"}, {}, "semantic_review_blocked", 0, False),
        ({"card_id":"i","name":"missing-cost","card_type":"마법"}, None, {}, "semantic_review_blocked", 0, False)
    ]
    for card, row, expected, status, upkeep, playable in cases:
        result = profile_for_card(card, row)
        assert result["runtimeCost"] == expected, (result, expected)
        assert result["runtimeCostStatus"] == status, (result, status)
        assert result["runtimeCostKnown"] is playable, result
        assert result["runtimeUpkeepCost"] == {"neutral": upkeep}, result
        assert result["playable"] is playable, result
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
