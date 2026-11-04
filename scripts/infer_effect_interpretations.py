#!/usr/bin/env python3
"""Build provenance-preserving semantic candidates for every FM1 card-text clause."""
import json,re,sqlite3,sys

def _uniq(values):
    out=[]
    for x in values:
        if x not in out: out.append(x)
    return out

def parse(text, known_skills=None):
    t=(text or "").strip()
    compact="".join(t.split())
    if not t:
        return {"classification":"empty_separator","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[],"numbers":[],"rawText":text or "",
                "inferenceMethod":"empty_text_v1","confidence":"not_applicable"}

    # Source notes, credits, collection restrictions and headings are not game effects.
    metadata_patterns=[
      r"^invalid$",
      r"^◈?\s*illustrated by\b",
      r"^\d+차\s*강화\s*유닛\s*특징$",
      r"^상성(?:효과|카드|유닛|아이템)\s*:?\s*$",
      r"^(?:성장목록|성장유닛|오오라 능력|변경되는 유닛 리스트)$",
      r"^해당\s*(?:유닛|아이템|마법|카드).*(?:가지고 있습니다|확인하실 수|확인할 수|FAQ를 참조|획득 가능합니다|획득할 수 있습니다)",
      r"^(?:랭크가 있는 카드입니다|랭크 카드 안내|랭크카드 각각에 대한 설명은)",
      r"^(?:FM 도움말|고객센터|홈페이지 메인화면|이벤트 페이지를 확인)",
      r"^20\d\d년.*(?:이벤트|부스터).*(?:획득|제공)",
      r"^상성(?:유닛|아이템)\s*[:：]",
      r"^◈\s*",
    ]
    if any(re.search(p,t,re.I) for p in metadata_patterns):
        return {"classification":"reference_or_metadata","triggers":[],"actors":[],
                "targets":[],"conditions":[],"operations":[{"kind":"source_metadata","rawText":t}],
                "numbers":re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t),
                "rawText":t,"inferenceMethod":"source_metadata_patterns_v2","confidence":"not_applicable"}

    # Exact skill names are linked to the rule catalogue; they are not re-parsed as prose.
    if known_skills and compact in known_skills:
        return {"classification":"ability_name_reference","triggers":[],"actors":[],"targets":[],
                "conditions":[],"operations":[{"kind":"skill_reference","ruleId":known_skills[compact]}],
                "numbers":[],"rawText":t,"inferenceMethod":"catalogue_name_link_v2","confidence":"medium"}

    triggers=[]
    for key,pat in [
      ("on_attack",r"공격\s*시|공격할 때|공격 선언"),
      ("on_defense",r"방어\s*시|방어할 때|방어 선언"),
      ("on_self_destroy",r"자신\s*파괴\s*시|자신이 파괴|자신 파괴"),
      ("on_enemy_destroy",r"적\s*\d*\s*파괴\s*시|적 유닛 파괴"),
      ("on_summon",r"소환\s*시|배치\s*시|필드로 소환"),
      ("on_status_expire",r"상태\s*해제\s*시|상태해제시|상태\s*발동\s*시"),
      ("on_soul_cost",r"소울\s*코스트\s*시|유지비\s*지불\s*시"),
      ("turn_start",r"턴 시작|준비 단계 시작"),
      ("turn_end",r"턴 종료|턴 끝"),
      ("each_turn",r"매\s*턴|턴마다"),
      ("on_play",r"발동\s*시|사용\s*시|장착\s*시")]:
        if re.search(pat,t): triggers.append(key)
    actors=[]
    for key,pat in [("self",r"자신|자기"),("friendly",r"아군"),("enemy",r"적군|상대|적 "),("both_sides",r"아군.{0,8}적군|양쪽")]:
        if re.search(pat,t): actors.append(key)
    targets=[]
    for key,pat in [
      ("unit",r"유닛"),("terrain",r"지형|백필드"),("spell",r"마법|인챈트|인첸트"),
      ("item",r"아이템|장비"),("hand",r"핸드"),("deck",r"덱|소각장"),
      ("player",r"플레이어|LP"),("field",r"필드")]:
        if re.search(pat,t): targets.append(key)

    ops=[]
    # Numeric stat deltas and assignments, including Korean names and grouped stats.
    stat_patterns={
      "ap":r"AP|공격력|공격치|공격\s*수치",
      "dp":r"DP|방어력|방어치|방어\s*수치",
      "hp":r"HP|체력|체력치",
      "lp":r"LP|랜드\s*포인트"
    }
    for stat,pat in stat_patterns.items():
        for m in re.finditer(r"("+pat+r")\s*([+-])\s*(\d+)",t):
            ops.append({"kind":"modify_stat","stat":stat,"operator":m.group(2),"value":int(m.group(3))})
        for m in re.finditer(r"("+pat+r")\s*=\s*([★▲▼]?\s*\d+)",t):
            ops.append({"kind":"set_stat","stat":stat,"value":m.group(2).replace(" ","")})
    if re.search(r"공방체|공체|공방|공격력|방어력|체력",t) and re.search(r"증가|감소|변경|상승|하락|올리|내리|영구",t):
        ops.append({"kind":"modify_combat_stats","statGroup":re.findall(r"공방체|공체|공방|공격력|방어력|체력",t),
                    "direction":"text_defined","rawText":t})
    # Coin formulas: preserve exact source formula rather than approximating arithmetic.
    coin_tokens=re.findall(r"(?:[+-]?\s*\d*C\d+|[+-]?\s*C\d+|AC[+-]?\d+|HC[+-]?\d+|[+-]\d+%)",t)
    if coin_tokens or re.search(r"코인|동전|코인수|코인 수|코인확률|코인 확률",t):
        ops.append({"kind":"modify_coin","formulas":coin_tokens,"rawText":t})
    if re.search(r"기호|★|▲|▼",t) and re.search(r"변경|삭제|부여|제거|하향|상향|유지",t):
        ops.append({"kind":"modify_stat_marks","rawText":t})
    if re.search(r"상태",t) and re.search(r"부여|추가|제거|해제|변경|전환|유지|증가|감소",t):
        ops.append({"kind":"modify_status","rawText":t})
    if re.search(r"특수\s*공격\s*기술|공격\s*기술|방어\s*기술|특수기술|기술",t) and re.search(r"부여|추가|변경|삭제|제거|일반공격|일반방어|봉쇄",t):
        ops.append({"kind":"modify_skill","rawText":t})
    if re.search(r"소환|소환한|소환시|소환할|배치",t):
        ops.append({"kind":"summon_or_deploy","rawText":t})
    if re.search(r"파괴|소멸|함께 파괴|소각",t):
        ops.append({"kind":"destroy_or_exile","rawText":t})
    if re.search(r"데미지|피해",t):
        ops.append({"kind":"deal_damage","rawText":t})
    if re.search(r"회복|치료|흡수",t):
        ops.append({"kind":"heal_or_recover","rawText":t})
    if re.search(r"드로우|뽑|덱.{0,8}(?:파괴|소각)|핸드로 이동",t):
        ops.append({"kind":"draw_or_mill","rawText":t})
    if re.search(r"이동|교체|변신|변경.{0,8}카드|다음 단계|성장|진화|폴리모프",t):
        ops.append({"kind":"transform_or_move_card","rawText":t})
    if re.search(r"레벨.{0,12}(?:감소|증가|변경)|소울.{0,12}(?:감소|증가|변경)|코스트.{0,12}(?:감소|증가|변경)",t):
        ops.append({"kind":"modify_card_cost_or_level","rawText":t})
    if re.search(r"종족|소속",t) and re.search(r"없음|삭제|변경|부여",t):
        ops.append({"kind":"modify_race_or_faction","rawText":t})
    if re.search(r"장착|해제|아이템을 장착",t):
        ops.append({"kind":"equip_or_unequip","rawText":t})
    if re.search(r"오오라|오라|아레아",t):
        ops.append({"kind":"aura_or_area_effect","rawText":t})
    # Card-to-card conditions and ranges are kept separately from effect operations.
    conditions=[]
    for pat in [
      r"\d+\s*(?:~|-|∼)\s*\d+\s*(?:레벨|턴|킬|장|개)",
      r"\d+\s*레벨\s*(?:이상|이하|초과|미만)",
      r"\d+\s*턴\s*(?:이상|이하|초과|미만|동안)",
      r"이하",r"이상",r"초과",r"미만",r"같으면",r"경우",r"조건",
      r"홀수|짝수",r"같은\s*(?:종족|소속|이름|속성)",r"차이만큼",
      r"최고|최저|절반|올림|내림",r"행동가능한",r"다음\s*위치"
    ]:
        if re.search(pat,t): conditions.append(pat)
    nums=re.findall(r"(?<!\d)[+-]?\d+(?:\.\d+)?%?",t)
    ops=_uniq([json.dumps(x,ensure_ascii=False,sort_keys=True) for x in ops])
    ops=[json.loads(x) for x in ops]

    if not ops:
        if re.match(r"^\s*(?:invalid$|▶|※|★|☆|illustrated|해당 카드는|카드타입)",t,re.I):
            classification="reference_or_flavor"; confidence="not_applicable"
            ops=[{"kind":"source_note","rawText":t}]
        elif re.match(r"^\s*(?:상성유닛|상성아이템|상성카드)\s*[:：]",t):
            classification="card_reference_list"; confidence="not_applicable"
            ops=[{"kind":"related_card_reference","rawText":t}]
        elif re.match(r"^\s*\[[^\]]{2,}\]\s*$",t):
            classification="flavor_or_lore"; confidence="not_applicable"
            ops=[{"kind":"flavor_text","rawText":t}]
        elif re.match(r"^\s*(?:성장목록|성장유닛|변경되는 유닛 리스트|상성효과|오오라 능력)\s*$",t):
            classification="section_heading"; confidence="not_applicable"
            ops=[{"kind":"section_heading","rawText":t}]
        elif re.search(r"[:：].{1,}",t) or re.search(r"(?:레벨|턴|킬|핸드카드|유닛수|필드 카드수).*(?:이상|이하|:)",t):
            classification="conditional_or_reference_candidate"; confidence="low"
            ops=[{"kind":"conditional_rule_candidate","rawText":t}]
        else:
            classification="unparsed_effect_text"; confidence="low"
            ops=[{"kind":"unparsed_operation","rawText":t}]
    else:
        classification="effect_candidate"; confidence="medium"
    return {"classification":classification,"triggers":triggers,"actors":actors,
            "targets":targets,"conditions":conditions,"operations":ops,
            "numbers":nums,"rawText":t,"inferenceMethod":"keyword_pattern_v3",
            "confidence":confidence}

