#!/usr/bin/env python3
"""Independent source-Release join for the 831-card RequireSoul visual audit."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path


def raw_of(row: dict) -> dict:
    value = row.get("raw_payload")
    return value if isinstance(value, dict) else row


def card_id_of(row: dict) -> str:
    raw = raw_of(row)
    return str(row.get("card_id") or row.get("id") or raw.get("ID") or "").strip()


def require_soul_of(row: dict) -> str:
    raw = raw_of(row)
    value = raw.get("RequireSoul", row.get("requireSoul"))
    return str(value or "")


def parse_tokens(value: str) -> list[str]:
    if not value or not value.isdigit() or len(value) % 4:
        return []
    return [value[i:i + 4] for i in range(0, len(value), 4)]


def read_jsonl(path: Path):
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if line.strip():
                try:
                    yield json.loads(line)
                except json.JSONDecodeError as exc:
                    raise SystemExit(f"{path}:{line_no}: invalid JSON: {exc}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--source-cards-jsonl", type=Path, required=True)
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)

    source = {}
    duplicate_ids = []
    for row in read_jsonl(args.source_cards_jsonl):
        cid = card_id_of(row)
        if not cid:
            continue
        if cid in source:
            duplicate_ids.append(cid)
        source[cid] = require_soul_of(row)
    if duplicate_ids:
        raise SystemExit(f"Duplicate source card IDs: {duplicate_ids[:10]}")

    target = {}
    for row in read_jsonl(args.evidence_dir / "target-cards.jsonl"):
        cid = str(row.get("card_id", ""))
        if cid in target:
            raise SystemExit(f"Duplicate target card ID: {cid}")
        target[cid] = row
    if len(target) != 831:
        raise SystemExit(f"Expected 831 target cards, got {len(target)}")

    rail_path = out / "require-soul-rail-card-audit.csv"
    hybrid_path = out / "require-soul-hybrid-orb-audit.csv"
    # The visual scripts run first and produce their CSVs in this same output folder.
    rail = {r["card_id"]: r for r in csv.DictReader(rail_path.open(encoding="utf-8-sig"))}
    hybrid = {r["card_id"]: r for r in csv.DictReader(hybrid_path.open(encoding="utf-8-sig"))}
    if len(rail) != 831 or len(hybrid) != 52:
        raise SystemExit(f"Visual output cardinality mismatch: rail={len(rail)}, hybrid={len(hybrid)}")

    fields = ["card_id", "name", "source_require_soul_evidence", "source_require_soul_release",
              "source_row_found", "raw_string_match", "token_sequence_match",
              "visual_status", "visual_scope", "result"]
    rows, counts = [], Counter()
    for cid, evidence_row in sorted(target.items()):
        expected = str(evidence_row.get("source_require_soul", ""))
        actual = source.get(cid)
        found = cid in source
        raw_match = found and actual == expected
        token_match = raw_match and parse_tokens(actual) == [str(t["raw"]) for t in evidence_row.get("all_tokens", [])]
        if cid in hybrid:
            visual = hybrid[cid]["status"]
            scope = "HYBRID_FULL_SEQUENCE"
        else:
            visual = rail.get(cid, {}).get("status", "VISUAL_ROW_MISSING")
            scope = "SPECIAL_TOKEN_RAIL"
        result = "SOURCE_AND_VISUAL_MATCH" if raw_match and token_match and visual in (
            "EXACT_COUNT_MATCH", "FULL_SEQUENCE_MATCH", "FULL_SEQUENCE_MATCH_MANUAL_HYBRID"
        ) else "SOURCE_MATCH_VISUAL_UNRESOLVED" if raw_match and token_match else "SOURCE_JOIN_MISMATCH"
        counts[result] += 1
        rows.append({
            "card_id": cid, "name": evidence_row.get("name", ""),
            "source_require_soul_evidence": expected, "source_require_soul_release": actual or "",
            "source_row_found": found, "raw_string_match": raw_match,
            "token_sequence_match": token_match, "visual_status": visual,
            "visual_scope": scope, "result": result,
        })

    with (out / "require-soul-source-join-audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "source_release_tag": "fm1-carddb-29",
        "source_card_rows": len(source),
        "target_cards": len(target),
        "visual_rows": len(rail),
        "hybrid_visual_rows": len(hybrid),
        "duplicate_source_ids": len(duplicate_ids),
        "counts": dict(counts),
        "source_join_complete": all(r["source_row_found"] and r["raw_string_match"] and r["token_sequence_match"] for r in rows),
        "interpretation": "This is an independent join against the original DB29 Release cards.jsonl.gz. SOURCE_MATCH_VISUAL_UNRESOLVED means the original RequireSoul string and token sequence match exactly but image evidence remains unresolved.",
    }
    (out / "require-soul-source-join-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    if not summary["source_join_complete"]:
        raise SystemExit("At least one target card failed the independent DB29 source join")


if __name__ == "__main__":
    main()
