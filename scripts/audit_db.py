#!/usr/bin/env python3
import json,sqlite3,sys
from pathlib import Path
target=15350;db=Path("data/fm1_cards.sqlite")
if not db.exists():raise SystemExit("DB missing")
c=sqlite3.connect(db);q=lambda sql:c.execute(sql).fetchone()[0]
manifest=Path("data/raw/image-manifest.jsonl");images=[]
if manifest.exists():
 with manifest.open(encoding="utf-8") as f:images=[json.loads(x) for x in f if x.strip()]
crawl_path=Path("data/raw/crawl-summary.json");crawl=json.loads(crawl_path.read_text()) if crawl_path.exists() else {}
large=[x for x in images if x.get("image_type")=="large"];small=[x for x in images if x.get("image_type")=="small"]
result={
 "required_cards":target,"firestore_source_count":crawl.get("source_count"),
 "unique_cards":q("select count(*) from cards"),
 "duplicate_ids":q("select count(*) from (select card_id from cards group by card_id having count(*)>1)"),
 "missing_names":q("select count(*) from cards where name is null or trim(name)=''"),
 "missing_individual_urls":q("select count(*) from cards where source_card_url is null or source_card_url=''"),
 "missing_list_urls":q("select count(*) from cards where source_list_url is null or source_list_url=''"),
 "distinct_source_fields":q("select count(distinct field_key) from card_fields"),
 "card_field_rows":q("select count(*) from card_fields"),
 "taxonomy_rows":q("select count(*) from taxonomy"),
 "cards_with_textbase":q("select count(distinct card_id) from card_fields where field_key='TextBase'"),
 "cards_with_textextra":q("select count(distinct card_id) from card_fields where field_key='TextExtra'"),
 "effect_source_mismatches":q("select count(*) from card_effects e left join card_texts t on t.card_id=e.card_id and t.text_type=case e.source_key when 'TextBase' then 'card_text' when 'TextExtra' then 'additional_text' else '' end and t.plain_text=e.effect_text where t.text_id is null"),
 "effect_source_text_rows":q("select count(*) from card_texts where text_type in ('card_text','additional_text')"),
 "effect_rows":q("select count(*) from card_effects"),
 "cards_with_effect_rows":q("select count(distinct card_id) from card_effects"),
 "effect_rows_unverified":q("select count(*) from card_effects where verification_status='extracted_unverified'"),
 "effect_rows_without_text":q("select count(*) from card_effects where effect_text is null or trim(effect_text)=''"),
 "cards_with_image_urls":q("select count(distinct card_id) from card_images where source_url is not null and source_url<>''"),
 "image_rows_in_db":q("select count(*) from card_images"),
 "large_images_downloaded":sum(x.get("status") in ("downloaded","archive_verified","verified") for x in large),
 "small_images_downloaded":sum(x.get("status") in ("downloaded","archive_verified","verified") for x in small),
 "large_image_failures":sum(x.get("status") not in ("downloaded","archive_verified","verified") for x in large),
 "small_image_failures":sum(x.get("status") not in ("downloaded","archive_verified","verified") for x in small),
 "large_image_manifest_rows":len(large),"small_image_manifest_rows":len(small),
 "lp_known_cards":q("select count(*) from card_costs where lp_known=1"),
 "lp_zero_cards":q("select count(*) from card_costs where lp_known=1 and lp_value=0"),
 "soul_cost_fully_parsed":q("select count(*) from card_costs where soul_known=1"),
 "soul_cost_needs_review":q("select count(*) from card_costs where soul_known=0"),
 "soul_cost_tokens":q("select count(*) from card_soul_cost_tokens"),
 "soul_mapping_review":q("select count(*) from card_costs where mapping_review=1"),
 "soul_semantic_review":q("select count(*) from card_costs where semantic_review=1"),
 "soul_manual_review":q("select count(*) from card_costs where soul_known=0"),
 "skill_mapping_rows":q("select count(*) from card_rule_mappings"),
 "skill_source_rows":q("select count(*) from card_fields where field_key in ('Skill1','Skill2')"),
 "skill_unmapped_rows":q("select count(*) from card_rule_mappings where mapping_status='unmapped'"),
 "skill_manual_verified_rows":q("select count(*) from card_rule_mappings where mapping_status='manual_verified'"),
 "skill_community_candidate_rows":q("select count(*) from card_rule_mappings where mapping_status='community_documented_candidate'"),
 "skill_no_special_rows":q("select count(*) from card_rule_mappings where mapping_status='no_special_skill'"),
 "skill_inventory_unmapped_values":q("select count(*) from skill_enum_inventory where mapping_status='unmapped'"),
 "unmapped_skill_inventory":[{"source_field":r[0],"source_enum_value":r[1],"source_name":r[2],"card_count":r[3],"mapping_status":r[4]} for r in c.execute("select source_field,source_enum_value,source_name,card_count,mapping_status from skill_enum_inventory where mapping_status='unmapped' order by source_field,source_name")],
 "skill_mapping_coverage_accounted_for":q("select count(*) from card_rule_mappings")==q("select count(*) from card_fields where field_key in ('Skill1','Skill2')"),
 "category_counts":dict(c.execute("select card_type,count(*) from cards group by card_type")),
 "crawl_pages":crawl.get("pages"),"crawl_complete":crawl.get("complete",False),"complete":False
}
result["field_coverage_rows"]=q("select count(*) from card_field_coverage")
result["field_coverage_source_verified"]=q("select count(*) from card_field_coverage where coverage_status='source_snapshot_verified'")
result["field_coverage_source_absent"]=q("select count(*) from card_field_coverage where coverage_status='source_absent_confirmed'")
result["field_coverage_not_applicable"]=q("select count(*) from card_field_coverage where coverage_status='not_applicable'")
result["field_coverage_missing"]=q("select count(*) from card_field_coverage where coverage_status='missing_on_card'")
result["field_coverage_payload_mismatches"]=q("select count(*) from card_field_coverage where source_payload_match<>1")
result["field_coverage_complete"]=(
 result["field_coverage_rows"]==target*55 and result["field_coverage_missing"]==0 and
 result["field_coverage_payload_mismatches"]==0
)
result["effect_interpretation_rows"]=q("select count(*) from card_effect_interpretations")
result["effect_clause_rows"]=q("select count(*) from card_effect_clauses")
result["effect_interpretation_missing"]=q("select count(*) from card_effect_clauses cl left join card_effect_interpretations i on i.clause_id=cl.clause_id where i.clause_id is null")
result["effect_interpretation_low_confidence"]=q("select count(*) from card_effect_interpretations where confidence='low'")
result["inferred_skill_card_rows"]=q("select count(*) from card_rule_mappings where mapping_status='inferred'")
result["unmapped_skill_card_rows_after_inference"]=q("select count(*) from card_rule_mappings where mapping_status='unmapped'")
result["inferred_skill_name_only_rows"]=q("select count(*) from game_rule_catalog where source_authority='inferred' and confidence='low'")
result["effect_text_accounted_for"]=result["effect_rows"]==result["effect_source_text_rows"] and result["effect_rows_without_text"]==0 and result["effect_source_mismatches"]==0
result["cost_parse_accounted_for"]=result["soul_cost_fully_parsed"]+result["soul_cost_needs_review"]==target
result["skill_mapping_coverage_accounted_for"]=result["skill_mapping_coverage_accounted_for"] and result["skill_mapping_rows"]>0
result["source_snapshot_integrity_pass"]=(
 result["firestore_source_count"]==target and result["unique_cards"]==target and
 result["duplicate_ids"]==0 and result["missing_names"]==0 and
 result["missing_individual_urls"]==0 and result["missing_list_urls"]==0 and
 result["distinct_source_fields"]==55 and result["taxonomy_rows"]>0 and
 result["cards_with_textbase"]==target and result["cards_with_textextra"]==target and
 result["cards_with_image_urls"]==target and result["image_rows_in_db"]==target*2 and
 result["large_image_manifest_rows"]==target and result["small_image_manifest_rows"]==target and
 result["large_images_downloaded"]==target and result["small_images_downloaded"]==target and
 result["large_image_failures"]==0 and result["small_image_failures"]==0 and
 result["lp_known_cards"]==289 and result["lp_zero_cards"]==72 and
 result["cost_parse_accounted_for"] and result["skill_mapping_coverage_accounted_for"] and result["effect_text_accounted_for"] and result["crawl_complete"] is True
)
result["semantic_completeness_pass"]=(
 result["field_coverage_complete"] and
 result["soul_cost_needs_review"]==0 and result["soul_cost_tokens"]>0 and
 result["skill_unmapped_rows"]==0 and result["skill_inventory_unmapped_values"]==0 and
 result["unmapped_skill_card_rows_after_inference"]==0 and
 result["effect_interpretation_rows"]==result["effect_clause_rows"] and
 result["effect_interpretation_missing"]==0
)
result["complete"]=result["source_snapshot_integrity_pass"] and result["semantic_completeness_pass"]
Path("data/audit-report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2));c.close();sys.exit(0 if result["source_snapshot_integrity_pass"] else 2)
