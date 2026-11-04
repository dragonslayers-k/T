#!/usr/bin/env python3
"""Probe official card detail pages for low-confidence, name-only skill evidence.

Evidence collection only: this script never promotes a rule or changes game_rule_catalog.
"""
import argparse
import concurrent.futures
import json
import re
import sqlite3
import urllib.request
from html.parser import HTMLParser
from pathlib import Path


class PageText(HTMLParser):
    BLOCKS = {"br", "p", "div", "li", "tr", "td", "th", "h1", "h2", "h3", "section"}
    def __init__(self):
        super().__init__()
        self.parts = []
        self.hidden = 0
        self.in_title = False
        self.title_parts = []

    def handle_starttag(self, tag, attrs):
        if tag in ("script", "style", "noscript"):
            self.hidden += 1
        if tag == "title":
            self.in_title = True
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_endtag(self, tag):
        if tag in ("script", "style", "noscript") and self.hidden:
            self.hidden -= 1
        if tag == "title":
            self.in_title = False
        if tag in self.BLOCKS:
            self.parts.append("\n")

    def handle_data(self, data):
        if self.hidden:
            return
        value = data.strip()
        if value:
            self.parts.append(value)
            if self.in_title:
                self.title_parts.append(value)


def parse_page(raw):
    parser = PageText()
    parser.feed(raw)
    text = re.sub(r"\s+", " ", " ".join(parser.parts)).strip()
    return " ".join(parser.title_parts).strip(), text


def contexts(text, skill_name, limit=4, radius=260):
    found = []
    for match in re.finditer(re.escape(skill_name), text, re.I):
        left = max(0, match.start() - radius)
        right = min(len(text), match.end() + radius)
        found.append(text[left:right])
        if len(found) >= limit:
            break
    return found


def fetch_page(url, timeout=20):
    request = urllib.request.Request(
        url, headers={"User-Agent": "Mozilla/5.0 (compatible; FM1CardDB/1.0)"}
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        raw = response.read(2_000_000).decode("utf-8", "replace")
        status = getattr(response, "status", 200)
    title, text = parse_page(raw)
    return {"httpStatus": status, "title": title, "text": text[:12000],
            "textLength": len(text)}


def probe(db_path: Path, output: Path):
    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    skills = db.execute("""
      SELECT e.source_field,e.source_enum_value,e.source_name,e.card_count,e.rule_id
      FROM skill_enum_inventory e
      JOIN game_rule_catalog g USING(rule_id)
      WHERE e.mapping_status='inferred' AND g.confidence='low'
      ORDER BY e.source_field,e.source_enum_value
    """).fetchall()
    work = []
    urls = set()
    for skill in skills:
        cards = db.execute("""
          SELECT DISTINCT c.card_id,c.name,c.source_card_url
          FROM card_rule_mappings m JOIN cards c USING(card_id)
          WHERE m.source_field=? AND m.source_enum_value=? AND m.source_name=?
          ORDER BY c.card_id
        """, (skill["source_field"], skill["source_enum_value"], skill["source_name"])).fetchall()
        card_rows = []
        for card in cards:
            texts = db.execute("""
              SELECT text_type,COALESCE(NULLIF(plain_text,''),source_text) AS text
              FROM card_texts WHERE card_id=? ORDER BY text_id
            """, (card["card_id"],)).fetchall()
            card_rows.append({
                "cardId": card["card_id"], "cardName": card["name"],
                "sourceCardUrl": card["source_card_url"],
                "storedCardTexts": [{"type": x["text_type"], "text": (x["text"] or "")[:1200]} for x in texts]
            })
            if card["source_card_url"]:
                urls.add(card["source_card_url"])
        work.append({
            "sourceField": skill["source_field"], "sourceEnumValue": skill["source_enum_value"],
            "skillName": skill["source_name"], "cardCount": skill["card_count"],
            "ruleId": skill["rule_id"], "cards": card_rows
        })

    def fetch_one(url):
        try:
            return url, {"fetchStatus": "success", **fetch_page(url)}
        except Exception as exc:
            return url, {"fetchStatus": "unavailable", "error": f"{type(exc).__name__}: {exc}"[:500]}

    page_results = {}
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        for url, result in pool.map(fetch_one, sorted(urls)):
            page_results[url] = result

    successful_pages = 0
    cards_with_name = 0
    for skill in work:
        for card in skill["cards"]:
            page = page_results.get(card["sourceCardUrl"], {})
            if page.get("fetchStatus") == "success":
                successful_pages += 1
                snippets = contexts(page.get("text", ""), skill["skillName"])
                card["officialPageProbe"] = {
                    "fetchStatus": "success", "httpStatus": page.get("httpStatus"),
                    "pageTitle": page.get("title"), "textLength": page.get("textLength"),
                    "skillNameOccurrences": len(snippets), "contexts": snippets
                }
                if snippets:
                    cards_with_name += 1
            else:
                card["officialPageProbe"] = page

    result = {
        "source": "official fmlunatic card detail pages",
        "evidencePolicy": "Source evidence only; no skill rule is promoted or marked executable.",
        "lowConfidenceSkillKinds": len(work), "uniqueDetailPages": len(urls),
        "successfulCardPageProbes": successful_pages,
        "cardsWithSkillNameInPageText": cards_with_name, "skills": work
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    db.close()
    print(json.dumps({k: result[k] for k in (
        "lowConfidenceSkillKinds", "uniqueDetailPages",
        "successfulCardPageProbes", "cardsWithSkillNameInPageText"
    )}, ensure_ascii=False))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("data/fm1_cards.sqlite"))
    parser.add_argument("--out", type=Path, default=Path("data/gap-reports/name-only-skill-source-probe.json"))
    args = parser.parse_args()
    probe(args.db, args.out)


if __name__ == "__main__":
    main()
