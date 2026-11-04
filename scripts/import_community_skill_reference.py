#!/usr/bin/env python3
"""Cross-check name-only inferred FM1 skills against the 2017 community catalogue."""
import html, json, re, sqlite3, sys, urllib.request
from html.parser import HTMLParser
from collections import Counter

URL="https://www.inven.co.kr/board/hs/3509/1426815"
class TextExtractor(HTMLParser):
    def __init__(self):
        super().__init__(); self.parts=[]
    def handle_starttag(self,tag,attrs):
        if tag in ("br","p","div","li","tr","td","th","h1","h2","h3"): self.parts.append("\n")
    def handle_endtag(self,tag):
        if tag in ("p","div","li","tr","td","th"): self.parts.append("\n")
    def handle_data(self,data): self.parts.append(data)

def fetch_text():
    req=urllib.request.Request(URL,headers={"User-Agent":"Mozilla/5.0 (compatible; FM1CardDB/1.0)"})
    with urllib.request.urlopen(req,timeout=25) as response:
        raw=response.read().decode("utf-8","replace")
    parser=TextExtractor();parser.feed(raw)
    return html.unescape("".join(parser.parts))

def norm(s): return re.sub(r"\s+","",s or "").strip()

def extract_skill_definitions(page, names):
    """Extract exact skill definitions from inline or split-line headings."""
    ordered=sorted(((key, value) for key,value in names.items()), key=lambda x:(-len(x[0]),x[0]))
    lines=[re.sub(r"\s+"," ",x).strip() for x in page.splitlines()]
    found={}; current=None; body=[]
    def flush():
        if current and body:
            value=" ".join(x for x in body if x).strip()
            if value: found.setdefault(current,[]).append(value)
    def tail_after_label(line, label):
        pos=0; consumed=0
        while pos<len(line) and consumed<len(label):
            if not line[pos].isspace(): consumed+=1
            pos+=1
        return line[pos:]
    for line in lines:
        if not line: continue
        clean=re.sub(r"^[★☆▶※◈●○◆◇■\s]+","",line).strip()
        compact=norm(clean)
        match=None; remainder=""
        for key,name in ordered:
            if not compact.startswith(key): continue
            tail=tail_after_label(clean,key)
            if not tail or tail[0].isspace() or tail[0] in ":：/／-":
                match=(key,name); remainder=re.sub(r"^[\s:：/／-]+","",tail).strip()
                break
        if match:
            flush(); current=match[1]; body=[remainder] if remainder else []
            continue
        if current:
            if line.startswith(("댓글","목록","추천","비추천","신고","로그인","회원가입")):
                flush(); current=None; body=[]; continue
            # A new definition heading closes the previous one, even when that
            # following name is not among the residual skills being searched.
            if re.match(r"^.{1,48}?\s*[:：]\s*.+$",clean):
                flush(); current=None; body=[]; continue
            continuation=re.sub(r"^[\s:：/／]+","",line).strip()
            if continuation: body.append(continuation)
    flush()
    return found

