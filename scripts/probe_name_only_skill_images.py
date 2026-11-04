#!/usr/bin/env python3
"""OCR archived large card images for evidence about name-only inferred skills.

OCR output is evidence only. It never promotes rules or marks them executable.
"""
import argparse
import hashlib
import json
import re
import sqlite3
import tarfile
import io
from pathlib import Path


def normalize_text(value):
    return re.sub(r"\\s+", "", value or "").casefold()


def contains_skill_name(ocr_text, skill_name):
    return bool(normalize_text(skill_name) and
                normalize_text(skill_name) in normalize_text(ocr_text))


def probe(db_path: Path, archive_path: Path, output: Path):
    from PIL import Image, ImageEnhance, ImageOps
    import pytesseract

    db = sqlite3.connect(db_path)
    db.row_factory = sqlite3.Row
    skills = db.execute("""
      SELECT e.source_field,e.source_enum_value,e.source_name,e.card_count,e.rule_id
      FROM skill_enum_inventory e JOIN game_rule_catalog g USING(rule_id)
      WHERE e.mapping_status='inferred' AND g.confidence='low'
      ORDER BY e.source_field,e.source_enum_value
    """).fetchall()
    skill_cards = {}
    target_ids = set()
    for skill in skills:
        cards = db.execute("""
          SELECT DISTINCT c.card_id,c.name,c.source_card_url
          FROM card_rule_mappings m JOIN cards c USING(card_id)
          WHERE m.source_field=? AND m.source_enum_value=? AND m.source_name=?
          ORDER BY c.card_id
        """, (skill["source_field"], skill["source_enum_value"], skill["source_name"])).fetchall()
        skill_cards[(skill["source_field"], str(skill["source_enum_value"]), skill["source_name"])] = [
            {"cardId": str(c["card_id"]), "cardName": c["name"], "sourceCardUrl": c["source_card_url"]}
            for c in cards
        ]
        target_ids.update(str(c["card_id"]) for c in cards)

    image_results = {}
    with tarfile.open(archive_path, mode="r|gz") as tf:
        for member in tf:
            if not member.isfile() or not member.name.lower().endswith((".webp", ".png", ".jpg", ".jpeg")):
                continue
            path = member.name.replace("\\", "/")
            parts = [p.lower() for p in Path(path).parts]
            card_id = Path(path).stem
            if card_id not in target_ids:
                continue
            kind = "large" if "large" in parts else ("small" if "small" in parts else "")
            if not kind:
                continue
            if card_id in image_results and image_results[card_id].get("imageType") == "large":
                continue
            stream = tf.extractfile(member)
            if stream is None:
                continue
            data = stream.read()
            try:
                with Image.open(io.BytesIO(data)) as original:
                    image = ImageOps.exif_transpose(original).convert("L")
                    if image.width < 1400:
                        scale = min(3, max(2, 1400 // max(1, image.width)))
                        image = image.resize((image.width * scale, image.height * scale))
                    image = ImageEnhance.Contrast(image).enhance(1.8)
                    ocr = pytesseract.image_to_string(image, lang="kor+eng", config="--psm 6")
                    image_results[card_id] = {
                        "imageType": kind, "archivePath": path,
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "width": original.width, "height": original.height,
                        "ocrText": ocr[:10000]
                    }
            except Exception as exc:
                image_results[card_id] = {
                    "imageType": kind, "archivePath": path,
                    "ocrError": f"{type(exc).__name__}: {exc}"[:500]
                }

    skill_results = []
    for skill in skills:
        key = (skill["source_field"], str(skill["source_enum_value"]), skill["source_name"])
        cards = []
        for card in skill_cards[key]:
            image = image_results.get(card["cardId"], {})
            text = image.get("ocrText", "")
            cards.append({
                **card, "imageEvidence": image,
                "skillNameFoundByOcr": contains_skill_name(text, skill["source_name"])
            })
        skill_results.append({
            "sourceField": skill["source_field"], "sourceEnumValue": str(skill["source_enum_value"]),
            "skillName": skill["source_name"], "cardCount": skill["card_count"],
            "ruleId": skill["rule_id"], "cards": cards
        })

    result = {
        "source": "archived original card images",
        "evidencePolicy": "OCR is a candidate transcription only; it does not verify rule semantics.",
        "lowConfidenceSkillKinds": len(skills), "targetCardIds": len(target_ids),
        "imagesOcrProcessed": sum(1 for x in image_results.values() if "ocrText" in x),
        "skillsWithOcrNameMatch": sum(1 for s in skill_results if any(c["skillNameFoundByOcr"] for c in s["cards"])),
        "skills": skill_results
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    db.close()
    matched = []
    for skill in skill_results:
        for card in skill["cards"]:
            if card["skillNameFoundByOcr"]:
                matched.append({
                    "skillName": skill["skillName"], "cardId": card["cardId"],
                    "cardName": card["cardName"],
                    "imageType": card["imageEvidence"].get("imageType"),
                    "archivePath": card["imageEvidence"].get("archivePath"),
                    "ocrText": card["imageEvidence"].get("ocrText", "")[:1800]
                })
    print(json.dumps({
        **{k: result[k] for k in ("lowConfidenceSkillKinds", "targetCardIds",
            "imagesOcrProcessed", "skillsWithOcrNameMatch")},
        "matchedSkillEvidence": matched
    }, ensure_ascii=False))
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--db", type=Path, default=Path("data/fm1_cards.sqlite"))
    parser.add_argument("--archive", type=Path, default=Path("data/images.tar.gz"))
    parser.add_argument("--out", type=Path, default=Path("data/gap-reports/name-only-skill-image-probe.json"))
    args = parser.parse_args()
    probe(args.db, args.archive, args.out)


if __name__ == "__main__":
    main()
