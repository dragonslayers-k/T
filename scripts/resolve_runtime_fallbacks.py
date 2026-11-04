#!/usr/bin/env python3
"""Read source-first runtime values from an FM1 SQLite database.

The resolver is intentionally read-only. Source payload values remain authoritative;
the additive runtime_fallbacks table supplies values only when a source field is
missing or JSON null. Every resolved fallback carries its provenance metadata.
"""
import argparse
import json
import sqlite3
from typing import Any


def resolve_field(db_path, card_id: str, field_key: str, rule_pack_id: str | None = None) -> dict[str, Any]:
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        card = db.execute("SELECT raw_payload_json FROM cards WHERE card_id=?", (str(card_id),)).fetchone()
        if card is None:
            raise KeyError(f"Unknown card_id: {card_id}")
        payload = json.loads(card["raw_payload_json"] or "{}")
        if field_key in payload and payload[field_key] is not None:
            return {
                "card_id": str(card_id), "field_key": field_key,
                "value": payload[field_key], "resolved_from": "source",
                "fallback_used": False, "provenance": None,
            }

        query = """
            SELECT fallback_value_json, fallback_kind, rationale, confidence,
                   evidence_json, rule_pack_id, rule_pack_sha256
            FROM runtime_fallbacks
            WHERE card_id=? AND field_key=?
        """
        args: list[Any] = [str(card_id), field_key]
        if rule_pack_id:
            query += " AND rule_pack_id=?"
            args.append(rule_pack_id)
        query += " ORDER BY CASE confidence WHEN 'high' THEN 0 WHEN 'medium' THEN 1 ELSE 2 END, created_at DESC LIMIT 1"
        row = db.execute(query, args).fetchone()
        if row is None:
            return {
                "card_id": str(card_id), "field_key": field_key,
                "value": None, "resolved_from": "missing",
                "fallback_used": False, "provenance": None,
            }
        return {
            "card_id": str(card_id), "field_key": field_key,
            "value": json.loads(row["fallback_value_json"]),
            "resolved_from": "runtime_fallback", "fallback_used": True,
            "provenance": {
                "kind": row["fallback_kind"], "rationale": row["rationale"],
                "confidence": row["confidence"], "evidence": json.loads(row["evidence_json"]),
                "rule_pack_id": row["rule_pack_id"], "rule_pack_sha256": row["rule_pack_sha256"],
            },
        }
    finally:
        db.close()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", required=True)
    parser.add_argument("--card-id", required=True)
    parser.add_argument("--field", required=True)
    parser.add_argument("--rule-pack-id")
    args = parser.parse_args()
    print(json.dumps(resolve_field(args.db, args.card_id, args.field, args.rule_pack_id),
                     ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
