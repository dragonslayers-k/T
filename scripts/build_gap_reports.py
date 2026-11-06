#!/usr/bin/env python3
"""Create card-by-card gap queues without changing immutable source values."""
import argparse, csv, hashlib, json, sqlite3
from collections import Counter
from pathlib import Path


def classify_cost_review(row, token_evidence):
    """Classify pending cost dimensions from explicit source tokens; never infer BONUS as neutral."""
    symbols={str(token.get("symbol") or "").upper() for token in (token_evidence or [])}
    normalized={str(token.get("normalized_color") or "").lower() for token in (token_evidence or [])}
    dimensions=[]
    if bool(row.get("mapping_review")):
        dimensions.append("hybrid_mapping_review_pending")
    if bool(row.get("semantic_review")):
        has_bonus = "BONUS" in symbols or "bonus" in normalized
        has_ncs = "NCS" in symbols or "ncs" in normalized
        if has_bonus:
            dimensions.append("bonus_semantics_unverified")
        if has_ncs:
            dimensions.append("ncs_semantics_unverified")
        if not has_bonus and not has_ncs:
            dimensions.append("semantic_review_unclassified")
    if not bool(row.get("soul_known")):
        dimensions.append("source_cost_unresolved")
    if row.get("card_type")=="지형" and not bool(row.get("lp_known")):
        dimensions.append("land_lp_unresolved")
    status=dimensions[0] if len(dimensions)==1 else "multiple_review_dimensions" if dimensions else "verified"
    return status,dimensions

def write_jsonl_rows(path, rows):
    """Write one independently parseable JSON object per physical line."""
    with Path(path).open("w", encoding="utf-8") as stream:
        for row in rows:
            stream.write(json.dumps(row, ensure_ascii=False) + "\n")


def expand_cost_token_review_rows(cost_rows, token_rows_by_card):
    """Expand pending card-level cost reviews into immutable token-occurrence evidence rows."""
    expanded=[]
    for card in cost_rows:
        status,dimensions=classify_cost_review(card,token_rows_by_card.get(card["card_id"],[]))
        if not dimensions:
            continue
        tokens=token_rows_by_card.get(card["card_id"],[])
        if not tokens:
            tokens=[{}]
        for token in tokens:
            symbol=str(token.get("symbol") or "").upper()
            normalized=str(token.get("normalized_color") or "").lower()
            parse_status=str(token.get("parse_status") or "").lower()
            token_dimensions=[]
            if "hybrid_mapping_review_pending" in dimensions and ("+" in normalized or "hybrid" in parse_status):
                token_dimensions.append("hybrid_mapping_review_pending")
            if "bonus_semantics_unverified" in dimensions and (symbol=="BONUS" or normalized=="bonus"):
                token_dimensions.append("bonus_semantics_unverified")
            if "ncs_semantics_unverified" in dimensions and (symbol=="NCS" or normalized=="ncs"):
                token_dimensions.append("ncs_semantics_unverified")
            if "semantic_review_unclassified" in dimensions:
                token_dimensions.append("semantic_review_unclassified")
            card_level_dimensions=[d for d in dimensions if d in {
                "source_cost_unresolved","land_lp_unresolved"
            }]
            if not token:
                token_relevance="no_token_evidence"
            elif token_dimensions:
                token_relevance="direct_token_evidence"
            else:
                token_relevance="context_only"
            expanded.append({
                "card_id":card["card_id"],
                "name":card.get("name"),
                "card_type":card.get("card_type"),
                "source_text":card.get("source_text"),
                "review_status":status,
                "review_dimensions":dimensions,
                "token_dimensions":token_dimensions,
                "card_level_dimensions":card_level_dimensions,
                "token_review_relevance":token_relevance,
                "review_scope":"token_occurrence" if token else "card_without_token_evidence",
                "ordinal":token.get("ordinal"),
                "raw_token":token.get("raw_token"),
                "code":token.get("code"),
                "count":token.get("count"),
                "symbol":token.get("symbol"),
                "normalized_color":token.get("normalized_color"),
                "parse_status":token.get("parse_status"),
            })
    return expanded


