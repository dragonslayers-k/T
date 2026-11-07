#!/usr/bin/env python3
import json,sqlite3,hashlib,re,html,sys
from pathlib import Path
from datetime import datetime,timezone
from soul_costs import parse_require_soul
ROOT=Path("data");RAW=ROOT/"raw"/"cards.jsonl";DB=ROOT/"fm1_cards.sqlite"
if not RAW.exists() and "--self-test" not in sys.argv:raise SystemExit("Missing Firestore cards.jsonl")
def j(v):return json.dumps(v,ensure_ascii=False,sort_keys=True)
def rows_of(v):return v if isinstance(v,list) else list(v.values()) if isinstance(v,dict) else []
enum_path=ROOT/"raw"/"enumtable.json";enum=json.loads(enum_path.read_text(encoding="utf-8")) if enum_path.exists() else {}
enum_lookup={}
for key,raw_values in enum.items():
 if not key.startswith("Enum+"):continue
 name=key.split("+",1)[1];lookup={}
 for row in rows_of(raw_values):
  if isinstance(row,list) and len(row)>=2:
   label=row[2] if len(row)>2 and isinstance(row[2],str) else row[1];lookup[str(row[0])]=label
  elif isinstance(row,dict) and row.get("KIND") is not None:lookup[str(row["KIND"])]=row.get("UIName") or row.get("TYPE")
 enum_lookup[name]=lookup
FIELD_ENUM={"Category":"Category","RaceType":"RaceType","SoulType":"SoulType","RareType":"RareType","RareUI":"RareUI","Episode":"Episode","DeckLimit":"DeckLimit","BuyGrade":"BuyGrade","CompanyType":"CompanyType","EtcType":"EtcType","UnitType":"UnitType","Skill1":"Skill1","Skill2":"Skill2","TurnType":"TurnType","DurationType":"DurationType","RequireLP":"RequireLP","CardUISoul":"CardUISoul","EnchantSlot":"EnchantSlot","RankType":"RankType","CoinOption":"CoinOption","CoinType":"CoinType","CoinCount":"CoinCount","StatType":"StatType","StatValue":"StatValue","MuSoul":"MuSoul","NameCount":"NameCount","ProbOption":"ProbOption","EarnSoul":"EarnSoul","LV":"LV","ATKStatType":"StatType","DEFStatType":"StatType","HPStatType":"StatType","ATKCoinType":"CoinType","DEFCoinType":"CoinType","HPCoinType":"CoinType","ATKCoinCount":"CoinCount","DEFCoinCount":"CoinCount","HPCoinCount":"CoinCount"}
def norm(k,v):
 en=FIELD_ENUM.get(k)
 if en and en in enum_lookup and isinstance(v,(int,float,str)):return enum_lookup[en].get(str(v))
 if k=="ReleaseDate" and isinstance(v,int) and len(str(v))==8:
  s=str(v);return f"{s[:4]}-{s[4:6]}-{s[6:]}"
 if isinstance(v,(str,int,float,bool)):return str(v)
 return None
MANUAL_STATUS={
 "Category":"current_taxonomy_verified","SoulType":"manual_semantics_verified","RequireLP":"manual_semantics_verified",
 "RequireSoul":"manual_partial","UnitType":"manual_partial","Skill1":"manual_partial","Skill2":"manual_partial",
 "CoinType":"manual_semantics_verified","CoinCount":"manual_semantics_verified","StatType":"manual_semantics_verified",
 "StatValue":"manual_semantics_verified","TurnType":"manual_semantics_verified","DurationType":"manual_semantics_verified",
 "EnchantSlot":"site_enum_only","RaceType":"site_enum_only","CompanyType":"site_enum_only","EtcType":"site_enum_only",
 "RareType":"site_enum_only","RareUI":"site_enum_only","Episode":"site_enum_only","DeckLimit":"manual_partial",
 "BuyGrade":"site_enum_only","CardUISoul":"site_enum_only","LV":"site_enum_only","RankType":"site_enum_only",
 "MuSoul":"site_enum_only","NameCount":"site_enum_only","ProbOption":"site_enum_only","EarnSoul":"site_enum_only"
}
soul_rows=rows_of(enum.get("Enum+RequireSoul",{}));soul_meta={}
for row in soul_rows:
 if isinstance(row,list) and len(row)>=3:soul_meta[int(row[0])]={"symbol":row[1],"icon":row[2]}
