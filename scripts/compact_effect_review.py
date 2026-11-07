#!/usr/bin/env python3
"""Build a compact, source-linked CSV and summary from effect review JSONL."""
from __future__ import annotations

import argparse
import csv
import json
import os
from collections import Counter
from pathlib import Path

COLUMNS = [
    "card_id", "name", "card_type", "clause_index", "confidence",
    "classification", "segment_text", "source_detail_url", "verification_status",
]


def build(input_path: Path, csv_path: Path, summary_path: Path) -> dict:
    rows = []
    for line in input_path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        source = json.loads(line)
        try:
            interpretation = json.loads(source.get("interpretation_json") or "{}")
        except (TypeError, json.JSONDecodeError):
            interpretation = {}
        rows.append({
            "card_id": source.get("card_id", ""),
            "name": source.get("name", ""),
            "card_type": source.get("card_type", ""),
            "clause_index": source.get("clause_index", ""),
            "confidence": source.get("confidence", ""),
            "classification": interpretation.get("classification", "unknown"),
            "segment_text": source.get("segment_text", ""),
            "source_detail_url": source.get("source_detail_url", ""),
            "verification_status": source.get("verification_status", ""),
        })

    csv_path.parent.mkdir(parents=True, exist_ok=True)
    with csv_path.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=COLUMNS)
        writer.writeheader()
        writer.writerows(rows)

    pattern_counts = Counter(" ".join(row["segment_text"].split()) or "(empty)" for row in rows)
    classification_counts = Counter(row["classification"] for row in rows)
    summary = {
        "rows": len(rows),
        "unique_card_ids": len({row["card_id"] for row in rows}),
        "unique_text_patterns": len(pattern_counts),
        "classification_counts": dict(sorted(classification_counts.items())),
        "top_text_patterns": [
            {"text": text, "count": count} for text, count in pattern_counts.most_common(20)
        ],
        "csv": csv_path.name,
        "note": "Rows are review candidates, not proof of incorrect semantics or engine behavior.",
    }
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    return summary


def write_step_summary(summary: dict, path: Path) -> None:
    with path.open("a", encoding="utf-8") as handle:
        handle.write("## Compact effect review queue\n\n")
        handle.write(f"- Rows: {summary['rows']}\n")
        handle.write(f"- Unique card IDs: {summary['unique_card_ids']}\n")
        handle.write(f"- Unique text patterns: {summary['unique_text_patterns']}\n")
        handle.write("- Classification counts: " + json.dumps(summary["classification_counts"], ensure_ascii=False) + "\n")
        handle.write("\nFull card-level source text and URLs are in the compact CSV artifact.\n")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--step-summary", type=Path)
    args = parser.parse_args()
    summary = build(args.input, args.csv, args.summary)
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    step_summary = args.step_summary or (Path(os.environ["GITHUB_STEP_SUMMARY"]) if os.getenv("GITHUB_STEP_SUMMARY") else None)
    if step_summary:
        write_step_summary(summary, step_summary)


if __name__ == "__main__":
    main()
