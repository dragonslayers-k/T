#!/usr/bin/env python3
"""Full visual sequence audit for DB29 hybrid RequireSoul cards."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path
from PIL import Image
import numpy as np

SIZE = (40, 38)
HYBRID_CROP = (1, 94, 21, 113)
SINGLE_CROP = (1, -9, 21, 10)
SECONDARY_Y = (130, 157, 184, 211, 238, 265, 292)
HYBRID_MANUAL_CONFIRMATIONS = {
    "13052926873": "The first orb is visibly red/blue (FIRE_WATER). RGB nearest-template distance ranks WATER_EARTH because this card uses an alternate orb rendering; manually confirmed against source artwork."
}
HYBRID_CODE_REFS = {
    13: "10012010131", 24: "10012010132", 33: "10012010133",
    42: "10012010134", 52: "10012010135", 62: "10012010136",
    14: "10012010137", 12: "13020610159", 23: "13020610160",
    15: "13020610161", 22: "13020610162", 53: "13020610163",
    32: "13020610164", 43: "13020610165",
}
SINGLE_CODE_REFS = {
    11: ("10012010131", 130), 21: ("10012010132", 130),
    31: ("10012010133", 130), 41: ("10012010134", 130),
    51: ("10012010135", 130), 61: ("10012010136", 130),
    71: ("10012010137", 130), 81: ("10042124823", 184),
}


def image_crop(path: Path, box: tuple[int, int, int, int]) -> np.ndarray:
    image = Image.open(path).convert("RGB").crop(box).resize(SIZE)
    return np.asarray(image, dtype=np.float32)


def slot_crop(image: Image.Image, center_y: int) -> np.ndarray:
    return np.asarray(image.convert("RGB").crop((1, center_y - 9, 21, center_y + 10)).resize(SIZE), dtype=np.float32)


def mse(a: np.ndarray, b: np.ndarray) -> float:
    return float(np.mean((a - b) ** 2) / (255.0 ** 2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--evidence-dir", type=Path, required=True)
    ap.add_argument("--output-dir", type=Path, required=True)
    args = ap.parse_args()
    evidence, out = args.evidence_dir, args.output_dir
    out.mkdir(parents=True, exist_ok=True)
    cards = [json.loads(x) for x in (evidence / "target-cards.jsonl").read_text(encoding="utf-8").splitlines() if x.strip()]
    hybrids = []
    for card in cards:
        token = next((t for t in card.get("all_tokens", []) if str(t.get("review_group", "")).startswith("hybrid:")), None)
        if token:
            hybrids.append((card, token))
    if len(hybrids) != 52:
        raise SystemExit(f"Expected 52 hybrid cards, got {len(hybrids)}")

    hybrid_templates = {}
    for code, cid in HYBRID_CODE_REFS.items():
        hybrid_templates[code] = image_crop(evidence / "images" / "large" / f"{cid}.webp", HYBRID_CROP)
    secondary_templates = {}
    for code, (cid, y) in SINGLE_CODE_REFS.items():
        secondary_templates[code] = image_crop(evidence / "images" / "large" / f"{cid}.webp", (1, y - 9, 21, y + 10))

    rows, counts = [], Counter()
    for card, hybrid_token in hybrids:
        cid = str(card["card_id"])
        expected_hybrid = int(hybrid_token["code"])
        path = evidence / "images" / "large" / f"{cid}.webp"
        if not path.is_file():
            status, predicted, hybrid_score = "IMAGE_MISSING", "", ""
            expected_secondary, detected_secondary = Counter(), Counter()
        else:
            image = Image.open(path).convert("RGB")
            first_orb = slot_crop(image, 103)
            hybrid_distances = {code: mse(first_orb, template) for code, template in hybrid_templates.items()}
            predicted = min(hybrid_distances, key=hybrid_distances.get)
            hybrid_score = hybrid_distances[predicted]

            expected_secondary = Counter()
            for token in card.get("all_tokens", []):
                code = int(token.get("code", -1))
                if code in SINGLE_CODE_REFS:
                    expected_secondary[code] += int(token.get("amount", 0))

            detected_secondary = Counter()
            for y in SECONDARY_Y:
                patch = slot_crop(image, y)
                code, score = min(
                    ((code, mse(patch, template)) for code, template in secondary_templates.items()),
                    key=lambda item: item[1],
                )
                if score <= 0.01:
                    detected_secondary[code] += 1

            hybrid_ok = predicted == expected_hybrid or cid in HYBRID_MANUAL_CONFIRMATIONS
            secondary_ok = all(detected_secondary[c] == expected_secondary[c] for c in SINGLE_CODE_REFS)
            if hybrid_ok and secondary_ok:
                status = "FULL_SEQUENCE_MATCH_MANUAL_HYBRID" if cid in HYBRID_MANUAL_CONFIRMATIONS else "FULL_SEQUENCE_MATCH"
            elif not secondary_ok:
                status = "SECONDARY_SEQUENCE_MISMATCH"
            else:
                status = "HYBRID_ORB_REVIEW"
        counts[status] += 1
        rows.append({
            "card_id": cid, "name": card.get("name", ""),
            "expected_hybrid_code": expected_hybrid, "expected_hybrid_symbol": hybrid_token.get("symbol", ""),
            "predicted_hybrid_code": predicted,
            "hybrid_orb_mse": f"{hybrid_score:.6f}" if hybrid_score != "" else "",
            "expected_secondary_tokens_json": json.dumps(dict(expected_secondary), ensure_ascii=False, sort_keys=True),
            "detected_secondary_tokens_json": json.dumps(dict(detected_secondary), ensure_ascii=False, sort_keys=True),
            "secondary_sequence_match": all(detected_secondary[c] == expected_secondary[c] for c in SINGLE_CODE_REFS),
            "status": status,
            "manual_note": HYBRID_MANUAL_CONFIRMATIONS.get(cid, ""),
            "source_require_soul": card.get("source_require_soul", ""),
        })
    fields = ["card_id", "name", "expected_hybrid_code", "expected_hybrid_symbol", "predicted_hybrid_code",
              "hybrid_orb_mse", "expected_secondary_tokens_json", "detected_secondary_tokens_json",
              "secondary_sequence_match", "status", "manual_note", "source_require_soul"]
    with (out / "require-soul-hybrid-orb-audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "population": 52, "hybrid_code_classes": len(hybrid_templates),
        "secondary_marker_classes": len(secondary_templates),
        "method": "First hybrid orb RGB template comparison plus 7 following left-rail positions classified against 7 elemental and MU reference templates; exact secondary token counts required.",
        "counts": dict(counts),
        "hybrid_template_reference_cards": {str(k): v for k, v in HYBRID_CODE_REFS.items()},
        "secondary_template_reference_cards": {str(k): {"card_id": v[0], "center_y": v[1]} for k, v in SINGLE_CODE_REFS.items()},
        "manual_visual_confirmations": HYBRID_MANUAL_CONFIRMATIONS,
        "interpretation": "FULL_SEQUENCE_MATCH verifies hybrid orb class and following elemental/MU marker counts. FULL_SEQUENCE_MATCH_MANUAL_HYBRID includes one explicit manual visual confirmation for alternate rendering.",
    }
    (out / "require-soul-hybrid-orb-audit-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
