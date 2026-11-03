#!/usr/bin/env python3
import json, sqlite3, sys
from pathlib import Path

TARGET = 15350
EXPECTED_CATEGORIES = {
    "지형": 289,
    "유닛": 8633,
    "마법": 3857,
    "아이템": 1748,
    "인챈트": 823,
}
db = Path("data/fm1_cards.sqlite")
if not db.exists():
    raise SystemExit("DB missing")

con = sqlite3.connect(db)
def scalar(sql, params=()):
    return con.execute(sql, params).fetchone()[0]
def grouped(sql, params=()):
    return {row[0]: row[1] for row in con.execute(sql, params).fetchall()}

manifest_path = Path("data/raw/image-manifest.jsonl")
image_rows = []
if manifest_path.exists():
    with manifest_path.open(encoding="utf-8") as source:
        image_rows = [json.loads(line) for line in source if line.strip()]
crawl_path = Path("data/raw/crawl-summary.json")
crawl = json.loads(crawl_path.read_text(encoding="utf-8")) if crawl_path.exists() else {}

large = [x for x in image_rows if x.get("image_type") == "large"]
small = [x for x in image_rows if x.get("image_type") == "small"]
category_counts = grouped("SELECT card_type, COUNT(*) FROM cards GROUP BY card_type")
cost_rows = con.execute("""
    SELECT c.card_type,
           COUNT(*) AS card_count,
           SUM(CASE WHEN cc.soul_known = 1 THEN 1 ELSE 0 END) AS soul_parsed,
           SUM(CASE WHEN cc.soul_known = 0 OR cc.soul_known IS NULL THEN 1 ELSE 0 END) AS soul_review
    FROM cards c
    LEFT JOIN card_costs cc ON cc.card_id = c.card_id
    GROUP BY c.card_type
    ORDER BY c.card_type
""").fetchall()
cost_by_category = {
    row[0]: {
        "cards": row[1],
        "soulCostParsed": row[2] or 0,
        "soulCostNeedsReview": row[3] or 0,
    }
    for row in cost_rows
}

field_presence = {}
for field in ("RequireSoul", "RequireLP", "MuSoul", "EarnSoulList"):
    field_presence[field] = grouped("""
        SELECT c.card_type, COUNT(DISTINCT f.card_id)
        FROM cards c
        JOIN card_fields f ON f.card_id = c.card_id
        WHERE f.field_key = ?
        GROUP BY c.card_type
    """, (field,))

review_tokens = {
    row[0]: {"tokenCount": row[1], "cardsAffected": row[2]}
    for row in con.execute("""
        SELECT c.card_type, COUNT(*), COUNT(DISTINCT t.card_id)
        FROM cards c
        JOIN card_soul_cost_tokens t ON t.card_id = c.card_id
        WHERE t.parse_status = 'manual_review'
        GROUP BY c.card_type
        ORDER BY c.card_type
    """).fetchall()
}

unpacked_category_counts = {k: v for k, v in category_counts.items() if k not in EXPECTED_CATEGORIES}
missing_or_wrong_categories = {
    name: {"expected": expected, "actual": category_counts.get(name, 0)}
    for name, expected in EXPECTED_CATEGORIES.items()
    if category_counts.get(name, 0) != expected
}

