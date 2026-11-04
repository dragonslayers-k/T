#!/usr/bin/env python3
"""Infer FM1 skill meanings from card-local descriptions, including split heading/body lines.

Unlike the earlier implementation, this module inserts a stable rule catalogue row
before attaching a previously unmapped card skill. A successful extraction count
therefore means persisted mappings, not merely analyzed candidates.
"""
import json, re, sqlite3, sys, hashlib
from collections import Counter

ALIASES={
 "네이처드레인":["네이쳐드레인"],"기계배치":["기체배치"],"다잉메시지":["다잉메세지"],
 "구원자의인정":["구원자의인장"],"눈사람만들기":["눈사람소환"],
 "디펜스브레스":["디펜브레스"],"순수한광휘":["순수의광휘"],
 "순화공격":["순화능력"],"블러드스웜":["블러드스윕"],
 "언럭":["언력"],"치명능력":["치명공격"],"파워트랜스":["파워트렌스"],
 "크로스카운터":["크로스카운트"],"탈부수기":["달부수기"]
}
def norm(s): return "".join(str(s or "").split())
def clean_line(s): return re.sub(r"^[★☆▶※◈●○◆◇■\s]+","",s.strip())

def extract_definitions(name, text):
    labels=[name]+ALIASES.get(name,[])
    lines=(text or "").replace("<br/>","\n").replace("<br>","\n").replace("<br />","\n").splitlines()
    found=[]
    for i,line in enumerate(lines):
        clean=clean_line(line)
        clean_norm=norm(clean)
        label=next((x for x in labels if clean_norm.startswith(norm(x))),None)
        if not label: continue
        # Preserve the original substring after the matched label even when spaces
        # occur inside the visible heading.
        pos=0; consumed=0
        while pos<len(clean) and consumed<len(norm(label)):
            if not clean[pos].isspace(): consumed+=1
            pos+=1
        rest=clean[pos:].strip()
        rest=re.sub(r"^(?:[/／]\s*)+","",rest).strip()
        rest=re.sub(r"^[:：]\s*","",rest).strip()
        parts=[rest] if rest else []
        if not parts:
            for j in range(i+1,min(len(lines),i+6)):
                nxt=lines[j].strip()
                if not nxt:
                    continue
                if re.match(r"^[★☆▶※◈●○◆◇■]",nxt): break
                nxt=re.sub(r"^[/:：\s]+","",nxt).strip()
                if nxt: parts.append(nxt)
                if parts: break
        body=" ".join(parts).strip()
        if body:
            found.append({"label":label,"body":body,"line":i})
    unique={}
    for x in found: unique.setdefault(norm(x["body"]),x)
    return list(unique.values())

def operations_from_text(body):
    t=body or ""; ops=[]
    for stat,aliases in {
      "ap":r"AP|공격력|공격치","dp":r"DP|방어력|방어치","hp":r"HP|체력|체력치"
    }.items():
        for m in re.finditer(r"("+aliases+r")\s*([+-])\s*(\d+)",t):
            ops.append({"kind":"modify_stat","stat":stat,"operator":m.group(2),"value":int(m.group(3))})
        for m in re.finditer(r"("+aliases+r")\s*=\s*(\d+)",t):
            ops.append({"kind":"set_stat","stat":stat,"value":int(m.group(2))})
    if re.search(r"코인|동전|C\d|AC|HC",t):
        ops.append({"kind":"modify_coin","scope":"text_defined","rawFormulaCandidates":re.findall(r"[+-]?\d*C\d+|[+-]\d+%|AC[+-]?\d+|HC[+-]?\d+",t)})
    if re.search(r"공방체|공체|공방|공격력|방어력|체력",t) and re.search(r"증가|감소|변경|높|낮|올리|내리",t):
        ops.append({"kind":"modify_combat_stats","stats":"text_defined","rawText":t})
    if re.search(r"상태",t) and re.search(r"부여|제거|해제|변경|유지|증가|감소",t):
        ops.append({"kind":"modify_status","scope":"text_defined"})
    if re.search(r"기술",t) and re.search(r"부여|추가|변경|삭제|제거|일반공격|일반방어",t):
        ops.append({"kind":"modify_skill","scope":"text_defined"})
    if re.search(r"소환|배치",t): ops.append({"kind":"summon_or_deploy","scope":"text_defined"})
    if re.search(r"파괴|소멸|함께 파괴|소각",t): ops.append({"kind":"destroy","scope":"text_defined"})
    if re.search(r"데미지|피해",t): ops.append({"kind":"deal_damage","scope":"text_defined"})
    if re.search(r"회복|치료|흡수",t): ops.append({"kind":"heal_or_recover","scope":"text_defined"})
    if re.search(r"드로우|뽑|덱.{0,8}(?:파괴|소각)|핸드로 이동",t): ops.append({"kind":"draw_or_mill","scope":"text_defined"})
    if re.search(r"종족|소속",t) and re.search(r"없음|삭제|변경",t): ops.append({"kind":"modify_race_or_faction","scope":"text_defined"})
    if re.search(r"기호|★|▲|▼",t): ops.append({"kind":"modify_stat_mark","scope":"text_defined"})
    if re.search(r"소울|유지비|무소울|유소울|코스트",t): ops.append({"kind":"modify_soul_cost","scope":"text_defined"})
    if not ops:
        ops=[{"kind":"text_defined_effect","rawText":t,"executable":False}]
    # Keep one copy of every operation.
    return [json.loads(x) for x in dict.fromkeys(json.dumps(x,ensure_ascii=False,sort_keys=True) for x in ops)]