def parse_soul(raw):
 return parse_require_soul(raw, soul_meta)

if "--self-test" in sys.argv:
 sample=parse_soul("43017101")
 assert sample["known"] and sample["mapping_review"]
 assert sample["colors"]["forest"]==0 and sample["colors"]["light"]==1
 assert sample["tokens"][0]["components"]==["forest","light"]
 assert parse_soul("5101")["colors"]["iron"]==1
 mu=parse_soul("8101")
 assert mu["known"] and mu["colors"]["neutral"]==1
 ncs=parse_soul("8201")
 assert ncs["known"] and ncs["semantic_review"] and ncs["colors"]["ncs"]==1
 assert ncs["tokens"][0]["status"]=="semantic_review"
 bonus=parse_soul("8301")
 assert bonus["known"] and bonus["semantic_review"] and bonus["colors"]["bonus"]==1
 assert bonus["tokens"][0]["status"]=="semantic_review"
 assert parse_soul("0100")["known"] and not parse_soul("0101")["known"]
 assert not parse_soul("9901")["known"] and not parse_soul("")["known"]
 print("SQLite builder RequireSoul self-test passed")
 raise SystemExit(0)
def plain_text(value):
 value=html.unescape(value or "")
 value=re.sub(r"(?i)<br\s*/?>","\n",value)
 value=re.sub(r"<[^>]+>","",value)
 return re.sub(r"\n{3,}","\n\n",value).strip()
