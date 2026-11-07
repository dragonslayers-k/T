#!/usr/bin/env python3
"""Full-population DB29 effect-text census for NCS, BONUS and hybrid RequireSoul cards.

This is an evidence extraction step, not a rules interpreter. It preserves source
text verbatim and classifies lexical mentions only; no payment semantics are inferred.
"""
from __future__ import annotations
import argparse, csv, json, re
from collections import Counter
from pathlib import Path

HYBRID={12,13,14,15,22,23,24,32,33,42,43,52,53,62}
SPECIAL={82,83}
NAMES={12:"DARK_EARTH",13:"DARK_FIRE",14:"DARK_LIGHT",15:"DARK_WATER",
22:"FIRE_FOREST",23:"FIRE_IRON",24:"FIRE_WATER",32:"WATER_EARTH",
33:"WATER_FOREST",42:"FOREST_IRON",43:"FOREST_LIGHT",52:"IRON_EARTH",
53:"IRON_LIGHT",62:"EARTH_LIGHT",82:"NCS",83:"BONUS"}
LEXICON=[
 ("literal_ncs", r"NCS\\s*소울|NCS소울|NCS"),
 ("literal_bonus", r"BONUS|보너스"),
 ("literal_mu_or_colorless", r"무소울|무속성|무색"),
 ("ordinary_soul", r"유소울"),
 ("upkeep", r"유지비|유지 비용|유지"),
 ("summon_or_pay", r"소환|지불|소비|결제|비용"),
 ("convert_or_change", r"변환|전환|교체|변경|바꿔|바꾸"),
 ("generate_or_create", r"생성|만들|획득|추가"),
 ("reduce_or_discount", r"감소|줄이|할인|경감"),
 ("all_purpose", r"올라운드|모든 속성|전속성|아무 속성"),
]
PATTERNS=[(label,re.compile(pattern,re.I)) for label,pattern in LEXICON]

def raw(row):
    x=row.get("raw_payload")
    return x if isinstance(x,dict) else row.get("sourceFields") if isinstance(row.get("sourceFields"),dict) else row

def cid(row):
    r=raw(row)
    return str(row.get("card_id") or row.get("id") or r.get("ID") or r.get("NumID") or "").strip()

def tokens(value):
    s=str(value or "")
    if not s or not s.isdigit() or len(s)%4: raise ValueError(f"Invalid RequireSoul {s!r}")
    out=[]
    for i in range(0,len(s),4):
        code=int(s[i:i+2]); amount=int(s[i+2:i+4])
        if code not in NAMES: continue
        out.append((s[i:i+4],code,amount))
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source-cards-jsonl",type=Path,required=True)
    p.add_argument("--evidence-dir",type=Path,required=True)
    p.add_argument("--output-dir",type=Path,required=True)
    a=p.parse_args(); a.output_dir.mkdir(parents=True,exist_ok=True)
    src={}
    for ln,line in enumerate(a.source_cards_jsonl.read_text(encoding="utf-8").splitlines(),1):
        if not line.strip(): continue
        row=json.loads(line); key=cid(row)
        if key: 
            if key in src: raise SystemExit(f"duplicate source ID {key} line {ln}")
            src[key]=row
    target={}
    for line in (a.evidence_dir/"target-cards.jsonl").read_text(encoding="utf-8").splitlines():
        if line.strip():
            row=json.loads(line); target[str(row["card_id"])]=row
    if len(target)!=831: raise SystemExit(f"expected 831 target cards, got {len(target)}")
    rows=[]; groups=Counter(); text_nonempty=Counter(); label_counts=Counter(); overlap=[]
    for key,e in sorted(target.items()):
        if key not in src: raise SystemExit(f"missing source card {key}")
        r=raw(src[key]); req=str(r.get("RequireSoul",""))
        if req != str(e.get("source_require_soul","")): raise SystemExit(f"RequireSoul mismatch {key}")
        ts=tokens(req); codes={x[1] for x in ts}
        selected=[x for x in ts if x[1] in SPECIAL or x[1] in HYBRID]
        if not selected: continue
        base=str(r.get("TextBase") or "")
        extra=str(r.get("TextExtra") or "")
        combined=re.sub(r"<br\\s*/?>","\n",base+"\n"+extra,flags=re.I)
        hits=[label for label,pat in PATTERNS if pat.search(combined)]
        if base.strip(): text_nonempty["TextBase"]+=1
        if extra.strip(): text_nonempty["TextExtra"]+=1
        if 82 in codes and 83 in codes: overlap.append(key)
        cardtype=str(r.get("Category",e.get("card_type","")))
        group="NCS+BONUS" if {82,83}.issubset(codes) else "NCS" if 82 in codes else "BONUS" if 83 in codes else "HYBRID"
        groups[group]+=1
        for token,code,amount in selected:
            for hit in hits: label_counts[hit]+=1
            rows.append({
             "card_id":key,"name":str(r.get("Name") or e.get("name") or ""),
             "card_type_code":cardtype,"review_group":group,
             "require_soul_raw":req,"token_raw":token,"token_code":code,
             "token_name":NAMES[code],"amount":amount,
             "text_base_raw":base,"text_extra_raw":extra,
             "lexical_evidence_labels":";".join(hits),
             "text_has_any_lexical_hit":bool(hits),
             "source_card_url":str(e.get("source_card_url") or ""),
             "semantics":"UNVERIFIED_LEXICAL_EVIDENCE_ONLY",
            })
    out=a.output_dir/"db29-requiresoul-special-card-effect-text-census.csv"
    fields=list(rows[0].keys())
    with out.open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)
    summary={
      "source_release":"fm1-carddb-29","target_cards":len(target),
      "special_token_cards":len({x["card_id"] for x in rows}),
      "special_token_rows":len(rows),"group_card_counts":dict(sorted(groups.items())),
      "ncs_bonus_overlap_count":len(overlap),"ncs_bonus_overlap_ids":sorted(overlap),
      "source_join_complete":True,"require_soul_join_complete":True,
      "cards_with_textbase":text_nonempty["TextBase"],
      "cards_with_textextra":text_nonempty["TextExtra"],
      "lexical_label_counts_by_token_row":dict(sorted(label_counts.items())),
      "runtime_promotion_allowed":False,"db29_modified":False,"db30_created":False,
      "interpretation":"Full population source-text census only. Lexical matches are not payment-rule evidence; no NCS, BONUS, or hybrid runtime mapping is authorized."
    }
    (a.output_dir/"db29-requiresoul-special-card-effect-text-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(summary,ensure_ascii=False,indent=2))
if __name__=="__main__": main()
