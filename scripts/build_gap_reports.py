#!/usr/bin/env python3
"""Create card-by-card gap queues without changing immutable source values."""
import argparse, csv, hashlib, json, sqlite3
from pathlib import Path

def cost_interpretation_status(mapping_review, semantic_review):
    if mapping_review and semantic_review:
        return "hybrid_and_special_identity_preserved_pending_rule"
    if mapping_review:
        return "hybrid_identity_preserved_pending_rule"
    if semantic_review:
        return "special_identity_preserved_pending_rule"
    return "unresolved"


def build_soul_semantic_review_queue(rows):
    """Group every pending hybrid/special soul token while retaining every card source."""
    groups={}
    card_ids=set()
    for row in rows:
        key=(row.get("code"),row.get("symbol") or "",row.get("normalized_color") or "",
             row.get("parse_status") or "")
        group=groups.setdefault(key,{
            "code":row.get("code"),"symbol":row.get("symbol"),
            "candidate_color_mapping":row.get("normalized_color"),
            "parse_status":row.get("parse_status"),
            "review_reasons":[],
            "token_rows":0,"card_ids":[],
            "occurrences":[]
        })
        reasons=[]
        if int(row.get("mapping_review") or 0):
            reasons.append("hybrid_payment_rule_unverified")
        if int(row.get("semantic_review") or 0):
            reasons.append("special_soul_payment_rule_unverified")
        for reason in reasons:
            if reason not in group["review_reasons"]:
                group["review_reasons"].append(reason)
        group["token_rows"]+=1
        card_id=str(row["card_id"])
        if card_id not in group["card_ids"]:
            group["card_ids"].append(card_id)
        group["occurrences"].append({
            "card_id":card_id,"name":row.get("name"),
            "card_type":row.get("card_type"),
            "source_card_url":row.get("source_card_url"),
            "source_require_soul":row.get("source_text"),
            "token_ordinal":row.get("ordinal"),
            "raw_token":row.get("raw_token"),
            "amount":row.get("count")
        })
        card_ids.add(card_id)
    result=sorted(groups.values(),key=lambda x:(str(x["code"]),str(x["symbol"] or ""),str(x["candidate_color_mapping"] or "")))
    for group in result:
        group["card_count"]=len(group["card_ids"])
        group["verification_status"]="pending_source_and_engine_verification"
        group["executable"]=False
    return {
        "pending_card_rows":len(card_ids),
        "token_rows":sum(x["token_rows"] for x in result),
        "groups":result,
        "policy":"Token identity and candidate color mapping are preserved; no payment rule is inferred or made executable."
    }


def build_effect_review_queue(low_effects, source_context_by_card=None):
    """Group low-confidence clauses while retaining each card's raw source context."""
    source_context_by_card=source_context_by_card or {}
    groups={}
    for row in low_effects:
        raw_text=" ".join((row.get("segment_text") or "").split()) or "(empty)"
        text=raw_text.lstrip("◇◆※▶★☆◈●○").strip() or raw_text
        try:
            parsed=json.loads(row.get("interpretation_json") or "{}")
        except Exception:
            parsed={}
        group=groups.setdefault(text,{
            "pattern_id":hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
            "text":text,
            "source_text_variants":[],
            "occurrences":0,
            "classification":parsed.get("classification","unknown"),
            "confidence":parsed.get("confidence","low"),
            "classification_variants":[],
            "confidence_variants":[],
            "classification_conflict":False,
            "confidence_conflict":False,
            "inference_methods":[],
            "card_types":[],
            "cards":[],
            "review_status":"pending_manual_semantic_review"
        })
        classification=parsed.get("classification","unknown")
        confidence=parsed.get("confidence","low")
        if classification not in group["classification_variants"]:
            group["classification_variants"].append(classification)
        if confidence not in group["confidence_variants"]:
            group["confidence_variants"].append(confidence)
        group["classification_conflict"]=len(group["classification_variants"])>1
        group["confidence_conflict"]=len(group["confidence_variants"])>1
        if group["classification_conflict"]:
            group["classification"]="mixed"
        if group["confidence_conflict"]:
            confidence_rank={"low":0,"medium":1,"high":2,"not_applicable":3}
            group["confidence"]=min(
                group["confidence_variants"],
                key=lambda value:confidence_rank.get(value,0)
            )
        group["occurrences"]+=1
        if raw_text not in group["source_text_variants"]:
            group["source_text_variants"].append(raw_text)
        method=parsed.get("inferenceMethod")
        if method and method not in group["inference_methods"]:
            group["inference_methods"].append(method)
        card_type=row.get("card_type")
        if card_type and card_type not in group["card_types"]:
            group["card_types"].append(card_type)
        source_context=source_context_by_card.get(str(row["card_id"]),{})
        card={"card_id":row["card_id"],"name":row.get("name"),
              "card_type":card_type,"clause_index":row.get("clause_index"),
              "url":row.get("source_detail_url") or source_context.get("source_card_url"),
              "source_card_url":source_context.get("source_card_url") or row.get("source_detail_url"),
              "source_text_fields":{
                  "TextBase":source_context.get("TextBase"),
                  "TextExtra":source_context.get("TextExtra")
              }}
        if not any(x["card_id"]==card["card_id"] and x["clause_index"]==card["clause_index"]
                   for x in group["cards"]):
            group["cards"].append(card)
    return sorted(groups.values(),key=lambda x:(-x["occurrences"],x["text"]))