if DB.exists():DB.unlink()
con=sqlite3.connect(DB)
con.executescript("""
PRAGMA foreign_keys=ON;
CREATE TABLE cards(card_id TEXT PRIMARY KEY,name TEXT NOT NULL,card_type TEXT,attribute TEXT,source_list_url TEXT NOT NULL,source_card_url TEXT,detail_url_status TEXT,raw_payload_json TEXT NOT NULL,content_hash TEXT,collected_at TEXT,verification_status TEXT NOT NULL DEFAULT 'extracted_unverified');
CREATE TABLE card_fields(field_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),field_key TEXT NOT NULL,source_value_json TEXT,normalized_value TEXT,source_location TEXT,verification_status TEXT DEFAULT 'extracted_unverified',UNIQUE(card_id,field_key,source_location));
CREATE TABLE card_texts(text_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),text_type TEXT NOT NULL,source_text TEXT NOT NULL,plain_text TEXT,source_location TEXT);
CREATE TABLE card_costs(card_id TEXT PRIMARY KEY REFERENCES cards(card_id),lp_value REAL,lp_known INTEGER NOT NULL DEFAULT 0,soul_json TEXT,soul_known INTEGER NOT NULL DEFAULT 0,semantic_review INTEGER NOT NULL DEFAULT 0,mapping_review INTEGER NOT NULL DEFAULT 0,source_text TEXT,verification_status TEXT DEFAULT 'extracted_unverified');
CREATE TABLE card_soul_cost_tokens(token_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),ordinal INTEGER NOT NULL,raw_token TEXT NOT NULL,code INTEGER,count INTEGER,symbol TEXT,icon_path TEXT,normalized_color TEXT,parse_status TEXT NOT NULL);
CREATE TABLE card_images(image_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),image_type TEXT NOT NULL,source_url TEXT,local_path TEXT,archive_path TEXT,mime_type TEXT,byte_size INTEGER,sha256 TEXT,download_status TEXT DEFAULT 'pending');
CREATE TABLE card_effects(effect_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),effect_index INTEGER NOT NULL,source_key TEXT NOT NULL,effect_text TEXT NOT NULL,trigger_text TEXT,target_text TEXT,condition_text TEXT,duration_text TEXT,verification_status TEXT DEFAULT 'extracted_unverified');
CREATE TABLE source_pages(page_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),page_type TEXT NOT NULL,url TEXT NOT NULL,http_status INTEGER,collected_at TEXT,content_hash TEXT,UNIQUE(card_id,page_type,url));
CREATE TABLE taxonomy(taxonomy_id INTEGER PRIMARY KEY,field_key TEXT NOT NULL,source_value_json TEXT,normalized_value TEXT,manual_mapping_status TEXT DEFAULT 'unmapped',UNIQUE(field_key,source_value_json));
CREATE TABLE verification(verification_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),field_key TEXT,status TEXT NOT NULL,evidence TEXT,verified_by TEXT,verified_at TEXT);
CREATE INDEX idx_cards_name ON cards(name);CREATE INDEX idx_cards_type ON cards(card_type);CREATE INDEX idx_fields_key ON card_fields(field_key);CREATE INDEX idx_fields_value ON card_fields(normalized_value);CREATE INDEX idx_images_card ON card_images(card_id);CREATE INDEX idx_soul_token_code ON card_soul_cost_tokens(code);
""")
con.execute("CREATE VIRTUAL TABLE card_search USING fts5(card_id UNINDEXED,name,card_type,attribute,card_text,additional_text,tokenize='unicode61')")
processed=0
with RAW.open(encoding="utf-8") as f,con:
 for line in f:
  if not line.strip():continue
  r=json.loads(line);obj=r.get("raw_payload") or {};cid=str(r.get("card_id") or "");name=str(r.get("name") or obj.get("Name") or "")
  if not cid or not name:continue
  raw_json=j(obj);digest=hashlib.sha256(raw_json.encode()).hexdigest();detail=r.get("source_card_url");collected=r.get("collected_at") or datetime.now(timezone.utc).isoformat()
  con.execute("INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?)",(cid,name,norm("Category",obj.get("Category")) or str(obj.get("Category","")),norm("SoulType",obj.get("SoulType")) or str(obj.get("SoulType","")),r.get("source_list_url") or "https://fmlunatic.com/cardlist",detail,"source_url_present" if detail else "missing",raw_json,digest,collected,"extracted_unverified"))
  for k,v in obj.items():
   if v is None:continue
   con.execute("INSERT INTO card_fields(card_id,field_key,source_value_json,normalized_value,source_location) VALUES(?,?,?,?,?)",(cid,str(k),j(v),norm(k,v),"firestore"))
  for k,typ in [("TextBase","card_text"),("TextExtra","additional_text")]:
   v=obj.get(k)
   if isinstance(v,str) and v:con.execute("INSERT INTO card_texts(card_id,text_type,source_text,plain_text,source_location) VALUES(?,?,?,?,?)",(cid,typ,v,plain_text(v),"Firestore"))
  # Preserve base and supplementary card text as separate effect-source records.
  # This is source extraction only; it must not be interpreted as executable rules.
  effect_index=0
  for source_key in ("TextBase","TextExtra"):
   source_value=obj.get(source_key)
   if isinstance(source_value,str) and source_value.strip():
    clean_effect=plain_text(source_value)
    if clean_effect:
     con.execute("INSERT INTO card_effects(card_id,effect_index,source_key,effect_text,trigger_text,target_text,condition_text,duration_text,verification_status) VALUES(?,?,?,?,?,?,?,?,?)",
      (cid,effect_index,source_key,clean_effect,norm("TurnType",obj.get("TurnType")) if source_key=="TextBase" else None,None,None,str(obj.get("Duration")) if obj.get("Duration") is not None else None,"extracted_unverified"))
     effect_index+=1
  lp=obj.get("RequireLP");lp_known=isinstance(lp,(int,float)) and norm("RequireLP",lp) is not None;soul=parse_soul(obj.get("RequireSoul"))
  cost_status=("manual_review" if not soul["known"] else ("mapping_review" if soul["mapping_review"] else ("semantic_review" if soul["semantic_review"] else "enum_decoded")))
  con.execute("INSERT INTO card_costs(card_id,lp_value,lp_known,soul_json,soul_known,semantic_review,mapping_review,source_text,verification_status) VALUES(?,?,?,?,?,?,?,?,?)",(cid,float(lp) if lp_known else None,1 if lp_known else 0,j(soul),1 if soul["known"] else 0,1 if soul["semantic_review"] else 0,1 if soul["mapping_review"] else 0,str(obj.get("RequireSoul")) if obj.get("RequireSoul") is not None else None,cost_status))
  for ordinal,t in enumerate(soul["tokens"]):
   con.execute("INSERT INTO card_soul_cost_tokens(card_id,ordinal,raw_token,code,count,symbol,icon_path,normalized_color,parse_status) VALUES(?,?,?,?,?,?,?,?,?)",(cid,ordinal,t["raw"],t["code"],t["count"],t["symbol"],t["icon"],t["normalized_color"],t["status"]))
  con.execute("INSERT INTO verification(card_id,field_key,status,evidence) VALUES(?,?,?,?)",(cid,"RequireSoul",cost_status,j(soul["tokens"])))
  for typ,url in (r.get("source_image_urls") or {}).items():
   if url:con.execute("INSERT INTO card_images(card_id,image_type,source_url) VALUES(?,?,?)",(cid,typ,url))
  for typ,url in [("detail",detail),("list",r.get("source_list_url") or "https://fmlunatic.com/cardlist")]:
   if url:con.execute("INSERT OR IGNORE INTO source_pages(card_id,page_type,url,collected_at) VALUES(?,?,?,?)",(cid,typ,url,collected))
  processed+=1
