#!/usr/bin/env python3
"""Build a full 831-card RequireSoul semantic evidence matrix without guessing payment rules."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter, defaultdict
from pathlib import Path

CODE_NAMES = {
    1:"NONE", 11:"DARK", 12:"DARK_EARTH", 13:"DARK_FIRE", 14:"DARK_LIGHT",
    15:"DARK_WATER", 21:"FIRE", 22:"FIRE_FOREST", 23:"FIRE_IRON", 24:"FIRE_WATER",
    31:"WATER", 32:"WATER_EARTH", 33:"WATER_FOREST", 41:"FOREST", 42:"FOREST_IRON",
    43:"FOREST_LIGHT", 51:"IRON", 52:"IRON_EARTH", 53:"IRON_LIGHT", 61:"EARTH",
    62:"EARTH_LIGHT", 71:"LIGHT", 81:"MU", 82:"NCS", 83:"BONUS",
}
HYBRID = {12,13,14,15,22,23,24,32,33,42,43,52,53,62}
SPECIAL = {81,82,83}
EVIDENCE_STATE = {
    81: ("manual_rule_verified", "MU colorless-bead rule: any attribute soul may pay initial summon; recurring unit upkeep from preparation turn; unpaid amount destroys deck cards, not the unit. Applies only to MU."),
    82: ("semantic_review_blocked", "NCS is a distinct enum and appears in direct card-effect text; no authoritative RequireSoul payment/debit rule established."),
    83: ("semantic_review_blocked", "BONUS is a distinct enum; Manual does not define its RequireSoul payment semantics."),
}
for code in HYBRID:
    EVIDENCE_STATE[code] = ("semantic_review_blocked", "Two-color icon/name identity verified; whether both colors or either color pays, and payment priority, remain unverified.")


def raw_of(row: dict) -> dict:
    value = row.get("raw_payload")
    if isinstance(value, dict):
        return value
    value = row.get("sourceFields")
    return value if isinstance(value, dict) else row


def card_id_of(row: dict) -> str:
    raw = raw_of(row)
    return str(row.get("card_id") or row.get("id") or raw.get("ID") or raw.get("NumID") or "").strip()


def require_soul_of(row: dict) -> str:
    raw = raw_of(row)
    value = raw.get("RequireSoul", row.get("requireSoul", row.get("soulCostRaw", "")))
    return str(value or "")


def card_type_of(row: dict) -> str:
    raw = raw_of(row)
    category = str(raw.get("Category", row.get("category", row.get("type", "unknown"))))
    return {"1":"land", "2":"unit", "3":"spell", "4":"item", "5":"enchant"}.get(category, category.lower() or "unknown")


def parse(raw: str) -> list[dict]:
    if not raw or not raw.isdigit() or len(raw) % 4:
        raise ValueError(f"Invalid RequireSoul token string: {raw!r}")
    result=[]
    for i in range(0,len(raw),4):
        chunk=raw[i:i+4]
        code=int(chunk[:2]); amount=int(chunk[2:])
        if code not in CODE_NAMES:
            raise ValueError(f"Unknown RequireSoul code {code} in {raw}")
        result.append({"raw":chunk,"code":code,"name":CODE_NAMES[code],"amount":amount})
    return result


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--source-cards-jsonl",type=Path,required=True)
    ap.add_argument("--evidence-dir",type=Path,required=True)
    ap.add_argument("--enumtable-json",type=Path,required=True)
    ap.add_argument("--output-dir",type=Path,required=True)
    args=ap.parse_args()
    out=args.output_dir; out.mkdir(parents=True,exist_ok=True)

    source={}
    for line_no,line in enumerate(args.source_cards_jsonl.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        row=json.loads(line); cid=card_id_of(row)
        if cid:
            if cid in source: raise SystemExit(f"Duplicate source ID {cid} at line {line_no}")
            source[cid]=row
    target={}
    for line in (args.evidence_dir/"target-cards.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row=json.loads(line); cid=str(row["card_id"])
            if cid in target: raise SystemExit(f"Duplicate evidence card {cid}")
            target[cid]=row
    if len(target)!=831: raise SystemExit(f"Expected 831 evidence cards, got {len(target)}")

    enum=json.loads(args.enumtable_json.read_text(encoding="utf-8"))
    enum_entries=enum.get("Enum+RequireSoul") if isinstance(enum,dict) else None
    if not isinstance(enum_entries,dict): raise SystemExit("Missing enumtable Enum+RequireSoul object")
    enum_by_id={int(item[0]):item for item in enum_entries.values() if isinstance(item,list) and item and str(item[0]).isdigit()}
    for code,name in CODE_NAMES.items():
        if code not in enum_by_id: raise SystemExit(f"Enum missing code {code}")
        enum_name=str(enum_by_id[code][1])
        if enum_name != name: raise SystemExit(f"Enum mismatch {code}: expected {name}, got {enum_name}")

    rows=[]; card_type_counts=Counter(); token_card_counts=Counter(); token_occurrences=Counter()
    status_counts=Counter(); hybrid_group_counts=Counter(); overlaps=[]
    for cid,evidence in sorted(target.items()):
        source_row=source.get(cid)
        if source_row is None: raise SystemExit(f"DB29 source card missing: {cid}")
        raw=require_soul_of(source_row)
        evidence_raw=str(evidence.get("source_require_soul",""))
        if raw!=evidence_raw: raise SystemExit(f"RequireSoul mismatch for {cid}: {raw} != {evidence_raw}")
        tokens=parse(raw)
        evidence_tokens=[str(x.get("raw")) for x in evidence.get("all_tokens",[])]
        if [x["raw"] for x in tokens]!=evidence_tokens: raise SystemExit(f"Token sequence mismatch {cid}")
        codes={x["code"] for x in tokens}
        type_name=card_type_of(source_row)
        card_type_counts[type_name]+=1
        for token in tokens:
            token_occurrences[token["code"]]+=1
            token_card_counts[token["code"]]+=1
        groups=[x for x in tokens if x["code"] in HYBRID]
        specials=[x for x in tokens if x["code"] in (82,83)]
        if 82 in codes and 83 in codes: overlaps.append(cid)
        for token in tokens:
            code=token["code"]
            state, rationale = EVIDENCE_STATE.get(code,("decoded_identity_only","Element token identity is decoded; this matrix does not adjudicate its payment behavior."))
            rows.append({
                "card_id":cid,"name":evidence.get("name",""),"card_type":type_name,
                "require_soul_raw":raw,"token_raw":token["raw"],"token_code":code,
                "token_name":token["name"],"amount":token["amount"],
                "review_group":f"hybrid:{token['name']}" if code in HYBRID else token["name"],
                "evidence_state":state,"payment_semantics":rationale,
                "source_record_verified":True,"token_sequence_verified":True,
            })
        if groups:
            hybrid_group_counts[groups[0]["name"]]+=1
        status_counts["contains_hybrid" if groups else "contains_NCS_BONUS" if specials else "contains_MU" if 81 in codes else "other"]+=1

    fields=list(rows[0].keys())
    with (out/"db29-requiresoul-semantic-token-matrix.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields);w.writeheader();w.writerows(rows)

    card_rows=[]
    for cid,evidence in sorted(target.items()):
        tokens=parse(require_soul_of(source[cid]))
        codes={t["code"] for t in tokens}
        type_name=card_type_of(source[cid])
        groups=[f"hybrid:{CODE_NAMES[t['code']]}" for t in tokens if t["code"] in HYBRID]
        card_rows.append({
            "card_id":cid,"name":evidence.get("name",""),"card_type":type_name,
            "require_soul_raw":require_soul_of(source[cid]),
            "token_sequence":";".join(f"{t['name']}:{t['amount']}" for t in tokens),
            "contains_MU":81 in codes,"contains_NCS":82 in codes,"contains_BONUS":83 in codes,
            "contains_hybrid":bool(groups),"hybrid_group":";".join(groups),
            "semantic_state":"MU_RULE_VERIFIED_ONLY" if codes=={81} else "BLOCKED_NCS_BONUS_HYBRID" if codes & (HYBRID|{82,83}) else "OTHER",
        })
    with (out/"db29-requiresoul-semantic-card-matrix.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(card_rows[0].keys()));w.writeheader();w.writerows(card_rows)

    summary={
        "source_release":"fm1-carddb-29","unique_target_cards":len(target),
        "source_join_complete":True,"token_sequence_join_complete":True,
        "token_occurrences":len(rows),"card_type_distribution":dict(sorted(card_type_counts.items())),
        "token_card_occurrences_by_code":{str(k):token_card_counts[k] for k in sorted(token_card_counts)},
        "token_occurrences_by_code":{str(k):token_occurrences[k] for k in sorted(token_occurrences)},
        "hybrid_card_counts_by_code":dict(sorted(hybrid_group_counts.items())),
        "ncs_bonus_overlap_card_count":len(overlaps),"ncs_bonus_overlap_card_ids":sorted(overlaps),
        "evidence_states":{"81":"MU rule verified, no extension to NCS/BONUS/hybrid","82":"blocked","83":"blocked","hybrid_codes":"blocked"},
        "runtime_promotion_allowed":False,"db29_modified":False,"db30_created":False,
        "interpretation":"This is a complete card/token inventory and evidence-boundary matrix. It does not infer or implement payment rules for NCS, BONUS, or hybrid tokens."
    }
    (out/"db29-requiresoul-semantic-matrix-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))


if __name__=="__main__":
    main()
