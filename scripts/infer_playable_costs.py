#!/usr/bin/env python3
"""Generate playable cost estimates for cards whose source cost cannot be decoded.

Estimates are intentionally emitted as a separate overlay, preserving source data.
Candidates are matched by card type, faction, raw RequireSoul prefix/pattern and
nearby episode. No unknown is silently treated as a zero-cost card.
"""
import argparse, collections, json, statistics
from pathlib import Path

def get_raw(card):
    return card.get("sourceFields") or card.get("raw_payload") or {}

def peer_key(card):
    raw=get_raw(card)
    soul=str(card.get("soulCostRaw") or raw.get("RequireSoul") or "")
    # Preserve token classes and counts while stripping the unresolved suffix.
    tokens=[]
    if len(soul)%4==0:
        for i in range(0,len(soul),4):
            t=soul[i:i+4]
            tokens.append((t[:2],t[2:]))
    return str(card.get("type") or raw.get("Category")), str(card.get("faction") or raw.get("SoulType")), tuple(tokens[:-1] if tokens else ())

def usable_cost(card):
    cost=card.get("cost")
    if not card.get("costKnown") or not isinstance(cost,dict) or not cost:
        return None
    if any(not isinstance(v,(int,float)) or v<0 for v in cost.values()):
        return None
    return {str(k):int(v) for k,v in cost.items() if v}

def dist(a,b):
    return sum(abs(a.get(k,0)-b.get(k,0)) for k in set(a)|set(b))

def infer(cards):
    known=[c for c in cards if usable_cost(c) is not None]
    exact=collections.defaultdict(list); by_type_faction=collections.defaultdict(list); by_type=collections.defaultdict(list)
    for c in known:
        exact[peer_key(c)].append(c)
        by_type_faction[(c.get("type"),c.get("faction"))].append(c)
        by_type[c.get("type")].append(c)
    output=[]
    for c in cards:
        if usable_cost(c) is not None: continue
        key=peer_key(c); candidates=exact.get(key,[])
        tier="exact-pattern"
        if len(candidates)<3:
            candidates=by_type_faction[(c.get("type"),c.get("faction"))];tier="type-faction"
        if len(candidates)<3:
            candidates=by_type[c.get("type")];tier="type"
        if not candidates:
            # Fallback uses global distribution, still explicit and low-confidence.
            candidates=known;tier="global"
        if not candidates:
            estimate={"neutral":1}; confidence="very-low"; explanation="No decodable peer costs; conservative playable fallback"
        else:
            # Nearest records in common raw semantic fields.
            raw=get_raw(c)
            def score(peer):
                pr=get_raw(peer)
                s=0
                for field in ("Episode","RareType","RaceType","CompanyType","UnitType","LV","DeckLimit"):
                    if raw.get(field) is not None and raw.get(field)==pr.get(field): s+=1
                if c.get("faction")==peer.get("faction"):s+=2
                if c.get("type")==peer.get("type"):s+=2
                return s
            candidates=sorted(candidates,key=score,reverse=True)[:25]
            allcolors=set(k for peer in candidates for k in (usable_cost(peer) or {}))
            estimate={}
            for color in allcolors:
                vals=[(usable_cost(peer) or {}).get(color,0) for peer in candidates]
                # Median of peers minimizes influence from extreme card designs.
                value=int(round(statistics.median(vals)))
                if value: estimate[color]=value
            if not estimate: estimate={"neutral":1}
            confidence="medium" if tier in ("exact-pattern","type-faction") and len(candidates)>=8 else "low"
            explanation=f"Median cost across {len(candidates)} nearest source-known peers at {tier} level"
        output.append({
            "cardId":str(c.get("id") or c.get("card_id") or ""),
            "name":c.get("name",""),
            "type":c.get("type",""),
            "faction":c.get("faction",""),
            "sourceCost":c.get("cost"),
            "sourceCostKnown":bool(c.get("costKnown")),
            "inferredPlayableCost":estimate,
            "costValueStatus":"inferred",
            "confidence":confidence,
            "method":tier,
            "reason":explanation,
            "sourceCardUrl":c.get("sourceCardUrl") or c.get("source_card_url"),
            "rawSoulCost":c.get("soulCostRaw") or get_raw(c).get("RequireSoul")
        })
    return output

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--cards",type=Path)
    p.add_argument("--output",type=Path,default=Path("inferred-cost-overlay.json"))
    p.add_argument("--self-test",action="store_true")
    a=p.parse_args()
    if a.self_test:
        sample=[{"id":"known","type":"unit","faction":"fire","cost":{"fire":2},"costKnown":True,"sourceFields":{}},{"id":"missing","type":"unit","faction":"fire","cost":{},"costKnown":False,"sourceFields":{}}]
        out=infer(sample);assert len(out)==1 and out[0]["costValueStatus"]=="inferred" and out[0]["inferredPlayableCost"]
        print("cost inference self-test passed");return
    if not a.cards:
        p.error("--cards is required unless --self-test")
    rows=json.loads(a.cards.read_text(encoding="utf-8"))
    result=infer(rows);a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
    print(json.dumps({"cards":len(rows),"inferred":len(result),"confidence":dict(collections.Counter(x["confidence"] for x in result))},ensure_ascii=False))
if __name__=="__main__":main()