result = {
    "requiredCards": TARGET,
    "firestoreSourceCount": crawl.get("source_count"),
    "uniqueCards": scalar("SELECT COUNT(*) FROM cards"),
    "duplicateIds": scalar("SELECT COUNT(*) FROM (SELECT card_id FROM cards GROUP BY card_id HAVING COUNT(*) > 1)"),
    "missingNames": scalar("SELECT COUNT(*) FROM cards WHERE name IS NULL OR TRIM(name) = ''"),
    "missingIndividualUrls": scalar("SELECT COUNT(*) FROM cards WHERE source_card_url IS NULL OR source_card_url = ''"),
    "missingListUrls": scalar("SELECT COUNT(*) FROM cards WHERE source_list_url IS NULL OR source_list_url = ''"),
    "distinctSourceFields": scalar("SELECT COUNT(DISTINCT field_key) FROM card_fields"),
    "cardFieldRows": scalar("SELECT COUNT(*) FROM card_fields"),
    "taxonomyRows": scalar("SELECT COUNT(*) FROM taxonomy"),
    "cardsWithTextBase": scalar("SELECT COUNT(DISTINCT card_id) FROM card_fields WHERE field_key = 'TextBase'"),
    "cardsWithTextExtra": scalar("SELECT COUNT(DISTINCT card_id) FROM card_fields WHERE field_key = 'TextExtra'"),
    "cardsWithImageUrls": scalar("SELECT COUNT(DISTINCT card_id) FROM card_images WHERE source_url IS NOT NULL AND source_url <> ''"),
    "imageRowsInDb": scalar("SELECT COUNT(*) FROM card_images"),
    "largeImagesDownloaded": sum(x.get("status") == "downloaded" for x in large),
    "smallImagesDownloaded": sum(x.get("status") == "downloaded" for x in small),
    "largeImageFailures": sum(x.get("status") != "downloaded" for x in large),
    "smallImageFailures": sum(x.get("status") != "downloaded" for x in small),
    "largeImageManifestRows": len(large),
    "smallImageManifestRows": len(small),
    "largeImageBytes": sum(int(x.get("byte_size") or 0) for x in large if x.get("status") == "downloaded"),
    "smallImageBytes": sum(int(x.get("byte_size") or 0) for x in small if x.get("status") == "downloaded"),
    "lpKnownCards": scalar("SELECT COUNT(*) FROM card_costs WHERE lp_known = 1"),
    "lpZeroCards": scalar("SELECT COUNT(*) FROM card_costs WHERE lp_known = 1 AND lp_value = 0"),
    "soulCostFullyParsed": scalar("SELECT COUNT(*) FROM card_costs WHERE soul_known = 1"),
    "soulCostNeedsReview": scalar("SELECT COUNT(*) FROM card_costs WHERE soul_known = 0"),
    "soulCostTokens": scalar("SELECT COUNT(*) FROM card_soul_cost_tokens"),
    "categoryCounts": category_counts,
    "expectedCategoryCounts": EXPECTED_CATEGORIES,
    "categoryCountMismatches": missing_or_wrong_categories,
    "unexpectedCategories": unpacked_category_counts,
    "soulCostByCategory": cost_by_category,
    "manualReviewTokensByCategory": review_tokens,
    "fieldPresenceByCategory": field_presence,
    "crawlPages": crawl.get("pages"),
    "crawlComplete": crawl.get("complete", False),
}
result["categoryTotalsMatch"] = category_counts == EXPECTED_CATEGORIES
result["costParseAccountedFor"] = (
    result["soulCostFullyParsed"] + result["soulCostNeedsReview"] == TARGET
)
result["complete"] = (
    result["firestoreSourceCount"] == TARGET
    and result["uniqueCards"] == TARGET
    and result["duplicateIds"] == 0
    and result["missingNames"] == 0
    and result["missingIndividualUrls"] == 0
    and result["missingListUrls"] == 0
    and result["distinctSourceFields"] == 55
    and result["taxonomyRows"] > 0
    and result["cardsWithTextBase"] == TARGET
    and result["cardsWithTextExtra"] == TARGET
    and result["cardsWithImageUrls"] == TARGET
    and result["imageRowsInDb"] == TARGET * 2
    and result["largeImageManifestRows"] == TARGET
    and result["smallImageManifestRows"] == TARGET
    and result["largeImagesDownloaded"] == TARGET
    and result["smallImagesDownloaded"] == TARGET
    and result["largeImageFailures"] == 0
    and result["smallImageFailures"] == 0
    and result["lpKnownCards"] == 289
    and result["lpZeroCards"] == 72
    and result["costParseAccountedFor"]
    and result["categoryTotalsMatch"]
    and not result["unexpectedCategories"]
    and result["crawlComplete"] is True
)
Path("data/audit-report.json").write_text(
    json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8"
)
print(json.dumps(result, ensure_ascii=False, indent=2))
con.close()
sys.exit(0 if result["complete"] else 2)