def main(path="data/fm1_cards.sqlite"):
    db=sqlite3.connect(path); db.execute("PRAGMA foreign_keys=ON")
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
    known_skills={}
    for rid,canonical,aliases_json in db.execute("SELECT rule_id,canonical_name,aliases_json FROM game_rule_catalog"):
        for label in [canonical]+(json.loads(aliases_json or "[]")):
            known_skills["".join(str(label).split())]=rid
    for field,name,rid in db.execute("SELECT source_field,source_name,rule_id FROM skill_enum_inventory WHERE rule_id IS NOT NULL"):
        known_skills["".join(str(name).split())]=rid
    rows=db.execute("""SELECT cl.clause_id,cl.card_id,cl.segment_text,cl.segment_type,c.source_card_url
      FROM card_effect_clauses cl JOIN cards c ON c.card_id=cl.card_id
      ORDER BY cl.card_id,cl.clause_index""").fetchall()
    counts={}
    with db:
      for clause_id,cid,text,segtype,url in rows:
        parsed=parse(text,known_skills)
        status=("not_applicable" if segtype=="separator" or parsed["classification"] in
                ("reference_or_flavor","card_reference_list","section_heading","flavor_or_lore")
                else "linked_rule_reference" if parsed["classification"]=="ability_name_reference" else "inferred")
        db.execute("""INSERT INTO card_effect_interpretations VALUES(?,?,?,?,?,?,?,?)""",
          (clause_id,cid,url,text,json.dumps(parsed,ensure_ascii=False,sort_keys=True),status,
           parsed["confidence"],parsed["inferenceMethod"]))
        counts[status]=counts.get(status,0)+1
    total=db.execute("SELECT COUNT(*) FROM card_effect_interpretations").fetchone()[0]
    missing=db.execute("""SELECT COUNT(*) FROM card_effect_clauses cl LEFT JOIN card_effect_interpretations i USING(clause_id) WHERE i.clause_id IS NULL""").fetchone()[0]
    fk=len(db.execute("PRAGMA foreign_key_check").fetchall())
    low=db.execute("SELECT COUNT(*) FROM card_effect_interpretations WHERE confidence='low'").fetchone()[0]
    low_by_class=db.execute("""
      SELECT COALESCE(json_extract(interpretation_json,'$.classification'),'unknown') AS classification,
             COUNT(*) AS n,COUNT(DISTINCT source_text) AS distinct_texts
      FROM card_effect_interpretations
      WHERE confidence='low'
      GROUP BY classification ORDER BY n DESC
    """).fetchall()
    low_examples=db.execute("""
      SELECT i.source_text,COUNT(*) AS card_count,MIN(i.card_id) AS example_card_id,
             MIN(i.source_detail_url) AS example_url,
             json_extract(MIN(i.interpretation_json),'$.classification') AS classification
      FROM card_effect_interpretations i
      WHERE i.confidence='low' AND length(trim(i.source_text))>0
      GROUP BY i.source_text ORDER BY card_count DESC,i.source_text LIMIT 120
    """).fetchall()
    result={"sourceClauses":len(rows),"interpretationRows":total,"statusCounts":counts,
            "lowConfidenceRows":low,"missingInterpretations":missing,"foreignKeyErrors":fk,
            "lowConfidenceByClassification":[dict(x) for x in low_by_class],
            "lowConfidenceDistinctTexts":db.execute(
              "SELECT COUNT(DISTINCT source_text) FROM card_effect_interpretations WHERE confidence='low'"
            ).fetchone()[0],
            "lowConfidenceSamples":[{"text":x[0],"cardCount":x[1],"cardId":x[2],
                                     "url":x[3],"classification":x[4]} for x in low_examples]}
    print(json.dumps(result,ensure_ascii=False,indent=2)); db.close()
    if missing or fk or total!=len(rows): sys.exit(2)

if __name__=="__main__": main(sys.argv[1] if len(sys.argv)>1 else "data/fm1_cards.sqlite")
