#!/usr/bin/env python3
"""Audit field applicability against immutable raw card payloads.

This is intentionally independent of normalized card_fields: normalization gaps
must not cause a field to be declared not-applicable for an entire category.
"""
import argparse
import json
import sqlite3
from collections import defaultdict
from pathlib import Path


def is_populated(value):
    return value is not None and not (isinstance(value, str) and not value.strip())


def audit_raw_applicability(db_path):
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    cards = db.execute(
        "SELECT card_id, card_type, raw_payload_json FROM cards ORDER BY card_id"
    ).fetchall()
    category_totals = defaultdict(int)
    field_counts = defaultdict(lambda: {"present": 0, "populated": 0, "empty": 0})
    examples = defaultdict(list)

    for card in cards:
        payload = json.loads(card["raw_payload_json"] or "{}")
        category = payload.get("Category")
        category_totals[category] += 1
        for field, value in payload.items():
            key = (category, field)
            field_counts[key]["present"] += 1
            if is_populated(value):
                field_counts[key]["populated"] += 1
            else:
                field_counts[key]["empty"] += 1
            if len(examples[key]) < 5:
                examples[key].append(card["card_id"])

    rows = []
    fields = sorted({field for _, field in field_counts})
    for category, total in sorted(category_totals.items(), key=lambda x: str(x[0])):
        for field in fields:
            counts = field_counts.get((category, field), {"present": 0, "populated": 0, "empty": 0})
            if counts["present"] == 0:
                status = "raw_absent_in_category"
            elif counts["populated"] == 0:
                status = "raw_present_but_empty_in_category"
            elif counts["present"] < total:
                status = "raw_presence_varies_in_category"
            else:
                status = "raw_present_in_all_category_cards"
            rows.append({
                "source_category": category,
                "card_type": next((c["card_type"] for c in cards
                                   if json.loads(c["raw_payload_json"] or "{}").get("Category") == category), None),
                "field_key": field,
                "category_card_count": total,
                "raw_key_present_count": counts["present"],
                "raw_populated_count": counts["populated"],
                "raw_empty_or_null_count": counts["empty"],
                "raw_applicability_status": status,
                "example_card_ids": examples.get((category, field), []),
                "basis": "immutable_cards.raw_payload_json"
            })
    db.close()
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    rows = audit_raw_applicability(args.db)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(
        "".join(json.dumps(row, ensure_ascii=False) + "\n" for row in rows),
        encoding="utf-8"
    )
    print(json.dumps({"categories": len({r["source_category"] for r in rows}),
                      "field_category_rows": len(rows), "output": str(args.out)},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