def build_skill2_execution_review_rows(skill_rows, rules):
    """Join Skill2 candidate rules to card-local source excerpts without promoting verification."""
    by_name={rule.get("name"):rule for rule in rules if rule.get("name")}
    review=[]
    for source in skill_rows:
        if source.get("source_field")!="Skill2" or source.get("source_name") not in by_name:
            continue
        try:
            refs=json.loads(source.get("evidence_references_json") or "[]")
        except Exception:
            refs=[]
        local=next((x for x in refs if x.get("kind") in ("card_text_inference","card_text_evidence_missing")),{})
        count=int(local.get("evidenceCount") or 0)
        row=dict(source)
        row["execution_rule"]=by_name[source["source_name"]]
        row["card_local_evidence_count"]=count
        row["card_local_evidence_references"]=local.get("references",[])
        row["other_evidence_references"]=[x for x in refs if x is not local]
        row["verification_status"]=(
            "card_source_excerpt_available_pending_semantic_review" if count
            else "card_source_excerpt_missing"
        )
        review.append(row)
    return sorted(review,key=lambda x:(x["source_name"],x["card_id"]))


def build(db_path: Path, out_dir: Path):
    db=sqlite3.connect(db_path)
    db.row_factory=sqlite3.Row
    out_dir.mkdir(parents=True,exist_ok=True)
    cards=db.execute("SELECT card_id,name,card_type,source_card_url,raw_payload_json FROM cards ORDER BY card_id").fetchall()
    fields=[r[0] for r in db.execute("SELECT DISTINCT field_key FROM card_fields ORDER BY field_key")]
    present={(r["card_id"],r["field_key"]):r for r in db.execute(
        "SELECT field_id,card_id,field_key,source_value_json,normalized_value,verification_status FROM card_fields"
    )}
    # Determine applicability from non-empty values in the raw source Category.
    # Explicit empty/null values remain separate statuses; they do not prove applicability.
    source_payloads={card["card_id"]:json.loads(card["raw_payload_json"]) for card in cards}
    source_effect_context_by_card={
        card["card_id"]:{
            "source_card_url":card["source_card_url"],
            "TextBase":{
                "source_key_present":"TextBase" in source_payloads[card["card_id"]],
                "source_value":source_payloads[card["card_id"]].get("TextBase")
            },
            "TextExtra":{
                "source_key_present":"TextExtra" in source_payloads[card["card_id"]],
                "source_value":source_payloads[card["card_id"]].get("TextExtra")
            }
        }
        for card in cards
    }
    source_categories={card_id:payload.get("Category") for card_id,payload in source_payloads.items()}
    observed_type_fields=set()
    for (card_id,field),row in present.items():
        raw=row["source_value_json"]
        try:
            value=json.loads(raw) if raw is not None else None
        except Exception:
            continue
        if value is not None and not (isinstance(value,str) and not value.strip()):
            observed_type_fields.add((source_categories.get(card_id),field))
    db.executescript("""
      CREATE TABLE IF NOT EXISTS card_field_coverage(
        card_id TEXT NOT NULL REFERENCES cards(card_id),
        field_key TEXT NOT NULL,
        coverage_status TEXT NOT NULL,
        applicability_status TEXT NOT NULL,
        field_id INTEGER REFERENCES card_fields(field_id),
        source_payload_match INTEGER NOT NULL,
        source_value_sha256 TEXT,
        PRIMARY KEY(card_id,field_key)
      );
      CREATE INDEX IF NOT EXISTS idx_card_field_coverage_status
        ON card_field_coverage(coverage_status,field_key);
    """)
    coverage_columns={r[1] for r in db.execute("PRAGMA table_info(card_field_coverage)")}
    if "applicability_status" not in coverage_columns:
        db.execute("ALTER TABLE card_field_coverage ADD COLUMN applicability_status TEXT NOT NULL DEFAULT 'unknown'")
    db.execute("DELETE FROM card_field_coverage")
    field_rows=[]
    coverage_inserts=[]
    card_field_summaries=[]
    per_field_status_counts={field:{} for field in fields}
    per_field_applicability_counts={field:{} for field in fields}
    per_field_examples={field:{} for field in fields}
    applicability_scope={}
    for card in cards:
        payload=source_payloads[card["card_id"]]
        source_category=payload.get("Category")
        verified_fields=[]
        absent_fields=[]
        empty_fields=[]
        null_fields=[]
        not_applicable_fields=[]
        missing_fields=[]
        for field in fields:
            row=present.get((card["card_id"],field))
            if row is None:
                # Source presence and semantic applicability are separate facts.
                # The raw snapshot confirms whether a key exists; category-level
                # absence only creates an applicability candidate, never erases absence.
                source_has_key=field in payload
                if source_has_key and payload[field] is None:
                    status="source_null_confirmed"; applicability="source_present_null"
                elif source_has_key:
                    status="missing_on_card"; applicability="source_present_missing_normalization"
                else:
                    status="source_absent_confirmed"
                    if (source_category,field) not in observed_type_fields:
                        # All cards in this source category were present in the complete
                        # 15,350-card snapshot and none carries this field. Record the
                        # raw absence and the category-scoped N/A conclusion separately.
                        applicability="not_applicable_confirmed"
                        not_applicable_fields.append(field)
                        key=(source_category,field)
                        item=applicability_scope.setdefault(key,{
                            "source_category":source_category,"card_type":card["card_type"],
                            "field_key":field,"card_count":0,"cards_with_field_in_category":0,
                            "source_snapshot_card_count":len(cards),
                            "verification_status":"source_snapshot_category_scope",
                            "example_card_ids":[]
                        })
                        item["card_count"]+=1
                        if len(item["example_card_ids"])<5:
                            item["example_card_ids"].append(card["card_id"])
                    else:
                        applicability="applicable_source_absent"
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
                applicability="source_present"
            coverage_inserts.append((card["card_id"],field,status,applicability,field_id,payload_match,value_hash))
            per_field_status_counts[field][status]=per_field_status_counts[field].get(status,0)+1
            per_field_applicability_counts[field][applicability]=per_field_applicability_counts[field].get(applicability,0)+1
            if len(per_field_examples[field].get(status,[]))<5:
                per_field_examples[field].setdefault(status,[]).append(card["card_id"])
            if status=="source_snapshot_verified": verified_fields.append(field)
            elif status=="source_absent_confirmed": absent_fields.append(field)
            elif status=="source_empty_confirmed": empty_fields.append(field)
            elif status=="source_null_confirmed": null_fields.append(field)
            elif status=="missing_on_card": missing_fields.append(field)
            field_rows.append({
                "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
                "field_key":field,"status":status,"applicability_status":applicability,
                "source_value_json":raw,"normalized_value":normalized,
                "verification_status":verification,"source_payload_match":payload_match
            })
        card_field_summaries.append({
            "card_id":card["card_id"],"name":card["name"],"card_type":card["card_type"],
            "source_category":source_category,
            "source_snapshot_verified_fields":verified_fields,
            "source_absent_confirmed_fields":absent_fields,
            "source_empty_confirmed_fields":empty_fields,
            "source_null_confirmed_fields":null_fields,
            "not_applicable_confirmed_fields":not_applicable_fields,
            "missing_on_card_fields":missing_fields
        })
    db.executemany("""INSERT INTO card_field_coverage
      (card_id,field_key,coverage_status,applicability_status,field_id,source_payload_match,source_value_sha256)
      VALUES(?,?,?,?,?,?,?)""",coverage_inserts)
    if len(coverage_inserts)!=len(cards)*len(fields):
        raise ValueError("Card-field coverage matrix is incomplete")
    if any(x[5]!=1 for x in coverage_inserts):
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
        "field_applicability_counts":per_field_applicability_counts,
        "example_card_ids_by_status":per_field_examples
    }
    applicability_rows=sorted(applicability_scope.values(),
        key=lambda x:(x["source_category"],x["field_key"]))
    with (out_dir/"field-applicability-scope-report.jsonl").open("w",encoding="utf-8") as f:
        for row in applicability_rows:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
    with (out_dir/"field-applicability-scope-report.csv").open("w",newline="",encoding="utf-8-sig") as f:
        w=csv.DictWriter(f,fieldnames=["source_category","card_type","field_key","card_count","cards_with_field_in_category","source_snapshot_card_count","verification_status","example_card_ids"])
        w.writeheader()
        for row in applicability_rows:
            w.writerow({**row,"example_card_ids":";".join(row["example_card_ids"])})
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
            r["interpretationStatus"]=cost_interpretation_status(r["mapping_review"],r["semantic_review"])
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

    # Full source-linked review queue: unlike the compact inventory above, this
    # retains every card occurrence rather than only five examples per token.
    soul_review_rows=[dict(r) for r in db.execute("""
      SELECT t.card_id,c.name,c.card_type,c.source_card_url,cc.source_text,
             CASE WHEN t.parse_status='hybrid_identity_preserved_pending_rule' THEN 1 ELSE 0 END AS mapping_review,
             CASE WHEN t.parse_status='special_identity_preserved_pending_rule' THEN 1 ELSE 0 END AS semantic_review,
             t.ordinal,t.raw_token,t.code,t.count,t.symbol,t.normalized_color,t.parse_status
      FROM card_soul_cost_tokens t
      JOIN card_costs cc USING(card_id)
      JOIN cards c USING(card_id)
      WHERE t.parse_status IN (
        'hybrid_identity_preserved_pending_rule',
        'special_identity_preserved_pending_rule'
      )
      ORDER BY t.code,t.symbol,t.normalized_color,t.parse_status,t.card_id,t.ordinal
    """)]
    soul_review_queue=build_soul_semantic_review_queue(soul_review_rows)
    (out_dir/"soul-semantic-review-queue.json").write_text(
        json.dumps(soul_review_queue,ensure_ascii=False,indent=2),encoding="utf-8")

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
      SELECT m.card_id,c.name,c.card_type,c.source_card_url,m.source_field,m.source_enum_value,m.source_name,
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

    skill2_catalog_path=Path("data/rules/fm1-skill2-execution-catalog-v1.json")
    skill2_catalog=json.loads(skill2_catalog_path.read_text(encoding="utf-8")) if skill2_catalog_path.exists() else {"rules":[]}
    skill2_review=build_skill2_execution_review_rows(skills,skill2_catalog.get("rules",[]))
    with (out_dir/"skill2-execution-review.jsonl").open("w",encoding="utf-8") as f:
        for row in skill2_review:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
    skill2_review_by_rule={}
    for row in skill2_review:
        item=skill2_review_by_rule.setdefault(row["source_name"],{"card_rows":0,"rows_with_card_local_evidence":0,"rows_missing_card_local_evidence":0})
        item["card_rows"]+=1
        item["rows_with_card_local_evidence"]+=int(row["card_local_evidence_count"]>0)
        item["rows_missing_card_local_evidence"]+=int(row["card_local_evidence_count"]==0)
    skill2_review_summary={
        "catalog_rule_count":len(skill2_catalog.get("rules",[])),
        "candidate_card_rows":len(skill2_review),
        "card_rows_with_local_source_evidence":sum(x["rows_with_card_local_evidence"] for x in skill2_review_by_rule.values()),
        "card_rows_missing_local_source_evidence":sum(x["rows_missing_card_local_evidence"] for x in skill2_review_by_rule.values()),
        "by_skill":skill2_review_by_rule,
        "verification_policy":"Source excerpts are candidates only; no card mapping is promoted to source_card_verified by this report."
    }
    (out_dir/"skill2-execution-review-summary.json").write_text(
        json.dumps(skill2_review_summary,ensure_ascii=False,indent=2),encoding="utf-8")

    named_effect_definitions=[]
    try:
        for r in db.execute("""SELECT definition_id,source_card_id,source_card_name,source_field,marker,
            effect_name,definition_text,source_text_sha256,extraction_method,verification_status
            FROM card_named_effect_definitions ORDER BY effect_name,source_card_id,definition_id"""):
            named_effect_definitions.append(dict(r))
    except sqlite3.OperationalError:
        named_effect_definitions=[]
    with (out_dir/"named-effect-definition-index.jsonl").open("w",encoding="utf-8") as f:
        for row in named_effect_definitions:
            f.write(json.dumps(row,ensure_ascii=False)+"\n")
    named_effect_reference_rows=0
    try:
        named_effect_reference_rows=db.execute("""SELECT COUNT(*) FROM card_effect_interpretations
            WHERE json_extract(interpretation_json,'$.classification')='named_effect_reference'""").fetchone()[0]
    except sqlite3.OperationalError:
        named_effect_reference_rows=0

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

    effect_review_queue=build_effect_review_queue(low_effects,source_effect_context_by_card)
    with (out_dir/"effect-review-queue.jsonl").open("w",encoding="utf-8") as f:
        for item in effect_review_queue:
            f.write(json.dumps(item,ensure_ascii=False)+chr(10))

    summary={
      "cards":len(cards),"source_field_keys":len(fields),"card_field_matrix_rows":len(field_rows),
      "field_status_counts":{},
      "field_applicability_counts":{},
      "field_status_counts_by_field":per_field_status_counts,
      "field_applicability_counts_by_field":per_field_applicability_counts,
      "field_applicability_candidate_pairs":0,
      "field_applicability_candidate_cells":0,
      "field_applicability_not_applicable_pairs":len(applicability_rows),
      "field_applicability_not_applicable_cells":sum(x["card_count"] for x in applicability_rows),
      "source_payload_mismatches":sum(1 for x in coverage_inserts if x[5]!=1),
      "sqlite_field_coverage_rows":len(coverage_inserts),
      "cost_review_provenance_rows":len(cost_review),
      "unresolved_cost_rows":sum(1 for r in costs if not r["soul_known"] or (r["card_type"]=="지형" and not r["lp_known"])),
      "unmapped_skill_card_rows":sum(1 for r in skills if r["mapping_status"]=="unmapped"),
      "inferred_skill_card_rows":len(inferred_skills),
      "community_skill_card_rows":len(community_skills),
      "unmapped_skill_unique_values":len(skill_inventory),
      "low_confidence_effect_interpretations":sum(1 for r in effects if r["confidence"]=="low"),
      "effect_low_confidence_unique_patterns":len(effect_groups),
      "effect_review_queue_patterns":len(effect_review_queue),
      "named_effect_definition_rows":len(named_effect_definitions),
      "named_effect_definition_unique_names":len({x["effect_name"] for x in named_effect_definitions}),
      "named_effect_reference_rows":named_effect_reference_rows,
      "skill2_execution_candidate_rows":len(skill2_review),
      "skill2_execution_candidate_rules":len(skill2_review_by_rule),
      "skill2_execution_rows_with_card_local_evidence":skill2_review_summary["card_rows_with_local_source_evidence"],
      "skill2_execution_rows_missing_card_local_evidence":skill2_review_summary["card_rows_missing_local_source_evidence"],
      "effect_low_confidence_classification_counts":effect_classes,
      "outputs":["card-field-gap-report.csv","card-field-gap-report.jsonl","cost-gap-report.jsonl","skill-gap-report.jsonl","inferred-skill-report.jsonl","community-skill-report.jsonl","unmapped-skill-inventory.csv","effect-gap-report.jsonl","effect-low-confidence-summary.json","effect-review-queue.jsonl","cost-inference-report.jsonl","cost-code-inventory.json","field-applicability-scope-report.jsonl","field-applicability-scope-report.csv","named-effect-definition-index.jsonl","skill2-execution-review.jsonl","skill2-execution-review-summary.json"]
    }
    for r in field_rows:
        summary["field_status_counts"][r["status"]]=summary["field_status_counts"].get(r["status"],0)+1
        summary["field_applicability_counts"][r["applicability_status"]]=summary["field_applicability_counts"].get(r["applicability_status"],0)+1
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