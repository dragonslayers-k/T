#!/usr/bin/env python3
"""Audit exact DB29 Skill1 rows and attach card-local TextBase/TextExtra evidence.

This is a source-evidence inventory only. Text fields are preserved verbatim and
must not be mistaken for proof that a text fragment defines the Skill1 effect.
The report never changes DB29 or promotes a runtime rule.
"""
from __future__ import annotations

import argparse
import json
import sqlite3
import unicodedata
from collections import Counter, defaultdict
from pathlib import Path


def norm(value: object) -> str:
    return "".join(unicodedata.normalize("NFKC", str(value or "")).split())


def decode_source_value(value: object) -> object:
    if value is None:
        return None
    try:
        return json.loads(value) if isinstance(value, str) else value
    except (TypeError, json.JSONDecodeError):
        return value


def has_text(value: object) -> bool:
    return isinstance(value, str) and bool(value.strip())


def audit(db_path: Path, catalog_path: Path, source_release_tag: str = "fm1-carddb-29") -> dict:
    if source_release_tag != "fm1-carddb-29":
        raise ValueError("This source-evidence audit is pinned to immutable fm1-carddb-29")
    catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
    rules = catalog.get("manualRules", [])
    if len(rules) != 27 or any(rule.get("authority") != "manual" for rule in rules):
        raise ValueError("Expected exactly 27 Manual-authority special-skill rules")

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    try:
        columns = {row["name"] for row in db.execute("PRAGMA table_info(cards)")}
        required = {"card_id", "name", "source_card_url"}
        if not required.issubset(columns):
            raise ValueError(f"cards table missing required columns: {sorted(required-columns)}")
        field_columns = {row["name"] for row in db.execute("PRAGMA table_info(card_fields)")}
        required_fields = {"card_id", "field_key", "source_value_json", "normalized_value"}
        if not required_fields.issubset(field_columns):
            raise ValueError(f"card_fields table missing required columns: {sorted(required_fields-field_columns)}")

        source_rows = db.execute("""
            SELECT f.card_id, f.source_value_json, f.normalized_value,
                   c.name AS card_name, c.source_card_url
            FROM card_fields f
            JOIN cards c ON c.card_id=f.card_id
            WHERE f.field_key='Skill1'
              AND COALESCE(f.normalized_value,'') NOT IN ('', '없음')
            ORDER BY f.normalized_value, f.card_id
        """).fetchall()

        text_by_card: dict[str, dict[str, object]] = defaultdict(dict)
        text_rows = db.execute("""
            SELECT card_id, field_key, source_value_json
            FROM card_fields
            WHERE field_key IN ('TextBase', 'TextExtra')
            ORDER BY card_id, field_key
        """).fetchall()
        for row in text_rows:
            text_by_card[str(row["card_id"])][row["field_key"]] = decode_source_value(row["source_value_json"])

        by_label: dict[str, list[sqlite3.Row]] = {}
        for row in source_rows:
            by_label.setdefault(norm(row["normalized_value"]), []).append(row)

        records = []
        matched_card_rows = 0
        matched_rules = 0
        total_text_counts = Counter()
        for rule in rules:
            canonical = rule["name"]
            labels = {norm(canonical)}
            labels.update(norm(alias) for alias in rule.get("aliases", []))
            hits = []
            for label in sorted(labels):
                for row in by_label.get(label, []):
                    raw_value = row["source_value_json"]
                    try:
                        raw_value = json.loads(raw_value) if raw_value is not None else None
                    except (TypeError, json.JSONDecodeError):
                        pass
                    match_type = "exact_manual_label" if label == norm(canonical) else "catalog_alias_match"
                    hits.append({
                        "card_id": row["card_id"],
                        "card_name": row["card_name"],
                        "source_field": "Skill1",
                        "source_value": raw_value,
                        "exact_source_label": row["normalized_value"],
                        "match_type": match_type,
                        "source_card_url": row["source_card_url"],
                    })
            dedup = {}
            for hit in hits:
                key = (hit["card_id"], hit["source_field"])
                previous = dedup.get(key)
                if previous is None or hit["match_type"] == "exact_manual_label":
                    dedup[key] = hit
            card_matches = sorted(dedup.values(), key=lambda item: item["card_id"])
            if card_matches:
                matched_rules += 1

            rule_text_counts = Counter()
            for hit in card_matches:
                fields = text_by_card.get(str(hit["card_id"]), {})
                text_base = fields.get("TextBase")
                text_extra = fields.get("TextExtra")
                if has_text(text_extra):
                    evidence_type = "additional_text"
                elif has_text(text_base):
                    evidence_type = "card_text_only"
                else:
                    evidence_type = "missing"
                hit["source_text_fields"] = {
                    "TextBase": text_base,
                    "TextExtra": text_extra,
                }
                hit["text_evidence_type"] = evidence_type
                rule_text_counts[evidence_type] += 1
                total_text_counts[evidence_type] += 1

            matched_card_rows += len(card_matches)
            records.append({
                "rule_id": rule["id"],
                "manual_skill_name": canonical,
                "aliases": rule.get("aliases", []),
                "source_match_status": "matched_exact_db29_skill1_rows" if card_matches else "no_exact_db29_skill1_match",
                "matched_card_rows": card_matches,
                "text_evidence_summary": {
                    "additional_text_rows": rule_text_counts["additional_text"],
                    "card_text_only_rows": rule_text_counts["card_text_only"],
                    "missing_text_rows": rule_text_counts["missing"],
                },
                "runtime_promotion": "not_authorized",
            })

        return {
            "schema_version": "FM1-MANUAL-SKILL-DB29-SOURCE-MATCH-WITH-CARD-TEXT-1.0",
            "baseline": {
                "db_release": source_release_tag,
                "immutable": True,
                "db30_issued": False,
                "main_merge": False,
            },
            "source": {
                "database": str(db_path),
                "catalog": str(catalog_path),
                "release_tag": source_release_tag,
                "field": "Skill1",
                "card_text_fields": ["TextBase", "TextExtra"],
                "matching": "Unicode NFKC + whitespace removal; exact canonical label or catalog alias only",
            },
            "summary": {
                "manual_rule_count": len(rules),
                "rules_with_exact_card_rows": matched_rules,
                "rules_without_exact_card_rows": len(rules) - matched_rules,
                "matched_card_rows": matched_card_rows,
                "rows_with_additional_text": total_text_counts["additional_text"],
                "rows_with_card_text_only": total_text_counts["card_text_only"],
                "rows_missing_both_text_fields": total_text_counts["missing"],
                "runtime_executable_rules": 0,
            },
            "policy": {
                "source_values_preserved": True,
                "text_base_and_text_extra_preserved_verbatim": True,
                "text_presence_is_not_skill_semantic_approval": True,
                "inferred_or_substring_matches_used": False,
                "card_rows_are_not_runtime_promotion": True,
                "missing_source_url_remains_visible": True,
                "db29_is_immutable": True,
            },
            "rules": records,
        }
    finally:
        db.close()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--db", type=Path, required=True, help="Immutable DB29 SQLite database")
    parser.add_argument("--catalog", type=Path, default=Path("data/rules/fm1-skill-catalog-v1.json"))
    parser.add_argument("--source-release-tag", default="fm1-carddb-29")
    parser.add_argument("--output", type=Path, required=True, help="JSON evidence report path")
    args = parser.parse_args()
    report = audit(args.db, args.catalog, args.source_release_tag)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], ensure_ascii=False))


if __name__ == "__main__":
    main()
