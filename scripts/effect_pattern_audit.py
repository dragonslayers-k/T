#!/usr/bin/env python3
"""Create a conservative inventory of recurring Korean card-text patterns.

This tool only assigns a candidate topic based on surface words. It never
marks a card effect as semantically verified or executable.
"""
import argparse
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

RULES = [
    ("damage_resolution", r"직접공격|DP를 무시|DP에 막힐|반격받지|추가데미지|데미지"),
    ("stat_change", r"AP|DP|HP|능력치"),
    ("status_control", r"봉쇄|석화|혼란|공포|매료|저주|상태"),
    ("resource", r"소울|LP|마력"),
    ("summon_or_field", r"소환|필드|지형|배치"),
    ("timing_or_condition", r"공격시|턴|이하 레벨|이상으로|경우"),
]
NON_EFFECT = re.compile(r"^invalid$|보유LP는|더블클릭하여 소울|소울은 카드를 소환", re.I)


def classify(text):
    if NON_EFFECT.search(text.strip()):
        return "non_effect_or_invalid"
    matches = [key for key, pattern in RULES if re.search(pattern, text)]
    return matches[0] if matches else "unclassified_candidate"


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/fm1_cards.sqlite")
    ap.add_argument("--out", default="data/effect-pattern-inventory.json")
    ap.add_argument("--top", type=int, default=100)
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    rows = con.execute("""
        SELECT ct.text_type, COALESCE(ct.plain_text, ct.source_text), COUNT(*)
        FROM card_texts ct
        WHERE ct.text_type IN ('card_text','additional_text')
        GROUP BY ct.text_type, COALESCE(ct.plain_text, ct.source_text)
    """).fetchall()
    buckets = Counter()
    by_text = defaultdict(int)
    for text_type, text, count in rows:
        if not text or not text.strip():
            continue
        buckets[classify(text)] += count
        by_text[(text_type, text)] += count
    ordered = sorted(
        ({"text_type": typ, "text": txt, "count": count,
          "candidate_topic": classify(txt), "verification_status": "pattern_candidate"}
         for (typ, txt), count in by_text.items()),
        key=lambda row: (-row["count"], row["text_type"], row["text"])
    )
    result = {
        "schema_version": 1,
        "source_database": str(args.db),
        "classification_note": "Surface-word candidate only; not executable semantics.",
        "total_distinct_texts": len(ordered),
        "total_text_rows": sum(row["count"] for row in ordered),
        "candidate_topic_counts": dict(sorted(buckets.items())),
        "top_patterns": ordered[:args.top],
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")
    print(json.dumps({k: result[k] for k in ("total_distinct_texts", "total_text_rows", "candidate_topic_counts")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
