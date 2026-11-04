#!/usr/bin/env python3
"""Infer FM1 skill meanings from card-local descriptions, including split heading/body lines."""
import json, re, sqlite3, sys
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
    lines=(text or "").replace("<br/>","\n").replace("<br>","\n").splitlines()
    found=[]
    for i,line in enumerate(lines):
        clean=clean_line(line)
        for label in labels:
            if not norm(clean).startswith(norm(label)): continue
            rest=clean[len(label):].strip()
            rest=re.sub(r"^(?:[/／]\s*)+","",rest).strip()
            rest=re.sub(r"^[:：]\s*","",rest).strip()
            parts=[rest] if rest else []
            if not parts:
                # Several official card descriptions put the skill name on one line
                # and its colon/body on the next line.
                for j in range(i+1,min(len(lines),i+5)):
                    nxt=lines[j].strip()
                    if not nxt:
                        if parts: break
                        continue
                    if re.match(r"^[★☆▶※◈●○◆◇■]",nxt): break
                    nxt=re.sub(r"^[/:：\s]+","",nxt).strip()
                    if nxt: parts.append(nxt)
                    if parts: break
            body=" ".join(parts).strip()
            if body:
                found.append({"label":label,"body":body,"line":i})
            break
    # Deduplicate equivalent statements while preserving source order.
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
        if re.search(r"("+aliases+r")\s*=\s*\d+",t):
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
    if re.search(r"파괴|소멸|함께 파괴",t): ops.append({"kind":"destroy","scope":"text_defined"})
    if re.search(r"데미지|피해",t): ops.append({"kind":"deal_damage","scope":"text_defined"})
    if re.search(r"기호|★|▲|▼",t): ops.append({"kind":"modify_stat_mark","scope":"text_defined"})
    if re.search(r"종족|소속",t) and re.search(r"없음|삭제|변경",t):
        ops.append({"kind":"modify_race_or_faction","scope":"text_defined"})
    if re.search(r"소울|유지비|무소울|유소울|코스트",t):
        ops.append({"kind":"modify_soul_cost","scope":"text_defined"})
    if not ops:
        ops=[{"kind":"text_defined_effect","rawText":t,"executable":False}]
    return ops

def lexical_family(name):
    rules=[
      (r"동전|코인","coin_or_combat_coin_manipulation"),
      (r"아레아|오오라|오라","elemental_area_or_aura"),
      (r"펌프킨","pumpkin_archetype_effect"),
      (r"눈덩이|눈사람","snowball_or_snowman_chain"),
      (r"그레이브|그레이브|묘지","graveyard_interaction"),
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
    done=evidence_backed=name_only=0
    for field,enum_value,name,card_count in rows:
        if not name or name=="없음": continue
        evidence=db.execute("""
          SELECT DISTINCT c.card_id,c.name,c.source_card_url,ct.text_type,
                 COALESCE(NULLIF(ct.plain_text,''),ct.source_text)
          FROM card_rule_mappings m
          JOIN cards c ON c.card_id=m.card_id
          JOIN card_texts ct ON ct.card_id=c.card_id
          WHERE m.source_field=? AND m.source_name=?
            AND ct.text_type IN ('card_text','additional_text')
          ORDER BY c.card_id,ct.text_id
        """,(field,name)).fetchall()
        candidates=[]
        for cid,cname,url,typ,txt in evidence:
            for item in extract_definitions(name,txt):
                candidates.append((cid,cname,url,typ,item["body"],item["label"]))
        variants=Counter(norm(x[4]) for x in candidates)
        body=""
        if variants:
            best=variants.most_common(1)[0][0]
            body=next(x[4] for x in candidates if norm(x[4])==best)
        refs=[]
        seen=set()
        for x in candidates:
            k=(x[0],x[2],norm(x[4]))
            if k in seen: continue
            seen.add(k)
            refs.append({"cardId":x[0],"cardName":x[1],"url":x[2],"textType":x[3],
                         "matchedSkillLabel":x[5],"effectText":x[4]})
        rid="inferred_"+field.lower()+"_"+str(enum_value)
        if body:
            definition={"trigger":"text_defined","target":"text_defined","rawEffectText":body,
                        "operations":operations_from_text(body),
                        "uniqueEffectVariants":len(variants)}
            confidence="medium"; kind="card_text_inference"
        else:
            family=lexical_family(name)
            definition={"trigger":"unknown","target":"unknown","rawEffectText":"",
                        "operations":[{"kind":"name_based_semantic_candidate",
                                       "semanticFamily":family,"value":"unknown","executable":False}],
                        "nameBasedGuess":{"semanticFamily":family,"confidence":"low",
                          "note":"기술명과 주변 카드 문맥에서 분류한 추정. 실제 수치·대상·발동 조건은 원문 근거 없음"}}
            confidence="low"; kind="name_only_inference"
        source={"kind":kind,"sourceField":field,"sourceEnumValue":str(enum_value),
                "cardCount":card_count,"evidenceCount":len(candidates),
                "uniqueEffectVariants":len(variants),"references":refs}
        db.execute("""
          UPDATE game_rule_catalog SET definition_json=?,source_authority='inferred',
            confidence=?,verification_status='inferred',
            implementation_status='inferred_pending_validation',
            source_references_json=?,catalogue_version=3
          WHERE rule_id=?
        """,(json.dumps(definition,ensure_ascii=False,sort_keys=True),confidence,
             json.dumps([source],ensure_ascii=False,sort_keys=True),rid))
        db.execute("""
          UPDATE card_rule_mappings SET mapping_status='inferred',
            confidence=?,evidence_references_json=?
          WHERE source_field=? AND source_name=? AND rule_id=?
        """,(confidence,json.dumps([source],ensure_ascii=False,sort_keys=True),field,name,rid))
        db.execute("""
          UPDATE skill_enum_inventory SET mapping_status='inferred',rule_id=?,
            mapped_card_count=card_count
          WHERE source_field=? AND source_name=? AND rule_id=?
        """,(rid,field,name,rid))
        done+=1
        if body: evidence_backed+=1
        else: name_only+=1
    db.commit()
    remaining=db.execute("SELECT COUNT(*) FROM skill_enum_inventory WHERE mapping_status='unmapped'").fetchone()[0]
    low=db.execute("SELECT COUNT(*) FROM game_rule_catalog WHERE source_authority='inferred' AND confidence='low'").fetchone()[0]
    result={"processedSkillKinds":done,"evidenceBackedSkillKinds":evidence_backed,
            "nameOnlyLowConfidenceSkillKinds":name_only,"remainingUnmappedKinds":remaining,
            "remainingLowConfidenceSkillKinds":low,
            "remainingUnmappedCardRows":db.execute("SELECT COUNT(*) FROM card_rule_mappings WHERE mapping_status='unmapped'").fetchone()[0],
            "foreignKeyErrors":len(db.execute("PRAGMA foreign_key_check").fetchall())}
    print(json.dumps(result,ensure_ascii=False,indent=2)); db.close()
    if remaining or result["remainingUnmappedCardRows"] or result["foreignKeyErrors"]: sys.exit(2)
if __name__=="__main__": main(sys.argv[1] if len(sys.argv)>1 else "data/fm1_cards.sqlite")
