#!/usr/bin/env python3
"""Decode the documented four-character RequireSoul token format without guessing.

Known token IDs are validated against the existing normalized costs before being
used. Unknown/special token families remain in a review queue; they are never
coerced to zero or estimated by this decoder.
"""
from __future__ import annotations
import argparse, collections, hashlib, json
from pathlib import Path

COLOR_CODES = {
    "11": "dark", "21": "fire", "31": "water", "41": "forest",
    "51": "metal", "61": "earth", "71": "light", "81": "neutral",
}
CATEGORY_NAMES = {"1": "land", "2": "unit", "3": "spell", "4": "item", "5": "enchant"}

def raw_of(row):
    value = row.get("raw_payload")
    return value if isinstance(value, dict) else row.get("sourceFields") or row

def card_type(row, raw):
    value = row.get("type")
    return value or CATEGORY_NAMES.get(str(raw.get("Category", "")), "unknown")

def decode(raw_value):
    raw = str(raw_value or "").strip()
    if not raw or len(raw) % 4:
        return None, "invalid_token_length"
    costs = collections.Counter()
    for offset in range(0, len(raw), 4):
        token = raw[offset:offset + 4]
        code, amount_text = token[:2], token[2:]
        if code == "01" and amount_text == "00":
            continue
        if code not in COLOR_CODES:
            return None, "unsupported_token_" + code
        if not amount_text.isdigit():
            return None, "invalid_amount"
        costs[COLOR_CODES[code]] += int(amount_text)
    return dict(sorted((k, v) for k, v in costs.items() if v)), None

def normalized_source_cost(row):
    value = row.get("cost")
    if row.get("costKnown") and isinstance(value, dict):
        return {k: int(v) for k, v in value.items() if int(v)}
    return None

def run(rows):
    decoded, unresolved, validated, mismatches = [], [], 0, []
    for index, row in enumerate(rows):
        raw = raw_of(row)
        source = raw.get("RequireSoul", row.get("soulCostRaw"))
        value, reason = decode(source)
        cid = str(row.get("id") or row.get("card_id") or raw.get("NumID") or index)
        if reason:
            unresolved.append({"cardId": cid, "name": row.get("name") or raw.get("Name", ""),
                               "type": card_type(row, raw), "rawRequireSoul": source,
                               "reason": reason, "sourceCardUrl": row.get("sourceCardUrl") or
                               ("https://fmlunatic.com/card/" + str(raw.get("NumID")) if raw.get("NumID") else None)})
            continue
        existing = normalized_source_cost(row)
        if existing is not None:
            if existing != value:
                mismatches.append({"cardId": cid, "rawRequireSoul": source,
                                   "existingCost": existing, "decodedCost": value})
            else:
                validated += 1
        decoded.append({"cardId": cid, "name": row.get("name") or raw.get("Name", ""),
                        "type": card_type(row, raw), "faction": row.get("faction"),
                        "rawRequireSoul": source, "decodedCost": value,
                        "costValueStatus": "decoded_source", "confidence": "exact",
                        "method": "RequireSoul-4char-token-v1",
                        "sourceCardUrl": row.get("sourceCardUrl") or
                        ("https://fmlunatic.com/card/" + str(raw.get("NumID")) if raw.get("NumID") else None)})
    return {"decoded": decoded, "unresolved": unresolved, "validatedKnownCosts": validated,
            "knownCostMismatches": mismatches}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--cards-jsonl", type=Path)
    p.add_argument("--cards-json", type=Path)
    p.add_argument("--output-dir", type=Path, default=Path("cost-decoding"))
    p.add_argument("--self-test", action="store_true")
    a = p.parse_args()
    if a.self_test:
        assert decode("71028104") == ({"light": 2, "neutral": 4}, None)
        assert decode("0100") == ({}, None)
        assert decode("8201")[1] == "unsupported_token_82"
        sample = [{"id":"x","soulCostRaw":"7101","cost":{"light":1},"costKnown":True}]
        result = run(sample)
        assert len(result["decoded"]) == 1 and result["validatedKnownCosts"] == 1
        print("RequireSoul decoder self-test passed")
        return
    if bool(a.cards_jsonl) == bool(a.cards_json):
        p.error("provide exactly one of --cards-jsonl or --cards-json")
    if a.cards_jsonl:
        rows = [json.loads(line) for line in a.cards_jsonl.read_text(encoding="utf-8").splitlines() if line.strip()]
    else:
        rows = json.loads(a.cards_json.read_text(encoding="utf-8"))
    result = run(rows)
    a.output_dir.mkdir(parents=True, exist_ok=True)
    for key in ("decoded", "unresolved"):
        (a.output_dir / f"requiresoul-{key}.json").write_text(
            json.dumps(result[key], ensure_ascii=False, indent=2), encoding="utf-8")
    summary = {"inputRecords": len(rows), "decodedRecords": len(result["decoded"]),
               "unresolvedRecords": len(result["unresolved"]),
               "validatedKnownCosts": result["validatedKnownCosts"],
               "knownCostMismatches": result["knownCostMismatches"],
               "decodedSha256": hashlib.sha256(json.dumps(result["decoded"], ensure_ascii=False, sort_keys=True).encode()).hexdigest()}
    (a.output_dir / "requiresoul-decoding-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False))
    if result["knownCostMismatches"]:
        raise SystemExit("Known normalized costs disagree with deterministic decoder; refusing to publish.")

if __name__ == "__main__":
    main()
