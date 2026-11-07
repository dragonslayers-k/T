#!/usr/bin/env python3
"""Conservative template-based audit of DB29 RequireSoul left-rail markers."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageChops

SLOTS_Y = (103, 130, 157, 184, 211, 238, 265, 292)
TEMPLATE_CARDS = {
    "NCS": ("10020324677", 103),
    "NEUTRAL": ("10020324677", 211),
    "BONUS": ("13041726794", 238),
}
THRESHOLD = 0.015


def load_gray(path: Path) -> Image.Image:
    return Image.open(path).convert("L")


def marker_crop(image: Image.Image, center_y: int) -> Image.Image:
    return image.crop((1, center_y - 9, 21, center_y + 10)).resize((40, 38))


def mse(a: Image.Image, b: Image.Image) -> float:
    hist = ImageChops.difference(a, b).histogram()
    total = sum((i * i) * n for i, n in enumerate(hist))
    return total / (a.width * a.height * 255.0 * 255.0)


def token_amounts(card: dict) -> Counter:
    result = Counter()
    for token in card.get("all_tokens", []):
        code = int(token.get("code", -1))
        if code in (81, 82, 83):
            label = {81: "NEUTRAL", 82: "NCS", 83: "BONUS"}[code]
            result[label] += int(token.get("amount", 0))
    return result


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    evidence, out = args.evidence_dir, args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    cards_path = evidence / "target-cards.jsonl"
    if not cards_path.is_file():
        raise SystemExit(f"Missing target-cards.jsonl: {cards_path}")
    cards = [json.loads(x) for x in cards_path.read_text(encoding="utf-8").splitlines() if x.strip()]
    if len(cards) != 831 or len({c["card_id"] for c in cards}) != 831:
        raise SystemExit(f"Expected 831 unique cards, got {len(cards)}")

    templates = {}
    for label, (cid, y) in TEMPLATE_CARDS.items():
        path = evidence / "images" / "large" / f"{cid}.webp"
        if not path.is_file():
            raise SystemExit(f"Missing template image: {path}")
        templates[label] = marker_crop(load_gray(path), y)

    fields = ["card_id", "name", "review_groups", "source_require_soul",
              "expected_ncs", "expected_neutral", "expected_bonus",
              "detected_ncs", "detected_neutral", "detected_bonus",
              "unknown_slots", "best_template_score", "status", "image_path"]
    rows, counts = [], Counter()
    special_population = 0
    for card in cards:
        cid = str(card["card_id"])
        groups = card.get("review_groups", [])
        expected = token_amounts(card)
        hybrid = any(str(g).startswith("hybrid:") for g in groups)
        rel = f"images/large/{cid}.webp"
        path = evidence / rel
        row = {
            "card_id": cid, "name": card.get("name", ""),
            "review_groups": ";".join(groups),
            "source_require_soul": card.get("source_require_soul", ""),
            "expected_ncs": expected["NCS"], "expected_neutral": expected["NEUTRAL"],
            "expected_bonus": expected["BONUS"], "detected_ncs": "",
            "detected_neutral": "", "detected_bonus": "", "unknown_slots": "",
            "best_template_score": "", "status": "", "image_path": rel,
        }
        if hybrid:
            row["status"] = "HYBRID_OUT_OF_SCOPE"
        elif not any(expected.values()):
            row["status"] = "NO_SPECIAL_TOKEN"
        elif not path.is_file():
            row["status"] = "IMAGE_MISSING"
        else:
            special_population += 1
            image = load_gray(path)
            if image.size != (285, 405):
                row["status"] = "NONSTANDARD_IMAGE_SIZE"
            else:
                detected, scores, unknown = Counter(), [], 0
                for y in SLOTS_Y:
                    patch = marker_crop(image, y)
                    label, score = min(
                        ((name, mse(patch, template)) for name, template in templates.items()),
                        key=lambda item: item[1],
                    )
                    scores.append(score)
                    if score <= THRESHOLD:
                        detected[label] += 1
                    else:
                        unknown += 1
                row.update({
                    "detected_ncs": detected["NCS"],
                    "detected_neutral": detected["NEUTRAL"],
                    "detected_bonus": detected["BONUS"],
                    "unknown_slots": unknown,
                    "best_template_score": f"{min(scores):.5f}",
                })
                if all(detected[k] == expected[k] for k in ("NCS", "NEUTRAL", "BONUS")):
                    row["status"] = "EXACT_COUNT_MATCH"
                else:
                    row["status"] = "TEMPLATE_FAMILY_UNMATCHED" if unknown else "COUNT_MISMATCH"
        counts[row["status"]] += 1
        rows.append(row)

    with (out / "require-soul-rail-card-audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "source": "DB29 immutable release evidence, workflow run 42357466809",
        "expected_unique_cards": 831,
        "actual_unique_cards": len(cards),
        "template_method": "8 left-rail slots; normalized grayscale marker-template MSE; threshold <= 0.015",
        "templates": {k: {"card_id": v[0], "center_y": v[1]} for k, v in TEMPLATE_CARDS.items()},
        "counts": dict(counts),
        "special_token_population": special_population,
        "exact_count_match_rate_of_special_population": round(counts["EXACT_COUNT_MATCH"] / max(1, special_population), 4),
        "interpretation": "EXACT_COUNT_MATCH means known NCS/neutral/BONUS marker templates matched source counts. TEMPLATE_FAMILY_UNMATCHED is unresolved, not a source-data error. No DB source data is modified.",
    }
    (out / "require-soul-rail-audit-summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
