import { chromium } from "playwright";
import { mkdir, writeFile } from "node:fs/promises";

const target = process.env.TARGET_URL || "https://fmlunatic.com/cardlist";
const out = "artifacts/probe";
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
const page = await browser.newPage({ viewport: { width: 1440, height: 1000 } });
const requests = [];
const jsonBodies = [];
page.on("request", req => {
  if (/fmlunatic\.com/.test(req.url())) requests.push({
    method: req.method(), url: req.url(), resourceType: req.resourceType(),
    postData: req.postData()?.slice(0, 4000) || null
  });
});
page.on("response", async res => {
  const ct = res.headers()["content-type"] || "";
  const url = res.url();
  if (/json|graphql/i.test(ct) || /api|graphql|search|card/i.test(url)) {
    let body = null;
    try {
      if (/json|graphql/i.test(ct)) body = await res.json();
    } catch {}
    jsonBodies.push({ url, status: res.status(), contentType: ct, body });
  }
});
let navigationError = null;
try {
  await page.goto(target, { waitUntil: "domcontentloaded", timeout: 90000 });
  await page.waitForTimeout(20000);
} catch (e) { navigationError = String(e); }

const dom = await page.evaluate(() => {
  const compact = el => ({
    tag: el.tagName, text: (el.innerText || el.getAttribute("aria-label") || "").trim().slice(0, 300),
    href: el.href || null, src: el.src || null,
    cls: String(el.className || "").slice(0, 300),
    id: el.id || null, role: el.getAttribute("role"),
    data: Object.fromEntries([...el.attributes].filter(a => a.name.startsWith("data-")).map(a => [a.name, a.value]).slice(0, 20))
  });
  return {
    title: document.title, url: location.href, htmlLang: document.documentElement.lang,
    bodyText: (document.body?.innerText || "").slice(0, 40000),
    scripts: [...document.scripts].map(s => s.src).filter(Boolean),
    links: [...document.querySelectorAll("a")].slice(0, 3000).map(compact),
    buttons: [...document.querySelectorAll("button,[role=button]")].slice(0, 1000).map(compact),
    inputs: [...document.querySelectorAll("input,select")].slice(0, 500).map(compact),
    images: [...document.images].slice(0, 3000).map(compact),
    elementCounts: Object.fromEntries(["a","button","img","input","article","li","tr","[role=grid]","[role=list]"].map(s => [s, document.querySelectorAll(s).length])),
    storageKeys: { local: Object.keys(localStorage), session: Object.keys(sessionStorage) }
  };
});
await writeFile(`${out}/dom.json`, JSON.stringify({ navigationError, ...dom }, null, 2));
await writeFile(`${out}/requests.json`, JSON.stringify(requests, null, 2));
await writeFile(`${out}/responses.json`, JSON.stringify(jsonBodies, null, 2));
await page.screenshot({ path: `${out}/page.png`, fullPage: true }).catch(() => {});
console.log(JSON.stringify({
  url: target, title: dom.title, navigationError,
  requests: requests.length, jsonResponses: jsonBodies.length,
  anchors: dom.elementCounts.a, buttons: dom.elementCounts.button,
  images: dom.elementCounts.img, bodyPreview: dom.bodyText.slice(0, 2000)
}, null, 2));
await browser.close();
