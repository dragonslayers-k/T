#!/usr/bin/env python3
"""Infer remaining FM1 skill enums from card-local text, preserving provenance."""
import json, re, sqlite3, sys
from collections import Counter
from pathlib import Path

def norm(s):
    return "".join(str(s or "").split())

def main(db_path="data/fm1_cards.sqlite"):
    db=sqlite3.connect(db_path)
    db.execute("PRAGMA foreign_keys=ON")
    rows=db.execute("""
      SELECT source_field,source_enum_value,source_name,card_count
      FROM skill_enum_inventory WHERE mapping_status='unmapped' OR (mapping_status='inferred' AND rule_id IN (SELECT rule_id FROM game_rule_catalog WHERE confidence='low'))
      ORDER BY source_field,source_enum_value
    """).fetchall()
    done=0; evidence_backed=0; name_only=0
    for field,enum_value,name,card_count in rows:
        if not name or name=="없음": continue
        evidence=db.execute("""
          SELECT c.card_id,c.name,c.source_card_url,ct.text_type,
                 COALESCE(NULLIF(ct.plain_text,''),ct.source_text)
          FROM card_rule_mappings m
          JOIN cards c ON c.card_id=m.card_id
          JOIN card_texts ct ON ct.card_id=c.card_id
          WHERE m.source_field=? AND m.source_name=?
            AND ct.text_type IN ('card_text','additional_text')
          ORDER BY c.card_id,ct.text_id
        """,(field,name)).fetchall()
        candidates=[]
        aliases={
          "네이처드레인":["네이쳐드레인"],"기계배치":["기체배치"],"다잉메시지":["다잉메세지"],
          "구원자의인정":["구원자의인장"],"눈사람만들기":["눈사람소환"],
          "디펜스브레스":["디펜브레스"],"순수한광휘":["순수의광휘"],
          "순화공격":["순화능력"],"블러드스웜":["블러드스윕"],
          "언럭":["언력"],"치명능력":["치명공격"],"파워트랜스":["파워트렌스"],
          "크로스카운터":["크로스카운트"],"탈부수기":["달부수기"]
        }
        labels=[name]+aliases.get(name,[])
        for cid,cname,url,typ,txt in evidence:
            for block in re.split(r"\n+|(?=[★☆▶※◈])",txt or ""):
                block=re.sub(r"^[★☆▶※◈●○\s]+","",block.strip())
                for label in labels:
                    if norm(block).startswith(norm(label)):
                        body=re.sub(r"^\s*"+re.escape(label)+r"\s*[:：]?\s*","",block,count=1).strip()
                        if body:
                            candidates.append((cid,cname,url,typ,body,label))
                            break
        variants=Counter(norm(x[4]) for x in candidates)
        body=""
        if variants:
            best=variants.most_common(1)[0][0]
            body=next(x[4] for x in candidates if norm(x[4])==best)
        refs=[{"cardId":x[0],"cardName":x[1],"url":x[2],"textType":x[3],"effectText":x[4],"matchedSkillLabel":x[5]} for x in candidates[:8]]
        rid="inferred_"+field.lower()+"_"+str(enum_value)
        definition={"trigger":"conditional_or_passive","target":"text_defined","rawEffectText":body,"operations":[]}
        if body:
            if re.search(r"공격\s*시|공격시",body): definition["trigger"]="on_attack"
            elif re.search(r"방어\s*시|방어시",body): definition["trigger"]="on_defense"
            elif re.search(r"자신\s*파괴\s*시",body): definition["trigger"]="on_self_destroy"
            elif re.search(r"적\s*\d*\s*파괴\s*시",body): definition["trigger"]="on_enemy_destroy"
            for stat in ("AP","DP","HP"):
                for m in re.finditer(stat+r"\s*([+-])\s*(\d+)",body):
                    definition["operations"].append({"kind":"modify_stat","stat":stat.lower(),"operator":m.group(1),"value":int(m.group(2))})
                if re.search(stat+r"\s*=\s*0",body):
                    definition["operations"].append({"kind":"set_stat","stat":stat.lower(),"value":0})
            if re.search(r"파괴",body): definition["operations"].append({"kind":"destroy","target":"text_defined"})
            if re.search(r"데미지|피해",body): definition["operations"].append({"kind":"damage","amount":"text_defined"})
            if re.search(r"회복|흡수",body): definition["operations"].append({"kind":"recover","amount":"text_defined"})
            if re.search(r"소환",body): definition["operations"].append({"kind":"summon","target":"text_defined"})
            if re.search(r"부여",body): definition["operations"].append({"kind":"grant_status_or_skill","target":"text_defined"})
        if not definition["operations"]:
            definition["operations"]=[{"kind":"unparsed_operation","note":"원문 보존; 실행 연산은 추가 검증 필요"}]
        authority="inferred"
        confidence="medium" if body else "low"
        source={"kind":"card_text_inference" if body else "name_only_inference",
                "sourceField":field,"sourceEnumValue":str(enum_value),
                "cardCount":card_count,"evidenceCount":len(candidates),
                "uniqueEffectVariants":len(variants),"references":refs}
        db.execute("""
          INSERT OR REPLACE INTO game_rule_catalog(
            rule_id,rule_family,canonical_name,aliases_json,definition_json,
            source_authority,confidence,verification_status,implementation_status,
            source_references_json,source_conflicts_json,playable_by_default,catalogue_version
          ) VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?)
        """,(rid,"unit_special_skill",name,json.dumps([name],ensure_ascii=False),
             json.dumps(definition,ensure_ascii=False,sort_keys=True),authority,confidence,
             "inferred","inferred_pending_validation",json.dumps([source],ensure_ascii=False),
             "[]",0,2))
        db.execute("""
          UPDATE card_rule_mappings SET rule_id=?,mapping_status='inferred',
            confidence=?,evidence_references_json=?
          WHERE source_field=? AND source_name=? AND mapping_status IN ('unmapped','inferred')
        """,(rid,confidence,json.dumps([source],ensure_ascii=False),field,name))
        db.execute("""
          UPDATE skill_enum_inventory SET mapping_status='inferred',rule_id=?,
            mapped_card_count=card_count
          WHERE source_field=? AND source_name=? AND mapping_status IN ('unmapped','inferred')
        """,(rid,field,name))
        done+=1
        if body: evidence_backed+=1
        else: name_only+=1
    db.commit()
    remaining=db.execute("SELECT COUNT(*) FROM skill_enum_inventory WHERE mapping_status='unmapped'").fetchone()[0]
    result={"inferredSkillKinds":done,"evidenceBacked":evidence_backed,"nameOnlyLowConfidence":name_only,
            "remainingUnmappedKinds":remaining,
            "remainingUnmappedCardRows":db.execute("SELECT COUNT(*) FROM card_rule_mappings WHERE mapping_status='unmapped'").fetchone()[0],
            "foreignKeyErrors":len(db.execute("PRAGMA foreign_key_check").fetchall())}
    print(json.dumps(result,ensure_ascii=False,indent=2))
    db.close()
    if remaining or result["remainingUnmappedCardRows"] or result["foreignKeyErrors"]: sys.exit(2)

if __name__=="__main__":
    main(sys.argv[1] if len(sys.argv)>1 else "data/fm1_cards.sqlite")
