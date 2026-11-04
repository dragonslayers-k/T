#!/usr/bin/env python3
"""Create card-by-card gap queues without changing immutable source values."""
import argparse, csv, json, sqlite3
from pathlib import Path

def build(db_path: Path, out_dir: Path):
    db=sqlite3.connect(db_path)
    db.row_factory=sqlite3.Row
    out_dir.mkdir(parents=True,exist_ok=True)
    cards=db.execute("SELECT card_id,name,card_type FROM cards ORDER BY card_id").fetchall()
    fields=[r[0] for r in db.execute("SELECT DISTINCT field_key FROM card_fields ORDER BY field_key")]
    present={(r["card_id"],r["field_key"]):r for r in db.execute(
        "SELECT card_id,field_key,source_value_json,normalized_value,verification_status FROM card_fields"
    )}
    applicable=set()
    for r in db.execute("""
      SELECT DISTINCT c.card_type,cf.field_key
      FROM card_fields cf JOIN cards c USING(card_id)
      WHERE cf.source_value_json IS NOT NULL AND trim(cf.source_value_json)<>'""'
    """):
        applicable.add((r[0],r[1]))
    field_rows=[]
    for card in cards:
        for field in fields:
            row=present.get((card["card_id"],field))
            if row is None:
                status="missing_on_card" if (card["card_type"],field) in applicable else "not_applicable"
                raw=None; normalized=None; verification="not_recorded"
            else:
                raw=row["source_value_json"]; normalized=row["normalized_value"]; verification=row["verification_status"]
                try: value=json.loads(raw) if raw is not None else None
                except Exception: value=raw
                status=("not_applicable" if (card["card_type"],field) not in applicable
                        else "empty_source_value" if value is None or value=="" else "present_unverified")
            field_rows.append({
                "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
                "field_key":field,"status":status,"source_value_json":raw,
                "normalized_value":normalized,"verification_status":verification
            })
    with (out_dir/"card-field-gap-report.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(field_rows[0]) if field_rows else ["card_id","field_key","status"])
        w.writeheader();w.writerows(field_rows)
    with (out_dir/"card-field-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for row in field_rows:f.write(json.dumps(row,ensure_ascii=False)+"\n")

    costs=[]
    for r in db.execute("""
      SELECT c.card_id,c.name,c.card_type,cc.source_text,cc.soul_json,cc.lp_value,cc.lp_known,
             cc.soul_known,cc.mapping_review,cc.semantic_review,cc.verification_status
      FROM cards c JOIN card_costs cc USING(card_id) ORDER BY c.card_id
    """):
        costs.append(dict(r))
    cost_review=[]
    for r in costs:
        if not r["soul_known"] or r["mapping_review"] or r["semantic_review"] or (r["card_type"]=="지형" and not r["lp_known"]):
            r["tokenEvidence"]=[dict(x) for x in db.execute(
                "SELECT ordinal,raw_token,code,count,symbol,normalized_color,parse_status FROM card_soul_cost_tokens WHERE card_id=? ORDER BY ordinal",
                (r["card_id"],))]
            r["interpretationStatus"]="inferred_hybrid_both_colors" if r["mapping_review"] else "inferred_flexible_neutral" if r["semantic_review"] else "unresolved"
            cost_review.append(r)
    with (out_dir/"cost-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    with (out_dir/"cost-inference-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")

    skill_inventory=[]
    for r in db.execute("""
      SELECT source_field,source_enum_value,source_name,COUNT(*) AS card_count,
             MIN(card_id) AS example_card_id
      FROM card_rule_mappings WHERE mapping_status='unmapped'
      GROUP BY source_field,source_enum_value,source_name
      ORDER BY source_field,source_name
    """):
        skill_inventory.append(dict(r))
    with (out_dir/"unmapped-skill-inventory.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=["source_field","source_enum_value","source_name","card_count","example_card_id"])
        w.writeheader();w.writerows(skill_inventory)

    skills=[]
    for r in db.execute("""
      SELECT m.card_id,c.name,c.card_type,m.source_field,m.source_enum_value,m.source_name,
             m.mapping_status,m.rule_id,m.confidence,m.evidence_references_json
      FROM card_rule_mappings m JOIN cards c USING(card_id)
      WHERE m.mapping_status IN ('unmapped','inferred','community_documented_candidate')
      ORDER BY m.source_field,m.source_name,m.card_id
    """):
        skills.append(dict(r))
    with (out_dir/"skill-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for r in skills:f.write(json.dumps(r,ensure_ascii=False)+"\n")

    inferred_skills=[r for r in skills if r["mapping_status"]=="inferred"]
    with (out_dir/"inferred-skill-report.jsonl").open("w",encoding="utf-8") as f:
        for r in inferred_skills:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")

    community_skills=[r for r in skills if r["mapping_status"]=="community_documented_candidate"]
    with (out_dir/"community-skill-report.jsonl").open("w",encoding="utf-8") as f:
        for r in community_skills:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")

    effects=[]
    for r in db.execute("""
      SELECT i.card_id,c.name,c.card_type,cl.clause_index,cl.segment_text,
             i.interpretation_json,i.verification_status,i.confidence,i.source_detail_url
      FROM card_effect_interpretations i
      JOIN card_effect_clauses cl USING(clause_id)
      JOIN cards c USING(card_id)
      ORDER BY i.card_id,cl.clause_index
    """):
        effects.append(dict(r))
    with (out_dir/"effect-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for r in effects:
            if r["confidence"]=="low":
                f.write(json.dumps(r,ensure_ascii=False)+"\n")

    summary={
      "cards":len(cards),"source_field_keys":len(fields),"card_field_matrix_rows":len(field_rows),
      "field_status_counts":{},
      "cost_review_provenance_rows":len(cost_review),
      "unresolved_cost_rows":sum(1 for r in costs if not r["soul_known"] or (r["card_type"]=="지형" and not r["lp_known"])),
      "unmapped_skill_card_rows":sum(1 for r in skills if r["mapping_status"]=="unmapped"),
      "inferred_skill_card_rows":len(inferred_skills),
      "community_skill_card_rows":len(community_skills),
      "unmapped_skill_unique_values":len(skill_inventory),
      "low_confidence_effect_interpretations":sum(1 for r in effects if r["confidence"]=="low"),
      "outputs":["card-field-gap-report.csv","card-field-gap-report.jsonl","cost-gap-report.jsonl","skill-gap-report.jsonl","inferred-skill-report.jsonl","community-skill-report.jsonl","unmapped-skill-inventory.csv","effect-gap-report.jsonl","cost-inference-report.jsonl"]
    }
    for r in field_rows:summary["field_status_counts"][r["status"]]=summary["field_status_counts"].get(r["status"],0)+1
    (out_dir/"gap-report-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    db.close()
    return summary

def main():
    p=argparse.ArgumentParser()
    p.add_argument("--db",type=Path,default=Path("data/fm1_cards.sqlite"))
    p.add_argument("--out-dir",type=Path,default=Path("data/gap-reports"))
    a=p.parse_args()
    result=build(a.db,a.out_dir)
    print(json.dumps(result,ensure_ascii=False,indent=2))

if __name__=="__main__":main()
