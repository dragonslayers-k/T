#!/usr/bin/env python3
import json, sqlite3, hashlib
from pathlib import Path
from datetime import datetime, timezone

ROOT = Path("data")
RAW = ROOT / "raw" / "cards.jsonl"
DB = ROOT / "fm1_cards.sqlite"
ROOT.mkdir(exist_ok=True)
schema = """
PRAGMA foreign_keys=ON;
CREATE TABLE IF NOT EXISTS cards (
 card_id TEXT PRIMARY KEY, name TEXT NOT NULL, card_type TEXT, attribute TEXT,
 source_list_url TEXT NOT NULL, source_card_url TEXT, detail_url_status TEXT,
 raw_payload_json TEXT NOT NULL, content_hash TEXT, collected_at TEXT,
 verification_status TEXT NOT NULL DEFAULT 'extracted_unverified'
);
CREATE TABLE IF NOT EXISTS card_fields (
 field_id INTEGER PRIMARY KEY, card_id TEXT NOT NULL REFERENCES cards(card_id),
 field_key TEXT NOT NULL, source_value_json TEXT, normalized_value TEXT,
 source_location TEXT, verification_status TEXT DEFAULT 'extracted_unverified',
 UNIQUE(card_id, field_key, source_location)
);
CREATE TABLE IF NOT EXISTS card_texts (
 text_id INTEGER PRIMARY KEY, card_id TEXT NOT NULL REFERENCES cards(card_id),
 text_type TEXT NOT NULL, source_text TEXT NOT NULL, source_location TEXT
);
CREATE TABLE IF NOT EXISTS card_costs (
 card_id TEXT PRIMARY KEY REFERENCES cards(card_id),
 lp_value REAL, lp_known INTEGER NOT NULL DEFAULT 0,
 soul_json TEXT, soul_known INTEGER NOT NULL DEFAULT 0,
 source_text TEXT, verification_status TEXT DEFAULT 'extracted_unverified'
);
CREATE TABLE IF NOT EXISTS card_images (
 image_id INTEGER PRIMARY KEY, card_id TEXT NOT NULL REFERENCES cards(card_id),
 image_type TEXT NOT NULL, source_url TEXT, local_path TEXT, mime_type TEXT,
 byte_size INTEGER, sha256 TEXT, download_status TEXT DEFAULT 'pending'
);
CREATE TABLE IF NOT EXISTS card_effects (
 effect_id INTEGER PRIMARY KEY, card_id TEXT NOT NULL REFERENCES cards(card_id),
 effect_index INTEGER NOT NULL, effect_text TEXT NOT NULL,
 trigger_text TEXT, target_text TEXT, condition_text TEXT, duration_text TEXT,
 verification_status TEXT DEFAULT 'extracted_unverified'
);
CREATE TABLE IF NOT EXISTS source_pages (
 page_id INTEGER PRIMARY KEY, card_id TEXT NOT NULL REFERENCES cards(card_id),
 page_type TEXT NOT NULL, url TEXT NOT NULL, http_status INTEGER,
 collected_at TEXT, content_hash TEXT, UNIQUE(card_id,page_type,url)
);
CREATE TABLE IF NOT EXISTS taxonomy (
 taxonomy_id INTEGER PRIMARY KEY, field_key TEXT NOT NULL, source_value_json TEXT,
 normalized_value TEXT, manual_mapping_status TEXT DEFAULT 'unmapped',
 UNIQUE(field_key,source_value_json)
);
CREATE TABLE IF NOT EXISTS verification (
 verification_id INTEGER PRIMARY KEY, card_id TEXT NOT NULL REFERENCES cards(card_id),
 field_key TEXT, status TEXT NOT NULL, evidence TEXT, verified_by TEXT, verified_at TEXT
);
CREATE INDEX IF NOT EXISTS idx_cards_name ON cards(name);
CREATE INDEX IF NOT EXISTS idx_cards_type ON cards(card_type);
CREATE INDEX IF NOT EXISTS idx_fields_key ON card_fields(field_key);
CREATE INDEX IF NOT EXISTS idx_fields_value ON card_fields(normalized_value);
"""
FIELD_SKIP = {"id","card_id","cardId","name","cardName","title","url","detailUrl","detail_url","href","image","imageUrl","artImage","thumbnail","thumbnailUrl","largeImage"}
TEXT_KEYS = {"text":"card_text","description":"description","flavorText":"flavor_text","flavor_text":"flavor_text","skill":"skill_text","unitAbility":"unit_ability"}
IMAGE_KEYS = {"artImage":"art","image":"original","imageUrl":"original","thumbnail":"thumbnail","thumbnailUrl":"thumbnail","largeImage":"large"}
def j(v): return json.dumps(v, ensure_ascii=False, sort_keys=True)
def first(d, keys):
    for k in keys:
        if d.get(k) is not None: return d[k]
    return None

