#!/usr/bin/env python3
"""Probe the source card page for a higher-resolution image of one unresolved card."""
from __future__ import annotations
import hashlib, json
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urljoin, urlparse
from urllib.request import Request, urlopen
from PIL import Image
import io

CARD_ID = "10091525191"
PAGE_URL = f"https://fmlunatic.com/card/{CARD_ID}"
MAX_BYTES = 12 * 1024 * 1024


class ImageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.urls, self.title, self.text = [], False, []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.title = True
        if tag == "img":
            for key in ("src", "data-src", "data-original", "data-lazy-src"):
                if attrs.get(key):
                    self.urls.append(attrs[key])
            if attrs.get("srcset"):
                self.urls.extend(part.strip().split(" ")[0] for part in attrs["srcset"].split(","))
        if tag == "meta" and attrs.get("property") in ("og:image", "twitter:image") and attrs.get("content"):
            self.urls.append(attrs["content"])

    def handle_endtag(self, tag):
        if tag == "title":
            self.title = False

    def handle_data(self, data):
        if self.title:
            self.text.append(data.strip())


def get(url: str, limit: int = MAX_BYTES) -> tuple[bytes, str]:
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; FM-OFFLINE-research/1.0)", "Accept": "text/html,image/*,*/*"})
    with urlopen(req, timeout=25) as response:
        data = response.read(limit + 1)
        if len(data) > limit:
            raise ValueError("response exceeds byte limit")
        return data, response.headers.get("Content-Type", "")


def main():
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    out = args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    result = {"card_id": CARD_ID, "page_url": PAGE_URL, "page_status": "not_fetched", "image_candidates": []}
    try:
        body, content_type = get(PAGE_URL, 2 * 1024 * 1024)
        html = body.decode("utf-8", errors="replace")
        (out / "source-page.html").write_text(html, encoding="utf-8")
        result.update({"page_status": "fetched", "content_type": content_type, "html_bytes": len(body), "html_sha256": hashlib.sha256(body).hexdigest()})
        parser = ImageParser()
        parser.feed(html)
        result["page_title"] = " ".join(parser.text)
        urls = []
        for raw in parser.urls:
            url = urljoin(PAGE_URL, raw.strip())
            parsed = urlparse(url)
            if parsed.scheme in ("http", "https") and url not in urls:
                urls.append(url)
        result["discovered_image_urls"] = urls
        for index, url in enumerate(urls[:20], 1):
            item = {"url": url, "status": "not_downloaded"}
            try:
                data, candidate_type = get(url)
                image = Image.open(io.BytesIO(data))
                image.load()
                ext = (image.format or "img").lower()
                name = f"candidate-{index:02d}.{ext}"
                (out / name).write_bytes(data)
                item.update({
                    "status": "downloaded", "file": name, "content_type": candidate_type,
                    "width": image.width, "height": image.height, "format": image.format,
                    "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                })
            except Exception as exc:
                item.update({"status": "unavailable_or_not_image", "error": str(exc)[:240]})
            result["image_candidates"].append(item)
    except Exception as exc:
        result["page_status"] = "unavailable"
        result["page_error"] = str(exc)[:400]
    (out / "source-image-probe-summary.json").write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
