#!/usr/bin/env python3
"""Visual consistency audit for all DB29 hybrid RequireSoul orb classes."""
from __future__ import annotations
import argparse, csv, json
from collections import Counter
from pathlib import Path
from PIL import Image
import numpy as np

CROP_BOX = (1, 94, 21, 113)
SIZE = (40, 38)
MANUAL_VISUAL_CONFIRMATIONS = {
    "13052926873": "The orb is visibly red/blue (FIRE_WATER); RGB template distance ranks WATER_EARTH due to this card's alternate rendering. Manually confirmed against source artwork."
}


def orb(path: Path) -> np.ndarray:
    image = Image.open(path).convert("RGB").crop(CROP_BOX).resize(SIZE)
    return np.asarray(image, dtype=np.float32)


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

    refs = {}
    for card, token in hybrids:
        code = int(token["code"])
        refs.setdefault(code, (str(card["card_id"]), orb(evidence / "images" / "large" / f"{card['card_id']}.webp")))
    rows, counts = [], Counter()
    for card, token in hybrids:
        cid, expected = str(card["card_id"]), int(token["code"])
        image_path = evidence / "images" / "large" / f"{cid}.webp"
        if not image_path.is_file():
            status, predicted, score, candidates = "IMAGE_MISSING", "", "", []
        else:
            patch = orb(image_path)
            distances = {code: mse(patch, template) for code, (_, template) in refs.items()}
            ranked = sorted(distances.items(), key=lambda item: item[1])
            predicted, score = ranked[0]
            candidates = [{"code": code, "symbol": next(t.get("symbol") for c, t in hybrids if int(t["code"]) == code), "mse": round(value, 6)} for code, value in ranked[:3]]
            if predicted == expected:
                status = "TEMPLATE_MATCH"
            elif cid in MANUAL_VISUAL_CONFIRMATIONS:
                status = "MANUAL_VISUAL_CONFIRMED"
            else:
                status = "MANUAL_REVIEW"
        counts[status] += 1
        rows.append({
            "card_id": cid, "name": card.get("name", ""),
            "expected_hybrid_code": expected, "expected_symbol": token.get("symbol", ""),
            "template_reference_card_id": refs.get(expected, ("", None))[0],
            "predicted_code": predicted, "best_mse": f"{score:.6f}" if score != "" else "",
            "top_3_candidates_json": json.dumps(candidates, ensure_ascii=False),
            "status": status, "manual_note": MANUAL_VISUAL_CONFIRMATIONS.get(cid, ""),
            "source_require_soul": card.get("source_require_soul", ""),
        })
    fields = ["card_id", "name", "expected_hybrid_code", "expected_symbol", "template_reference_card_id",
              "predicted_code", "best_mse", "top_3_candidates_json", "status", "manual_note", "source_require_soul"]
    with (out / "require-soul-hybrid-orb-audit.csv").open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)
    summary = {
        "population": len(hybrids), "hybrid_codes": len(refs),
        "method": "RGB crop of first left-rail hybrid orb (x=1..20, y=94..112), nearest reference template by normalized RGB MSE.",
        "reference_cards_by_code": {str(code): card_id for code, (card_id, _) in refs.items()},
        "counts": dict(counts),
        "manual_visual_confirmations": MANUAL_VISUAL_CONFIRMATIONS,
        "interpretation": "TEMPLATE_MATCH indicates same-code orb appearance. MANUAL_VISUAL_CONFIRMED is an explicit visual override. This audit checks hybrid-orb class identity, not the entire remaining single-element rail sequence.",
    }
    (out / "require-soul-hybrid-orb-audit-summary.json").write_text(json.dumps(summary, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(summary, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
