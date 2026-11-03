#!/usr/bin/env python3
"""Evidence-preserving field/taxonomy audit for the immutable FM1 source dump."""
import argparse, collections, json, re
from pathlib import Path

CATEGORY_NAMES = {"1":"Land","2":"Unit","3":"Magic","4":"Item","5":"Enchant",
                  "land":"Land","unit":"Unit","magic":"Magic","item":"Item","enchant":"Enchant"}
DETAIL_BASE = "https://fmlunatic.com/card/"
IMPORTANT_FIELDS = (
    "Name","Category","SoulType","RequireSoul","RequireLP","RareType","RareUI","Episode",
    "RaceType","CompanyType","EtcType","UnitType","Skill1","Skill2","RankType",
    "DeckLimit","BuyGrade","EnchantSlot","ReleaseDate","TextBase","TextExtra"
)

def rows(v):
    return v if isinstance(v,list) else list(v.values()) if isinstance(v,dict) else []

def enum_values(enum):
    out={}
    for key, raw in enum.items():
        if not key.startswith("Enum+"): continue
        field=key.split("+",1)[1]
        values=set()
        for item in rows(raw):
            if isinstance(item,list) and item: values.add(str(item[0]))
            elif isinstance(item,dict) and item.get("KIND") is not None: values.add(str(item["KIND"]))
        out[field]=values
    return out

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cards-jsonl",required=True,type=Path)
    p.add_argument("--enumtable",required=True,type=Path)
    p.add_argument("--output",required=True,type=Path)
    p.add_argument("--expected",type=int,default=15350)
    a=p.parse_args()
    enum=json.loads(a.enumtable.read_text(encoding="utf-8"))
    allowed=enum_values(enum)
    counts=collections.Counter()
    present=collections.Counter()
    values=collections.defaultdict(collections.Counter)
    missing=[]
    url_errors=[]
    invalid_dates=[]
    duplicate_ids=[]
    ids=set()
    by_category=collections.defaultdict(collections.Counter)
    total=0
    with a.cards_jsonl.open(encoding="utf-8") as f:
        for n,line in enumerate(f,1):
            if not line.strip(): continue
            row=json.loads(line); raw=row.get("raw_payload") or {}
            total+=1
            cid=str(row.get("card_id") or row.get("id") or raw.get("KIND") or "")
            if cid in ids: duplicate_ids.append(cid)
            ids.add(cid)
            cat=str(raw.get("Category","missing"))
            category=CATEGORY_NAMES.get(cat,CATEGORY_NAMES.get(cat.lower(),"UNKNOWN"))
            counts[category]+=1
            detail=row.get("source_card_url")
            if not detail:
                url_errors.append({"card_id":cid,"reason":"missing_detail_url"})
            elif not detail.startswith(DETAIL_BASE):
                url_errors.append({"card_id":cid,"reason":"unexpected_detail_url","url":detail})
            else:
                tail=detail[len(DETAIL_BASE):].strip("/")
                if not tail or "/" in tail:
                    url_errors.append({"card_id":cid,"reason":"malformed_detail_url","url":detail})
            for field in IMPORTANT_FIELDS:
                val=raw.get(field)
                if val is not None and val!="":
                    present[field]+=1
                    values[field][str(val)]+=1
                    if field in allowed and field != "RequireSoul" and str(val) not in allowed[field]:
                        missing.append({"card_id":cid,"field":field,"value":val,"reason":"enum_value_not_in_enumtable"})
                elif field in ("Category","Name","RequireSoul"):
                    missing.append({"card_id":cid,"field":field,"reason":"required_source_field_missing"})
                if val is not None and val!="":
                    by_category[category][field]+=1
            date=raw.get("ReleaseDate")
            if date is not None and not re.fullmatch(r"\d{8}",str(date)) and not re.fullmatch(r"\d{4}-\d{2}-\d{2}",str(date)):
                invalid_dates.append({"card_id":cid,"value":date})
    summary={
      "expected_records":a.expected,"records":total,"unique_ids":len(ids),
      "duplicate_ids":duplicate_ids,"count_delta":total-a.expected,
      "category_counts":dict(counts),
      "field_presence":{k:{"present":present[k],"missing":total-present[k],"distinct_values":len(values[k])} for k in IMPORTANT_FIELDS},
      "enum_unknown_values":missing,"invalid_release_dates":invalid_dates,
      "detail_url_errors":url_errors,
      "category_field_presence":{cat:{field:{"present":v[field],"records":counts[cat]} for field in IMPORTANT_FIELDS} for cat,v in by_category.items()},
      "enum_field_count":len(allowed),
      "pass": total==a.expected and len(ids)==total and not duplicate_ids and not missing and not invalid_dates and not url_errors
    }
    a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("enum_unknown_values","invalid_release_dates","detail_url_errors","category_field_presence")},ensure_ascii=False))
    if not summary["pass"]: raise SystemExit("Card field/taxonomy audit requires review; inspect JSON report")

if __name__=="__main__": main()