def lexical_family(name):
    rules=[
      (r"동전|코인","coin_or_combat_coin_manipulation"),
      (r"아레아|오오라|오라","elemental_area_or_aura"),
      (r"펌프킨","pumpkin_archetype_effect"),
      (r"눈덩이|눈사람","snowball_or_snowman_chain"),
      (r"그레이브|묘지","graveyard_interaction"),
      (r"드레인|바인드|워터","elemental_drain_or_bind"),
      (r"파이어|화염|스웜|스파크|검기|메테오|스톰","elemental_or_direct_attack"),
      (r"카운터|반격|리벤지|후폭풍|히트","counterattack_or_retaliation"),
      (r"트랩|타워","field_structure_or_trap"),
      (r"서먼|소환|헌트","summon_interaction"),
      (r"코스트|코스트다운","cost_reduction_or_change"),
      (r"폴리모프|체인지|변신|탈부수기","transformation_or_replacement"),
      (r"각인|결계","mark_or_barrier_control"),
      (r"타임|시간","time_conditioned_effect"),
      (r"재능|소질|개화|만개","growth_or_progression"),
      (r"치명","critical_or_fatal_attack"),
      (r"사신|집행","execute_or_destruction"),
    ]
    for pat,family in rules:
        if re.search(pat,name,re.I): return family
    return "named_special_effect_unclassified"

def _rule_id(field, enum_value):
    raw=f"{field.lower()}_{enum_value}"
    safe=re.sub(r"[^a-z0-9_]+","_",raw.casefold()).strip("_")
    return "inferred_"+safe

def infer_one(db, field, enum_value, name, card_count):
    evidence=db.execute("""
      SELECT DISTINCT c.card_id,c.name,c.source_card_url,ct.text_type,
             COALESCE(NULLIF(ct.plain_text,''),ct.source_text)
      FROM card_rule_mappings m
      JOIN cards c ON c.card_id=m.card_id
      JOIN card_texts ct ON ct.card_id=c.card_id
      WHERE m.source_field=? AND m.source_enum_value=? AND m.source_name=?
        AND ct.text_type IN ('card_text','additional_text')
      ORDER BY c.card_id,ct.text_id
    """,(field,str(enum_value),name)).fetchall()
    candidates=[]
    for cid,cname,url,typ,txt in evidence:
        for item in extract_definitions(name,txt):
            candidates.append((cid,cname,url,typ,item["body"],item["label"]))
    variants=Counter(norm(x[4]) for x in candidates)
    chosen=""
    if variants:
        best=variants.most_common(1)[0][0]
        chosen=next(x[4] for x in candidates if norm(x[4])==best)
    refs=[]; seen=set()
    for x in candidates:
        k=(x[0],x[2],norm(x[4]))
        if k in seen: continue
        seen.add(k)
        refs.append({"cardId":x[0],"cardName":x[1],"url":x[2],
                     "textType":x[3],"matchedSkillLabel":x[5],"effectText":x[4]})
    rid=_rule_id(field,enum_value)
    if chosen:
        definition={"trigger":"text_defined","target":"text_defined","rawEffectText":chosen,
                    "operations":operations_from_text(chosen),
                    "uniqueEffectVariants":len(variants),
                    "allObservedVariants":[{"text":next(x[4] for x in candidates if norm(x[4])==k),
                                            "count":n} for k,n in variants.most_common()]}
        confidence="medium"; kind="card_text_inference"
    else:
        family=lexical_family(name)
        definition={"trigger":"unknown","target":"unknown","rawEffectText":"",
                    "operations":[{"kind":"name_based_semantic_candidate",
                                   "semanticFamily":family,"skillName":name,
                                   "executable":False}],
                    "nameBasedGuess":{"semanticFamily":family,"confidence":"low",
                      "note":"원문 설명에서 해당 기술명을 포함한 정의 문장을 찾지 못해 명칭과 카드 문맥으로 분류한 추정. 정확한 수치·대상·발동 조건은 미확인"}}
        confidence="low"; kind="name_only_inference"
    source={"kind":kind,"sourceField":field,"sourceEnumValue":str(enum_value),
            "cardCount":card_count,"evidenceCount":len(candidates),
            "uniqueEffectVariants":len(variants),"references":refs}
    db.execute("""
      INSERT INTO game_rule_catalog(
        rule_id,rule_family,canonical_name,aliases_json,definition_json,
        source_authority,confidence,verification_status,implementation_status,
        source_references_json,source_conflicts_json,playable_by_default,catalogue_version
      ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
      ON CONFLICT(rule_id) DO UPDATE SET
        rule_family=excluded.rule_family,canonical_name=excluded.canonical_name,
        aliases_json=excluded.aliases_json,definition_json=excluded.definition_json,
        source_authority=excluded.source_authority,confidence=excluded.confidence,
        verification_status=excluded.verification_status,
        implementation_status=excluded.implementation_status,
        source_references_json=excluded.source_references_json,
        source_conflicts_json=excluded.source_conflicts_json,
        playable_by_default=excluded.playable_by_default,
        catalogue_version=excluded.catalogue_version
    """,(rid,lexical_family(name),name,json.dumps(ALIASES.get(name,[]),ensure_ascii=False),
         json.dumps(definition,ensure_ascii=False,sort_keys=True),"inferred",confidence,
         "inferred","inferred_pending_validation",json.dumps([source],ensure_ascii=False,sort_keys=True),
         "[]",0,3))
    refs_json=json.dumps([source],ensure_ascii=False,sort_keys=True)
    db.execute("""
      UPDATE card_rule_mappings SET rule_id=?,mapping_status='inferred',
        confidence=?,evidence_references_json=?
      WHERE source_field=? AND source_enum_value=? AND source_name=?
    """,(rid,confidence,refs_json,field,str(enum_value),name))
    db.execute("""
      UPDATE skill_enum_inventory SET rule_id=?,mapping_status='inferred',
        mapped_card_count=card_count
      WHERE source_field=? AND source_enum_value=? AND source_name=?
    """,(rid,field,str(enum_value),name))
    mapped=db.execute("""
      SELECT COUNT(*) FROM card_rule_mappings
      WHERE source_field=? AND source_enum_value=? AND source_name=? AND rule_id=?
        AND mapping_status='inferred'
    """,(field,str(enum_value),name,rid)).fetchone()[0]
    if mapped!=card_count:
        raise RuntimeError(f"Persisted skill mapping mismatch {field}/{enum_value}/{name}: {mapped}!={card_count}")
    return {"ruleId":rid,"confidence":confidence,"evidenceCount":len(candidates),
            "uniqueEffectVariants":len(variants),"mappedCardRows":mapped}