if not RAW.exists():
    raise SystemExit("Missing data/raw/cards.jsonl; run the crawler first.")
if DB.exists(): DB.unlink()
con=sqlite3.connect(DB)
con.executescript(schema)
processed=0
with RAW.open(encoding="utf-8") as f, con:
    for line in f:
        if not line.strip(): continue
        r=json.loads(line)
        raw=r.get("raw_payload") or {}
        obj=raw.get("object",r)
        if not isinstance(obj,dict): obj=r
        cid=str(r.get("card_id") or obj.get("id") or "")
        name=str(r.get("name") or obj.get("name") or obj.get("cardName") or "")
        if not cid or not name: continue
        raw_json=j(raw); digest=hashlib.sha256(raw_json.encode()).hexdigest()
        source_url=r.get("source_card_url") or obj.get("url") or obj.get("detailUrl") or obj.get("href")
        collected=r.get("collected_at") or datetime.now(timezone.utc).isoformat()
        con.execute("""INSERT OR REPLACE INTO cards
          (card_id,name,card_type,attribute,source_list_url,source_card_url,detail_url_status,raw_payload_json,content_hash,collected_at,verification_status)
          VALUES(?,?,?,?,?,?,?,?,?,?,?)""",
          (cid,name,str(first(obj,["type","cardType","category"]) or ""),
           str(first(obj,["faction","attribute","element"]) or ""),
           r.get("source_list_url") or "https://fmlunatic.com/cardlist",source_url,
           "found" if source_url else "not_observed",raw_json,digest,collected,"extracted_unverified"))
        for k,v in obj.items():
            if k in FIELD_SKIP or v is None: continue
            con.execute("INSERT OR IGNORE INTO card_fields(card_id,field_key,source_value_json,normalized_value,source_location) VALUES(?,?,?,?,?)",
                        (cid,str(k),j(v),str(v) if isinstance(v,(str,int,float,bool)) else None,"json"))
            con.execute("INSERT OR IGNORE INTO taxonomy(field_key,source_value_json,normalized_value) VALUES(?,?,?)",
                        (str(k),j(v),str(v) if isinstance(v,(str,int,float,bool)) else None))
            if k in TEXT_KEYS and isinstance(v,str) and v:
                con.execute("INSERT INTO card_texts(card_id,text_type,source_text,source_location) VALUES(?,?,?,?)",
                            (cid,TEXT_KEYS[k],v,"json"))
            if k in IMAGE_KEYS and isinstance(v,str) and v:
                con.execute("INSERT INTO card_images(card_id,image_type,source_url) VALUES(?,?,?)",
                            (cid,IMAGE_KEYS[k],v))
        for typ,key in [("original","source_image_url"),("thumbnail","source_thumbnail_url"),("large","source_large_image_url")]:
            url=r.get(key)
            if url: con.execute("INSERT INTO card_images(card_id,image_type,source_url) VALUES(?,?,?)",(cid,typ,url))
        for typ,url in [("detail",source_url),("list",r.get("source_list_url") or "https://fmlunatic.com/cardlist")]:
            if url: con.execute("INSERT OR IGNORE INTO source_pages(card_id,page_type,url,collected_at) VALUES(?,?,?,?)",(cid,typ,url,collected))
        con.execute("INSERT OR IGNORE INTO card_costs(card_id) VALUES(?)",(cid,))
        processed+=1
print(json.dumps({"database":str(DB),"rows_processed":processed,"unique_cards":con.execute("select count(*) from cards").fetchone()[0]},ensure_ascii=False))
con.close()
