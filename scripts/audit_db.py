#!/usr/bin/env python3
import json,sqlite3,sys
from pathlib import Path
target=15350;db=Path("data/fm1_cards.sqlite")
if not db.exists():raise SystemExit("DB missing")
c=sqlite3.connect(db);q=lambda s:c.execute(s).fetchone()[0]
manifest=Path("data/raw/image-manifest.jsonl");images=[]
if manifest.exists():
 with manifest.open(encoding="utf-8") as f:images=[json.loads(x) for x in f if x.strip()]
crawl_path=Path("data/raw/crawl-summary.json");crawl=json.loads(crawl_path.read_text()) if crawl_path.exists() else {}
large=[x for x in images if x.get("image_type")=="large"];small=[x for x in images if x.get("image_type")=="small"]
result={"required_cards":target,"firestore_source_count":crawl.get("source_count"),"unique_cards":q("select count(*) from cards"),"duplicate_ids":q("select count(*) from (select card_id from cards group by card_id having count(*)>1)"),"missing_names":q("select count(*) from cards where name is null or trim(name)=''"),"missing_individual_urls":q("select count(*) from cards where source_card_url is null or source_card_url=''"),"missing_list_urls":q("select count(*) from cards where source_list_url is null or source_list_url=''"),"card_field_rows":q("select count(*) from card_fields"),"distinct_source_fields":q("select count(distinct field_key) from card_fields"),"taxonomy_rows":q("select count(*) from taxonomy"),"cards_with_text":q("select count(distinct card_id) from card_texts"),"cards_with_image_urls":q("select count(distinct card_id) from card_images where source_url is not null and source_url<>''"),"large_images_downloaded":sum(x.get("status")=="downloaded" for x in large),"small_images_downloaded":sum(x.get("status")=="downloaded" for x in small),"large_image_failures":sum(x.get("status")!="downloaded" for x in large),"small_image_failures":sum(x.get("status")!="downloaded" for x in small),"large_image_manifest_rows":len(large),"small_image_manifest_rows":len(small),"crawl_complete":crawl.get("complete",False),"complete":False}
result["complete"]=(result["firestore_source_count"]==target and result["unique_cards"]==target and result["duplicate_ids"]==0 and result["missing_names"]==0 and result["missing_individual_urls"]==0 and result["missing_list_urls"]==0 and result["large_image_manifest_rows"]==target and result["small_image_manifest_rows"]==target and result["large_images_downloaded"]==target and result["small_images_downloaded"]==target and result["large_image_failures"]==0 and result["small_image_failures"]==0 and result["crawl_complete"] is True)
Path("data/audit-report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8");print(json.dumps(result,ensure_ascii=False,indent=2));c.close();sys.exit(0 if result["complete"] else 2)