def build(db_path: Path, out_dir: Path):
    db=sqlite3.connect(db_path)
    db.row_factory=sqlite3.Row
    out_dir.mkdir(parents=True,exist_ok=True)
    cards=db.execute("SELECT card_id,name,card_type,raw_payload_json FROM cards ORDER BY card_id").fetchall()
    fields=[r[0] for r in db.execute("SELECT DISTINCT field_key FROM card_fields ORDER BY field_key")]
    present={(r["card_id"],r["field_key"]):r for r in db.execute(
        "SELECT field_id,card_id,field_key,source_value_json,normalized_value,verification_status FROM card_fields"
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
    for card in cards:
        payload=json.loads(card["raw_payload_json"])
        for field in fields:
            row=present.get((card["card_id"],field))
            if row is None:
                # The source snapshot is authoritative. An absent key is a confirmed
                # source absence; a key present in the raw payload but absent here is
                # a genuine ingestion/normalization gap.
                source_has_key=field in payload
                status="missing_on_card" if source_has_key else "source_absent_confirmed"
                raw=None; normalized=None; verification="not_recorded"; field_id=None
                payload_match=0 if source_has_key else 1
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
                status=("source_absent_confirmed" if value is None or value=="" else "source_snapshot_verified")
            coverage_inserts.append((card["card_id"],field,status,field_id,payload_match,value_hash))
            field_rows.append({
                "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
                "field_key":field,"status":status,"source_value_json":raw,
                "normalized_value":normalized,"verification_status":verification,
                "source_payload_match":payload_match
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

    costs=[]
    for r in db.execute("""
      SELECT c.card_id,c.name,c.card_type,cc.source_text,cc.soul_json,cc.lp_value,cc.lp_known,
             cc.soul_known,cc.mapping_review,cc.semantic_review,cc.verification_status
      FROM cards c JOIN card_costs cc USING(card_id) ORDER BY c.card_id
    """):
        costs.append(dict(r))
    cost_review=[]
    cost_tokens_by_card={}
    for r in costs:
        if not r["soul_known"] or r["mapping_review"] or r["semantic_review"] or (r["card_type"]=="지형" and not r["lp_known"]):
            token_evidence=[dict(x) for x in db.execute(
                "SELECT ordinal,raw_token,code,count,symbol,normalized_color,parse_status FROM card_soul_cost_tokens WHERE card_id=? ORDER BY ordinal",
                (r["card_id"],))]
            cost_tokens_by_card[r["card_id"]]=token_evidence
            r["tokenEvidence"]=token_evidence
            r["interpretationStatus"],r["reviewDimensions"]=classify_cost_review(r,token_evidence)
            cost_review.append(r)
    token_review_rows=expand_cost_token_review_rows(cost_review,cost_tokens_by_card)
    write_jsonl_rows(out_dir/"cost-token-review-queue.jsonl", token_review_rows)
    with (out_dir/"cost-token-review-queue.csv").open("w",newline="",encoding="utf-8-sig") as f:
        columns=list(token_review_rows[0]) if token_review_rows else [
            "card_id","name","card_type","source_text","review_status","review_dimensions",
            "token_dimensions","card_level_dimensions","token_review_relevance","review_scope",
            "ordinal","raw_token","code","count","symbol","normalized_color","parse_status"]
        w=csv.DictWriter(f,fieldnames=columns)
        w.writeheader()
        for row in token_review_rows:
            item=dict(row)
            item["review_dimensions"]=";".join(row["review_dimensions"])
            w.writerow(item)
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

    cost_review_status_counts=Counter(r["interpretationStatus"] for r in cost_review)
    cost_review_dimension_counts=Counter(
        dimension for r in cost_review for dimension in r["reviewDimensions"]
    )
    summary={
      "cards":len(cards),"source_field_keys":len(fields),"card_field_matrix_rows":len(field_rows),
      "field_status_counts":{},
      "source_payload_mismatches":sum(1 for x in coverage_inserts if x[4]!=1),
      "sqlite_field_coverage_rows":len(coverage_inserts),
      "cost_review_provenance_rows":len(cost_review),
      "cost_review_token_occurrence_rows":sum(1 for r in token_review_rows if r["review_scope"]=="token_occurrence"),
      "cost_review_direct_token_evidence_rows":sum(1 for r in token_review_rows if r["token_review_relevance"]=="direct_token_evidence"),
      "cost_review_context_only_token_rows":sum(1 for r in token_review_rows if r["token_review_relevance"]=="context_only"),
      "cost_review_card_without_token_evidence_rows":sum(1 for r in token_review_rows if r["review_scope"]=="card_without_token_evidence"),
      "cost_review_token_symbol_counts":dict(sorted(Counter(str(r["symbol"] or "unlabelled") for r in token_review_rows).items())),
      "cost_review_status_counts":dict(sorted(cost_review_status_counts.items())),
      "cost_review_dimension_counts":dict(sorted(cost_review_dimension_counts.items())),
      "cost_review_count_note":"Status counts are mutually exclusive; dimension counts may overlap when one card has multiple pending review dimensions.",
      "unresolved_cost_rows":sum(1 for r in costs if not r["soul_known"] or (r["card_type"]=="지형" and not r["lp_known"])),
      "unmapped_skill_card_rows":sum(1 for r in skills if r["mapping_status"]=="unmapped"),
      "inferred_skill_card_rows":len(inferred_skills),
      "community_skill_card_rows":len(community_skills),
      "unmapped_skill_unique_values":len(skill_inventory),
      "low_confidence_effect_interpretations":sum(1 for r in effects if r["confidence"]=="low"),
      "effect_low_confidence_unique_patterns":len(effect_groups),
      "effect_low_confidence_classification_counts":effect_classes,
      "outputs":["card-field-gap-report.csv","card-field-gap-report.jsonl","cost-gap-report.jsonl","skill-gap-report.jsonl","inferred-skill-report.jsonl","community-skill-report.jsonl","unmapped-skill-inventory.csv","effect-gap-report.jsonl","effect-low-confidence-summary.json","cost-inference-report.jsonl","cost-token-review-queue.jsonl","cost-token-review-queue.csv"]
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