def main(db_path="data/fm1_cards.sqlite"):
    db=sqlite3.connect(db_path); db.execute("PRAGMA foreign_keys=ON")
    rows=db.execute("""
      SELECT source_field,source_enum_value,source_name,card_count
      FROM skill_enum_inventory
      WHERE mapping_status='unmapped'
         OR (mapping_status='inferred' AND rule_id IN
             (SELECT rule_id FROM game_rule_catalog WHERE confidence='low'))
      ORDER BY source_field,source_enum_value
    """).fetchall()
    done=evidence_backed=name_only=0; persisted_rows=0
    details=[]
    with db:
      for field,enum_value,name,card_count in rows:
        if not name or name=="없음": continue
        result=infer_one(db,field,str(enum_value),name,int(card_count))
        done+=1; persisted_rows+=result["mappedCardRows"]; details.append(result)
        if result["confidence"]=="low": name_only+=1
        else: evidence_backed+=1
    remaining=db.execute("SELECT COUNT(*) FROM skill_enum_inventory WHERE mapping_status='unmapped'").fetchone()[0]
    low=db.execute("""
      SELECT COUNT(*) FROM game_rule_catalog
      WHERE source_authority='inferred' AND confidence='low'
    """).fetchone()[0]
    remaining_rows=db.execute("SELECT COUNT(*) FROM card_rule_mappings WHERE mapping_status='unmapped'").fetchone()[0]
    total_inventory=db.execute("SELECT COUNT(*) FROM skill_enum_inventory").fetchone()[0]
    total_map_rows=db.execute("SELECT COUNT(*) FROM card_rule_mappings").fetchone()[0]
    fk=len(db.execute("PRAGMA foreign_key_check").fetchall())
    result={"processedSkillKinds":done,"evidenceBackedSkillKinds":evidence_backed,
            "nameOnlyLowConfidenceSkillKinds":name_only,"remainingUnmappedKinds":remaining,
            "remainingLowConfidenceSkillKinds":low,"remainingUnmappedCardRows":remaining_rows,
            "persistedMappingRows":persisted_rows,"inventoryRows":total_inventory,
            "cardMappingRows":total_map_rows,"foreignKeyErrors":fk}
    print(json.dumps(result,ensure_ascii=False,indent=2)); db.close()
    if remaining or remaining_rows or fk or total_inventory==0 or total_map_rows==0: sys.exit(2)

if __name__=="__main__": main(sys.argv[1] if len(sys.argv)>1 else "data/fm1_cards.sqlite")
