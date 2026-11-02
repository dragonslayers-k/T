import { chromium } from "playwright";
import { mkdir, readFile, writeFile } from "node:fs/promises";

const TARGET = Number(process.env.EXPECTED_CARDS || 15350);
const URL = process.env.TARGET_URL || "https://fmlunatic.com/cardlist";
const ROOT = "data/raw";
await mkdir(ROOT, { recursive: true });
await mkdir("data/images", { recursive: true });
const jsonl = `${ROOT}/cards.jsonl`;
const seen = new Map();
try {
  for (const line of (await readFile(jsonl, "utf8")).split("\n").filter(Boolean)) {
    try { const x = JSON.parse(line); if (x.card_id) seen.set(String(x.card_id), x); } catch {}
  }
} catch {}
const mergeRecord = record => {
  const id = String(record.card_id || "");
  if (!id) return;
  const previous = seen.get(id) || {};
  seen.set(id, { ...previous, ...record,
    raw_payload: { ...(previous.raw_payload || {}), ...(record.raw_payload || {}) } });
};
const checkpoint = async () => writeFile(jsonl,
  [...seen.values()].map(x => JSON.stringify(x)).join("\n") + (seen.size ? "\n" : ""));
const isCard = x => x && typeof x === "object" && !Array.isArray(x) &&
  (x.id != null || x.cardId != null || x.card_id != null || x.assetCode != null) &&
  (x.name || x.cardName || x.title) &&
  (x.type || x.category || x.cardType || x.faction || x.assetCode || x.image || x.artImage);
const idOf = x => String(x.card_id ?? x.cardId ?? x.id ?? x.assetCode ?? "");
const walk = (node, found, depth=0) => {
  if (!node || typeof node !== "object" || depth > 20) return;
  if (Array.isArray(node)) { for (const v of node) walk(v, found, depth+1); return; }
  if (isCard(node)) found.push(node);
  for (const v of Object.values(node)) if (v && typeof v === "object") walk(v, found, depth+1);
};
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const pending = new Set();
let responseCount = 0;
const handleResponse = async res => {
  const ct = res.headers()["content-type"] || "";
  if (!/json/i.test(ct)) return;
  try {
    const payload = await res.json(), found = [];
    walk(payload, found);
    for (const x of found) {
      const id = idOf(x);
      if (!id) continue;
      mergeRecord({
        card_id: id, name: x.name || x.cardName || x.title || "",
        source_list_url: URL,
        source_card_url: x.url || x.detailUrl || x.detail_url || x.href || null,
        source_image_url: x.imageUrl || x.image || x.artImage || x.largeImage || null,
        source_thumbnail_url: x.thumbnail || x.thumbnailUrl || null,
        raw_payload: { observed_from: res.url(), object: x },
        collection_status: "extracted_unverified"
      });
    }
    responseCount++;
  } catch {}
};
page.on("response", res => {
  const p=handleResponse(res);
  pending.add(p);
  p.finally(()=>pending.delete(p));
});
const errors = [];
try {
  await page.goto(URL, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(15000);
  let stagnant = 0;
  for (let pageNo=0; pageNo<2000 && seen.size<TARGET && stagnant<8; pageNo++) {
    const domCards = await page.evaluate(() => {
      const els = [...document.querySelectorAll("a,article,[data-id],[data-card-id],[role=button]")];
      return els.map(el => {
        const data = Object.fromEntries([...el.attributes].filter(a => a.name.startsWith("data-")).map(a => [a.name,a.value]));
        const img = el.querySelector("img");
        return {
          card_id: data["data-id"] || data["data-card-id"] || null,
          name: (el.innerText || img?.alt || "").trim().slice(0,500),
          source_card_url: el.href || null, source_image_url: img?.src || null,
          raw_payload: { tag:el.tagName, className:String(el.className||""), data }
        };
      }).filter(x => x.card_id && x.name);
    });
    const before = seen.size;
    for (const x of domCards) mergeRecord({ ...x, source_list_url:URL, collection_status:"extracted_unverified" });
    await Promise.all([...pending]);
    const links = await page.locator("a[href]").evaluateAll(as => as.map(a => ({
      href:a.href, text:(a.innerText || a.getAttribute("aria-label") || "").trim()
    })).filter(x => x.text && x.href.startsWith(location.origin)));
    await writeFile(`${ROOT}/observed-links.json`, JSON.stringify(links,null,2));
    await checkpoint();
    const next = page.locator('button[aria-label*="next" i],button[aria-label*="다음"],a[aria-label*="next" i],a[aria-label*="다음"],button:has-text("다음"),a:has-text("다음")').first();
    if (await next.count() && await next.isVisible().catch(()=>false) && await next.isEnabled().catch(()=>false)) {
      await next.click().catch(()=>{});
      await page.waitForTimeout(1500);
    } else {
      await page.evaluate(() => window.scrollTo(0, document.body.scrollHeight));
      await page.waitForTimeout(1500);
    }
    await Promise.all([...pending]);
    stagnant = seen.size===before ? stagnant+1 : 0;
    if (pageNo % 5 === 0) console.log(JSON.stringify({pageNo, uniqueCards:seen.size, target:TARGET, responseCount}));
  }
} catch (e) { errors.push(String(e)); }
await Promise.all([...pending]);
await checkpoint();
await writeFile(`${ROOT}/crawl-summary.json`, JSON.stringify({
  target:TARGET, uniqueCards:seen.size, complete:seen.size===TARGET,
  responseCount, errors, finishedAt:new Date().toISOString()
},null,2));
await browser.close();
console.log(JSON.stringify({target:TARGET, uniqueCards:seen.size, complete:seen.size===TARGET, errors},null,2));
if (seen.size!==TARGET) process.exitCode=2;
