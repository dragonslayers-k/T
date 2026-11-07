#!/usr/bin/env python3
"""Stream-extract the exact DB29 card images in the RequireSoul semantic-review queue.

The source image archive is large. This tool reads it sequentially and writes only
small/large images for cards whose RequireSoul contains one of the 14 hybrid
tokens or NCS(82)/BONUS(83). It never changes DB29 or assigns payment semantics.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import tarfile
from collections import Counter
from pathlib import Path, PurePosixPath
from typing import Iterable

HYBRID_CODES = {
    12: "DARK_EARTH", 13: "DARK_FIRE", 14: "DARK_LIGHT", 15: "DARK_WATER",
    22: "FIRE_FOREST", 23: "FIRE_IRON", 24: "FIRE_WATER",
    32: "WATER_EARTH", 33: "WATER_FOREST", 42: "FOREST_IRON",
    43: "FOREST_LIGHT", 52: "IRON_EARTH", 53: "IRON_LIGHT", 62: "EARTH_LIGHT",
}
SPECIAL_CODES = {82: "NCS", 83: "BONUS"}
REVIEW_CODES = set(HYBRID_CODES) | set(SPECIAL_CODES)


def raw_of(row: dict) -> dict:
    value = row.get("raw_payload")
    return value if isinstance(value, dict) else row


def parse_tokens(raw_value: object) -> list[dict]:
    if not isinstance(raw_value, str) or not raw_value.isdigit() or len(raw_value) % 4:
        return []
    result = []
    for ordinal in range(0, len(raw_value), 4):
        token = raw_value[ordinal:ordinal + 4]
        code = int(token[:2])
        amount = int(token[2:])
        result.append({
            "ordinal": ordinal // 4,
            "raw": token,
            "code": code,
            "amount": amount,
            "symbol": HYBRID_CODES.get(code) or SPECIAL_CODES.get(code),
            "review_group": (
                "hybrid:" + HYBRID_CODES[code] if code in HYBRID_CODES
                else SPECIAL_CODES.get(code) if code in SPECIAL_CODES
                else None
            ),
        })
    return result


def build_target_cards(rows: Iterable[dict], expected_cards: int | None = 831) -> dict[str, dict]:
    targets: dict[str, dict] = {}
    for row in rows:
        raw = raw_of(row)
        card_id = str(row.get("card_id") or row.get("id") or raw.get("ID") or "").strip()
        if not card_id:
            continue
        source_cost = raw.get("RequireSoul", row.get("requireSoul"))
        tokens = parse_tokens(source_cost)
        review_tokens = [token for token in tokens if token["code"] in REVIEW_CODES]
        if not review_tokens:
            continue

        groups = sorted({token["review_group"] for token in review_tokens if token["review_group"]})
        record = {
            "card_id": card_id,
            "name": str(row.get("name") or raw.get("Name") or ""),
            "card_type": str(row.get("card_type") or row.get("type") or raw.get("Category") or ""),
            "source_card_url": row.get("source_card_url") or row.get("sourceCardUrl"),
            "source_require_soul": str(source_cost or ""),
            "all_tokens": tokens,
            "review_tokens": review_tokens,
            "review_groups": groups,
        }
        previous = targets.get(card_id)
        if previous and previous["source_require_soul"] != record["source_require_soul"]:
            raise ValueError(f"Duplicate card ID has conflicting RequireSoul: {card_id}")
        targets[card_id] = record

    if expected_cards is not None and len(targets) != expected_cards:
        raise ValueError(
            f"Target card population mismatch: expected {expected_cards}, found {len(targets)}"
        )
    return dict(sorted(targets.items()))


def export_archive(
    archive_path: Path,
    rows: Iterable[dict],
    output_dir: Path,
    expected_cards: int | None = 831,
) -> dict:
    try:
        from PIL import Image
    except ImportError as exc:
        raise RuntimeError("Pillow is required for image verification") from exc

    targets = build_target_cards(rows, expected_cards)
    target_ids = set(targets)
    output_dir.mkdir(parents=True, exist_ok=True)
    image_root = output_dir / "images"
    image_root.mkdir(parents=True, exist_ok=True)

    manifest_path = output_dir / "image-manifest.jsonl"
    seen: set[tuple[str, str]] = set()
    counts = Counter()
    invalid = []

    with tarfile.open(archive_path, mode="r|gz") as archive, manifest_path.open(
        "w", encoding="utf-8"
    ) as manifest:
        for member in archive:
            if not member.isfile() or not member.name.lower().endswith(".webp"):
                continue
            normalized_name = member.name.replace("\\", "/")
            parts = [part.lower() for part in PurePosixPath(normalized_name).parts]
            image_type = "small" if "small" in parts else "large" if "large" in parts else None
            card_id = PurePosixPath(normalized_name).stem
            if image_type is None or card_id not in target_ids:
                continue

            key = (card_id, image_type)
            if key in seen:
                invalid.append({"card_id": card_id, "image_type": image_type, "error": "duplicate_image"})
                continue
            stream = archive.extractfile(member)
            if stream is None:
                invalid.append({"card_id": card_id, "image_type": image_type, "error": "unreadable_member"})
                continue
            data = stream.read()
            record = {
                "card_id": card_id,
                "image_type": image_type,
                "archive_path": normalized_name,
                "byte_size": len(data),
                "sha256": hashlib.sha256(data).hexdigest(),
                "status": "verified",
            }
            try:
                with Image.open(io.BytesIO(data)) as image:
                    image.verify()
                with Image.open(io.BytesIO(data)) as image:
                    image.load()
                    record["width"] = image.width
                    record["height"] = image.height
                    if image.format != "WEBP":
                        raise ValueError("not_webp:" + str(image.format))
            except Exception as exc:
                record["status"] = "invalid_image"
                record["error"] = str(exc)
                invalid.append({"card_id": card_id, "image_type": image_type, "error": str(exc)})
            else:
                destination = image_root / image_type / f"{card_id}.webp"
                destination.parent.mkdir(parents=True, exist_ok=True)
                destination.write_bytes(data)
                seen.add(key)
                counts[image_type] += 1
            manifest.write(json.dumps(record, ensure_ascii=False) + "\n")

    expected_images = len(targets) * 2
    missing = [
        {"card_id": card_id, "image_type": image_type}
        for card_id in sorted(target_ids)
        for image_type in ("small", "large")
        if (card_id, image_type) not in seen
    ]
    summary = {
        "source": "immutable Release fm1-carddb-29",
        "expected_cards": len(targets),
        "expected_images": expected_images,
        "verified_images": sum(counts.values()),
        "small_images": counts["small"],
        "large_images": counts["large"],
        "missing_images": len(missing),
        "invalid_images": len(invalid),
        "complete": len(missing) == 0 and not invalid and sum(counts.values()) == expected_images,
        "policy": {
            "source_db_modified": False,
            "db30_published": False,
            "payment_semantics_assigned": False,
            "selection": "14 RequireSoul hybrid codes + NCS(82) + BONUS(83)",
        },
        "missing": missing,
        "invalid": invalid,
    }
    (output_dir / "target-cards.jsonl").write_text(
        "".join(json.dumps(record, ensure_ascii=False) + "\n" for record in targets.values()),
        encoding="utf-8",
    )
    (output_dir / "image-audit-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2), encoding="utf-8"
    )
    if not summary["complete"]:
        raise RuntimeError(
            f"Focused image evidence is incomplete: {len(missing)} missing, {len(invalid)} invalid"
        )
    return summary


def load_jsonl(path: Path) -> list[dict]:
    rows = []
    with path.open(encoding="utf-8") as stream:
        for line_no, line in enumerate(stream, 1):
            if not line.strip():
                continue
            try:
                rows.append(json.loads(line))
            except json.JSONDecodeError as exc:
                raise ValueError(f"{path}:{line_no}: invalid JSON: {exc}") from exc
    return rows


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--archive", type=Path, required=True)
    parser.add_argument("--cards-jsonl", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--expected-cards", type=int, default=831)
    args = parser.parse_args()
    summary = export_archive(
        args.archive, load_jsonl(args.cards_jsonl), args.output_dir, args.expected_cards
    )
    print(json.dumps({key: value for key, value in summary.items() if key not in ("missing", "invalid")}, ensure_ascii=False))


if __name__ == "__main__":
    main()
