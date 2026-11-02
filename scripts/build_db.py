#!/usr/bin/env python3
import json,sqlite3,hashlib,re,html
from pathlib import Path
from datetime import datetime,timezone
ROOT=Path("data");RAW=ROOT/"raw"/"cards.jsonl";DB=ROOT/"fm1_cards.sqlite"
if not RAW.exists():raise SystemExit("Missing Firestore cards.jsonl")
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
soul_rows=rows_of(enum.get("Enum+RequireSoul",{}));soul_meta={}
for row in soul_rows:
 if isinstance(row,list) and len(row)>=3:soul_meta[int(row[0])]={"symbol":row[1],"icon":row[2]}
PURE_SOUL={11:"dark",21:"fire",31:"water",41:"forest",51:"iron",61:"earth",71:"light",81:"neutral",1:"none"}
def parse_soul(raw):
 result={"raw":raw,"tokens":[],"colors":{"dark":0,"fire":0,"earth":0,"water":0,"forest":0,"iron":0,"light":0,"neutral":0},"known":False}
 if not isinstance(raw,str) or len(raw)%4:return result
 known=True
 for i in range(0,len(raw),4):
  token=raw[i:i+4]
  if not token.isdigit():known=False;continue
  code,count=int(token[:2]),int(token[2:]);meta=soul_meta.get(code,{})
  color=PURE_SOUL.get(code);status="mapped" if color else "manual_review"
  if color=="none" and count==0:status="no_cost"
  elif color:result["colors"][color]+=count
  else:known=False
  result["tokens"].append({"raw":token,"code":code,"count":count,"symbol":meta.get("symbol"),"icon":meta.get("icon"),"normalized_color":color,"status":status})
 result["known"]=known
 return result
def plain_text(value):
 value=html.unescape(value or "")
 value=re.sub(r"(?i)<br\\s*/?>","\\n",value)
 value=re.sub(r"<[^>]+>","",value)
 return re.sub(r"\\n{3,}","\\n\\n",value).strip()
if DB.exists():DB.unlink()
con=sqlite3.connect(DB)
con.executescript("""
PRAGMA foreign_keys=ON;
CREATE TABLE cards(card_id TEXT PRIMARY KEY,name TEXT NOT NULL,card_type TEXT,attribute TEXT,source_list_url TEXT NOT NULL,source_card_url TEXT,detail_url_status TEXT,raw_payload_json TEXT NOT NULL,content_hash TEXT,collected_at TEXT,verification_status TEXT NOT NULL DEFAULT 'extracted_unverified');
CREATE TABLE card_fields(field_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),field_key TEXT NOT NULL,source_value_json TEXT,normalized_value TEXT,source_location TEXT,verification_status TEXT DEFAULT 'extracted_unverified',UNIQUE(card_id,field_key,source_location));
CREATE TABLE card_texts(text_id INTEGER PRIMARY KEY,card_id TEXT NOT NULL REFERENCES cards(card_id),text_type TEXT NOT NULL,source_text TEXT NOT NULL,plain_text TEXT,source_location TEXT);
CREATE TABLE card_costs(card_id TEXT PRIMARY KEY REFERENCES cards(card_id),lp_value REAL,lp_known INTEGER NOT NULL DEFAULT 0,soul_json TEXT,soul_known INTEGER NOT NULL DEFAULT 0,source_text TEXT,verification_status TEXT DEFAULT 'extracted_unverified');
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
  con.execute("INSERT INTO card_costs(card_id,lp_value,lp_known,soul_json,soul_known,source_text) VALUES(?,?,?,?,?,?)",(cid,float(lp) if lp_known else None,1 if lp_known else 0,j(soul),1 if soul["known"] else 0,str(obj.get("RequireSoul")) if obj.get("RequireSoul") is not None else None))
  for ordinal,t in enumerate(soul["tokens"]):
   con.execute("INSERT INTO card_soul_cost_tokens(card_id,ordinal,raw_token,code,count,symbol,icon_path,normalized_color,parse_status) VALUES(?,?,?,?,?,?,?,?,?)",(cid,ordinal,t["raw"],t["code"],t["count"],t["symbol"],t["icon"],t["normalized_color"],t["status"]))
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
  values=rows_of(raw_values);field_key=key.split("+",1)[-1] if "+" in key else key
  for item in values:
   if isinstance(item,dict):label=item.get("UIName") or item.get("TYPE")
   elif isinstance(item,list):label=item[2] if len(item)>2 and isinstance(item[2],str) else (item[1] if len(item)>1 else None)
   else:label=None
   con.execute("INSERT OR IGNORE INTO taxonomy(field_key,source_value_json,normalized_value) VALUES(?,?,?)",(field_key,j(item),label))
print(json.dumps({"database":str(DB),"rows_processed":processed,"unique_cards":con.execute("select count(*) from cards").fetchone()[0],"fields":con.execute("select count(*) from card_fields").fetchone()[0],"taxonomy":con.execute("select count(*) from taxonomy").fetchone()[0],"images":con.execute("select count(*) from card_images").fetchone()[0],"soul_cost_fully_parsed":con.execute("select count(*) from card_costs where soul_known=1").fetchone()[0],"soul_cost_needs_review":con.execute("select count(*) from card_costs where soul_known=0").fetchone()[0]},ensure_ascii=False))
con.close()
