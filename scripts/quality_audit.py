#!/usr/bin/env python3
"""Quality audit for FM1 card records and downloaded images.

This audit intentionally distinguishes an absent value from an explicit zero.
It does not invent game values; it emits a machine-readable review queue for
later evidence-based inference. Image decoding is performed with Pillow.
"""
from __future__ import annotations
import argparse, collections, hashlib, json, math, sys
from pathlib import Path

EXPECTED = 15350
NUMERIC_FIELDS_BY_CATEGORY = {"1": ("RequireLP",), "2": ("HP",)}
ENCODED_FIELDS = ("RequireSoul",)
REQUIRED_IDENTITY = ("Name",)

def load_jsonl(path: Path):
    records = []
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                row = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
            records.append(row)
    return records

def raw_of(row):
    return row.get("raw_payload") if isinstance(row.get("raw_payload"), dict) else row

def audit(records, expected=EXPECTED):
    ids, duplicates, missing = set(), [], []
    field_counts = collections.Counter()
    categories = collections.Counter()
    review = []
    explicit_zero = collections.Counter()
    for index, row in enumerate(records):
        raw = raw_of(row)
        cid = str(row.get("card_id") or row.get("id") or raw.get("KIND") or f"row-{index}")
        if cid in ids:
            duplicates.append(cid)
        ids.add(cid)
        categories[str(raw.get("Category", "missing"))] += 1
        for key in raw:
            field_counts[key] += 1
        for key in REQUIRED_IDENTITY:
            if raw.get(key) is None or str(raw.get(key)).strip() == "":
                missing.append({"card_id": cid, "field": key, "reason": "missing_identity"})
        category = str(raw.get("Category", ""))
        for key in NUMERIC_FIELDS_BY_CATEGORY.get(category, ()):
            val = raw.get(key)
            if val is None or val == "":
                review.append({"card_id": cid, "field": key, "status": "missing", "game_value_required": True, "category": category})
            elif isinstance(val, (int, float)) and not isinstance(val, bool):
                if val == 0:
                    explicit_zero[key] += 1
                if not math.isfinite(float(val)) or val < 0:
                    review.append({"card_id": cid, "field": key, "status": "invalid_numeric", "raw": val, "category": category})
            else:
                review.append({"card_id": cid, "field": key, "status": "needs_numeric_parse", "raw": val, "category": category})
        for key in ENCODED_FIELDS:
            val = raw.get(key)
            if val is None or val == "":
                review.append({"card_id": cid, "field": key, "status": "missing_encoded_source", "game_value_required": False, "category": category})
            else:
                review.append({"card_id": cid, "field": key, "status": "encoded_source_present", "raw": val, "category": category})
    return {
        "expected_cards": expected, "record_count": len(records), "unique_ids": len(ids),
        "duplicate_ids": duplicates, "count_delta": len(records)-expected,
        "category_counts": dict(categories), "field_presence_counts": dict(field_counts),
        "missing_identity": missing, "explicit_zero_counts": dict(explicit_zero),
        "value_review_queue": review,
        "playable_values_filled": False,
        "note": "This tool audits source facts. Inference is a separate reviewed stage; missing values are not silently converted to zero."
    }

def audit_images(manifest_path: Path, root: Path):
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required: pip install Pillow") from exc
    rows = load_jsonl(manifest_path)
    result = {"manifest_rows": len(rows), "decoded": 0, "decode_failures": [], "hash_mismatches": [], "missing_files": []}
    for row in rows:
        local = row.get("local_path") or row.get("path")
        if not local:
            result["missing_files"].append({"card_id": row.get("card_id"), "image_type": row.get("image_type"), "reason": "no_path"})
            continue
        path = Path(local)
        if not path.is_absolute():
            path = root / path
        if not path.is_file():
            result["missing_files"].append({"card_id": row.get("card_id"), "image_type": row.get("image_type"), "path": str(path)})
            continue
        try:
            with Image.open(path) as image:
                image.verify()
            with Image.open(path) as image:
                image.load()
                width, height, fmt = image.width, image.height, image.format
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            result["decoded"] += 1
            if row.get("sha256") and row["sha256"] != digest:
                result["hash_mismatches"].append({"card_id": row.get("card_id"), "path": str(path), "expected": row["sha256"], "actual": digest})
        except Exception as exc:
            result["decode_failures"].append({"card_id": row.get("card_id"), "image_type": row.get("image_type"), "path": str(path), "error": str(exc)})
    result["image_integrity_pass"] = not (result["missing_files"] or result["decode_failures"] or result["hash_mismatches"])
    return result

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--cards-jsonl", type=Path)
    parser.add_argument("--image-manifest", type=Path)
    parser.add_argument("--image-root", type=Path, default=Path("data/images"))
    parser.add_argument("--expected", type=int, default=EXPECTED)
    parser.add_argument("--output", type=Path, default=Path("data/quality-audit.json"))
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()
    if args.self_test:
        sample = [{"card_id":"x","raw_payload":{"Name":"sample","Category":2,"RequireLP":0,"AP":0}}]
        result = audit(sample, expected=1)
        assert result["record_count"] == 1 and result["explicit_zero_counts"]["RequireLP"] == 1
        assert any(x["field"] == "HP" and x["status"] == "missing" for x in result["value_review_queue"])
        assert not any(x["field"] in ("AP", "DP") for x in result["value_review_queue"])
        assert any(x["field"] == "RequireSoul" and x["status"] == "encoded_source_present" for x in result["value_review_queue"])
        print("quality audit self-test passed")
        return 0
    if not args.cards_jsonl:
        parser.error("--cards-jsonl is required unless --self-test")
    report = audit(load_jsonl(args.cards_jsonl), args.expected)
    if args.image_manifest:
        report["images"] = audit_images(args.image_manifest, args.image_root)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k: report[k] for k in ("expected_cards","record_count","unique_ids","count_delta","duplicate_ids")}, ensure_ascii=False))
    return 0 if report["record_count"] == args.expected and not report["duplicate_ids"] else 2

if __name__ == "__main__":
    raise SystemExit(main())
