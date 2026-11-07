#!/usr/bin/env python3
"""Probe source SPA, DB29 metadata, and original image URLs for one unresolved card."""
from __future__ import annotations
import argparse, hashlib, json, re
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from PIL import Image
import io

CARD_ID = "10091525191"
PAGE_URL = f"https://fmlunatic.com/card/{CARD_ID}"
MAX_BYTES = 12 * 1024 * 1024


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.image_urls, self.script_urls, self.title, self.title_text = [], [], False, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.title = True
        if tag == "script" and attrs.get("src"):
            self.script_urls.append(attrs["src"])
        if tag == "img":
            for key in ("src", "data-src", "data-original", "data-lazy-src"):
                if attrs.get(key):
                    self.image_urls.append(attrs[key])
            if attrs.get("srcset"):
                self.image_urls.extend(part.strip().split(" ")[0] for part in attrs["srcset"].split(","))
        if tag == "meta" and attrs.get("property") in ("og:image", "twitter:image") and attrs.get("content"):
            self.image_urls.append(attrs["content"])


def get(url: str, limit: int = MAX_BYTES) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; FM-OFFLINE-research/1.0)", "Accept": "text/html,application/javascript,image/*,*/*"})
    with urlopen(req, timeout=25) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("response exceeds byte limit")
        return data, response.headers.get("Content-Type", "")


def find_source_row(path: Path) -> dict | None:
    with path.open(encoding="utf-8") as stream:
        for line in stream:
            row = json.loads(line)
            raw = row.get("raw_payload") if isinstance(row.get("raw_payload"), dict) else row
            cid = str(row.get("card_id") or row.get("id") or raw.get("ID") or "").strip()
            if cid == CARD_ID:
                return row
    return None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    ap.add_argument("--source-cards-jsonl", type=Path, required=True)
    ap.add_argument("--enumtable-json", type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    result = {"card_id": CARD_ID, "page_url": PAGE_URL, "page_status": "not_fetched", "image_candidates": [], "bundle_analysis": []}

    source_row = find_source_row(args.source_cards_jsonl)
    if source_row:
        (out / "source-card-record.json").write_text(json.dumps(source_row, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        raw = source_row.get("raw_payload") if isinstance(source_row.get("raw_payload"), dict) else source_row
        result["source_card_fields"] = {k: raw.get(k) for k in ("ID", "Name", "Category", "KIND", "RequireSoul") if k in raw}
        source_urls = source_row.get("source_image_urls") or {}
        result["source_image_urls"] = source_urls
        for label in ("large", "small"):
            url = source_urls.get(label)
            if not url:
                continue
            item = {"kind": label, "url": url, "status": "not_downloaded"}
            try:
                data, ctype = get(url)
                image = Image.open(io.BytesIO(data)); image.load()
                ext = (image.format or "img").lower()
                name = f"source-original-{label}.{ext}"
                (out / name).write_bytes(data)
                item.update({"status": "downloaded", "file": name, "content_type": ctype, "width": image.width, "height": image.height, "format": image.format, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
            except Exception as exc:
                item.update({"status": "download_failed", "error": str(exc)[:300]})
            result["image_candidates"].append(item)
    else:
        result["source_card_record_found"] = False

    enum = json.loads(args.enumtable_json.read_text(encoding="utf-8"))
    (out / "enumtable.json").write_text(json.dumps(enum, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    result["enumtable_top_level_keys"] = list(enum.keys()) if isinstance(enum, dict) else []
    result["enumtable_category"] = enum.get("Enum+Category") if isinstance(enum, dict) else None

    try:
        body, content_type = get(PAGE_URL, 2 * 1024 * 1024)
        html = body.decode("utf-8", errors="replace")
        (out / "source-page.html").write_text(html, encoding="utf-8")
        result.update({"page_status": "fetched", "content_type": content_type, "html_bytes": len(body), "html_sha256": hashlib.sha256(body).hexdigest()})
        parser = PageParser()
        parser.feed(html)
        result["page_title"] = " ".join(parser.title_text)
        page_images = []
        for raw in parser.image_urls:
            url = urljoin(PAGE_URL, raw.strip())
            if urlparse(url).scheme in ("http", "https") and url not in page_images:
                page_images.append(url)
        result["discovered_image_urls"] = page_images
        bundle_urls = []
        for raw in parser.script_urls:
            url = urljoin(PAGE_URL, raw.strip())
            if urlparse(url).scheme in ("http", "https") and url not in bundle_urls:
                bundle_urls.append(url)
        result["script_urls"] = bundle_urls
        for index, url in enumerate(bundle_urls[:10], 1):
            try:
                data, ctype = get(url, MAX_BYTES)
                text = data.decode("utf-8", errors="replace")
                name = f"source-bundle-{index:02d}.js"
                (out / name).write_text(text, encoding="utf-8")
                hits = re.findall(r"""['"]([^'"]{1,240})['"]""", text)
                selected = [s for s in hits if re.search(r"(image|\.webp|\.png|\.jpg|\.jpeg|/api|firestore|storage|card)", s, re.I)]
                selected = list(dict.fromkeys(selected))[:250]
                (out / f"bundle-{index:02d}-interesting-strings.txt").write_text("\n".join(selected), encoding="utf-8")
                result["bundle_analysis"].append({"url": url, "file": name, "content_type": ctype, "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(), "interesting_string_count": len(selected), "interesting_strings_file": f"bundle-{index:02d}-interesting-strings.txt"})
            except Exception as exc:
                result["bundle_analysis"].append({"url": url, "error": str(exc)[:240]})
    except Exception as exc:
        result["page_status"] = "unavailable"
        result["page_error"] = str(exc)[:400]
    (out / "source-image-probe-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
