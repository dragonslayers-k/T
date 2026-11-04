#!/usr/bin/env python3
"""Create explicit inferred semantic records for every extracted effect clause."""
import json,re,sqlite3,sys
from pathlib import Path

def parse(text):
    t=text or ""
    triggers=[]
    for key,pat in [
      ("on_attack",r"공격\s*시|공격할 때|공격 선언"),
      ("on_defense",r"방어\s*시|방어할 때"),
      ("on_self_destroy",r"자신\s*파괴\s*시|자신이 파괴"),
      ("on_enemy_destroy",r"적\s*\d*\s*파괴\s*시|적 유닛 파괴"),
      ("on_summon",r"소환\s*시|배치\s*시"),
      ("turn_start",r"턴 시작|준비 단계 시작"),
      ("turn_end",r"턴 종료|턴 끝"),
      ("on_play",r"발동\s*시|사용\s*시|장착\s*시")]:
        if re.search(pat,t): triggers.append(key)
    actors=[]
    for key,pat in [("self",r"자신|자기"),("friendly",r"아군"),("enemy",r"적군|상대|적 유닛"),("both_sides",r"아군적군|양쪽")]:
        if re.search(pat,t): actors.append(key)
    targets=[]
    for key,pat in [("unit",r"유닛"),("terrain",r"지형|백필드"),("spell",r"마법|인챈트|인첸트"),("item",r"아이템|장비"),("hand",r"핸드"),("deck",r"덱"),("player",r"플레이어|LP")]:
        if re.search(pat,t): targets.append(key)
    ops=[]
    for stat in ("AP","DP","HP","LP"):
        for m in re.finditer(stat+r"\s*([+-])\s*(\d+)",t):
            ops.append({"kind":"modify_stat","stat":stat.lower(),"operator":m.group(1),"value":int(m.group(2))})
        for m in re.finditer(stat+r"\s*=\s*(\d+)",t):
            ops.append({"kind":"set_stat","stat":stat.lower(),"value":int(m.group(1))})
    for key,pat in [
      ("destroy",r"파괴|소각"),("damage",r"데미지|피해"),
      ("heal",r"회복|치료|흡수"),("draw",r"드로우|뽑"),
      ("summon",r"소환|필드에 꺼내"),("move",r"이동|돌려보내|핸드로"),
      ("grant_status",r"상태.{0,12}부여|상태를 부여|부여"),
      ("remove_status",r"상태.{0,12}해제|제거|해제"),
      ("grant_skill",r"기술.{0,12}부여|기술을 부여"),
      ("change_cost",r"소울|유소울|무소울|유지비"),
      ("coin",r"코인"),("copy",r"복사|복제")]:
        if re.search(pat,t): ops.append({"kind":key,"scope":"text_defined"})
    nums=re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t)
    conditions=[]
    for pat in [r"이하",r"이상",r"초과",r"미만",r"같으면",r"경우",r"조건",r"턴이\s*\d+턴"]:
        if re.search(pat,t): conditions.append(pat)
    if not ops:
        if re.match(r"^\s*(?:▶|※|★|☆|illustrated|해당 카드는|카드타입)",t,re.I):
            classification="reference_or_flavor"
        elif not t.strip():
            classification="empty_separator"
        else:
            classification="unparsed_effect_text"
        confidence="low"
        ops=[{"kind":"unparsed_operation","rawText":t}]
    else:
        classification="effect_candidate"
        confidence="medium"
    return {"classification":classification,"triggers":triggers,"actors":actors,"targets":targets,
            "conditions":conditions,"operations":ops,"numbers":nums,"rawText":t,
            "inferenceMethod":"keyword_pattern_v1","confidence":confidence}

def main(path="data/fm1_cards.sqlite"):
    db=sqlite3.connect(path);db.execute("PRAGMA foreign_keys=ON")
    db.executescript("""
    CREATE TABLE IF NOT EXISTS card_effect_interpretations(
      clause_id INTEGER PRIMARY KEY REFERENCES card_effect_clauses(clause_id),
      card_id TEXT NOT NULL REFERENCES cards(card_id),
      source_detail_url TEXT,
      source_text TEXT NOT NULL,
      interpretation_json TEXT NOT NULL,
      verification_status TEXT NOT NULL,
      confidence TEXT NOT NULL,
      inference_method TEXT NOT NULL
    );
    CREATE INDEX IF NOT EXISTS idx_effect_interpretations_card ON card_effect_interpretations(card_id);
    """)
    db.execute("DELETE FROM card_effect_interpretations")
    rows=db.execute("""SELECT cl.clause_id,cl.card_id,cl.segment_text,cl.segment_type,c.source_card_url
      FROM card_effect_clauses cl JOIN cards c ON c.card_id=cl.card_id
      ORDER BY cl.card_id,cl.clause_index""").fetchall()
    counts={}
    with db:
      for clause_id,cid,text,segtype,url in rows:
        parsed=parse(text)
        status="not_applicable" if segtype=="separator" else "inferred"
        db.execute("""INSERT INTO card_effect_interpretations VALUES(?,?,?,?,?,?,?,?)""",
          (clause_id,cid,url,text,json.dumps(parsed,ensure_ascii=False,sort_keys=True),status,
           parsed["confidence"],parsed["inferenceMethod"]))
        counts[status]=counts.get(status,0)+1
    total=db.execute("SELECT COUNT(*) FROM card_effect_interpretations").fetchone()[0]
    missing=db.execute("""SELECT COUNT(*) FROM card_effect_clauses cl LEFT JOIN card_effect_interpretations i USING(clause_id) WHERE i.clause_id IS NULL""").fetchone()[0]
    fk=len(db.execute("PRAGMA foreign_key_check").fetchall())
    result={"sourceClauses":len(rows),"interpretationRows":total,"statusCounts":counts,"missingInterpretations":missing,"foreignKeyErrors":fk}
    print(json.dumps(result,ensure_ascii=False,indent=2));db.close()
    if missing or fk or total!=len(rows):sys.exit(2)
if __name__=="__main__": main(sys.argv[1] if len(sys.argv)>1 else "data/fm1_cards.sqlite")
