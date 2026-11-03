#!/usr/bin/env python3
"""Inventory card-text candidates without asserting game semantics."""
import argparse
import json
import re
import sqlite3
from collections import Counter
from pathlib import Path

TOPICS = [
    ("direct_hp_attack", r"HP를?\s*직접공격|직접 공격"),
    ("dp_bypass", r"DP를?\s*무시|DP에 막히지|DP 무시"),
    ("counter_or_retaliation", r"반격|되받아"),
    ("damage", r"데미지|피해"),
    ("stat_ap", r"AP"), ("stat_dp", r"DP"), ("stat_hp", r"HP"),
    ("status_control", r"봉쇄|석화|혼란|공포|매료|저주|상태"),
    ("resource_soul", r"소울"), ("resource_lp", r"LP"),
    ("summon", r"소환"), ("field_or_land", r"필드|지형|배치"),
    ("condition", r"이하|이상|보다 높|보다 낮|경우|조건|만약"),
    ("duration", r"턴 동안|턴까지|다음 턴|지속|영구히"),
    ("on_destroy_or_death", r"자신 파괴시|자신 파괴 시|적 \d+파괴시|파괴시"),
    ("ability_definition", r"^[^:\n]{1,40}\s*[:：]\s*(?:자신|아군|적군|상대|유닛|기술|AP|DP|HP|○|●)"),
    ("card_reference", r"상성카드\s*:|연계카드\s*:"),
    ("card_profile_spec", r"[●○◯]|일반공격|장비능력|마법능력|공방체"),
    ("rule_note", r"^\s*▶"),
]
TRIGGERS = [
    ("attack_or_defense_window", r"공격/방어|공격 및 방어"),
    ("on_attack", r"공격시|공격할 때|공격 선언"),
    ("on_defense", r"방어시|방어할 때|방어 선언"),
    ("turn_start", r"턴 시작|준비 단계 시작"),
    ("turn_end", r"턴 종료|턴 끝"),
    ("on_summon", r"소환시|소환할 때|배치시"),
]
ACTORS = [
    ("friendly", r"아군"), ("enemy", r"적군|적 "),
    ("self", r"자신|자기"), ("both_sides", r"아군적군|양쪽"),
]
TARGETS = [
    ("field_unit", r"필드 유닛|유닛 전체|유닛 1"),
    ("hand_card", r"핸드|손패"),
    ("terrain", r"지형|백필드"),
    ("item", r"아이템|장착"),
    ("spell_or_enchant", r"마법|인첸트|인챈트"),
    ("deck", r"덱|카드 더미"),
    ("player_or_lp", r"플레이어|LP"),
]
OPERATIONS = [
    ("stat_modify", r"AP|DP|HP|능력치"),
    ("damage_or_destroy", r"데미지|피해|파괴|소각"),
    ("heal_or_recover", r"회복|치료|재생"),
    ("draw_or_mill", r"드로우|뽑|덱 파괴|덱을"),
    ("grant_or_remove_ability", r"기술.*부여|기술.*변경|기술.*제거|봉쇄"),
    ("move_or_replace", r"이동|교체|복제|소환"),
    ("resource_change", r"소울|LP|마력"),
    ("equip_or_unequip", r"장착|해제"),
]
NON_EFFECT = re.compile(r"^invalid$|보유LP는|더블클릭하여 소울|소울은 카드를 소환", re.I)
FLAVOR_ONLY = re.compile(r"^\s*\[[^\[\]]*\]\s*$", re.S)
REFERENCE_NOTE = re.compile(r"^\s*(?:▶|상성카드\s*:|해당 카드는|카드타입은|기호 소개)", re.I)
NUMBER = re.compile(r"(?<!\d)[-+]?\d+(?:\.\d+)?%?")
TOKEN = re.compile(r"(?:NCS|BONUS|[A-Z]{2,})", re.I)


def candidates(text, rules):
    return [key for key, pattern in rules if re.search(pattern, text)]


def classify_source_text(text):
    if FLAVOR_ONLY.fullmatch(text.strip()):
        return "flavor_only_candidate"
    if NON_EFFECT.search(text.strip()):
        return "invalid_or_non_effect_candidate"
    if REFERENCE_NOTE.search(text.strip()):
        return "reference_or_rule_note_candidate"
    return "effect_text_candidate"


