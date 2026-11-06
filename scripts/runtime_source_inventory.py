#!/usr/bin/env python3
"""Read-only DB29 SQLite inventory for the runtime overlay workstream."""
import argparse, collections, hashlib, json, sqlite3
from pathlib import Path
from soul_costs import parse_require_soul

def inspect_db(path):
    digest=hashlib.sha256(path.read_bytes()).hexdigest()
    db=sqlite3.connect(f"file:{path.resolve()}?mode=ro",uri=True)
    db.row_factory=sqlite3.Row
    try:
        tables={r[0] for r in db.execute("SELECT name FROM sqlite_master WHERE type='table'")}
        required={'cards','card_fields','card_costs'}
        if required-tables: raise ValueError(f"missing tables: {sorted(required-tables)}")
        integrity=db.execute('PRAGMA integrity_check').fetchone()[0]
        cards={r['card_type']:r['n'] for r in db.execute('SELECT card_type,COUNT(*) n FROM cards GROUP BY card_type')}
        costs=db.execute('''SELECT COUNT(*) rows,SUM(lp_known=1) lp,SUM(soul_known=1) soul,
            SUM(semantic_review=1) semantic,SUM(mapping_review=1) mapping FROM card_costs''').fetchone()
        fields={}
        for key in ('RequireLP','RequireSoul','EarnSoul'):
            fields[key]={r['card_type']:r['n'] for r in db.execute('''SELECT c.card_type,COUNT(DISTINCT f.card_id) n
                FROM card_fields f JOIN cards c USING(card_id) WHERE f.field_key=?
                AND f.source_value_json IS NOT NULL AND f.source_value_json NOT IN ('null','""') GROUP BY c.card_type''',(key,))}
        field_matrix={}
        for row in db.execute("SELECT f.field_key,c.card_type,COUNT(DISTINCT f.card_id) n FROM card_fields f JOIN cards c USING(card_id) GROUP BY f.field_key,c.card_type"):
            field_matrix.setdefault(row["field_key"],{})[row["card_type"]]=int(row["n"])
        land_fields={key:value.get("지형",0) for key,value in field_matrix.items() if value.get("지형",0)}
        token_code_status={}
        if 'card_soul_cost_tokens' in tables:
            token_code_status={f"{r[0]}|{r[1]}":r[2] for r in db.execute(
                "SELECT raw_token,parse_status,COUNT(*) FROM card_soul_cost_tokens GROUP BY raw_token,parse_status ORDER BY raw_token,parse_status")}
        review_cohorts=[
            dict(row) for row in db.execute("""
                SELECT c.card_type,c.attribute,cc.semantic_review,cc.mapping_review,COUNT(*) AS cards
                FROM cards c JOIN card_costs cc USING(card_id)
                WHERE cc.semantic_review=1 OR cc.mapping_review=1
                GROUP BY c.card_type,c.attribute,cc.semantic_review,cc.mapping_review
                ORDER BY c.card_type,c.attribute,cc.semantic_review,cc.mapping_review
            """)
        ]
        review_queue=[]
        for row in db.execute("""
            SELECT c.card_id,c.name,c.card_type,c.attribute,c.raw_payload_json,
                   cc.semantic_review,cc.mapping_review,cc.source_text,cc.soul_json
            FROM cards c JOIN card_costs cc USING(card_id)
            WHERE cc.semantic_review=1 OR cc.mapping_review=1
            ORDER BY c.card_type,c.card_id
        """):
            raw=json.loads(row["raw_payload_json"] or "{}")
            soul=json.loads(row["soul_json"] or "{}")
            review_queue.append({
                "cardId":row["card_id"],"name":row["name"],"cardType":row["card_type"],
                "attribute":row["attribute"],"semanticReview":int(row["semantic_review"]),
                "mappingReview":int(row["mapping_review"]),"requireSoul":row["source_text"],
                "colors":soul.get("colors",{}),"tokens":soul.get("tokens",[]),
                "cohortFields":{k:raw.get(k) for k in ("LV","RareType","UnitType","RaceType","SoulType","CompanyType","EtcType","Skill1","Skill2")}
            })
        stat_fields={r['field_key']:r['n'] for r in db.execute('''SELECT field_key,COUNT(DISTINCT card_id) n FROM card_fields
            WHERE field_key LIKE '%ATK%' OR field_key LIKE '%DEF%' OR field_key LIKE '%HP%'
            OR field_key IN ('AP','DP','HP','LV','RankType','UnitType','EarnSoul') GROUP BY field_key''')}
        vectors=collections.Counter()
        for row in db.execute('SELECT soul_json FROM card_costs WHERE soul_known=1'):
            try:
                obj=json.loads(row[0] or '{}').get('colors',{})
                vectors[json.dumps({k:int(v) for k,v in obj.items() if int(v)},sort_keys=True,ensure_ascii=False)]+=1
            except (TypeError,ValueError,json.JSONDecodeError): pass
        reparsed=collections.Counter()
        reparsed_by_type=collections.Counter()
        reparsed_tokens=collections.Counter()
        for row in db.execute("SELECT c.card_type,cc.source_text FROM cards c JOIN card_costs cc USING(card_id)"):
            parsed=parse_require_soul(row["source_text"])
            kind=str(row["card_type"])
            reparsed[(bool(parsed.get("known")),bool(parsed.get("mapping_review")),bool(parsed.get("semantic_review")))]+=1
            reparsed_by_type[(kind,bool(parsed.get("mapping_review")),bool(parsed.get("semantic_review")))]+=1
            for token in parsed.get("tokens",[]):
                reparsed_tokens[(str(token.get("code")),str(token.get("status")),str(token.get("normalized_color")))]+=1
        reparsed_summary={
            "cardStatuses":{str(k):v for k,v in reparsed.items()},
            "byType":[{"cardType":k[0],"mappingReview":k[1],"semanticReview":k[2],"cards":v} for k,v in reparsed_by_type.items()],
            "tokenStatuses":[{"code":k[0],"status":k[1],"normalizedColor":k[2],"tokens":v} for k,v in reparsed_tokens.items()]
        }
        land_production=collections.Counter()
        if "EarnSoulList" in {row["field_key"] for row in db.execute("SELECT DISTINCT field_key FROM card_fields")}:
            for row in db.execute("SELECT source_value_json FROM card_fields f JOIN cards c USING(card_id) WHERE c.card_type='지형' AND f.field_key='EarnSoulList'"):
                land_production[str(row[0])]+=1
        land_pairs=[]
        for row in db.execute("""
            SELECT e.source_value_json AS earn, m.source_value_json AS mu, COUNT(*) AS cards
            FROM cards c
            LEFT JOIN card_fields e ON e.card_id=c.card_id AND e.field_key='EarnSoulList'
            LEFT JOIN card_fields m ON m.card_id=c.card_id AND m.field_key='MuSoul'
            WHERE c.card_type='지형'
            GROUP BY e.source_value_json,m.source_value_json
            ORDER BY cards DESC,e.source_value_json,m.source_value_json
        """):
            try:
                earn=json.loads(row["earn"]) if row["earn"] is not None else None
                mu=json.loads(row["mu"]) if row["mu"] is not None else None
            except (TypeError,ValueError,json.JSONDecodeError):
                earn=row["earn"];mu=row["mu"]
            raw=str(earn or "")
            tokens=[raw[i:i+4] for i in range(0,len(raw),4) if len(raw[i:i+4])==4]
            land_pairs.append({"earnSoulList":earn,"muSoul":mu,"cards":int(row["cards"]),
                "tokenCodes":[t[:2] for t in tokens],"tokenAmounts":[t[2:] for t in tokens],"tokenCount":len(tokens)})
        land_examples=[]
        for row in db.execute("""
            SELECT c.card_id,c.name,
                   (SELECT source_value_json FROM card_fields f WHERE f.card_id=c.card_id AND f.field_key='EarnSoulList') AS earn_soul,
                   (SELECT source_value_json FROM card_fields f WHERE f.card_id=c.card_id AND f.field_key='MuSoul') AS mu_soul
            FROM cards c WHERE c.card_type='지형' ORDER BY c.card_id LIMIT 12
        """):
            land_examples.append(dict(row))
        stat_by_type={key:field_matrix.get(key,{}) for key in ("ATK","DEF","HP","ATKStatType","DEFStatType","HPStatType","ATKCoinCount","DEFCoinCount","HPCoinCount","MuSoul")}
        token_status={}
        if 'card_soul_cost_tokens' in tables:
            token_status={r[0]:r[1] for r in db.execute('SELECT parse_status,COUNT(*) FROM card_soul_cost_tokens GROUP BY parse_status')}
        effects={}
        for table in ('card_effects','card_effect_candidate_summaries','card_effect_clauses','card_effect_interpretations','game_rule_catalog','card_rule_mappings'):
            if table in tables: effects[table]=db.execute(f'SELECT COUNT(*) FROM "{table}"').fetchone()[0]
        if 'card_effect_interpretations' in tables:
            effects['interpretationConfidence']={r[0]:r[1] for r in db.execute('SELECT confidence,COUNT(*) FROM card_effect_interpretations GROUP BY confidence')}
        return {'schemaVersion':1,'sourceReleaseTag':'fm1-carddb-29','databaseSha256':digest,'integrityCheck':integrity,
            'cardCount':db.execute('SELECT COUNT(*) FROM cards').fetchone()[0],'cardsByType':cards,
            'costs':{'rows':costs['rows'],'lpKnownRows':costs['lp'],'soulKnownRows':costs['soul'],
                'semanticReviewRows':costs['semantic'],'mappingReviewRows':costs['mapping'],'sourceFieldPresenceByType':fields,
                'soulTokenStatus':token_status,'topSoulVectors':[{'vector':json.loads(k),'cards':v} for k,v in vectors.most_common(30)]},
            'runtimeStatSourceFields':stat_fields,'landSourceFieldPresence':land_fields,'landEarnSoulListValues':dict(land_production),'landProductionPairs':land_pairs,'landExamples':land_examples,'statFieldPresenceByType':stat_by_type,'fieldPresenceByType':field_matrix,'tokenCodeStatus':token_code_status,'reviewCohorts':review_cohorts,'reviewQueue':review_queue,'currentDecoderReparse':reparsed_summary,'effectsAndSkills':effects}
    finally: db.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--db',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=inspect_db(a.db);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('REVIEW_QUEUE_JSON='+json.dumps(result['reviewQueue'],ensure_ascii=False,separators=(',',':')))
    print(json.dumps({'cards':result['cardCount'],'byType':result['cardsByType'],'costs':result['costs'],'stats':result['runtimeStatSourceFields'],'effects':result['effectsAndSkills'],'landSourceFieldPresence':result['landSourceFieldPresence'],'landEarnSoulListValues':result['landEarnSoulListValues'],'landProductionPairs':result['landProductionPairs'],'landExamples':result['landExamples'],'statFieldPresenceByType':result['statFieldPresenceByType'],'currentDecoderReparse':result['currentDecoderReparse'],'reviewCohorts':result['reviewCohorts'],'output':str(a.output)},ensure_ascii=False))
if __name__=='__main__': main()

# Inventory extension pending: field_matrix must join cards for card_type.
