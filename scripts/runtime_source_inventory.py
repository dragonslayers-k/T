#!/usr/bin/env python3
"""Read-only DB29 SQLite inventory for the runtime overlay workstream."""
import argparse, collections, hashlib, json, sqlite3
from pathlib import Path

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
        for row in db.execute("SELECT field_key,card_type,COUNT(DISTINCT card_id) n FROM card_fields GROUP BY field_key,card_type"):
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
            'runtimeStatSourceFields':stat_fields,'landSourceFieldPresence':land_fields,'fieldPresenceByType':field_matrix,'tokenCodeStatus':token_code_status,'reviewCohorts':review_cohorts,'reviewQueue':review_queue,'effectsAndSkills':effects}
    finally: db.close()

def main():
    p=argparse.ArgumentParser();p.add_argument('--db',type=Path,required=True);p.add_argument('--output',type=Path,required=True);a=p.parse_args()
    result=inspect_db(a.db);a.output.parent.mkdir(parents=True,exist_ok=True)
    a.output.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print('REVIEW_QUEUE_JSON='+json.dumps(result['reviewQueue'],ensure_ascii=False,separators=(',',':')))
    print(json.dumps({'cards':result['cardCount'],'byType':result['cardsByType'],'costs':result['costs'],'stats':result['runtimeStatSourceFields'],'effects':result['effectsAndSkills'],'landSourceFieldPresence':result['landSourceFieldPresence'],'reviewCohorts':result['reviewCohorts'],'output':str(a.output)},ensure_ascii=False))
if __name__=='__main__': main()