def split_clause_candidates(text):
    """Split on strong punctuation/branch markers while preserving exact spans."""
    chunks = []
    start = 0
    for match in re.finditer(r"[。;；\n]|[※◇◆]", text):
        token = match.group(0)
        if token in "※◇◆":
            if match.start() > start:
                chunks.append((start, match.start()))
            start = match.start()
        else:
            chunks.append((start, match.end()))
            start = match.end()
    if start < len(text):
        chunks.append((start, len(text)))
    result = []
    for index, (begin, end) in enumerate(chunks):
        clause = text[begin:end]
        is_separator = not clause.strip()
        result.append({
            "clause_index": index,
            "start_char": begin,
            "end_char": end,
            "text": clause,
            "segment_type": "separator" if is_separator else "clause",
            "topic_candidates": [] if is_separator else candidates(clause, TOPICS),
            "trigger_candidates": [] if is_separator else candidates(clause, TRIGGERS),
            "actor_candidates": [] if is_separator else candidates(clause, ACTORS),
            "target_candidates": [] if is_separator else candidates(clause, TARGETS),
            "operation_candidates": [] if is_separator else candidates(clause, OPERATIONS),
            "verification_status": "pattern_candidate",
        })
    return result


def analyze(text):
    text_class = classify_source_text(text)
    if text_class in ("flavor_only_candidate", "invalid_or_non_effect_candidate"):
        return {
            "source_text_class_candidate": text_class,
            "topic_candidates": ["non_effect_or_invalid"],
            "trigger_candidates": [], "actor_candidates": [],
            "target_candidates": [], "operation_candidates": [],
            "number_candidates": [], "special_token_candidates": [],
        }
    topics = candidates(text, TOPICS) or ["unclassified_candidate"]
    return {
        "source_text_class_candidate": text_class,
        "topic_candidates": topics,
        "clause_candidates": split_clause_candidates(text),
        "trigger_candidates": candidates(text, TRIGGERS),
        "actor_candidates": candidates(text, ACTORS),
        "target_candidates": candidates(text, TARGETS),
        "operation_candidates": candidates(text, OPERATIONS),
        "number_candidates": NUMBER.findall(text),
        "special_token_candidates": sorted(set(TOKEN.findall(text))),
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--db", default="data/fm1_cards.sqlite")
    ap.add_argument("--out", default="data/effect-pattern-inventory.json")
    ap.add_argument("--top", type=int, default=200)
    args = ap.parse_args()
    con = sqlite3.connect(args.db)
    rows = con.execute("""
        SELECT ct.text_id, ct.card_id, ct.text_type,
               COALESCE(NULLIF(ct.plain_text, ''), ct.source_text),
               ct.source_text, c.source_card_url
        FROM card_texts ct
        LEFT JOIN cards c ON c.card_id = ct.card_id
        WHERE ct.text_type IN ('card_text','additional_text')
        ORDER BY ct.card_id, ct.text_id
    """).fetchall()
    topic_count = Counter()
    records = []
    pattern_counts = Counter()
    for text_id, card_id, text_type, plain_text, source_text, source_card_url in rows:
        text = plain_text or source_text or ""
        if not text.strip():
            continue
        parsed = analyze(text)
        topic_count.update(parsed["topic_candidates"])
        pattern_counts[(text_type, text)] += 1
        records.append({
            "text_id": text_id, "card_id": card_id, "text_type": text_type,
            "text": text, **parsed,
            "verification_status": "pattern_candidate",
            "source_detail_url": source_card_url,
        })
    patterns = []
    for (text_type, text), count in pattern_counts.items():
        patterns.append({
            "text_type": text_type, "text": text, "count": count,
            **analyze(text), "verification_status": "pattern_candidate",
        })
    patterns.sort(key=lambda r: (-r["count"], r["text_type"], r["text"]))
    result = {
        "schema_version": 5,
        "source_database": str(args.db),
        "classification_note": "Candidate extraction from surface text only. Text-class labels, clause splits and semantic fields are candidates, not executable rules; source text and character spans are preserved, and absent candidates do not prove absent rules.",
        "total_text_rows": len(records),
        "distinct_text_patterns": len(patterns),
        "topic_candidate_counts": dict(sorted(topic_count.items())),
        "top_patterns": patterns[:args.top],
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