def main(path="data/fm1_cards.sqlite"):
    db=sqlite3.connect(path); db.execute("PRAGMA foreign_keys=ON")
    rows=db.execute("""
      SELECT source_field,source_enum_value,source_name,card_count
      FROM skill_enum_inventory
      WHERE mapping_status='inferred' AND rule_id IN
        (SELECT rule_id FROM game_rule_catalog WHERE confidence='low')
      ORDER BY source_name
    """).fetchall()
    try:
        page=fetch_text()
    except Exception as exc:
        print(json.dumps({"communityFetch":"unavailable","reason":str(exc),"upgradedKinds":0},ensure_ascii=False))
        db.close(); return
    names={norm(r[2]):r[2] for r in rows}
    found=extract_skill_definitions(page,names)
    upgraded=0; total_evidence=0
    with db:
      for field,enumv,name,card_count in rows:
        matches=found.get(name,[])
        if not matches: continue
        counts=Counter(norm(x) for x in matches)
        best_key=counts.most_common(1)[0][0]
        definition=next(x for x in matches if norm(x)==best_key)
        rid="inferred_"+field.lower()+"_"+str(enumv)
        source={"kind":"community_reference","url":URL,"title":"이쯤에서 카드특수능력을 마구찍는 판마를보자(강스압)",
                "publishedDate":"2017-01-30","authority":"community","cardCount":card_count,
                "matchedDefinition":definition,"matchingVariants":len(counts)}
        rule=db.execute("SELECT definition_json,source_references_json FROM game_rule_catalog WHERE rule_id=?",(rid,)).fetchone()
        if not rule: continue
        parsed=json.loads(rule[0])
        parsed["communityDefinition"]=definition
        parsed["communityReferenceUrl"]=URL
        refs=json.loads(rule[1] or "[]"); refs.append(source)
        db.execute("""UPDATE game_rule_catalog SET definition_json=?,source_authority='community',
          confidence='medium',verification_status='community_documented_candidate',
          implementation_status='community_candidate_pending_validation',
          source_references_json=?,catalogue_version=2 WHERE rule_id=?""",
          (json.dumps(parsed,ensure_ascii=False,sort_keys=True),json.dumps(refs,ensure_ascii=False),rid))
        db.execute("""UPDATE card_rule_mappings SET mapping_status='community_documented_candidate',
          confidence='medium',evidence_references_json=? WHERE source_field=? AND source_name=? AND rule_id=?""",
          (json.dumps([source],ensure_ascii=False),field,name,rid))
        db.execute("""UPDATE skill_enum_inventory SET mapping_status='community_documented_candidate',
          rule_id=? WHERE source_field=? AND source_name=? AND rule_id=?""",(rid,field,name,rid))
        upgraded+=1; total_evidence+=len(matches)
    remaining=db.execute("SELECT COUNT(*) FROM skill_enum_inventory WHERE mapping_status='inferred' AND rule_id IN (SELECT rule_id FROM game_rule_catalog WHERE confidence='low')").fetchone()[0]
    unresolved=[]
    low_rows=db.execute("""
      SELECT e.source_field,e.source_enum_value,e.source_name,e.card_count,e.rule_id
      FROM skill_enum_inventory e JOIN game_rule_catalog g USING(rule_id)
      WHERE e.mapping_status='inferred' AND g.confidence='low'
      ORDER BY e.source_name,e.source_field
    """).fetchall()
    for field,enumv,name,card_count,rid in low_rows:
        examples=[]
        card_rows=db.execute("""
          SELECT c.card_id,c.name,c.source_card_url
          FROM card_rule_mappings m JOIN cards c USING(card_id)
          WHERE m.source_field=? AND m.source_enum_value=? AND m.source_name=?
          ORDER BY c.card_id LIMIT 3
        """,(field,str(enumv),name)).fetchall()
        for cid,cname,url in card_rows:
            texts=db.execute("""
              SELECT text_type,COALESCE(NULLIF(plain_text,''),source_text)
              FROM card_texts WHERE card_id=? ORDER BY text_id
            """,(cid,)).fetchall()
            examples.append({"cardId":cid,"cardName":cname,"url":url,
                             "cardTexts":[{"type":typ,"text":(txt or "")[:1200]} for typ,txt in texts]})
        unresolved.append({"sourceField":field,"sourceEnumValue":str(enumv),"skillName":name,
                           "cardCount":card_count,"ruleId":rid,"examples":examples})
    result={"communityFetch":"success","communityMatchedKinds":upgraded,"matchedDefinitionVariants":total_evidence,
            "remainingNameOnlyLowConfidenceKinds":remaining,"unresolvedSkillEvidence":unresolved,
            "unmappedKinds":db.execute("SELECT COUNT(*) FROM skill_enum_inventory WHERE mapping_status='unmapped'").fetchone()[0],
            "foreignKeyErrors":len(db.execute("PRAGMA foreign_key_check").fetchall())}
    print(json.dumps(result,ensure_ascii=False,indent=2));db.close()
if __name__=="__main__": main(sys.argv[1] if len(sys.argv)>1 else "data/fm1_cards.sqlite")
