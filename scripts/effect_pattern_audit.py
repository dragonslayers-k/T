#!/usr/bin/env python3
"""Create a conservative, multi-label inventory of card-text patterns.

Surface-language matching only. Nothing in this report is an executable rule
or semantic verification. Preserve original text and card-level references.
"""
import argparse
import json
import re
import sqlite3
from collections import Counter, defaultdict
from pathlib import Path

RULES = [
    ("direct_hp_attack", r"HP를?\s*직접공격|직접 공격"),
    ("dp_bypass", r"DP를?\s*무시|DP에 막히지|DP 무시"),
    ("counter_or_retaliation", r"반격|반격받|되받아"),
    ("damage", r"데미지|피해"),
    ("stat_ap", r"AP"),
    ("stat_dp", r"DP"),
    ("stat_hp", r"HP"),
    ("status_control", r"봉쇄|석화|혼란|공포|매료|저주|상태"),
    ("resource_soul", r"소울"),
    ("resource_lp", r"LP"),
    ("summon", r"소환"),
    ("field_or_land", r"필드|지형|배치"),
    ("timing", r"공격시|방어시|턴 시작|턴 종료|턴마다|턴 동안"),
    ("condition", r"이하|이상|보다 높|보다 낮|경우|조건"),
    ("duration", r"턴 동안|턴까지|다음 턴|지속"),
]
NON_EFFECT = re.compile(r"^invalid$|보유LP는|더블클릭하여 소울|소울은 카드를 소환", re.I)
NUMBER = re.compile(r"(?<![가-힣A-Za-z])[-+]?\d+(?:\.\d+)?%?")
TOKEN = re.compile(r"(?:NCS|BONUS|[A-Z]{2,})", re.I)


def analyze(text):
    if NON_EFFECT.search(text.strip()):
        return ["non_effect_or_invalid"], [], []
    topics = [name for name, pattern in RULES if re.search(pattern, text)]
    numbers = NUMBER.findall(text)
    special_tokens = sorted(set(TOKEN.findall(text)))
    if not topics:
        topics = ["unclassified_candidate"]
    return topics, numbers, special_tokens


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/fm1_cards.sqlite")
    ap.add_argument("--out", default="data/effect-pattern-inventory.json")
    ap.add_argument("--top", type=int, default=200)
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    rows = con.execute("""
        SELECT ct.text_id, ct.card_id, ct.text_type,
               COALESCE(ct.plain_text, ct.source_text), ct.source_text
        FROM card_texts ct
        WHERE ct.text_type IN ('card_text','additional_text')
        ORDER BY ct.card_id, ct.text_id
    """).fetchall()
    topics_count = Counter()
    unique = {}
    records = []
    for text_id, card_id, text_type, plain_text, source_text in rows:
        text = (plain_text or source_text or "").strip()
        if not text:
            continue
        topics, number_candidates, special_tokens = analyze(text)
        for topic in topics:
            topics_count[topic] += 1
        signature = (text_type, text)
        unique[signature] = unique.get(signature, 0) + 1
        records.append({
            "text_id": text_id,
            "card_id": card_id,
            "text_type": text_type,
            "text": text,
            "topic_candidates": topics,
            "number_candidates": number_candidates,
            "special_token_candidates": special_tokens,
            "verification_status": "pattern_candidate",
            "source_detail_url": f"https://fmlunatic.com/card/{card_id}",
        })
    pattern_rows = []
    for (text_type, text), count in unique.items():
        topics, nums, tokens = analyze(text)
        pattern_rows.append({
            "text_type": text_type, "text": text, "count": count,
            "topic_candidates": topics, "number_candidates": nums,
            "special_token_candidates": tokens,
            "verification_status": "pattern_candidate",
        })
    pattern_rows.sort(key=lambda r: (-r["count"], r["text_type"], r["text"]))
    result = {
        "schema_version": 2,
        "source_database": str(args.db),
        "classification_note": "Multi-label surface match only; not executable semantics. Numeric spans are candidates, not interpreted parameters.",
        "total_text_rows": len(records),
        "distinct_text_patterns": len(pattern_rows),
        "topic_candidate_counts": dict(sorted(topics_count.items())),
        "top_patterns": pattern_rows[:args.top],
        "card_text_candidates": records,
    }
    out = Path(args.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({
        "total_text_rows": result["total_text_rows"],
        "distinct_text_patterns": result["distinct_text_patterns"],
        "topic_candidate_counts": result["topic_candidate_counts"],
    }, ensure_ascii=False))


if __name__ == "__main__":
    main()
