import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";

const target = process.env.TARGET_URL || "https://fmlunatic.com/cardlist";
const out = "artifacts/probe";
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const requests = [], responses = [], streamBodies = [];
page.on("request", req => {
  const url=req.url();
  if (/fmlunatic|firestore|googleapis|firebase|storage.googleapis/i.test(url)) requests.push({
    method:req.method(), url, resourceType:req.resourceType(),
    postData:req.postData()?.slice(0,12000)||null
  });
});
page.on("response", async res => {
  const ct=res.headers()["content-type"]||"", url=res.url();
  if (!/fmlunatic|firestore|googleapis|firebase|storage.googleapis/i.test(url)) return;
  const item={url,status:res.status(),contentType:ct,body:null};
  try {
    if (/json/i.test(ct)) item.body=await res.json();
    else if (/Firestore\/Listen\/channel/i.test(url) && /text\/plain/i.test(ct)) {
      const body=await res.text();
      item.bodyPreview=body.slice(0,100000);
      streamBodies.push({url,status:res.status(),body});
    }
  } catch(e) { item.readError=String(e); }
  responses.push(item);
});
let navigationError=null;
try {
  await page.goto(target,{waitUntil:"domcontentloaded",timeout:90000});
  await page.waitForTimeout(18000);
} catch(e){navigationError=String(e);}
const collectDom=async()=>page.evaluate(()=>{
 const compact=el=>({
  tag:el.tagName,text:(el.innerText||el.getAttribute("aria-label")||"").trim().slice(0,500),
  href:el.href||null,src:el.src||null,cls:String(el.className||"").slice(0,500),
  id:el.id||null,role:el.getAttribute("role"),
  data:Object.fromEntries([...el.attributes].filter(a=>a.name.startsWith("data-")).map(a=>[a.name,a.value]).slice(0,30))
 });
 return {
  title:document.title,url:location.href,bodyText:(document.body?.innerText||"").slice(0,50000),
  scripts:[...document.scripts].map(s=>s.src).filter(Boolean),
  links:[...document.querySelectorAll("a")].slice(0,4000).map(compact),
  buttons:[...document.querySelectorAll("button,[role=button]")].slice(0,1500).map(compact),
  inputs:[...document.querySelectorAll("input,select")].slice(0,500).map(compact),
  images:[...document.images].slice(0,4000).map(compact),
  elementCounts:Object.fromEntries(["a","button","img","input","article","li","tr","[role=grid]","[role=list]"].map(s=>[s,document.querySelectorAll(s).length]))
 };
});
const dom=await collectDom();
const bundleTexts=[];
for(const src of dom.scripts){
 try {
  const item=await page.evaluate(async u=>({url:u,text:await (await fetch(u)).text()}),src);
  bundleTexts.push(item);
 }catch(e){bundleTexts.push({url:src,error:String(e)});}
}
const firstCard=page.locator("img.card-img-top").first();
let detailDom=null,detailError=null;
try{
 if(await firstCard.count()){
  await firstCard.click();
  await page.waitForTimeout(3500);
  detailDom=await collectDom();
  await page.screenshot({path:`${out}/detail.png`,fullPage:false}).catch(()=>{});
 }
}catch(e){detailError=String(e);}
await writeFile(`${out}/dom.json`,JSON.stringify({navigationError,...dom},null,2));
await writeFile(`${out}/detail-dom.json`,JSON.stringify({detailError,...(detailDom||{})},null,2));
await writeFile(`${out}/requests.json`,JSON.stringify(requests,null,2));
await writeFile(`${out}/responses.json`,JSON.stringify(responses,null,2));
await writeFile(`${out}/firestore-streams.json`,JSON.stringify(streamBodies,null,2));
await writeFile(`${out}/bundles.json`,JSON.stringify(bundleTexts,null,2));
await page.screenshot({path:`${out}/page.png`,fullPage:false}).catch(()=>{});
console.log(JSON.stringify({
 url:target,title:dom.title,navigationError,requests:requests.length,
 responses:responses.length,streams:streamBodies.length,
 buttons:dom.elementCounts.button,images:dom.elementCounts.img,
 detailError,detailText:detailDom?.bodyText?.slice(-6000)
},null,2));
await browser.close();
