#!/usr/bin/env python3
"""Create card-by-card gap queues without changing immutable source values."""
import argparse, csv, hashlib, json, sqlite3
from pathlib import Path

def build(db_path: Path, out_dir: Path):
    db=sqlite3.connect(db_path)
    db.row_factory=sqlite3.Row
    out_dir.mkdir(parents=True,exist_ok=True)
    cards=db.execute("SELECT card_id,name,card_type,raw_payload_json FROM cards ORDER BY card_id").fetchall()
    fields=[r[0] for r in db.execute("SELECT DISTINCT field_key FROM card_fields ORDER BY field_key")]
    present={(r["card_id"],r["field_key"]):r for r in db.execute(
        "SELECT field_id,card_id,field_key,source_value_json,normalized_value,verification_status FROM card_fields"
    )}
    # Category-level applicability is only a candidate: a field absent from every
    # peer card of the same type may be inapplicable, but this is not source proof.
    observed_type_fields={(r[0],r[1]) for r in db.execute(
        """SELECT DISTINCT json_extract(c.raw_payload_json,'$.Category'),cf.field_key
           FROM card_fields cf JOIN cards c USING(card_id)
           WHERE cf.source_value_json IS NOT NULL
             AND json_type(cf.source_value_json,'
    db.executescript("""
      CREATE TABLE IF NOT EXISTS card_field_coverage(
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        field_key TEXT NOT NULL,
        coverage_status TEXT NOT NULL,
        field_id INTEGER REFERENCES card_fields(field_id),
        source_payload_match INTEGER NOT NULL,
        source_value_sha256 TEXT,
        PRIMARY KEY(card_id,field_key)
      );
      CREATE INDEX IF NOT EXISTS idx_card_field_coverage_status
        ON card_field_coverage(coverage_status,field_key);
    """)
    db.execute("DELETE FROM card_field_coverage")
    field_rows=[]
    coverage_inserts=[]
    card_field_summaries=[]
    per_field_status_counts={field:{} for field in fields}
    per_field_examples={field:{} for field in fields}
    for card in cards:
        payload=json.loads(card["raw_payload_json"])
        source_category=payload.get("Category")
        verified_fields=[]
        absent_fields=[]
        empty_fields=[]
        null_fields=[]
        not_applicable_candidates=[]
        missing_fields=[]
        for field in fields:
            row=present.get((card["card_id"],field))
            if row is None:
                # The source snapshot is authoritative. An absent key is a confirmed
                # source absence; a key present in the raw payload but absent here is
                # a genuine ingestion/normalization gap.
                source_has_key=field in payload
                if source_has_key and payload[field] is None:
                    status="source_null_confirmed"
                elif source_has_key:
                    status="missing_on_card"
                elif (source_category,field) not in observed_type_fields:
                    status="not_applicable_candidate"
                    not_applicable_candidates.append(field)
                else:
                    status="source_absent_confirmed"
                raw=None; normalized=None; verification="not_recorded"; field_id=None
                payload_match=1 if (not source_has_key or payload[field] is None) else 0
                value_hash=None
            else:
                raw=row["source_value_json"]; normalized=row["normalized_value"]
                verification=row["verification_status"]; field_id=row["field_id"]
                try: value=json.loads(raw) if raw is not None else None
                except Exception as exc: raise ValueError(f"Invalid JSON source value: {card['card_id']} {field}: {exc}")
                payload_match=int(field in payload and value==payload.get(field))
                if not payload_match:
                    raise ValueError(f"Normalized field differs from immutable raw payload: {card['card_id']} {field}")
                value_hash=hashlib.sha256((raw or "null").encode("utf-8")).hexdigest()
                status=("source_null_confirmed" if value is None else
                        "source_empty_confirmed" if value=="" else "source_snapshot_verified")
            coverage_inserts.append((card["card_id"],field,status,field_id,payload_match,value_hash))
            per_field_status_counts[field][status]=per_field_status_counts[field].get(status,0)+1
            if len(per_field_examples[field].get(status,[]))<5:
                per_field_examples[field].setdefault(status,[]).append(card["card_id"])
            if status=="source_snapshot_verified": verified_fields.append(field)
            elif status=="source_absent_confirmed": absent_fields.append(field)
            elif status=="source_empty_confirmed": empty_fields.append(field)
            elif status=="source_null_confirmed": null_fields.append(field)
            elif status=="not_applicable_candidate": pass
            elif status=="missing_on_card": missing_fields.append(field)
            field_rows.append({
                "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
                "field_key":field,"status":status,"source_value_json":raw,
                "normalized_value":normalized,"verification_status":verification,
                "source_payload_match":payload_match
            })
        card_field_summaries.append({
            "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
            "source_category":source_category,
            "source_snapshot_verified_fields":verified_fields,
            "source_absent_confirmed_fields":absent_fields,
            "source_empty_confirmed_fields":empty_fields,
            "source_null_confirmed_fields":null_fields,
            "not_applicable_candidate_fields":not_applicable_candidates,
            "missing_on_card_fields":missing_fields
        })
    db.executemany("INSERT INTO card_field_coverage VALUES(?,?,?,?,?,?)",coverage_inserts)
    if len(coverage_inserts)!=len(cards)*len(fields):
        raise ValueError("Card-field coverage matrix is incomplete")
    if any(x[4]!=1 for x in coverage_inserts):
        raise ValueError("At least one normalized source field does not match its raw card payload")
    with (out_dir/"card-field-gap-report.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(field_rows[0]) if field_rows else ["card_id","field_key","status"])
        w.writeheader();w.writerows(field_rows)
    with (out_dir/"card-field-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for row in field_rows:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    with (out_dir/"card-field-card-summary.jsonl").open("w",encoding="utf-8") as f:
        for row in card_field_summaries:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    field_status_summary={
        "cards":len(cards),"fields":len(fields),
        "field_status_counts":per_field_status_counts,
        "example_card_ids_by_status":per_field_examples
    }
    (out_dir/"card-field-status-summary.json").write_text(
        json.dumps(field_status_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    costs=[]
    for r in db.execute("""
      SELECT c.card_id,c.name,c.card_type,c.source_card_url,cc.source_text,cc.soul_json,cc.lp_value,cc.lp_known,
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
            r["reviewReason"]=[]
            if r["mapping_review"]: r["reviewReason"].append("hybrid_color_payment_rule_unverified")
            if r["semantic_review"]: r["reviewReason"].append("special_soul_payment_rule_unverified")
            r["interpretationStatus"]="hybrid_identity_preserved_pending_rule" if r["mapping_review"] else "special_identity_preserved_pending_rule" if r["semantic_review"] else "unresolved"
            cost_review.append(r)
    with (out_dir/"cost-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    with (out_dir/"cost-inference-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")

    # Compact inventory of every decoded RequireSoul token identity, including
    # candidate semantics and original card URLs for manual verification.
    cost_code_inventory=[]
    grouped=db.execute("""
      SELECT code,symbol,normalized_color,parse_status,
             COUNT(*) AS token_rows,SUM(count) AS total_amount,
             COUNT(DISTINCT card_id) AS card_rows
      FROM card_soul_cost_tokens
      GROUP BY code,symbol,normalized_color,parse_status
      ORDER BY code,parse_status,normalized_color
    """).fetchall()
    for g in grouped:
        examples=[dict(x) for x in db.execute("""
          SELECT t.card_id,c.name,c.source_card_url,t.raw_token,t.count
          FROM card_soul_cost_tokens t JOIN cards c USING(card_id)
          WHERE t.code IS ? AND COALESCE(t.symbol,'')=COALESCE(?,'')
            AND COALESCE(t.normalized_color,'')=COALESCE(?,'')
            AND t.parse_status=?
          ORDER BY t.card_id LIMIT 5
        """,(g["code"],g["symbol"],g["normalized_color"],g["parse_status"]))]
        cost_code_inventory.append({
            "code":g["code"],"symbol":g["symbol"],
            "normalizedColorCandidate":g["normalized_color"],
            "parseStatus":g["parse_status"],"tokenRows":g["token_rows"],
            "totalAmount":g["total_amount"],"cardRows":g["card_rows"],
            "examples":examples
        })
    (out_dir/"cost-code-inventory.json").write_text(
        json.dumps(cost_code_inventory,ensure_ascii=False,indent=2),encoding="utf-8")

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

    # A compact diagnostic index makes the remaining low-confidence queue
    # actionable without downloading and opening the multi-hundred-MB DB artifact.
    low_effects=[r for r in effects if r["confidence"]=="low"]
    effect_groups={}
    effect_classes={}
    for r in low_effects:
        try:
            parsed=json.loads(r["interpretation_json"] or "{}")
        except Exception:
            parsed={}
        classification=parsed.get("classification","unknown")
        effect_classes[classification]=effect_classes.get(classification,0)+1
        key=" ".join((r["segment_text"] or "").split())
        if not key: key="(empty)"
        group=effect_groups.setdefault(key,{"text":key,"count":0,"classification":classification,
                                           "examples":[]})
        group["count"]+=1
        if len(group["examples"])<3:
            group["examples"].append({"card_id":r["card_id"],"name":r["name"],
                                      "url":r["source_detail_url"]})
    ranked_effect_groups=sorted(effect_groups.values(),key=lambda x:(-x["count"],x["text"]))
    effect_low_summary={
      "low_confidence_rows":len(low_effects),
      "unique_text_patterns":len(effect_groups),
      "classification_counts":dict(sorted(effect_classes.items())),
      "top_repeated_patterns":ranked_effect_groups[:100],
      "rare_pattern_samples":ranked_effect_groups[-100:]
    }
    (out_dir/"effect-low-confidence-summary.json").write_text(
      json.dumps(effect_low_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    summary={
      "cards":len(cards),"source_field_keys":len(fields),"card_field_matrix_rows":len(field_rows),
      "field_status_counts":{},
      "field_status_counts_by_field":per_field_status_counts,
      "source_payload_mismatches":sum(1 for x in coverage_inserts if x[4]!=1),
      "sqlite_field_coverage_rows":len(coverage_inserts),
      "cost_review_provenance_rows":len(cost_review),
      "unresolved_cost_rows":sum(1 for r in costs if not r["soul_known"] or (r["card_type"]=="지형" and not r["lp_known"])),
      "unmapped_skill_card_rows":sum(1 for r in skills if r["mapping_status"]=="unmapped"),
      "inferred_skill_card_rows":len(inferred_skills),
      "community_skill_card_rows":len(community_skills),
      "unmapped_skill_unique_values":len(skill_inventory),
      "low_confidence_effect_interpretations":sum(1 for r in effects if r["confidence"]=="low"),
      "effect_low_confidence_unique_patterns":len(effect_groups),
      "effect_low_confidence_classification_counts":effect_classes,
      "outputs":["card-field-gap-report.csv","card-field-gap-report.jsonl","cost-gap-report.jsonl","skill-gap-report.jsonl","inferred-skill-report.jsonl","community-skill-report.jsonl","unmapped-skill-inventory.csv","effect-gap-report.jsonl","effect-low-confidence-summary.json","cost-inference-report.jsonl","cost-code-inventory.json"]
    }
    for r in field_rows:summary["field_status_counts"][r["status"]]=summary["field_status_counts"].get(r["status"],0)+1
    (out_dir/"gap-report-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    db.commit()
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
)!='null'
             AND NOT (json_type(cf.source_value_json,'
    db.executescript("""
      CREATE TABLE IF NOT EXISTS card_field_coverage(
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        field_key TEXT NOT NULL,
        coverage_status TEXT NOT NULL,
        field_id INTEGER REFERENCES card_fields(field_id),
        source_payload_match INTEGER NOT NULL,
        source_value_sha256 TEXT,
        PRIMARY KEY(card_id,field_key)
      );
      CREATE INDEX IF NOT EXISTS idx_card_field_coverage_status
        ON card_field_coverage(coverage_status,field_key);
    """)
    db.execute("DELETE FROM card_field_coverage")
    field_rows=[]
    coverage_inserts=[]
    card_field_summaries=[]
    per_field_status_counts={field:{} for field in fields}
    per_field_examples={field:{} for field in fields}
    for card in cards:
        payload=json.loads(card["raw_payload_json"])
        verified_fields=[]
        absent_fields=[]
        empty_fields=[]
        null_fields=[]
        not_applicable_candidates=[]
        missing_fields=[]
        for field in fields:
            row=present.get((card["card_id"],field))
            if row is None:
                # The source snapshot is authoritative. An absent key is a confirmed
                # source absence; a key present in the raw payload but absent here is
                # a genuine ingestion/normalization gap.
                source_has_key=field in payload
                if source_has_key and payload[field] is None:
                    status="source_null_confirmed"
                elif source_has_key:
                    status="missing_on_card"
                elif (card["card_type"],field) not in observed_type_fields:
                    status="not_applicable_candidate"
                    not_applicable_candidates.append(field)
                else:
                    status="source_absent_confirmed"
                raw=None; normalized=None; verification="not_recorded"; field_id=None
                payload_match=1 if (not source_has_key or payload[field] is None) else 0
                value_hash=None
            else:
                raw=row["source_value_json"]; normalized=row["normalized_value"]
                verification=row["verification_status"]; field_id=row["field_id"]
                try: value=json.loads(raw) if raw is not None else None
                except Exception as exc: raise ValueError(f"Invalid JSON source value: {card['card_id']} {field}: {exc}")
                payload_match=int(field in payload and value==payload.get(field))
                if not payload_match:
                    raise ValueError(f"Normalized field differs from immutable raw payload: {card['card_id']} {field}")
                value_hash=hashlib.sha256((raw or "null").encode("utf-8")).hexdigest()
                status=("source_null_confirmed" if value is None else
                        "source_empty_confirmed" if value=="" else "source_snapshot_verified")
            coverage_inserts.append((card["card_id"],field,status,field_id,payload_match,value_hash))
            per_field_status_counts[field][status]=per_field_status_counts[field].get(status,0)+1
            if len(per_field_examples[field].get(status,[]))<5:
                per_field_examples[field].setdefault(status,[]).append(card["card_id"])
            if status=="source_snapshot_verified": verified_fields.append(field)
            elif status=="source_absent_confirmed": absent_fields.append(field)
            elif status=="source_empty_confirmed": empty_fields.append(field)
            elif status=="source_null_confirmed": null_fields.append(field)
            elif status=="not_applicable_candidate": pass
            elif status=="missing_on_card": missing_fields.append(field)
            field_rows.append({
                "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
                "field_key":field,"status":status,"source_value_json":raw,
                "normalized_value":normalized,"verification_status":verification,
                "source_payload_match":payload_match
            })
        card_field_summaries.append({
            "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
            "source_snapshot_verified_fields":verified_fields,
            "source_absent_confirmed_fields":absent_fields,
            "source_empty_confirmed_fields":empty_fields,
            "source_null_confirmed_fields":null_fields,
            "not_applicable_candidate_fields":not_applicable_candidates,
            "missing_on_card_fields":missing_fields
        })
    db.executemany("INSERT INTO card_field_coverage VALUES(?,?,?,?,?,?)",coverage_inserts)
    if len(coverage_inserts)!=len(cards)*len(fields):
        raise ValueError("Card-field coverage matrix is incomplete")
    if any(x[4]!=1 for x in coverage_inserts):
        raise ValueError("At least one normalized source field does not match its raw card payload")
    with (out_dir/"card-field-gap-report.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(field_rows[0]) if field_rows else ["card_id","field_key","status"])
        w.writeheader();w.writerows(field_rows)
    with (out_dir/"card-field-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for row in field_rows:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    with (out_dir/"card-field-card-summary.jsonl").open("w",encoding="utf-8") as f:
        for row in card_field_summaries:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    field_status_summary={
        "cards":len(cards),"fields":len(fields),
        "field_status_counts":per_field_status_counts,
        "example_card_ids_by_status":per_field_examples
    }
    (out_dir/"card-field-status-summary.json").write_text(
        json.dumps(field_status_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    costs=[]
    for r in db.execute("""
      SELECT c.card_id,c.name,c.card_type,c.source_card_url,cc.source_text,cc.soul_json,cc.lp_value,cc.lp_known,
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
            r["reviewReason"]=[]
            if r["mapping_review"]: r["reviewReason"].append("hybrid_color_payment_rule_unverified")
            if r["semantic_review"]: r["reviewReason"].append("special_soul_payment_rule_unverified")
            r["interpretationStatus"]="hybrid_identity_preserved_pending_rule" if r["mapping_review"] else "special_identity_preserved_pending_rule" if r["semantic_review"] else "unresolved"
            cost_review.append(r)
    with (out_dir/"cost-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    with (out_dir/"cost-inference-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")

    # Compact inventory of every decoded RequireSoul token identity, including
    # candidate semantics and original card URLs for manual verification.
    cost_code_inventory=[]
    grouped=db.execute("""
      SELECT code,symbol,normalized_color,parse_status,
             COUNT(*) AS token_rows,SUM(count) AS total_amount,
             COUNT(DISTINCT card_id) AS card_rows
      FROM card_soul_cost_tokens
      GROUP BY code,symbol,normalized_color,parse_status
      ORDER BY code,parse_status,normalized_color
    """).fetchall()
    for g in grouped:
        examples=[dict(x) for x in db.execute("""
          SELECT t.card_id,c.name,c.source_card_url,t.raw_token,t.count
          FROM card_soul_cost_tokens t JOIN cards c USING(card_id)
          WHERE t.code IS ? AND COALESCE(t.symbol,'')=COALESCE(?,'')
            AND COALESCE(t.normalized_color,'')=COALESCE(?,'')
            AND t.parse_status=?
          ORDER BY t.card_id LIMIT 5
        """,(g["code"],g["symbol"],g["normalized_color"],g["parse_status"]))]
        cost_code_inventory.append({
            "code":g["code"],"symbol":g["symbol"],
            "normalizedColorCandidate":g["normalized_color"],
            "parseStatus":g["parse_status"],"tokenRows":g["token_rows"],
            "totalAmount":g["total_amount"],"cardRows":g["card_rows"],
            "examples":examples
        })
    (out_dir/"cost-code-inventory.json").write_text(
        json.dumps(cost_code_inventory,ensure_ascii=False,indent=2),encoding="utf-8")

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

    # A compact diagnostic index makes the remaining low-confidence queue
    # actionable without downloading and opening the multi-hundred-MB DB artifact.
    low_effects=[r for r in effects if r["confidence"]=="low"]
    effect_groups={}
    effect_classes={}
    for r in low_effects:
        try:
            parsed=json.loads(r["interpretation_json"] or "{}")
        except Exception:
            parsed={}
        classification=parsed.get("classification","unknown")
        effect_classes[classification]=effect_classes.get(classification,0)+1
        key=" ".join((r["segment_text"] or "").split())
        if not key: key="(empty)"
        group=effect_groups.setdefault(key,{"text":key,"count":0,"classification":classification,
                                           "examples":[]})
        group["count"]+=1
        if len(group["examples"])<3:
            group["examples"].append({"card_id":r["card_id"],"name":r["name"],
                                      "url":r["source_detail_url"]})
    ranked_effect_groups=sorted(effect_groups.values(),key=lambda x:(-x["count"],x["text"]))
    effect_low_summary={
      "low_confidence_rows":len(low_effects),
      "unique_text_patterns":len(effect_groups),
      "classification_counts":dict(sorted(effect_classes.items())),
      "top_repeated_patterns":ranked_effect_groups[:100],
      "rare_pattern_samples":ranked_effect_groups[-100:]
    }
    (out_dir/"effect-low-confidence-summary.json").write_text(
      json.dumps(effect_low_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    summary={
      "cards":len(cards),"source_field_keys":len(fields),"card_field_matrix_rows":len(field_rows),
      "field_status_counts":{},
      "field_status_counts_by_field":per_field_status_counts,
      "source_payload_mismatches":sum(1 for x in coverage_inserts if x[4]!=1),
      "sqlite_field_coverage_rows":len(coverage_inserts),
      "cost_review_provenance_rows":len(cost_review),
      "unresolved_cost_rows":sum(1 for r in costs if not r["soul_known"] or (r["card_type"]=="지형" and not r["lp_known"])),
      "unmapped_skill_card_rows":sum(1 for r in skills if r["mapping_status"]=="unmapped"),
      "inferred_skill_card_rows":len(inferred_skills),
      "community_skill_card_rows":len(community_skills),
      "unmapped_skill_unique_values":len(skill_inventory),
      "low_confidence_effect_interpretations":sum(1 for r in effects if r["confidence"]=="low"),
      "effect_low_confidence_unique_patterns":len(effect_groups),
      "effect_low_confidence_classification_counts":effect_classes,
      "outputs":["card-field-gap-report.csv","card-field-gap-report.jsonl","cost-gap-report.jsonl","skill-gap-report.jsonl","inferred-skill-report.jsonl","community-skill-report.jsonl","unmapped-skill-inventory.csv","effect-gap-report.jsonl","effect-low-confidence-summary.json","cost-inference-report.jsonl","cost-code-inventory.json"]
    }
    for r in field_rows:summary["field_status_counts"][r["status"]]=summary["field_status_counts"].get(r["status"],0)+1
    (out_dir/"gap-report-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    db.commit()
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
)='text'
                      AND trim(json_extract(cf.source_value_json,'
    db.executescript("""
      CREATE TABLE IF NOT EXISTS card_field_coverage(
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        field_key TEXT NOT NULL,
        coverage_status TEXT NOT NULL,
        field_id INTEGER REFERENCES card_fields(field_id),
        source_payload_match INTEGER NOT NULL,
        source_value_sha256 TEXT,
        PRIMARY KEY(card_id,field_key)
      );
      CREATE INDEX IF NOT EXISTS idx_card_field_coverage_status
        ON card_field_coverage(coverage_status,field_key);
    """)
    db.execute("DELETE FROM card_field_coverage")
    field_rows=[]
    coverage_inserts=[]
    card_field_summaries=[]
    per_field_status_counts={field:{} for field in fields}
    per_field_examples={field:{} for field in fields}
    for card in cards:
        payload=json.loads(card["raw_payload_json"])
        verified_fields=[]
        absent_fields=[]
        empty_fields=[]
        null_fields=[]
        not_applicable_candidates=[]
        missing_fields=[]
        for field in fields:
            row=present.get((card["card_id"],field))
            if row is None:
                # The source snapshot is authoritative. An absent key is a confirmed
                # source absence; a key present in the raw payload but absent here is
                # a genuine ingestion/normalization gap.
                source_has_key=field in payload
                if source_has_key and payload[field] is None:
                    status="source_null_confirmed"
                elif source_has_key:
                    status="missing_on_card"
                elif (card["card_type"],field) not in observed_type_fields:
                    status="not_applicable_candidate"
                    not_applicable_candidates.append(field)
                else:
                    status="source_absent_confirmed"
                raw=None; normalized=None; verification="not_recorded"; field_id=None
                payload_match=1 if (not source_has_key or payload[field] is None) else 0
                value_hash=None
            else:
                raw=row["source_value_json"]; normalized=row["normalized_value"]
                verification=row["verification_status"]; field_id=row["field_id"]
                try: value=json.loads(raw) if raw is not None else None
                except Exception as exc: raise ValueError(f"Invalid JSON source value: {card['card_id']} {field}: {exc}")
                payload_match=int(field in payload and value==payload.get(field))
                if not payload_match:
                    raise ValueError(f"Normalized field differs from immutable raw payload: {card['card_id']} {field}")
                value_hash=hashlib.sha256((raw or "null").encode("utf-8")).hexdigest()
                status=("source_null_confirmed" if value is None else
                        "source_empty_confirmed" if value=="" else "source_snapshot_verified")
            coverage_inserts.append((card["card_id"],field,status,field_id,payload_match,value_hash))
            per_field_status_counts[field][status]=per_field_status_counts[field].get(status,0)+1
            if len(per_field_examples[field].get(status,[]))<5:
                per_field_examples[field].setdefault(status,[]).append(card["card_id"])
            if status=="source_snapshot_verified": verified_fields.append(field)
            elif status=="source_absent_confirmed": absent_fields.append(field)
            elif status=="source_empty_confirmed": empty_fields.append(field)
            elif status=="source_null_confirmed": null_fields.append(field)
            elif status=="not_applicable_candidate": pass
            elif status=="missing_on_card": missing_fields.append(field)
            field_rows.append({
                "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
                "field_key":field,"status":status,"source_value_json":raw,
                "normalized_value":normalized,"verification_status":verification,
                "source_payload_match":payload_match
            })
        card_field_summaries.append({
            "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
            "source_snapshot_verified_fields":verified_fields,
            "source_absent_confirmed_fields":absent_fields,
            "source_empty_confirmed_fields":empty_fields,
            "source_null_confirmed_fields":null_fields,
            "not_applicable_candidate_fields":not_applicable_candidates,
            "missing_on_card_fields":missing_fields
        })
    db.executemany("INSERT INTO card_field_coverage VALUES(?,?,?,?,?,?)",coverage_inserts)
    if len(coverage_inserts)!=len(cards)*len(fields):
        raise ValueError("Card-field coverage matrix is incomplete")
    if any(x[4]!=1 for x in coverage_inserts):
        raise ValueError("At least one normalized source field does not match its raw card payload")
    with (out_dir/"card-field-gap-report.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(field_rows[0]) if field_rows else ["card_id","field_key","status"])
        w.writeheader();w.writerows(field_rows)
    with (out_dir/"card-field-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for row in field_rows:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    with (out_dir/"card-field-card-summary.jsonl").open("w",encoding="utf-8") as f:
        for row in card_field_summaries:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    field_status_summary={
        "cards":len(cards),"fields":len(fields),
        "field_status_counts":per_field_status_counts,
        "example_card_ids_by_status":per_field_examples
    }
    (out_dir/"card-field-status-summary.json").write_text(
        json.dumps(field_status_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    costs=[]
    for r in db.execute("""
      SELECT c.card_id,c.name,c.card_type,c.source_card_url,cc.source_text,cc.soul_json,cc.lp_value,cc.lp_known,
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
            r["reviewReason"]=[]
            if r["mapping_review"]: r["reviewReason"].append("hybrid_color_payment_rule_unverified")
            if r["semantic_review"]: r["reviewReason"].append("special_soul_payment_rule_unverified")
            r["interpretationStatus"]="hybrid_identity_preserved_pending_rule" if r["mapping_review"] else "special_identity_preserved_pending_rule" if r["semantic_review"] else "unresolved"
            cost_review.append(r)
    with (out_dir/"cost-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    with (out_dir/"cost-inference-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")

    # Compact inventory of every decoded RequireSoul token identity, including
    # candidate semantics and original card URLs for manual verification.
    cost_code_inventory=[]
    grouped=db.execute("""
      SELECT code,symbol,normalized_color,parse_status,
             COUNT(*) AS token_rows,SUM(count) AS total_amount,
             COUNT(DISTINCT card_id) AS card_rows
      FROM card_soul_cost_tokens
      GROUP BY code,symbol,normalized_color,parse_status
      ORDER BY code,parse_status,normalized_color
    """).fetchall()
    for g in grouped:
        examples=[dict(x) for x in db.execute("""
          SELECT t.card_id,c.name,c.source_card_url,t.raw_token,t.count
          FROM card_soul_cost_tokens t JOIN cards c USING(card_id)
          WHERE t.code IS ? AND COALESCE(t.symbol,'')=COALESCE(?,'')
            AND COALESCE(t.normalized_color,'')=COALESCE(?,'')
            AND t.parse_status=?
          ORDER BY t.card_id LIMIT 5
        """,(g["code"],g["symbol"],g["normalized_color"],g["parse_status"]))]
        cost_code_inventory.append({
            "code":g["code"],"symbol":g["symbol"],
            "normalizedColorCandidate":g["normalized_color"],
            "parseStatus":g["parse_status"],"tokenRows":g["token_rows"],
            "totalAmount":g["total_amount"],"cardRows":g["card_rows"],
            "examples":examples
        })
    (out_dir/"cost-code-inventory.json").write_text(
        json.dumps(cost_code_inventory,ensure_ascii=False,indent=2),encoding="utf-8")

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

    # A compact diagnostic index makes the remaining low-confidence queue
    # actionable without downloading and opening the multi-hundred-MB DB artifact.
    low_effects=[r for r in effects if r["confidence"]=="low"]
    effect_groups={}
    effect_classes={}
    for r in low_effects:
        try:
            parsed=json.loads(r["interpretation_json"] or "{}")
        except Exception:
            parsed={}
        classification=parsed.get("classification","unknown")
        effect_classes[classification]=effect_classes.get(classification,0)+1
        key=" ".join((r["segment_text"] or "").split())
        if not key: key="(empty)"
        group=effect_groups.setdefault(key,{"text":key,"count":0,"classification":classification,
                                           "examples":[]})
        group["count"]+=1
        if len(group["examples"])<3:
            group["examples"].append({"card_id":r["card_id"],"name":r["name"],
                                      "url":r["source_detail_url"]})
    ranked_effect_groups=sorted(effect_groups.values(),key=lambda x:(-x["count"],x["text"]))
    effect_low_summary={
      "low_confidence_rows":len(low_effects),
      "unique_text_patterns":len(effect_groups),
      "classification_counts":dict(sorted(effect_classes.items())),
      "top_repeated_patterns":ranked_effect_groups[:100],
      "rare_pattern_samples":ranked_effect_groups[-100:]
    }
    (out_dir/"effect-low-confidence-summary.json").write_text(
      json.dumps(effect_low_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    summary={
      "cards":len(cards),"source_field_keys":len(fields),"card_field_matrix_rows":len(field_rows),
      "field_status_counts":{},
      "field_status_counts_by_field":per_field_status_counts,
      "source_payload_mismatches":sum(1 for x in coverage_inserts if x[4]!=1),
      "sqlite_field_coverage_rows":len(coverage_inserts),
      "cost_review_provenance_rows":len(cost_review),
      "unresolved_cost_rows":sum(1 for r in costs if not r["soul_known"] or (r["card_type"]=="지형" and not r["lp_known"])),
      "unmapped_skill_card_rows":sum(1 for r in skills if r["mapping_status"]=="unmapped"),
      "inferred_skill_card_rows":len(inferred_skills),
      "community_skill_card_rows":len(community_skills),
      "unmapped_skill_unique_values":len(skill_inventory),
      "low_confidence_effect_interpretations":sum(1 for r in effects if r["confidence"]=="low"),
      "effect_low_confidence_unique_patterns":len(effect_groups),
      "effect_low_confidence_classification_counts":effect_classes,
      "outputs":["card-field-gap-report.csv","card-field-gap-report.jsonl","cost-gap-report.jsonl","skill-gap-report.jsonl","inferred-skill-report.jsonl","community-skill-report.jsonl","unmapped-skill-inventory.csv","effect-gap-report.jsonl","effect-low-confidence-summary.json","cost-inference-report.jsonl","cost-code-inventory.json"]
    }
    for r in field_rows:summary["field_status_counts"][r["status"]]=summary["field_status_counts"].get(r["status"],0)+1
    (out_dir/"gap-report-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    db.commit()
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
))='')"""
    )}
    db.executescript("""
      CREATE TABLE IF NOT EXISTS card_field_coverage(
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        field_key TEXT NOT NULL,
        coverage_status TEXT NOT NULL,
        field_id INTEGER REFERENCES card_fields(field_id),
        source_payload_match INTEGER NOT NULL,
        source_value_sha256 TEXT,
        PRIMARY KEY(card_id,field_key)
      );
      CREATE INDEX IF NOT EXISTS idx_card_field_coverage_status
        ON card_field_coverage(coverage_status,field_key);
    """)
    db.execute("DELETE FROM card_field_coverage")
    field_rows=[]
    coverage_inserts=[]
    card_field_summaries=[]
    per_field_status_counts={field:{} for field in fields}
    per_field_examples={field:{} for field in fields}
    for card in cards:
        payload=json.loads(card["raw_payload_json"])
        verified_fields=[]
        absent_fields=[]
        empty_fields=[]
        null_fields=[]
        not_applicable_candidates=[]
        missing_fields=[]
        for field in fields:
            row=present.get((card["card_id"],field))
            if row is None:
                # The source snapshot is authoritative. An absent key is a confirmed
                # source absence; a key present in the raw payload but absent here is
                # a genuine ingestion/normalization gap.
                source_has_key=field in payload
                if source_has_key and payload[field] is None:
                    status="source_null_confirmed"
                elif source_has_key:
                    status="missing_on_card"
                elif (card["card_type"],field) not in observed_type_fields:
                    status="not_applicable_candidate"
                    not_applicable_candidates.append(field)
                else:
                    status="source_absent_confirmed"
                raw=None; normalized=None; verification="not_recorded"; field_id=None
                payload_match=1 if (not source_has_key or payload[field] is None) else 0
                value_hash=None
            else:
                raw=row["source_value_json"]; normalized=row["normalized_value"]
                verification=row["verification_status"]; field_id=row["field_id"]
                try: value=json.loads(raw) if raw is not None else None
                except Exception as exc: raise ValueError(f"Invalid JSON source value: {card['card_id']} {field}: {exc}")
                payload_match=int(field in payload and value==payload.get(field))
                if not payload_match:
                    raise ValueError(f"Normalized field differs from immutable raw payload: {card['card_id']} {field}")
                value_hash=hashlib.sha256((raw or "null").encode("utf-8")).hexdigest()
                status=("source_null_confirmed" if value is None else
                        "source_empty_confirmed" if value=="" else "source_snapshot_verified")
            coverage_inserts.append((card["card_id"],field,status,field_id,payload_match,value_hash))
            per_field_status_counts[field][status]=per_field_status_counts[field].get(status,0)+1
            if len(per_field_examples[field].get(status,[]))<5:
                per_field_examples[field].setdefault(status,[]).append(card["card_id"])
            if status=="source_snapshot_verified": verified_fields.append(field)
            elif status=="source_absent_confirmed": absent_fields.append(field)
            elif status=="source_empty_confirmed": empty_fields.append(field)
            elif status=="source_null_confirmed": null_fields.append(field)
            elif status=="not_applicable_candidate": pass
            elif status=="missing_on_card": missing_fields.append(field)
            field_rows.append({
                "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
                "field_key":field,"status":status,"source_value_json":raw,
                "normalized_value":normalized,"verification_status":verification,
                "source_payload_match":payload_match
            })
        card_field_summaries.append({
            "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
            "source_snapshot_verified_fields":verified_fields,
            "source_absent_confirmed_fields":absent_fields,
            "source_empty_confirmed_fields":empty_fields,
            "source_null_confirmed_fields":null_fields,
            "not_applicable_candidate_fields":not_applicable_candidates,
            "missing_on_card_fields":missing_fields
        })
    db.executemany("INSERT INTO card_field_coverage VALUES(?,?,?,?,?,?)",coverage_inserts)
    if len(coverage_inserts)!=len(cards)*len(fields):
        raise ValueError("Card-field coverage matrix is incomplete")
    if any(x[4]!=1 for x in coverage_inserts):
        raise ValueError("At least one normalized source field does not match its raw card payload")
    with (out_dir/"card-field-gap-report.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=list(field_rows[0]) if field_rows else ["card_id","field_key","status"])
        w.writeheader();w.writerows(field_rows)
    with (out_dir/"card-field-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for row in field_rows:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    with (out_dir/"card-field-card-summary.jsonl").open("w",encoding="utf-8") as f:
        for row in card_field_summaries:f.write(json.dumps(row,ensure_ascii=False)+"\n")
    field_status_summary={
        "cards":len(cards),"fields":len(fields),
        "field_status_counts":per_field_status_counts,
        "example_card_ids_by_status":per_field_examples
    }
    (out_dir/"card-field-status-summary.json").write_text(
        json.dumps(field_status_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    costs=[]
    for r in db.execute("""
      SELECT c.card_id,c.name,c.card_type,c.source_card_url,cc.source_text,cc.soul_json,cc.lp_value,cc.lp_known,
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
            r["reviewReason"]=[]
            if r["mapping_review"]: r["reviewReason"].append("hybrid_color_payment_rule_unverified")
            if r["semantic_review"]: r["reviewReason"].append("special_soul_payment_rule_unverified")
            r["interpretationStatus"]="hybrid_identity_preserved_pending_rule" if r["mapping_review"] else "special_identity_preserved_pending_rule" if r["semantic_review"] else "unresolved"
            cost_review.append(r)
    with (out_dir/"cost-gap-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")
    with (out_dir/"cost-inference-report.jsonl").open("w",encoding="utf-8") as f:
        for r in cost_review:
            f.write(json.dumps(r,ensure_ascii=False)+"\n")

    # Compact inventory of every decoded RequireSoul token identity, including
    # candidate semantics and original card URLs for manual verification.
    cost_code_inventory=[]
    grouped=db.execute("""
      SELECT code,symbol,normalized_color,parse_status,
             COUNT(*) AS token_rows,SUM(count) AS total_amount,
             COUNT(DISTINCT card_id) AS card_rows
      FROM card_soul_cost_tokens
      GROUP BY code,symbol,normalized_color,parse_status
      ORDER BY code,parse_status,normalized_color
    """).fetchall()
    for g in grouped:
        examples=[dict(x) for x in db.execute("""
          SELECT t.card_id,c.name,c.source_card_url,t.raw_token,t.count
          FROM card_soul_cost_tokens t JOIN cards c USING(card_id)
          WHERE t.code IS ? AND COALESCE(t.symbol,'')=COALESCE(?,'')
            AND COALESCE(t.normalized_color,'')=COALESCE(?,'')
            AND t.parse_status=?
          ORDER BY t.card_id LIMIT 5
        """,(g["code"],g["symbol"],g["normalized_color"],g["parse_status"]))]
        cost_code_inventory.append({
            "code":g["code"],"symbol":g["symbol"],
            "normalizedColorCandidate":g["normalized_color"],
            "parseStatus":g["parse_status"],"tokenRows":g["token_rows"],
            "totalAmount":g["total_amount"],"cardRows":g["card_rows"],
            "examples":examples
        })
    (out_dir/"cost-code-inventory.json").write_text(
        json.dumps(cost_code_inventory,ensure_ascii=False,indent=2),encoding="utf-8")

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

    # A compact diagnostic index makes the remaining low-confidence queue
    # actionable without downloading and opening the multi-hundred-MB DB artifact.
    low_effects=[r for r in effects if r["confidence"]=="low"]
    effect_groups={}
    effect_classes={}
    for r in low_effects:
        try:
            parsed=json.loads(r["interpretation_json"] or "{}")
        except Exception:
            parsed={}
        classification=parsed.get("classification","unknown")
        effect_classes[classification]=effect_classes.get(classification,0)+1
        key=" ".join((r["segment_text"] or "").split())
        if not key: key="(empty)"
        group=effect_groups.setdefault(key,{"text":key,"count":0,"classification":classification,
                                           "examples":[]})
        group["count"]+=1
        if len(group["examples"])<3:
            group["examples"].append({"card_id":r["card_id"],"name":r["name"],
                                      "url":r["source_detail_url"]})
    ranked_effect_groups=sorted(effect_groups.values(),key=lambda x:(-x["count"],x["text"]))
    effect_low_summary={
      "low_confidence_rows":len(low_effects),
      "unique_text_patterns":len(effect_groups),
      "classification_counts":dict(sorted(effect_classes.items())),
      "top_repeated_patterns":ranked_effect_groups[:100],
      "rare_pattern_samples":ranked_effect_groups[-100:]
    }
    (out_dir/"effect-low-confidence-summary.json").write_text(
      json.dumps(effect_low_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    summary={
      "cards":len(cards),"source_field_keys":len(fields),"card_field_matrix_rows":len(field_rows),
      "field_status_counts":{},
      "field_status_counts_by_field":per_field_status_counts,
      "source_payload_mismatches":sum(1 for x in coverage_inserts if x[4]!=1),
      "sqlite_field_coverage_rows":len(coverage_inserts),
      "cost_review_provenance_rows":len(cost_review),
      "unresolved_cost_rows":sum(1 for r in costs if not r["soul_known"] or (r["card_type"]=="지형" and not r["lp_known"])),
      "unmapped_skill_card_rows":sum(1 for r in skills if r["mapping_status"]=="unmapped"),
      "inferred_skill_card_rows":len(inferred_skills),
      "community_skill_card_rows":len(community_skills),
      "unmapped_skill_unique_values":len(skill_inventory),
      "low_confidence_effect_interpretations":sum(1 for r in effects if r["confidence"]=="low"),
      "effect_low_confidence_unique_patterns":len(effect_groups),
      "effect_low_confidence_classification_counts":effect_classes,
      "outputs":["card-field-gap-report.csv","card-field-gap-report.jsonl","cost-gap-report.jsonl","skill-gap-report.jsonl","inferred-skill-report.jsonl","community-skill-report.jsonl","unmapped-skill-inventory.csv","effect-gap-report.jsonl","effect-low-confidence-summary.json","cost-inference-report.jsonl","cost-code-inventory.json"]
    }
    for r in field_rows:summary["field_status_counts"][r["status"]]=summary["field_status_counts"].get(r["status"],0)+1
    (out_dir/"gap-report-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    db.commit()
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
