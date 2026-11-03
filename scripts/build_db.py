#!/usr/bin/env python3
import json,sqlite3,hashlib,re,html,sys
from pathlib import Path
from datetime import datetime,timezone
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
PURE_SOUL={11:"dark",21:"fire",31:"water",41:"forest",51:"iron",61:"earth",71:"light",81:"neutral",1:"none"}
HYBRID_SOUL={
 12:("dark","earth"),13:("dark","fire"),14:("dark","light"),15:("dark","water"),
 22:("fire","forest"),23:("fire","iron"),24:("fire","water"),32:("earth","water"),
 33:("forest","water"),42:("forest","iron"),43:("forest","light"),
 52:("earth","iron"),53:("iron","light"),62:("earth","light")
}
SPECIAL_SOUL={82:"ncs",83:"bonus"}
def parse_soul(raw):
 result={"raw":raw,"tokens":[],"colors":{"dark":0,"fire":0,"earth":0,"water":0,"forest":0,"iron":0,"light":0,"neutral":0,"ncs":0,"bonus":0},"known":False,"semantic_review":False}
 if not isinstance(raw,str) or len(raw)%4:return result
 known=True
 for i in range(0,len(raw),4):
  token=raw[i:i+4]
  if not token.isdigit():known=False;continue
  code,count=int(token[:2]),int(token[2:]);meta=soul_meta.get(code,{})
  color=PURE_SOUL.get(code);status="mapped" if color else "manual_review"
  if color=="none":
   if count==0:status="no_cost"
   else:known=False;status="manual_review"
  elif color:result["colors"][color]+=count
  elif code in HYBRID_SOUL:
   for hybrid_color in HYBRID_SOUL[code]:result["colors"][hybrid_color]+=count
   color="+".join(HYBRID_SOUL[code]);status="mapped_hybrid"
  elif code in SPECIAL_SOUL:
   color=SPECIAL_SOUL[code];result["colors"][color]+=count
   status="enum_special_token";result["semantic_review"]=True
  else:known=False
  result["tokens"].append({"raw":token,"code":code,"count":count,"symbol":meta.get("symbol"),"icon":meta.get("icon"),"normalized_color":color,"status":status})
 result["known"]=known
 return result
