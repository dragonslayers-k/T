#!/usr/bin/env python3
"""Decode RequireSoul tokens without overstating independent cost validation."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

try:
    from soul_costs import parse_require_soul
except ImportError:
    from scripts.soul_costs import parse_require_soul

CATEGORY_NAMES = {"1": "land", "2": "unit", "3": "spell", "4": "item", "5": "enchant"}


def raw_of(row):
    value = row.get("raw_payload")
    return value if isinstance(value, dict) else row.get("sourceFields") or row


def card_type(row, raw):
    return row.get("type") or CATEGORY_NAMES.get(str(raw.get("Category", "")), "unknown")


def normalized_source_cost(row):
    value = row.get("cost")
    if row.get("costKnown") and isinstance(value, dict):
        try:
            return {str(k): int(v) for k, v in value.items() if int(v)}
        except (TypeError, ValueError):
            return None
    return None


def canonical_cost(cost):
    """Normalize the legacy 'metal' alias to the DB's canonical 'iron' key."""
    result = dict(cost)
    if "metal" in result:
        result["iron"] = result.get("iron", 0) + result.pop("metal")
    return {k: int(v) for k, v in result.items() if int(v)}


def run(rows):
    decoded, unresolved, validated, mismatches = [], [], 0, []
    hybrid_rows = special_rows = reference_rows = 0

    for index, row in enumerate(rows):
        raw = raw_of(row)
        source = raw.get("RequireSoul", row.get("soulCostRaw"))
        parsed = parse_require_soul(source)
        card_id = str(row.get("card_id") or row.get("id") or raw.get("ID") or raw.get("NumID") or index)
        # Use only a URL that came from the source record. Never synthesize it.
        detail_url = row.get("source_card_url") or row.get("sourceCardUrl")

        if not parsed["known"]:
            unresolved.append({
                "cardId": card_id,
                "name": row.get("name") or raw.get("Name", ""),
                "type": card_type(row, raw),
                "rawRequireSoul": source,
                "reason": parsed["error_reason"] or "unresolved_token",
                "sourceCardUrl": detail_url,
            })
            continue

        value = {k: v for k, v in parsed["colors"].items() if v}
        existing = normalized_source_cost(row)
        if row.get("costKnown") and existing is not None:
            reference_rows += 1
            expected = canonical_cost(existing)
            if expected != canonical_cost(value):
                mismatches.append({
                    "cardId": card_id,
                    "rawRequireSoul": source,
                    "existingCost": expected,
                    "decodedCost": canonical_cost(value),
                })
            else:
                validated += 1

        if parsed["mapping_review"]:
            hybrid_rows += 1
        if parsed["semantic_review"]:
            special_rows += 1

        decoded.append({
            "cardId": card_id,
            "name": row.get("name") or raw.get("Name", ""),
            "type": card_type(row, raw),
            "rawRequireSoul": source,
            "decodedCost": value,
            "costValueStatus": (
                "mapping_review" if parsed["mapping_review"]
                else "semantic_review" if parsed["semantic_review"]
                else "decoded_source"
            ),
            "mappingReview": parsed["mapping_review"],
            "specialSemanticsReview": parsed["semantic_review"],
            "confidence": "token_identity_known",
            "sourceCardUrl": detail_url,
        })

    validation_status = (
        "mismatch" if mismatches
        else "matched_reference_rows" if validated
        else "not_available_no_reference_costs"
    )
    return {
        "decoded": decoded,
        "unresolved": unresolved,
        "validatedKnownCosts": validated,
        "referenceCostRows": reference_rows,
        "knownCostMismatches": mismatches,
        "hybridMappingReviewRecords": hybrid_rows,
        "specialSemanticsReviewRecords": special_rows,
        "validationStatus": validation_status,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards-jsonl", type=Path)
    parser.add_argument("--cards-json", type=Path)
    parser.add_argument("--output-dir", type=Path, default=Path("cost-decoding"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        hybrid = parse_require_soul("43017101")
        assert hybrid["known"] and hybrid["mapping_review"]
        assert hybrid["colors"]["forest"] == 1 and hybrid["colors"]["light"] == 2
        assert parse_require_soul("5301")["colors"]["iron"] == 1
        assert parse_require_soul("8201")["colors"]["ncs"] == 1
        assert parse_require_soul("8301")["colors"]["bonus"] == 1
        sample = run([{"card_id": "x", "raw_payload": {"RequireSoul": "7101"}, "source_card_url": "https://source.example/card/x"}])
        assert sample["validationStatus"] == "not_available_no_reference_costs"
        assert sample["decoded"][0]["sourceCardUrl"] == "https://source.example/card/x"
        assert sample["validatedKnownCosts"] == 0
        print("RequireSoul decoder self-test passed")
        return

    if bool(args.cards_jsonl) == bool(args.cards_json):
        parser.error("provide exactly one of --cards-jsonl or --cards-json")
    if args.cards_jsonl:
        rows = [
            json.loads(line)
            for line in args.cards_jsonl.read_text(encoding="utf-8").splitlines()
            if line.strip()
        ]
    else:
        rows = json.loads(args.cards_json.read_text(encoding="utf-8"))

    result = run(rows)
    args.output_dir.mkdir(parents=True, exist_ok=True)
    for key in ("decoded", "unresolved"):
        (args.output_dir / f"requiresoul-{key}.json").write_text(
            json.dumps(result[key], ensure_ascii=False, indent=2), encoding="utf-8"
        )

    summary = {
        "inputRecords": len(rows),
        "decodedRecords": len(result["decoded"]),
        "unresolvedRecords": len(result["unresolved"]),
        "specialSemanticsReviewRecords": result["specialSemanticsReviewRecords"],
        "hybridMappingReviewRecords": result["hybridMappingReviewRecords"],
        "referenceCostRows": result["referenceCostRows"],
        "validatedKnownCosts": result["validatedKnownCosts"],
        "validationStatus": result["validationStatus"],
        "knownCostMismatches": result["knownCostMismatches"],
        "decodedSha256": hashlib.sha256(
            json.dumps(result["decoded"], ensure_ascii=False, sort_keys=True).encode()
        ).hexdigest(),
    }
    (args.output_dir / "requiresoul-decoding-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False))
    if result["knownCostMismatches"]:
        raise SystemExit("Known normalized costs disagree with deterministic decoder.")


if __name__ == "__main__":
    main()
