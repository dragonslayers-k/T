#!/usr/bin/env python3
import json,sqlite3,hashlib
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path("data");RAW=ROOT/"raw"/"cards.jsonl";DB=ROOT/"fm1_cards.sqlite"
if not RAW.exists():raise SystemExit("Missing Firestore cards.jsonl")
def j(v):return json.dumps(v,ensure_ascii=False,sort_keys=True)
if DB.exists():DB.unlink()
con=sqlite3.connect(DB)
con.executescript("""
PRAGMA foreign_keys=ON;
CREATE TABLE cards(card_id TEXT PRIMARY KEY,name TEXT NOT NULL,card_type TEXT,attribute TEXT,source_list_url TEXT NOT NULL,source_card_url TEXT,detail_url_status TEXT,raw_payload_json TEXT NOT NULL,content_hash TEXT,collected_at TEXT,verification_status TEXT NOT NULL DEFAULT 'extracted_unverified');
CREATE TABLE card_fields(field_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),field_key TEXT NOT NULL,source_value_json TEXT,normalized_value TEXT,source_location TEXT,verification_status TEXT DEFAULT 'extracted_unverified',UNIQUE(card_id,field_key,source_location));
CREATE TABLE card_texts(text_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),text_type TEXT NOT NULL,source_text TEXT NOT NULL,source_location TEXT);
CREATE TABLE card_costs(card_id TEXT PRIMARY KEY REFERENCES cards(card_id),lp_value REAL,lp_known INTEGER NOT NULL DEFAULT 0,soul_json TEXT,soul_known INTEGER NOT NULL DEFAULT 0,source_text TEXT,verification_status TEXT DEFAULT 'extracted_unverified');
CREATE TABLE card_images(image_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),image_type TEXT NOT NULL,source_url TEXT,local_path TEXT,mime_type TEXT,byte_size INTEGER,sha256 TEXT,download_status TEXT DEFAULT 'pending');
CREATE TABLE card_effects(effect_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),effect_index INTEGER NOT NULL,effect_text TEXT NOT NULL,trigger_text TEXT,target_text TEXT,condition_text TEXT,duration_text TEXT,verification_status TEXT DEFAULT 'extracted_unverified');
CREATE TABLE source_pages(page_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),page_type TEXT NOT NULL,url TEXT NOT NULL,http_status INTEGER,collected_at TEXT,content_hash TEXT,UNIQUE(card_id,page_type,url));
CREATE TABLE taxonomy(taxonomy_id INTEGER PRIMARY KEY,field_key TEXT NOT NULL,source_value_json TEXT,normalized_value TEXT,manual_mapping_status TEXT DEFAULT 'unmapped',UNIQUE(field_key,source_value_json));
CREATE TABLE verification(verification_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),field_key TEXT,status TEXT NOT NULL,evidence TEXT,verified_by TEXT,verified_at TEXT);
CREATE INDEX idx_cards_name ON cards(name);CREATE INDEX idx_cards_type ON cards(card_type);CREATE INDEX idx_fields_key ON card_fields(field_key);CREATE INDEX idx_fields_value ON card_fields(normalized_value);CREATE INDEX idx_images_card ON card_images(card_id);
""")
processed=0
with RAW.open(encoding="utf-8") as f,con:
 for line in f:
  if not line.strip():continue
  r=json.loads(line);obj=r.get("raw_payload") or {};cid=str(r.get("card_id") or "");name=str(r.get("name") or obj.get("Name") or "")
  if not cid or not name:continue
  raw_json=j(obj);digest=hashlib.sha256(raw_json.encode()).hexdigest();detail=r.get("source_card_url");collected=r.get("collected_at") or datetime.now(timezone.utc).isoformat()
  con.execute("INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?)",(cid,name,str(obj.get("Category","")),str(obj.get("SoulType","")),r.get("source_list_url") or "https://fmlunatic.com/cardlist",detail,"constructed_from_verified_site_route" if detail else "missing",raw_json,digest,collected,"extracted_unverified"))
  for k,v in obj.items():
   if v is None:continue
   norm=str(v) if isinstance(v,(str,int,float,bool)) else None
   con.execute("INSERT INTO card_fields(card_id,field_key,source_value_json,normalized_value,source_location) VALUES(?,?,?,?,?)",(cid,str(k),j(v),norm,"firestore"))
  for k,typ in [("TextBase","card_text"),("TextExtra","additional_text")]:
   v=obj.get(k)
   if isinstance(v,str) and v:con.execute("INSERT INTO card_texts(card_id,text_type,source_text,source_location) VALUES(?,?,?,?)",(cid,typ,v,"Firestore"))
  if isinstance(obj.get("TextBase"),str) and obj["TextBase"]:
   con.execute("INSERT INTO card_effects(card_id,effect_index,effect_text,trigger_text,duration_text) VALUES(?,?,?,?,?)",(cid,0,obj["TextBase"],str(obj.get("TurnType")) if obj.get("TurnType") is not None else None,str(obj.get("Duration")) if obj.get("Duration") is not None else None))
  con.execute("INSERT INTO card_costs(card_id,soul_json,source_text) VALUES(?,?,?)",(cid,j(obj.get("RequireSoul")) if obj.get("RequireSoul") is not None else None,str(obj.get("RequireSoul")) if obj.get("RequireSoul") is not None else None))
  for typ,url in (r.get("source_image_urls") or {}).items():
   if url:con.execute("INSERT INTO card_images(card_id,image_type,source_url) VALUES(?,?,?)",(cid,typ,url))
  for typ,url in [("detail",detail),("list",r.get("source_list_url") or "https://fmlunatic.com/cardlist")]:
   if url:con.execute("INSERT OR IGNORE INTO source_pages(card_id,page_type,url,collected_at) VALUES(?,?,?,?)",(cid,typ,url,collected))
  processed+=1
manifest=ROOT/"raw"/"image-manifest.jsonl"
if manifest.exists():
 with manifest.open(encoding="utf-8") as f,con:
  for line in f:
   if not line.strip():continue
   x=json.loads(line)
   con.execute("UPDATE card_images SET local_path=?,mime_type=?,byte_size=?,sha256=?,download_status=? WHERE card_id=? AND image_type=?",(x.get("local_path"),"image/webp" if x.get("status")=="downloaded" else None,x.get("byte_size"),x.get("sha256"),x.get("status"),x["card_id"],x["image_type"]))
enum_path=ROOT/"raw"/"enumtable.json"
if enum_path.exists():
 enum=json.loads(enum_path.read_text(encoding="utf-8"))
 with con:
  for key,raw_values in enum.items():
   values=raw_values if isinstance(raw_values,list) else list(raw_values.values()) if isinstance(raw_values,dict) else []
   field_key=key.split("+",1)[-1] if "+" in key else key
   for item in values:
    label=item.get("UIName") if isinstance(item,dict) else (item[2] if isinstance(item,list) and len(item)>2 and isinstance(item[2],str) else None)
    con.execute("INSERT OR IGNORE INTO taxonomy(field_key,source_value_json,normalized_value) VALUES(?,?,?)",(field_key,j(item),label))
print(json.dumps({"database":str(DB),"rows_processed":processed,"unique_cards":con.execute("select count(*) from cards").fetchone()[0],"fields":con.execute("select count(*) from card_fields").fetchone()[0],"taxonomy":con.execute("select count(*) from taxonomy").fetchone()[0],"images":con.execute("select count(*) from card_images").fetchone()[0]},ensure_ascii=False))
con.close()
