import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";

const target=process.env.TARGET_URL||"https://fmlunatic.com/cardlist";
const out="artifacts/probe";
await mkdir(out,{recursive:true});
const browser=await chromium.launch({headless:true});
const page=await browser.newPage({viewport:{width:1440,height:1000}});
const requests=[],responses=[],bundles=[];
page.on("request",req=>{
 const url=req.url();
 if(/fmlunatic|firestore|googleapis|firebase|storage.googleapis/i.test(url))
  requests.push({method:req.method(),url,resourceType:req.resourceType(),postData:req.postData()?.slice(0,12000)||null});
});
page.on("response",async res=>{
 const ct=res.headers()["content-type"]||"",url=res.url();
 if(!/fmlunatic|firestore|googleapis|firebase|storage.googleapis/i.test(url))return;
 const item={url,status:res.status(),contentType:ct};
 // Do not consume Firestore Listen streaming bodies: they remain open for the lifetime of the app.
 try{if(/json/i.test(ct))item.body=await res.json();}catch(e){item.readError=String(e);}
 responses.push(item);
});
let navigationError=null;
try{await page.goto(target,{waitUntil:"domcontentloaded",timeout:90000});await page.waitForTimeout(15000);}
catch(e){navigationError=String(e);}
const collectDom=async()=>page.evaluate(()=>{
 const compact=el=>({tag:el.tagName,text:(el.innerText||el.getAttribute("aria-label")||"").trim().slice(0,500),href:el.href||null,src:el.src||null,cls:String(el.className||"").slice(0,500),id:el.id||null,role:el.getAttribute("role"),data:Object.fromEntries([...el.attributes].filter(a=>a.name.startsWith("data-")).map(a=>[a.name,a.value]).slice(0,30))});
 return {title:document.title,url:location.href,bodyText:(document.body?.innerText||"").slice(0,50000),scripts:[...document.scripts].map(s=>s.src).filter(Boolean),links:[...document.querySelectorAll("a")].slice(0,4000).map(compact),buttons:[...document.querySelectorAll("button,[role=button]")].slice(0,1500).map(compact),inputs:[...document.querySelectorAll("input,select")].slice(0,500).map(compact),images:[...document.images].slice(0,4000).map(compact),elementCounts:Object.fromEntries(["a","button","img","input","article","li","tr","[role=grid]","[role=list]"].map(s=>[s,document.querySelectorAll(s).length]))};
});
const dom=await collectDom();
for(const src of dom.scripts){try{bundles.push(await page.evaluate(async u=>({url:u,text:await(await fetch(u)).text()}),src));}catch(e){bundles.push({url:src,error:String(e)});}}
let detailDom=null,detailError=null;
try{const first=page.locator("img.card-img-top").first();if(await first.count()){await first.click();await page.waitForTimeout(2500);detailDom=await collectDom();await page.screenshot({path:`${out}/detail.png`}).catch(()=>{});}}catch(e){detailError=String(e);}
await writeFile(`${out}/dom.json`,JSON.stringify({navigationError,...dom},null,2));
await writeFile(`${out}/detail-dom.json`,JSON.stringify({detailError,...(detailDom||{})},null,2));
await writeFile(`${out}/requests.json`,JSON.stringify(requests,null,2));
await writeFile(`${out}/responses.json`,JSON.stringify(responses,null,2));
await writeFile(`${out}/bundles.json`,JSON.stringify(bundles,null,2));
await page.screenshot({path:`${out}/page.png`}).catch(()=>{});
console.log(JSON.stringify({title:dom.title,navigationError,requests:requests.length,responses:responses.length,images:dom.elementCounts.img,detailError,detailText:detailDom?.bodyText?.slice(-5000)},null,2));
await browser.close();
