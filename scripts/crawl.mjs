import { mkdir, readFile, appendFile, writeFile } from "node:fs/promises";

const PROJECT="fmdb-bcb70",DATABASE="(default)",COLLECTION="livecardlist";
const BASE=`https://firestore.googleapis.com/v1/projects/${PROJECT}/databases/${DATABASE}/documents`;
const TARGET=Number(process.env.EXPECTED_CARDS||15350),PAGE_SIZE=50;
const RAW_DIR="data/raw",STORAGE="https://storage.googleapis.com/fmdb-bcb70.appspot.com/";
await mkdir(RAW_DIR,{recursive:true});
let categoryMap=new Map();

function decode(v){
 if(!v||typeof v!=="object")return v;
 if("nullValue"in v)return null;
 if("stringValue"in v)return v.stringValue;
 if("booleanValue"in v)return v.booleanValue;
 if("integerValue"in v)return Number(v.integerValue);
 if("doubleValue"in v)return Number(v.doubleValue);
 if("timestampValue"in v)return v.timestampValue;
 if("referenceValue"in v)return v.referenceValue;
 if("bytesValue"in v)return v.bytesValue;
 if("geoPointValue"in v)return v.geoPointValue;
 if("arrayValue"in v)return(v.arrayValue.values||[]).map(decode);
 if("mapValue"in v)return decodeFields(v.mapValue.fields||{});
 return v;
}
function decodeFields(fields){return Object.fromEntries(Object.entries(fields||{}).map(([k,v])=>[k,decode(v)]));}
async function post(path,body){
 let last;
 for(let attempt=0;attempt<6;attempt++){
  try{
   const res=await fetch(`${BASE}:${path}`,{method:"POST",headers:{"content-type":"application/json"},body:JSON.stringify(body),signal:AbortSignal.timeout(45000)});
   const txt=await res.text();
   if(!res.ok)throw new Error(`Firestore ${path} HTTP ${res.status}: ${txt.slice(0,1200)}`);
   return JSON.parse(txt);
  }catch(e){last=e;if(attempt===5)break;const delay=Math.min(30000,1000*2**attempt);console.warn(`retry ${path} attempt ${attempt+1}: ${e}`);await new Promise(r=>setTimeout(r,delay));}
 }
 throw last;
}
async function runQuery(collectionId,limit=100){return post("runQuery",{structuredQuery:{from:[{collectionId}],limit}});}
async function getCount(){
 const result=await post("runAggregationQuery",{structuredAggregationQuery:{aggregations:[{count:{},alias:"count_alias"}],structuredQuery:{from:[{collectionId:COLLECTION}]}}});
 return Number(result?.[0]?.result?.aggregateFields?.count_alias?.integerValue||0);
}
function imageUrl(data,size){
 const cat=categoryMap.get(Number(data.Category)),kind=Number(data.KIND);
 if(!cat||!Number.isInteger(kind)||kind<0)return null;
 const base=size==="small"?cat.ImageSmall:cat.ImageLarge,prefix=cat.ImagePrefix;
 if(typeof base!=="string"||typeof prefix!=="string")return null;
 const path=`${base}${String(Math.floor(kind/1000)).padStart(2,"0")}/${prefix}${String(kind).padStart(5,"0")}${size==="small"?"S":"L"}.webp`;
 return new URL(path,STORAGE).toString();
}
function docRecord(doc){
 const id=doc.name.split("/").pop(),data=decodeFields(doc.fields||{});
 return {card_id:id,name:data.Name||"",source_list_url:"https://fmlunatic.com/cardlist",
  source_card_url:`https://fmlunatic.com/card/${encodeURIComponent(id)}`,
  source_image_urls:{small:imageUrl(data,"small"),large:imageUrl(data,"large")},
  raw_payload:data,firestore:{document_name:doc.name,create_time:doc.createTime||null,update_time:doc.updateTime||null},
  collection_status:"extracted_unverified",collected_at:new Date().toISOString()};
}
const count=await getCount();
console.log(`Firestore aggregation count: ${count}; required: ${TARGET}`);
if(count!==TARGET)throw new Error(`Source count mismatch: expected ${TARGET}, got ${count}`);
const settings=await runQuery("liveappsetting",20);
const settingDocs=settings.filter(x=>x.document).map(x=>({id:x.document.name.split("/").pop(),data:decodeFields(x.document.fields||{}),create_time:x.document.createTime||null,update_time:x.document.updateTime||null}));
await writeFile(`${RAW_DIR}/appsettings.json`,JSON.stringify(settingDocs,null,2));
const enumTable=settingDocs.find(x=>x.id==="enumtable");
if(!enumTable)throw new Error("Firestore liveappsetting/enumtable document was not found.");
await writeFile(`${RAW_DIR}/enumtable.json`,JSON.stringify(enumTable.data,null,2));
categoryMap=new Map((enumTable.data["Enum+Category"]||[]).map(x=>[Number(x.KIND),x]));
console.log(`Loaded ${settingDocs.length} appsetting docs; enum keys: ${Object.keys(enumTable.data).length}; image categories: ${categoryMap.size}`);
if(!categoryMap.size)throw new Error("Enum+Category image mapping is empty.");

const cardsPath=`${RAW_DIR}/cards.jsonl`;
await writeFile(cardsPath,"");
const seen=new Set(),pageAudit=[];
let cursor=null,total=0,pageNo=0;
while(total<TARGET){
 const structuredQuery={from:[{collectionId:COLLECTION}],
  orderBy:[{field:{fieldPath:"NumID"},direction:"DESCENDING"},{field:{fieldPath:"__name__"},direction:"DESCENDING"}],limit:PAGE_SIZE};
 if(cursor)structuredQuery.startAt={values:[{integerValue:String(cursor.NumID)}],before:false};
 const result=await post("runQuery",{structuredQuery});
 const docs=result.filter(x=>x.document).map(x=>x.document);
 if(!docs.length)break;
 const batch=[];
 for(const doc of docs){
  const record=docRecord(doc);
  if(seen.has(record.card_id))throw new Error(`Duplicate card ID across Firestore pages: ${record.card_id}`);
  if(!record.name)throw new Error(`Card name missing for ${record.card_id}`);
  seen.add(record.card_id);batch.push(JSON.stringify(record));
 }
 await appendFile(cardsPath,batch.join("\n")+"\n");
 const last=docRecord(docs[docs.length-1]);cursor={NumID:last.raw_payload.NumID};
 total+=docs.length;pageNo++;
 pageAudit.push({page:pageNo,count:docs.length,first_id:docs[0].name.split("/").pop(),last_id:last.card_id,last_num_id:cursor.NumID});
 console.log(JSON.stringify({page:pageNo,batch:docs.length,unique:total,target:TARGET,lastId:last.card_id,lastNumID:cursor.NumID}));
 await writeFile(`${RAW_DIR}/page-audit.json`,JSON.stringify({expected:TARGET,observed:total,pages:pageAudit},null,2));
 if(docs.length<PAGE_SIZE)break;
 await new Promise(r=>setTimeout(r,200));
}
const summary={source_count:count,expected:TARGET,unique_cards:seen.size,pages:pageNo,complete:seen.size===TARGET,finished_at:new Date().toISOString()};
await writeFile(`${RAW_DIR}/crawl-summary.json`,JSON.stringify(summary,null,2));
console.log(JSON.stringify(summary,null,2));
if(seen.size!==TARGET)process.exitCode=2;
