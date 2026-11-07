#!/usr/bin/env python3
"""Build a read-only, per-card semantic evidence ledger from DB29 SQLite."""
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, sqlite3
from collections import Counter, defaultdict
from pathlib import Path

SOURCE_TAG = "fm1-carddb-29"
EXPECTED = 15350

def decode(value):
    if value is None: return None
    try: return json.loads(value)
    except (TypeError, ValueError, json.JSONDecodeError): return value

def row_dict(row):
    return {key: row[key] for key in row.keys()}

def existing_tables(db):
    return {row[0] for row in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}

def grouped_rows(db, tables, table, key="card_id"):
    result = defaultdict(list)
    if table not in tables: return result
    columns = {row[1] for row in db.execute(f'PRAGMA table_info("{table}")')}
    if key not in columns: return result
    for row in db.execute(f'SELECT * FROM "{table}" ORDER BY "{key}"'):
        result[str(row[key])].append(row_dict(row))
    return result

def build(db_path, jsonl_gz, csv_path, summary_path, expected=EXPECTED):
    db_sha = hashlib.sha256(db_path.read_bytes()).hexdigest()
    db = sqlite3.connect(f"file:{db_path.resolve()}?mode=ro", uri=True)
    db.row_factory = sqlite3.Row
    try:
        tables = existing_tables(db)
        required = {"cards", "card_fields", "card_costs", "card_images"}
        if required - tables:
            raise ValueError(f"DB29 missing required tables: {sorted(required - tables)}")
        integrity = db.execute("PRAGMA integrity_check").fetchone()[0]
        if integrity != "ok":
            raise ValueError(f"DB29 SQLite integrity_check failed: {integrity}")

        relation_names = [
            "card_fields", "card_texts", "card_costs", "card_soul_cost_tokens",
            "card_images", "card_effects", "source_pages", "verification",
            "card_rule_mappings", "card_field_coverage", "card_effect_clauses",
            "card_effect_candidate_summaries"
        ]
        relations = {name: grouped_rows(db, tables, name) for name in relation_names if name in tables}
        clauses = relations.get("card_effect_clauses", {})
        clause_to_card = {}
        for card_id, rows in clauses.items():
            for row in rows:
                if row.get("clause_id") is not None:
                    clause_to_card[str(row["clause_id"])] = card_id
        interpretations = defaultdict(list)
        if "card_effect_interpretations" in tables:
            columns = {row[1] for row in db.execute('PRAGMA table_info("card_effect_interpretations")')}
            if "clause_id" in columns:
                for row in db.execute('SELECT * FROM card_effect_interpretations ORDER BY clause_id'):
                    item = row_dict(row)
                    card_id = clause_to_card.get(str(item.get("clause_id")))
                    if card_id:
                        interpretations[card_id].append(item)

        cards = db.execute("SELECT * FROM cards ORDER BY card_id").fetchall()
        if len(cards) != expected:
            raise ValueError(f"Expected {expected} cards, found {len(cards)}")

        seen, metrics, type_counts = set(), Counter(), Counter()
        csv_fields = [
            "card_id", "name", "card_type", "attribute", "source_card_url", "source_list_url",
            "source_field_rows", "distinct_source_fields", "text_rows", "image_rows",
            "archive_verified_images", "cost_source_text", "lp_known", "soul_known",
            "mapping_review", "semantic_review", "soul_token_rows", "skill_mapping_rows",
            "manual_verified_skill_rows", "effect_source_rows", "effect_clause_rows",
            "effect_interpretation_rows", "identity_status", "image_status", "cost_status",
            "skill_status", "effect_status", "overall_semantic_status"
        ]
        jsonl_gz.parent.mkdir(parents=True, exist_ok=True)
        csv_path.parent.mkdir(parents=True, exist_ok=True)
        summary_path.parent.mkdir(parents=True, exist_ok=True)
        with gzip.open(jsonl_gz, "wt", encoding="utf-8", newline="") as jsonl, csv_path.open("w", encoding="utf-8-sig", newline="") as csv_file:
            writer = csv.DictWriter(csv_file, fieldnames=csv_fields)
            writer.writeheader()
            for card_row in cards:
                card = row_dict(card_row)
                card_id = str(card["card_id"])
                if card_id in seen:
                    raise ValueError(f"Duplicate card_id: {card_id}")
                seen.add(card_id)
                raw = decode(card.get("raw_payload_json")) or {}
                fields = relations.get("card_fields", {}).get(card_id, [])
                texts = relations.get("card_texts", {}).get(card_id, [])
                costs = relations.get("card_costs", {}).get(card_id, [])
                cost = costs[0] if costs else {}
                tokens = relations.get("card_soul_cost_tokens", {}).get(card_id, [])
                images = relations.get("card_images", {}).get(card_id, [])
                effects = relations.get("card_effects", {}).get(card_id, [])
                effect_candidates = relations.get("card_effect_candidate_summaries", {}).get(card_id, [])
                pages = relations.get("source_pages", {}).get(card_id, [])
                verification = relations.get("verification", {}).get(card_id, [])
                skill_maps = relations.get("card_rule_mappings", {}).get(card_id, [])
                field_coverage = relations.get("card_field_coverage", {}).get(card_id, [])
                card_clauses = clauses.get(card_id, [])
                card_interpretations = interpretations.get(card_id, [])
                field_names = {str(item.get("field_key")) for item in fields}
                verified_images = sum(
                    1 for item in images
                    if item.get("download_status") == "archive_verified"
                    and item.get("sha256") and item.get("archive_path")
                )
                manual_skills = sum(1 for item in skill_maps if item.get("mapping_status") == "manual_verified")
                source_url = card.get("source_card_url")
                image_status = "archive_verified_2of2" if verified_images >= 2 else (
                    f"archive_verified_{verified_images}of2" if images else "image_provenance_missing"
                )
                cost_status = "missing_cost_row" if not cost else (
                    "semantic_review_blocked" if cost.get("semantic_review") else (
                        "mapping_review" if cost.get("mapping_review") else (
                            "source_parsed" if cost.get("soul_known") else "source_parse_unresolved"
                        )
                    )
                )
                skill1, skill2 = raw.get("Skill1"), raw.get("Skill2")
                skill_status = "manual_verified_mapping_present" if manual_skills else (
                    "mapping_rows_present_unverified" if skill_maps else (
                        "raw_skill_present_mapping_missing"
                        if skill1 not in (None, "", 0, "0") or skill2 not in (None, "", 0, "0")
                        else "no_raw_skill"
                    )
                )
                effect_verified = sum(
                    1 for item in card_interpretations
                    if str(item.get("verification_status") or item.get("status") or "").lower()
                    in {"verified", "manual_verified", "source_verified"}
                )
                effect_status = "verified_interpretation_present" if effect_verified else (
                    "interpretation_rows_present_not_verified" if card_interpretations else (
                        "clauses_and_candidate_summaries_not_verified" if card_clauses and effect_candidates else (
                            "clauses_extracted_not_verified" if card_clauses else (
                                "candidate_summaries_not_verified" if effect_candidates else (
                                    "effect_source_extracted" if effects else "no_effect_source_row"
                                )
                            )
                        )
                    )
                )
                identity_status = "source_card_url_present" if source_url else "source_card_url_missing"
                ledger_row = {
                    "schema_version": 1,
                    "source_release_tag": SOURCE_TAG,
                    "source_sqlite_sha256": db_sha,
                    "card_id": card_id,
                    "name": card.get("name"),
                    "card_type": card.get("card_type"),
                    "attribute": card.get("attribute"),
                    "source_card_url": source_url,
                    "source_list_url": card.get("source_list_url"),
                    "detail_url_status": card.get("detail_url_status"),
                    "content_hash": card.get("content_hash"),
                    "raw_payload": raw,
                    "source_fields": fields,
                    "source_texts": texts,
                    "cost": cost,
                    "cost_tokens": tokens,
                    "images": images,
                    "source_pages": pages,
                    "verification_records": verification,
                    "skill_mappings": skill_maps,
                    "effect_source_rows": effects,
                    "effect_candidate_summaries": effect_candidates,
                    "effect_clauses": card_clauses,
                    "effect_interpretations": card_interpretations,
                    "field_coverage": field_coverage,
                    "axis_status": {
                        "identity": identity_status,
                        "field_extraction": "source_fields_extracted",
                        "images": image_status,
                        "cost": cost_status,
                        "skills": skill_status,
                        "effects": effect_status,
                        "semantic_review": "pending_card_level_adjudication"
                    }
                }
                jsonl.write(json.dumps(ledger_row, ensure_ascii=False, separators=(",", ":")) + "\n")
                writer.writerow({
                    "card_id": card_id, "name": card.get("name"), "card_type": card.get("card_type"),
                    "attribute": card.get("attribute"), "source_card_url": source_url,
                    "source_list_url": card.get("source_list_url"), "source_field_rows": len(fields),
                    "distinct_source_fields": len(field_names), "text_rows": len(texts),
                    "image_rows": len(images), "archive_verified_images": verified_images,
                    "cost_source_text": cost.get("source_text"), "lp_known": cost.get("lp_known"),
                    "soul_known": cost.get("soul_known"), "mapping_review": cost.get("mapping_review"),
                    "semantic_review": cost.get("semantic_review"), "soul_token_rows": len(tokens),
                    "skill_mapping_rows": len(skill_maps), "manual_verified_skill_rows": manual_skills,
                    "effect_source_rows": len(effects), "effect_candidate_summary_rows": len(effect_candidates),
                    "effect_clause_rows": len(card_clauses),
                    "effect_interpretation_rows": len(card_interpretations), "identity_status": identity_status,
                    "image_status": image_status, "cost_status": cost_status, "skill_status": skill_status,
                    "effect_status": effect_status, "overall_semantic_status": "pending_card_level_adjudication"
                })
                type_counts[str(card.get("card_type"))] += 1
                metrics["cards"] += 1
                metrics["source_url_present"] += bool(source_url)
                metrics["cards_with_text"] += bool(texts)
                metrics["source_field_rows"] += len(fields)
                metrics["image_rows"] += len(images)
                metrics["archive_verified_images"] += verified_images
                metrics["cost_rows"] += bool(cost)
                metrics["soul_known_cards"] += bool(cost.get("soul_known"))
                metrics["mapping_review_cards"] += bool(cost.get("mapping_review"))
                metrics["semantic_review_cards"] += bool(cost.get("semantic_review"))
                metrics["soul_token_rows"] += len(tokens)
                metrics["skill_mapping_rows"] += len(skill_maps)
                metrics["manual_verified_skill_rows"] += manual_skills
                metrics["effect_source_rows"] += len(effects)
                metrics["effect_candidate_summary_rows"] += len(effect_candidates)
                metrics["effect_clause_rows"] += len(card_clauses)
                metrics["effect_interpretation_rows"] += len(card_interpretations)
                metrics["pending_semantic_cards"] += 1
        if len(seen) != expected:
            raise ValueError(f"Unique card count {len(seen)} != expected {expected}")
        metrics["distinct_source_field_keys"] = db.execute("SELECT COUNT(DISTINCT field_key) FROM card_fields").fetchone()[0]
        result = {
            "schema_version": 1, "source_release_tag": SOURCE_TAG,
            "source_sqlite_sha256": db_sha, "sqlite_integrity_check": integrity,
            "expected_cards": expected, "unique_cards": len(seen),
            "cards_by_type": dict(type_counts), "metrics": dict(metrics),
            "artifacts": {"card_level_jsonl_gz": str(jsonl_gz), "card_index_csv": str(csv_path)},
            "interpretation_note": (
                "Card-level source/evidence ledger only. Extraction, image integrity, cost parsing, "
                "skill mapping, effect interpretation and runtime behavior are separate axes; this "
                "does not claim semantic adjudication is complete."
            )
        }
        summary_path.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        return result
    finally:
        db.close()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, required=True)
    parser.add_argument("--jsonl-gz", type=Path, required=True)
    parser.add_argument("--csv", type=Path, required=True)
    parser.add_argument("--summary", type=Path, required=True)
    parser.add_argument("--expected", type=int, default=EXPECTED)
    args = parser.parse_args()
    result = build(args.db, args.jsonl_gz, args.csv, args.summary, args.expected)
    print(json.dumps(result, ensure_ascii=False))

if __name__ == "__main__":
    main()