con.execute("""WITH text_by_card AS (
 SELECT card_id,
  group_concat(CASE WHEN text_type='card_text' THEN plain_text END,' ') AS card_text,
  group_concat(CASE WHEN text_type='additional_text' THEN plain_text END,' ') AS additional_text
 FROM card_texts GROUP BY card_id
)
INSERT INTO card_search(card_id,name,card_type,attribute,card_text,additional_text)
SELECT c.card_id,c.name,coalesce(c.card_type,''),coalesce(c.attribute,''),
 coalesce(t.card_text,''),coalesce(t.additional_text,'')
FROM cards c LEFT JOIN text_by_card t ON t.card_id=c.card_id""")
manifest=ROOT/"raw"/"image-manifest.jsonl"
if manifest.exists():
 with manifest.open(encoding="utf-8") as f,con:
  for line in f:
   if not line.strip():continue
   x=json.loads(line)
   image_status=x.get("status")
   con.execute("UPDATE card_images SET local_path=?,archive_path=?,mime_type=?,byte_size=?,sha256=?,download_status=? WHERE card_id=? AND image_type=?",(x.get("local_path"),x.get("archive_path"),"image/webp" if image_status in ("downloaded","verified") else x.get("mime_type"),x.get("byte_size"),x.get("sha256"),"archive_verified" if image_status=="verified" else image_status,x["card_id"],x["image_type"]))
with con:
 for key,raw_values in enum.items():
  values=rows_of(raw_values);field_key=key.split("+",1)[-1] if key.startswith(("Enum+","Column+")) else key
  for item in values:
   if isinstance(item,dict):label=item.get("UIName") or item.get("TYPE")
   elif isinstance(item,list):label=item[2] if len(item)>2 and isinstance(item[2],str) else (item[1] if len(item)>1 else None)
   else:label=None
   status=MANUAL_STATUS.get(field_key,"site_enum_only" if key.startswith("Enum+") else "site_ui_metadata")
   con.execute("INSERT OR IGNORE INTO taxonomy(field_key,source_value_json,normalized_value,manual_mapping_status) VALUES(?,?,?,?)",(field_key,j(item),label,status))
print(json.dumps({"database":str(DB),"rows_processed":processed,"unique_cards":con.execute("select count(*) from cards").fetchone()[0],"fields":con.execute("select count(*) from card_fields").fetchone()[0],"taxonomy":con.execute("select count(*) from taxonomy").fetchone()[0],"images":con.execute("select count(*) from card_images").fetchone()[0],"archive_verified_images":con.execute("select count(*) from card_images where download_status='archive_verified'").fetchone()[0],"soul_cost_fully_parsed":con.execute("select count(*) from card_costs where soul_known=1").fetchone()[0],"soul_cost_needs_review":con.execute("select count(*) from card_costs where soul_known=0").fetchone()[0],"mapping_review":con.execute("select count(*) from card_costs where mapping_review=1").fetchone()[0],"semantic_review":con.execute("select count(*) from card_costs where semantic_review=1").fetchone()[0],"soul_tokens":con.execute("select count(*) from card_soul_cost_tokens").fetchone()[0],"search_index_rows":con.execute("select count(*) from card_search").fetchone()[0]},ensure_ascii=False))
con.close()
