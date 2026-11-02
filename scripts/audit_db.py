#!/usr/bin/env python3
import sqlite3,json,sys
from pathlib import Path
db=Path("data/fm1_cards.sqlite")
target=15350
if not db.exists():
    print("DB missing"); sys.exit(2)
c=sqlite3.connect(db)
q=lambda s:c.execute(s).fetchone()[0]
result={
 "target_cards":target,
 "unique_cards":q("select count(*) from cards"),
 "duplicate_ids":q("select count(*) from (select card_id from cards group by card_id having count(*)>1)"),
 "missing_names":q("select count(*) from cards where trim(name)='' or name is null"),
 "missing_list_urls":q("select count(*) from cards where source_list_url is null or source_list_url=''"),
 "missing_detail_urls":q("select count(*) from cards where source_card_url is null or source_card_url=''"),
 "cards_with_images":q("select count(distinct card_id) from card_images where source_url is not null and source_url<>''"),
 "unverified_cards":q("select count(*) from cards where verification_status<>'manual_verified'"),
 "taxonomy_keys":q("select count(distinct field_key) from taxonomy"),
 "field_rows":q("select count(*) from card_fields"),
 "complete":q("select count(*) from cards")==target and q("select count(*) from cards where trim(name)='' or name is null")==0
}
Path("data").mkdir(exist_ok=True)
Path("data/audit-report.json").write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding="utf-8")
print(json.dumps(result,ensure_ascii=False,indent=2))
sys.exit(0 if result["complete"] else 2)