if "--self-test" in sys.argv:
 sample=parse_soul("43017101")
 assert sample["known"] and sample["colors"]["forest"]==1 and sample["colors"]["light"]==2
 assert parse_soul("32016101")["colors"]["earth"]==2
 assert parse_soul("82018101")["known"] and parse_soul("82018101")["colors"]["ncs"]==1
 assert parse_soul("8301")["known"] and parse_soul("8301")["colors"]["bonus"]==1
 assert parse_soul("0100")["known"]
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
CREATE TABLE card_costs(card_id TEXT PRIMARY KEY REFERENCES cards(card_id),lp_value REAL,lp_known INTEGER NOT NULL DEFAULT 0,soul_json TEXT,soul_known INTEGER NOT NULL DEFAULT 0,semantic_review INTEGER NOT NULL DEFAULT 0,source_text TEXT,verification_status TEXT DEFAULT 'extracted_unverified');
CREATE TABLE card_soul_cost_tokens(token_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),ordinal INTEGER NOT NULL,raw_token TEXT NOT NULL,code INTEGER,count INTEGER,symbol TEXT,icon_path TEXT,normalized_color TEXT,parse_status TEXT NOT NULL);
CREATE TABLE card_images(image_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),image_type TEXT NOT NULL,source_url TEXT,local_path TEXT,mime_type TEXT,byte_size INTEGER,sha256 TEXT,download_status TEXT DEFAULT 'pending');
CREATE TABLE card_effects(effect_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),effect_index INTEGER NOT NULL,effect_text TEXT NOT NULL,trigger_text TEXT,target_text TEXT,condition_text TEXT,duration_text TEXT,verification_status TEXT DEFAULT 'extracted_unverified');
CREATE TABLE source_pages(page_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),page_type TEXT NOT NULL,url TEXT NOT NULL,http_status INTEGER,collected_at TEXT,content_hash TEXT,UNIQUE(card_id,page_type,url));
CREATE TABLE taxonomy(taxonomy_id INTEGER PRIMARY KEY,field_key TEXT NOT NULL,source_value_json TEXT,normalized_value TEXT,manual_mapping_status TEXT DEFAULT 'unmapped',UNIQUE(field_key,source_value_json));
CREATE TABLE verification(verification_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),field_key TEXT,status TEXT NOT NULL,evidence TEXT,verified_by TEXT,verified_at TEXT);
CREATE INDEX idx_cards_name ON cards(name);CREATE INDEX idx_cards_type ON cards(card_type);CREATE INDEX idx_fields_key ON card_fields(field_key);CREATE INDEX idx_fields_value ON card_fields(normalized_value);CREATE INDEX idx_images_card ON card_images(card_id);CREATE INDEX idx_soul_token_code ON card_soul_cost_tokens(code);
""")
processed=0
with RAW.open(encoding="utf-8") as f,con:
 for line in f:
  if not line.strip():continue
  r=json.loads(line);obj=r.get("raw_payload") or {};cid=str(r.get("card_id") or "");name=str(r.get("name") or obj.get("Name") or "")
  if not cid or not name:continue
  raw_json=j(obj);digest=hashlib.sha256(raw_json.encode()).hexdigest();detail=r.get("source_card_url");collected=r.get("collected_at") or datetime.now(timezone.utc).isoformat()
  con.execute("INSERT INTO cards VALUES(?,?,?,?,?,?,?,?,?,?,?)",(cid,name,norm("Category",obj.get("Category")) or str(obj.get("Category","")),norm("SoulType",obj.get("SoulType")) or str(obj.get("SoulType","")),r.get("source_list_url") or "https://fmlunatic.com/cardlist",detail,"constructed_from_verified_site_route" if detail else "missing",raw_json,digest,collected,"extracted_unverified"))
  for k,v in obj.items():
   if v is None:continue
   con.execute("INSERT INTO card_fields(card_id,field_key,source_value_json,normalized_value,source_location) VALUES(?,?,?,?,?)",(cid,str(k),j(v),norm(k,v),"firestore"))
  for k,typ in [("TextBase","card_text"),("TextExtra","additional_text")]:
   v=obj.get(k)
   if isinstance(v,str) and v:con.execute("INSERT INTO card_texts(card_id,text_type,source_text,plain_text,source_location) VALUES(?,?,?,?,?)",(cid,typ,v,plain_text(v),"Firestore"))
  if isinstance(obj.get("TextBase"),str) and obj["TextBase"]:
   con.execute("INSERT INTO card_effects(card_id,effect_index,effect_text,trigger_text,duration_text) VALUES(?,?,?,?,?)",(cid,0,plain_text(obj["TextBase"]),norm("TurnType",obj.get("TurnType")),str(obj.get("Duration")) if obj.get("Duration") is not None else None))
  lp=obj.get("RequireLP");lp_known=isinstance(lp,(int,float)) and norm("RequireLP",lp) is not None;soul=parse_soul(obj.get("RequireSoul"))
  cost_status="manual_review" if not soul["known"] else ("semantic_review" if soul["semantic_review"] else ("source_cross_validated" if any(t["status"]=="mapped_hybrid" for t in soul["tokens"]) else "enum_decoded"))
  con.execute("INSERT INTO card_costs(card_id,lp_value,lp_known,soul_json,soul_known,semantic_review,source_text,verification_status) VALUES(?,?,?,?,?,?,?,?)",(cid,float(lp) if lp_known else None,1 if lp_known else 0,j(soul),1 if soul["known"] else 0,1 if soul["semantic_review"] else 0,str(obj.get("RequireSoul")) if obj.get("RequireSoul") is not None else None,cost_status))
  for ordinal,t in enumerate(soul["tokens"]):
   con.execute("INSERT INTO card_soul_cost_tokens(card_id,ordinal,raw_token,code,count,symbol,icon_path,normalized_color,parse_status) VALUES(?,?,?,?,?,?,?,?,?)",(cid,ordinal,t["raw"],t["code"],t["count"],t["symbol"],t["icon"],t["normalized_color"],t["status"]))
  con.execute("INSERT INTO verification(card_id,field_key,status,evidence) VALUES(?,?,?,?)",(cid,"RequireSoul",cost_status,j(soul["tokens"])))
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
with con:
 for key,raw_values in enum.items():
  values=rows_of(raw_values);field_key=key.split("+",1)[-1] if key.startswith(("Enum+","Column+")) else key
  for item in values:
   if isinstance(item,dict):label=item.get("UIName") or item.get("TYPE")
   elif isinstance(item,list):label=item[2] if len(item)>2 and isinstance(item[2],str) else (item[1] if len(item)>1 else None)
   else:label=None
   status=MANUAL_STATUS.get(field_key,"site_enum_only" if key.startswith("Enum+") else "site_ui_metadata")
   con.execute("INSERT OR IGNORE INTO taxonomy(field_key,source_value_json,normalized_value,manual_mapping_status) VALUES(?,?,?,?)",(field_key,j(item),label,status))
print(json.dumps({"database":str(DB),"rows_processed":processed,"unique_cards":con.execute("select count(*) from cards").fetchone()[0],"fields":con.execute("select count(*) from card_fields").fetchone()[0],"taxonomy":con.execute("select count(*) from taxonomy").fetchone()[0],"images":con.execute("select count(*) from card_images").fetchone()[0],"soul_cost_fully_parsed":con.execute("select count(*) from card_costs where soul_known=1").fetchone()[0],"soul_cost_needs_review":con.execute("select count(*) from card_costs where soul_known=0").fetchone()[0],"special_semantics_review":con.execute("select count(*) from card_costs where semantic_review=1").fetchone()[0],"soul_tokens":con.execute("select count(*) from card_soul_cost_tokens").fetchone()[0]},ensure_ascii=False))
con.close()
