#!/usr/bin/env python3
"""Two-family conservative template audit of DB29 RequireSoul rail markers."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path
from PIL import Image, ImageChops

THRESHOLD = 0.015
FAMILIES = {
    "modern": {
        "ys": (103, 130, 157, 184, 211, 238, 265, 292),
        "crop": (1, -9, 21, 10),
        "templates": {
            "NCS": ("10020324677", 103),
            "MU": ("10020324677", 211),
            "BONUS": ("13041726794", 238),
        },
    },
    "legacy": {
        "ys": (88, 111, 134, 157, 180, 203, 226, 249, 272, 295, 318, 341, 364, 387),
        "crop": (7, -8, 25, 9),
        "templates": {
            "NCS": ("5042721718", 88),
            "MU": ("5042721718", 111),
            "BONUS_A": ("4061821131", 157),
            "BONUS_B": ("7111423264", 111),
        },
    },
}


def load_gray(path: Path) -> Image.Image:
    return Image.open(path).convert("L")


def marker_crop(image: Image.Image, center_y: int, crop: tuple[int, int, int, int]) -> Image.Image:
    left, top, right, bottom = crop
    return image.crop((left, center_y + top, right, center_y + bottom)).resize((40, 38))


def mse(a: Image.Image, b: Image.Image) -> float:
    hist = ImageChops.difference(a, b).histogram()
    return sum((i * i) * n for i, n in enumerate(hist)) / (a.width * a.height * 255.0 * 255.0)


def token_amounts(card: dict) -> Counter:
    result = Counter()
    for token in card.get("all_tokens", []):
        code = int(token.get("code", -1))
        if code in (81, 82, 83):
            result[{81: "MU", 82: "NCS", 83: "BONUS"}[code]] += int(token.get("amount", 0))
    return result


def build_templates(evidence: Path) -> dict:
    result = {}
    for family, spec in FAMILIES.items():
        result[family] = {}
        for label, (cid, y) in spec["templates"].items():
            path = evidence / "images" / "large" / f"{cid}.webp"
            if not path.is_file():
                raise SystemExit(f"Missing {family}/{label} template image: {path}")
            result[family][label] = marker_crop(load_gray(path), y, spec["crop"])
    return result


def detect_family(image: Image.Image, family: str, templates: dict) -> dict:
    spec = FAMILIES[family]
    detected, scores, unknown = Counter(), [], 0
    for y in spec["ys"]:
        patch = marker_crop(image, y, spec["crop"])
        label, score = min(
            ((name, mse(patch, template)) for name, template in templates[family].items()),
            key=lambda item: item[1],
        )
        scores.append(score)
        if score <= THRESHOLD:
            detected["BONUS" if label.startswith("BONUS") else label] += 1
        else:
            unknown += 1
    return {"detected": detected, "unknown": unknown, "score": min(scores), "mean_score": sum(scores) / len(scores)}


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
    templates = build_templates(evidence)

    fields = ["card_id", "name", "review_groups", "source_require_soul",
              "expected_ncs", "expected_MU", "expected_bonus",
              "detected_ncs", "detected_MU", "detected_bonus",
              "detected_family", "unknown_slots", "best_template_score", "status", "image_width", "image_height", "image_path"]
    rows, counts, family_matches = [], Counter(), Counter()
    special_population = 0
    for card in cards:
        cid = str(card["card_id"])
        groups = card.get("review_groups", [])
        expected = token_amounts(card)
        hybrid = any(str(g).startswith("hybrid:") for g in groups)
        rel = f"images/large/{cid}.webp"
        path = evidence / rel
        row = {
            "card_id": cid, "name": card.get("name", ""), "review_groups": ";".join(groups),
            "source_require_soul": card.get("source_require_soul", ""),
            "expected_ncs": expected["NCS"], "expected_MU": expected["MU"], "expected_bonus": expected["BONUS"],
            "detected_ncs": "", "detected_MU": "", "detected_bonus": "",
            "detected_family": "", "unknown_slots": "", "best_template_score": "",
            "status": "", "image_width": "", "image_height": "", "image_path": rel,
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
            row["image_width"], row["image_height"] = image.size
            if image.size != (285, 405):
                row["status"] = "LOW_RES_OR_NONSTANDARD_IMAGE"
            else:
                candidates = {family: detect_family(image, family, templates) for family in FAMILIES}
                exact = [
                    (family, result) for family, result in candidates.items()
                    if all(result["detected"][key] == expected[key] for key in ("NCS", "MU", "BONUS"))
                ]
                if exact:
                    family, result = min(exact, key=lambda item: item[1]["mean_score"])
                    row["status"] = "EXACT_COUNT_MATCH"
                    family_matches[family] += 1
                else:
                    family, result = min(candidates.items(), key=lambda item: (item[1]["unknown"], item[1]["mean_score"]))
                    row["status"] = "TEMPLATE_FAMILY_UNMATCHED" if result["unknown"] else "COUNT_MISMATCH"
                row.update({
                    "detected_ncs": result["detected"]["NCS"],
                    "detected_MU": result["detected"]["MU"],
                    "detected_bonus": result["detected"]["BONUS"],
                    "detected_family": family,
                    "unknown_slots": result["unknown"],
                    "best_template_score": f"{result['mean_score']:.5f}",
                })
        counts[row["status"]] += 1
        rows.append(row)

    with (out / "require-soul-rail-card-audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "source": "DB29 immutable release evidence, workflow run 42357466809",
        "expected_unique_cards": 831, "actual_unique_cards": len(cards),
        "method": "Two frame families; marker-template normalized grayscale MSE; threshold <= 0.015; exact source token count required.",
        "families": {
            "modern": {"slot_centers_y": list(FAMILIES["modern"]["ys"]), "template_cards": ["10020324677", "13041726794"]},
            "legacy": {"slot_centers_y": list(FAMILIES["legacy"]["ys"]), "template_cards": ["5042721718", "4061821131", "7111423264"]},
        },
        "counts": dict(counts), "exact_matches_by_family": dict(family_matches),
        "special_token_population": special_population,
        "exact_count_match_rate_of_special_population": round(counts["EXACT_COUNT_MATCH"] / max(1, special_population), 4),
        "interpretation": "EXACT_COUNT_MATCH means one of the two reviewed frame families matched NCS/MU/BONUS counts. LOW_RES_OR_NONSTANDARD_IMAGE remains unresolved. No DB source data is modified.",
    }
    (out / "require-soul-rail-audit-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
