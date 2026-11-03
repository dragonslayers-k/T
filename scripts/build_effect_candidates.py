#!/usr/bin/env python3
"""Persist effect-text analysis as non-executable review candidates in SQLite.

Original HTML/text remains in card_texts. Candidate summaries and clause spans
are derived indexes only; they never promote a phrase into an executable rule.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from effect_pattern_audit import analyze


def dump(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def build(connection: sqlite3.Connection) -> dict:
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript("""
    CREATE TABLE IF NOT EXISTS card_effect_candidate_summaries (
        candidate_id INTEGER PRIMARY KEY,
        text_id INTEGER NOT NULL UNIQUE REFERENCES card_texts(text_id),
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        text_type TEXT NOT NULL,
        source_text_sha256 TEXT NOT NULL,
        source_detail_url TEXT,
        source_text_class_candidate TEXT,
        topic_candidates_json TEXT NOT NULL,
        trigger_candidates_json TEXT NOT NULL,
        actor_candidates_json TEXT NOT NULL,
        target_candidates_json TEXT NOT NULL,
        operation_candidates_json TEXT NOT NULL,
        number_candidates_json TEXT NOT NULL,
        special_token_candidates_json TEXT NOT NULL,
        analysis_json TEXT NOT NULL,
        verification_status TEXT NOT NULL DEFAULT 'pattern_candidate',
        span_integrity_status TEXT NOT NULL DEFAULT 'not_checked'
    );
    CREATE TABLE IF NOT EXISTS card_effect_clauses (
        clause_id INTEGER PRIMARY KEY,
        candidate_id INTEGER NOT NULL REFERENCES card_effect_candidate_summaries(candidate_id),
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        clause_index INTEGER NOT NULL,
        start_char INTEGER NOT NULL,
        end_char INTEGER NOT NULL,
        segment_type TEXT NOT NULL CHECK(segment_type IN ('clause','separator')),
        segment_text TEXT NOT NULL,
        topic_candidates_json TEXT NOT NULL,
        trigger_candidates_json TEXT NOT NULL,
        actor_candidates_json TEXT NOT NULL,
        target_candidates_json TEXT NOT NULL,
        operation_candidates_json TEXT NOT NULL,
        verification_status TEXT NOT NULL DEFAULT 'pattern_candidate',
        UNIQUE(candidate_id, clause_index)
    );
    CREATE INDEX IF NOT EXISTS idx_effect_candidate_card ON card_effect_candidate_summaries(card_id);
    CREATE INDEX IF NOT EXISTS idx_effect_clause_card ON card_effect_clauses(card_id);
    CREATE INDEX IF NOT EXISTS idx_effect_clause_segment ON card_effect_clauses(segment_type);
    """)

    summary_columns = {
        row[1] for row in connection.execute(
            "PRAGMA table_info(card_effect_candidate_summaries)"
        )
    }
    if "span_integrity_status" not in summary_columns:
        connection.execute(
            "ALTER TABLE card_effect_candidate_summaries "
            "ADD COLUMN span_integrity_status TEXT NOT NULL DEFAULT 'not_checked'"
        )

    # A repeat run replaces only derived candidates, never original card text.
    connection.execute("DELETE FROM card_effect_clauses")
    connection.execute("DELETE FROM card_effect_candidate_summaries")

    rows = connection.execute("""
        SELECT ct.text_id, ct.card_id, ct.text_type,
               COALESCE(NULLIF(ct.plain_text, ''), ct.source_text) AS analysis_text,
               c.source_card_url
        FROM card_texts ct
        JOIN cards c ON c.card_id = ct.card_id
        WHERE ct.text_type IN ('card_text','additional_text')
        ORDER BY ct.card_id, ct.text_id
    """).fetchall()

    summaries = 0
    clauses = 0
    separators = 0
    with connection:
        for text_id, card_id, text_type, source_text, detail_url in rows:
            text = source_text or ""
            parsed = analyze(text)
            digest = hashlib.sha256(text.encode("utf-8")).hexdigest()
            cursor = connection.execute("""
                INSERT INTO card_effect_candidate_summaries (
                    text_id, card_id, text_type, source_text_sha256, source_detail_url,
                    source_text_class_candidate, topic_candidates_json,
                    trigger_candidates_json, actor_candidates_json,
                    target_candidates_json, operation_candidates_json,
                    number_candidates_json, special_token_candidates_json,
                    analysis_json, verification_status
                ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
            """, (
                text_id, card_id, text_type, digest, detail_url,
                parsed["source_text_class_candidate"],
                dump(parsed["topic_candidates"]),
                dump(parsed["trigger_candidates"]),
                dump(parsed["actor_candidates"]),
                dump(parsed["target_candidates"]),
                dump(parsed["operation_candidates"]),
                dump(parsed["number_candidates"]),
                dump(parsed["special_token_candidates"]),
                dump(parsed),
                "pattern_candidate",
            ))
            candidate_id = cursor.lastrowid
            summaries += 1
            clause_parts = []
            for item in parsed.get("clause_candidates", []):
                is_separator = item.get("segment_type") == "separator"
                connection.execute("""
                    INSERT INTO card_effect_clauses (
                        candidate_id, card_id, clause_index, start_char, end_char,
                        segment_type, segment_text, topic_candidates_json,
                        trigger_candidates_json, actor_candidates_json,
                        target_candidates_json, operation_candidates_json,
                        verification_status
                    ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)
                """, (
                    candidate_id, card_id, item["clause_index"],
                    item["start_char"], item["end_char"],
                    "separator" if is_separator else "clause",
                    item["text"],
                    dump(item.get("topic_candidates", [])),
                    dump(item.get("trigger_candidates", [])),
                    dump(item.get("actor_candidates", [])),
                    dump(item.get("target_candidates", [])),
                    dump(item.get("operation_candidates", [])),
                    "pattern_candidate",
                ))
                clauses += 1
                separators += int(is_separator)
                clause_parts.append(item["text"])
                if text[item["start_char"]:item["end_char"]] != item["text"]:
                    raise RuntimeError(
                        f"Clause span does not match source text: card={card_id} text_id={text_id} index={item['clause_index']}"
                    )
            if parsed.get("clause_candidates"):
                if "".join(clause_parts) != text:
                    raise RuntimeError(
                        f"Clause spans do not reconstruct source text: card={card_id} text_id={text_id}"
                    )
                span_status = "exact"
            else:
                span_status = "not_split"
            connection.execute(
                "UPDATE card_effect_candidate_summaries SET span_integrity_status=? WHERE candidate_id=?",
                (span_status, candidate_id),
            )

    integrity = connection.execute("PRAGMA foreign_key_check").fetchall()
    span_errors = connection.execute(
        "SELECT COUNT(*) FROM card_effect_candidate_summaries "
        "WHERE span_integrity_status NOT IN ('exact','not_split')"
    ).fetchone()[0]
    if span_errors:
        raise RuntimeError(f"Effect candidate span validation failed for {span_errors} source records")
    return {
        "sourceTextRows": len(rows),
        "candidateSummaryRows": summaries,
        "clauseRows": clauses,
        "separatorRows": separators,
        "foreignKeyErrors": len(integrity),
        "spanIntegrityErrors": span_errors,
        "status": "pattern_candidate_only",
    }


def self_test() -> None:
    connection = sqlite3.connect(":memory:")
    connection.execute("PRAGMA foreign_keys=ON")
    connection.executescript("""
    CREATE TABLE cards(card_id TEXT PRIMARY KEY, source_card_url TEXT);
    CREATE TABLE card_texts(
        text_id INTEGER PRIMARY KEY, card_id TEXT, text_type TEXT,
        source_text TEXT, plain_text TEXT
    );
    INSERT INTO cards VALUES('card-1','https://fmlunatic.com/card/card-1');
    INSERT INTO card_texts VALUES(1,'card-1','card_text','아군 AP+1.\n\n※ 적 HP-2','아군 AP+1.\n\n※ 적 HP-2');
    """)
    result = build(connection)
    assert result["candidateSummaryRows"] == 1
    assert result["foreignKeyErrors"] == 0
    record = connection.execute("""
        SELECT source_detail_url, verification_status, span_integrity_status
        FROM card_effect_candidate_summaries
    """).fetchone()
    assert record == ("https://fmlunatic.com/card/card-1", "pattern_candidate", "exact")
    segments = connection.execute("""
        SELECT segment_type, segment_text
        FROM card_effect_clauses ORDER BY clause_index
    """).fetchall()
    assert "".join(text for _, text in segments) == "아군 AP+1.\n\n※ 적 HP-2"
    assert any(kind == "separator" for kind, _ in segments)
    assert all(
        status == "pattern_candidate"
        for (status,) in connection.execute(
            "SELECT verification_status FROM card_effect_clauses"
        )
    )
    connection.close()
    print("effect candidate DB self-test passed")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("data/fm1_cards.sqlite"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        self_test()
        return
    connection = sqlite3.connect(args.db)
    try:
        result = build(connection)
        connection.commit()
        print(json.dumps(result, ensure_ascii=False))
        if result["foreignKeyErrors"]:
            raise SystemExit("Effect candidate DB foreign-key validation failed")
    finally:
        connection.close()


if __name__ == "__main__":
    main()
