import { mkdir,readFile,appendFile,writeFile } from "node:fs/promises";
import crypto from "node:crypto";
const enumData=JSON.parse(await readFile("data/raw/enumtable.json","utf8"));
const raw=enumData["Enum+Category"]||[],rows=Array.isArray(raw)?raw:Object.values(raw);
const categoryMap=new Map(rows.map(r=>[Number(Array.isArray(r)?r[0]:r.KIND),Array.isArray(r)?{KIND:r[0],TYPE:r[1],UIName:r[2],UIPriority:r[3],ImageSmall:r[4],ImageLarge:r[5],ImagePrefix:r[6]}:r]));
const bucket="https://storage.googleapis.com/fmdb-bcb70.appspot.com/",concurrency=Number(process.env.IMAGE_CONCURRENCY||6);
const cards=(await readFile("data/raw/cards.jsonl","utf8")).split("\n").filter(Boolean).map(JSON.parse);
await mkdir("data/images/small",{recursive:true});await mkdir("data/images/large",{recursive:true});await writeFile("data/raw/image-manifest.jsonl","");
const jobs=[];
function imageUrl(card,size){const d=card.raw_payload||{},cat=categoryMap.get(Number(d.Category)),kind=Number(d.KIND);if(!cat||!Number.isInteger(kind)||kind<0)return null;const base=size==="small"?cat.ImageSmall:cat.ImageLarge,prefix=cat.ImagePrefix;if(typeof base!=="string"||typeof prefix!=="string")return null;const path=base+String(Math.floor(kind/1000)).padStart(2,"0")+"/"+prefix+String(kind).padStart(5,"0")+(size==="small"?"S":"L")+".webp";return new URL(path,bucket).toString();}
for(const card of cards)for(const size of ["small","large"])jobs.push({card,size,url:imageUrl(card,size)});
let cursor=0,ok=0,failed=0,missing=0;
async function worker(){while(true){const index=cursor++;if(index>=jobs.length)return;const job=jobs[index],id=job.card.card_id,path="data/images/"+job.size+"/"+id+".webp";const item={card_id:id,image_type:job.size,source_url:job.url,local_path:job.url?path:null,status:"pending",byte_size:null,sha256:null,http_status:null};
 if(!job.url){item.status="no_image_mapping";missing++;}
 else{
  let done=false,last=null;
  for(let attempt=0;attempt<4&&!done;attempt++){
   try{
    const res=await fetch(job.url,{signal:AbortSignal.timeout(30000)});item.http_status=res.status;
    if(res.status===404||res.status===410||(res.status>=400&&res.status<500&&res.status!==429)){item.status="http_"+res.status;failed++;done=true;break;}
    if(!res.ok)throw new Error("HTTP "+res.status);
    const buf=Buffer.from(await res.arrayBuffer());if(!buf.length)throw new Error("empty image");
    const hash=crypto.createHash("sha256").update(buf).digest("hex");await writeFile(path,buf);
    item.status="downloaded";item.byte_size=buf.length;item.sha256=hash;ok++;done=true;
   }catch(e){last=e;if(attempt<3)await new Promise(r=>setTimeout(r,700*2**attempt));}
  }
  if(!done){item.status="download_failed";item.error=String(last);failed++;}
 }
 await appendFile("data/raw/image-manifest.jsonl",JSON.stringify(item)+"\n");
 if((ok+failed+missing)%250===0)console.log(JSON.stringify({processed:ok+failed+missing,total:jobs.length,downloaded:ok,failed,missing}));
}}
await Promise.all(Array.from({length:concurrency},worker));
const summary={cards:cards.length,image_jobs:jobs.length,downloaded:ok,failed,missing_mapping:missing,complete:ok===jobs.length,finished_at:new Date().toISOString()};
await writeFile("data/raw/image-summary.json",JSON.stringify(summary,null,2));console.log(JSON.stringify(summary,null,2));
// Leave image gaps visible for the SQLite audit; do not abort before the report is produced.
