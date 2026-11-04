#!/usr/bin/env python3
"""Apply provenance-preserving gameplay fallbacks to an FM1 SQLite copy.

This never edits cards.raw_payload_json or card_fields. It writes a separate
runtime_fallbacks layer which engine adapters can consult before using source
values. Only rules supplied in a reviewed JSON pack are applied; unknown
semantics are intentionally not guessed by this generic layer.
"""
import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

SCHEMA = """
CREATE TABLE IF NOT EXISTS runtime_fallbacks (
  card_id TEXT NOT NULL REFERENCES cards(card_id),
  field_key TEXT NOT NULL,
  fallback_value_json TEXT NOT NULL,
  source_value_json TEXT,
  fallback_kind TEXT NOT NULL CHECK(fallback_kind IN ('inferred','safe_default','rule_pack')),
  rationale TEXT NOT NULL,
  confidence TEXT NOT NULL CHECK(confidence IN ('low','medium','high')),
  evidence_json TEXT NOT NULL DEFAULT '[]',
  rule_pack_id TEXT NOT NULL,
  rule_pack_sha256 TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  PRIMARY KEY(card_id, field_key, rule_pack_id)
);
CREATE INDEX IF NOT EXISTS idx_runtime_fallbacks_field
  ON runtime_fallbacks(field_key, fallback_kind);
"""

def apply(db_path: Path, pack_path: Path):
    pack_bytes = pack_path.read_bytes()
    pack = json.loads(pack_bytes)
    pack_id = pack.get("id")
    if not isinstance(pack_id, str) or not pack_id.strip():
        raise ValueError("Rule pack must include a non-empty id")
    rules = pack.get("rules")
    if not isinstance(rules, list):
        raise ValueError("Rule pack must include a rules array")
    digest = hashlib.sha256(pack_bytes).hexdigest()
    db = sqlite3.connect(db_path)
    db.execute("PRAGMA foreign_keys=ON")
    if db.execute("SELECT 1 FROM sqlite_master WHERE type='table' AND name='cards'").fetchone() is None:
        raise ValueError("Database does not contain cards table")
    db.executescript(SCHEMA)
    applied = 0
    for rule in rules:
        required = ("card_id", "field_key", "value", "rationale", "confidence")
        if any(k not in rule for k in required):
            raise ValueError(f"Rule missing required key(s): {rule}")
        if rule["confidence"] not in ("low", "medium", "high"):
            raise ValueError("confidence must be low, medium, or high")
        if not rule["rationale"].strip():
            raise ValueError("rationale must not be empty")
        if db.execute("SELECT 1 FROM cards WHERE card_id=?", (str(rule["card_id"]),)).fetchone() is None:
            raise ValueError(f"Unknown card_id: {rule['card_id']}")
        field_key = str(rule["field_key"])
        source = db.execute(
            "SELECT source_value_json FROM card_fields WHERE card_id=? AND field_key=? ORDER BY field_id LIMIT 1",
            (str(rule["card_id"]), field_key)).fetchone()
        source_json = source[0] if source else None
        # Existing source values are retained. A rule pack may add an override layer,
        # but it must explicitly acknowledge source replacement when the source exists.
        if source_json is not None and not rule.get("allow_source_override", False):
            raise ValueError(f"Source value exists for {rule['card_id']}:{field_key}; set allow_source_override explicitly")
        db.execute("""
          INSERT INTO runtime_fallbacks
          (card_id,field_key,fallback_value_json,source_value_json,fallback_kind,
           rationale,confidence,evidence_json,rule_pack_id,rule_pack_sha256)
          VALUES(?,?,?,?,?,?,?,?,?,?)
          ON CONFLICT(card_id,field_key,rule_pack_id) DO UPDATE SET
            fallback_value_json=excluded.fallback_value_json,
            source_value_json=excluded.source_value_json,
            fallback_kind=excluded.fallback_kind,
            rationale=excluded.rationale,
            confidence=excluded.confidence,
            evidence_json=excluded.evidence_json,
            rule_pack_sha256=excluded.rule_pack_sha256,
            created_at=CURRENT_TIMESTAMP
        """, (str(rule["card_id"]), field_key,
              json.dumps(rule["value"], ensure_ascii=False, sort_keys=True),
              source_json, rule.get("fallback_kind", "rule_pack"),
              rule["rationale"], rule["confidence"],
              json.dumps(rule.get("evidence", []), ensure_ascii=False, sort_keys=True),
              pack_id, digest))
        applied += 1
    db.commit()
    count = db.execute("SELECT COUNT(*) FROM runtime_fallbacks").fetchone()[0]
    fk_errors = db.execute("PRAGMA foreign_key_check").fetchall()
    db.close()
    if fk_errors:
        raise RuntimeError(f"Foreign-key errors after applying fallback pack: {fk_errors[:5]}")
    return {"rule_pack_id": pack_id, "sha256": digest, "rules_applied": applied,
            "runtime_fallback_rows": count, "foreign_key_errors": 0}

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--db", type=Path, required=True, help="Writable database copy; never point this at DB29")
    p.add_argument("--rule-pack", type=Path, required=True, help="Reviewed JSON fallback pack")
    args = p.parse_args()
    print(json.dumps(apply(args.db, args.rule_pack), ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
