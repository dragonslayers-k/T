#!/usr/bin/env python3
"""Stream-audit the immutable Release 27 WebP archive without extracting 30k files."""
import argparse
import hashlib
import io
import json
import re
import tarfile
from collections import Counter
from pathlib import Path

from PIL import Image

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--archive", required=True)
    ap.add_argument("--cards-jsonl", required=True)
    ap.add_argument("--output-dir", required=True)
    args = ap.parse_args()
    out = Path(args.output_dir)
    out.mkdir(parents=True, exist_ok=True)
    expected = set()
    with open(args.cards_jsonl, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                row = json.loads(line)
                cid = row.get("card_id")
                if cid is not None:
                    expected.add(str(cid))
    seen = set()
    counts = Counter()
    invalid = []
    unknown = []
    manifest = out / "image-manifest.jsonl"
    with tarfile.open(args.archive, mode="r|gz") as tf, manifest.open("w", encoding="utf-8") as mf:
        for member in tf:
            if not member.isfile() or not member.name.lower().endswith((".webp", ".png", ".jpg", ".jpeg")):
                continue
            name = member.name.replace("\\", "/")
            stem = Path(name).stem
            parts = [p.lower() for p in Path(name).parts]
            kind = "small" if "small" in parts else ("large" if "large" in parts else None)
            if not kind or stem not in expected:
                unknown.append(name)
                continue
            key = (stem, kind)
            if key in seen:
                invalid.append({"path": name, "error": "duplicate_card_size"})
                continue
            seen.add(key)
            stream = tf.extractfile(member)
            if stream is None:
                invalid.append({"path": name, "error": "unreadable_tar_member"})
                continue
            data = stream.read()
            record = {"card_id": stem, "image_type": kind, "archive_path": name,
                      "byte_size": len(data), "sha256": hashlib.sha256(data).hexdigest(),
                      "status": "verified"}
            try:
                with Image.open(io.BytesIO(data)) as im:
                    im.verify()
                    fmt = im.format
                    if fmt != "WEBP":
                        raise ValueError("not_webp:" + str(fmt))
                record["mime_type"] = "image/webp"
            except Exception as exc:
                record["status"] = "invalid_image"
                record["error"] = str(exc)
                invalid.append({"path": name, "error": str(exc)})
            counts[kind] += 1
            mf.write(json.dumps(record, ensure_ascii=False) + "\\n")
    missing = [{"card_id": cid, "image_type": size}
               for cid in sorted(expected) for size in ("small", "large")
               if (cid, size) not in seen]
    summary = {
        "expected_cards": len(expected),
        "expected_image_files": len(expected) * 2,
        "verified_candidates": sum(counts.values()),
        "small_files": counts["small"],
        "large_files": counts["large"],
        "missing_pairs": len(missing),
        "invalid_files": len(invalid),
        "unknown_paths": len(unknown),
        "complete": len(missing) == 0 and not invalid and not unknown and sum(counts.values()) == len(expected) * 2,
        "missing": missing,
        "invalid": invalid,
        "unknown_paths_sample": unknown[:100]
    }
    (out / "image-audit-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8")
    print(json.dumps({k:v for k,v in summary.items() if k not in ("missing","invalid","unknown_paths_sample")}, ensure_ascii=False))
    if invalid or missing or unknown:
        raise SystemExit("Image archive validation did not pass; see image-audit-summary.json")

if __name__ == "__main__":
    main()
