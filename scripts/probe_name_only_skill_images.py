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
from difflib import SequenceMatcher


def normalize_text(value):
    return re.sub(r"[\W_]+", "", value or "", flags=re.UNICODE).casefold()


def contains_skill_name(ocr_text, skill_name):
    return bool(normalize_text(skill_name) and
                normalize_text(skill_name) in normalize_text(ocr_text))


def fuzzy_skill_name_match(ocr_text, skill_name, threshold=0.78):
    target=normalize_text(skill_name)
    source=normalize_text(ocr_text)
    if not target or target in source:
        return {"matched":False,"score":1.0 if target and target in source else 0.0,"matchedText":target or None}
    if len(target)<4 or len(source)<len(target)-1:
        return {"matched":False,"score":0.0,"matchedText":None}
    best_score=0.0
    best_text=None
    for width in range(max(3,len(target)-1),len(target)+2):
        for start in range(0,max(0,len(source)-width+1)):
            candidate=source[start:start+width]
            raw_score=SequenceMatcher(None,target,candidate,autojunk=False).ratio()
            length_penalty=min(len(target),len(candidate))/max(len(target),len(candidate))
            score=raw_score*length_penalty
            if score>best_score:
                best_score,best_text=score,candidate
    return {"matched":best_score>=threshold,"score":round(best_score,4),
            "matchedText":best_text if best_score>=threshold else None}




def classify_image_match(skill_name, card_name, exact, fuzzy, matched_text, ocr_text):
    skill_key=normalize_text(skill_name)
    card_key=normalize_text(card_name)
    lines=[line.strip() for line in (ocr_text or "").splitlines() if line.strip()]
    candidates=[]
    for line in lines:
        line_key=normalize_text(line)
        if skill_key and skill_key in line_key:
            candidates.append(line)
        elif matched_text and normalize_text(matched_text) and normalize_text(matched_text) in line_key:
            candidates.append(line)
    candidates.sort(key=lambda line: ("/" not in line and "／" not in line, len(line)))
    context=candidates[0] if candidates else None
    has_slash=bool(context and ("/" in context or "／" in context))
    name_collision=bool(skill_key and card_key and skill_key==card_key and not has_slash)
    if exact and not name_collision:
        if has_slash or (context and len(context)<=42 and not re.search(r"[.!?。！？]",context)):
            status="image_text_exact"
        else:
            status="exact_text_unclassified"
    elif exact and name_collision:
        status="name_collision"
    elif fuzzy and name_collision:
        status="name_collision"
    elif fuzzy:
        status="fuzzy_candidate"
    else:
        status="not_found"
    return status,context,has_slash,name_collision

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
                        scale = min(4, max(2, 1400 // max(1, image.width)))
                        image = image.resize((image.width * scale, image.height * scale))
                    image = ImageOps.autocontrast(ImageEnhance.Contrast(image).enhance(1.8))
                    center = image.crop((0,int(image.height*0.22),image.width,int(image.height*0.86)))
                    lower = image.crop((0,int(image.height*0.38),image.width,int(image.height*0.78)))
                    passes=[
                        {"name":"full_psm6","text":pytesseract.image_to_string(image,lang="kor+eng",config="--psm 6")},
                        {"name":"full_psm11","text":pytesseract.image_to_string(image,lang="kor+eng",config="--psm 11")},
                        {"name":"center_psm6","text":pytesseract.image_to_string(center,lang="kor+eng",config="--psm 6")},
                        {"name":"lower_psm6","text":pytesseract.image_to_string(lower,lang="kor+eng",config="--psm 6")}
                    ]
                    ocr="\n".join("["+x["name"]+"]\n"+x["text"] for x in passes)
                    image_results[card_id] = {
                        "imageType": kind, "archivePath": path,
                        "sha256": hashlib.sha256(data).hexdigest(),
                        "width": original.width, "height": original.height,
                        "ocrPasses": passes, "ocrText": ocr[:20000]
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
            exact=contains_skill_name(text,skill["source_name"])
            fuzzy=fuzzy_skill_name_match(text,skill["source_name"])
            fuzzy_candidate=bool(not exact and fuzzy["matched"])
            match_status,match_context,context_has_slash,name_collision=classify_image_match(
                skill["source_name"],card["cardName"],exact,fuzzy_candidate,fuzzy["matchedText"],text)
            cards.append({
                **card, "imageEvidence": image,
                "skillNameFoundByOcr": exact,
                "skillNameFuzzyCandidate": fuzzy_candidate,
                "skillNameMatchScore": fuzzy["score"] if not exact else 1.0,
                "skillNameMatchText": fuzzy["matchedText"],
                "skillNameMatchMethod": "exact_normalized" if exact else ("fuzzy_candidate" if fuzzy_candidate else "not_found"),
                "skillNameEvidenceStatus":match_status,
                "skillNameMatchContext":match_context,
                "skillNameContextHasSlash":context_has_slash,
                "skillNameCardNameCollision":name_collision
            })
        skill_results.append({
            "sourceField": skill["source_field"], "sourceEnumValue": str(skill["source_enum_value"]),
            "skillName": skill["source_name"], "cardCount": skill["card_count"],
            "ruleId": skill["rule_id"], "cards": cards
        })

    db.executescript("""
    CREATE TABLE IF NOT EXISTS card_skill_ocr_evidence(
      card_id TEXT NOT NULL REFERENCES cards(card_id),
      source_field TEXT NOT NULL,
      source_enum_value TEXT NOT NULL,
      source_name TEXT NOT NULL,
      skill_rule_id TEXT,
      image_type TEXT NOT NULL,
      image_archive_path TEXT,
      image_sha256 TEXT,
      match_status TEXT NOT NULL,
      match_score REAL,
      matched_text TEXT,
      match_context TEXT,
      context_has_slash INTEGER NOT NULL,
      card_name_equals_skill_name INTEGER NOT NULL,
      ocr_passes_json TEXT NOT NULL,
      ocr_text_sha256 TEXT,
      evidence_policy TEXT NOT NULL,
      rule_semantics_verified INTEGER NOT NULL DEFAULT 0,
      executable INTEGER NOT NULL DEFAULT 0,
      PRIMARY KEY(card_id,source_field,source_enum_value,image_type)
    );
    """)
    db.execute("DELETE FROM card_skill_ocr_evidence")
    evidence_rows=[]
    for skill in skill_results:
        for card in skill["cards"]:
            image=card.get("imageEvidence",{})
            ocr_text=image.get("ocrText","")
            passes=[{"name":p.get("name"),"sha256":hashlib.sha256(p.get("text","").encode("utf-8")).hexdigest()}
                    for p in image.get("ocrPasses",[])]
            evidence_rows.append((
                str(card["cardId"]),skill["sourceField"],skill["sourceEnumValue"],skill["skillName"],
                str(skill["ruleId"]),image.get("imageType") or "unknown",image.get("archivePath"),
                image.get("sha256"),card.get("skillNameEvidenceStatus","not_found"),
                float(card.get("skillNameMatchScore") or 0),card.get("skillNameMatchText"),
                card.get("skillNameMatchContext"),int(bool(card.get("skillNameContextHasSlash"))),
                int(bool(card.get("skillNameCardNameCollision"))),json.dumps(passes,ensure_ascii=False),
                hashlib.sha256(ocr_text.encode("utf-8")).hexdigest() if ocr_text else None,
                "image_text_only_not_semantic",0,0
            ))
    if evidence_rows:
        db.executemany("""INSERT OR REPLACE INTO card_skill_ocr_evidence
          (card_id,source_field,source_enum_value,source_name,skill_rule_id,image_type,image_archive_path,
           image_sha256,match_status,match_score,matched_text,match_context,context_has_slash,
           card_name_equals_skill_name,ocr_passes_json,ocr_text_sha256,evidence_policy,
           rule_semantics_verified,executable)
          VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",evidence_rows)
    db.commit()
    evidence_counts={r[0]:r[1] for r in db.execute("SELECT match_status,COUNT(*) FROM card_skill_ocr_evidence GROUP BY match_status")}
    db.close()

    result = {
        "source": "archived original card images",
        "evidencePolicy": "OCR is a candidate transcription only; it does not verify rule semantics.",
        "lowConfidenceSkillKinds": len(skills), "targetCardIds": len(target_ids),
        "imagesOcrProcessed": sum(1 for x in image_results.values() if "ocrText" in x),
        "skillsWithOcrNameMatch": sum(1 for s in skill_results if any(c["skillNameFoundByOcr"] for c in s["cards"])),
        "skillsWithFuzzyOcrCandidate": sum(1 for s in skill_results if any(c["skillNameFuzzyCandidate"] for c in s["cards"])),
        "skillImageEvidenceRows":sum(evidence_counts.values()),
        "skillImageEvidenceStatusCounts":evidence_counts,
        "ruleSemanticsVerifiedByOcr":False,
        "skills": skill_results
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
    db.close()
    matched = []
    for skill in skill_results:
        for card in skill["cards"]:
            if card["skillNameFoundByOcr"] or card["skillNameFuzzyCandidate"]:
                matched.append({
                    "skillName": skill["skillName"], "cardId": card["cardId"],
                    "cardName": card["cardName"],
                    "imageType": card["imageEvidence"].get("imageType"),
                    "matchMethod": card["skillNameMatchMethod"],
                    "matchScore": card["skillNameMatchScore"],
                    "matchedText": card["skillNameMatchText"],
                    "evidenceStatus":card["skillNameEvidenceStatus"],
                    "matchContext":card["skillNameMatchContext"],
                    "archivePath": card["imageEvidence"].get("archivePath"),
                    "ocrText": card["imageEvidence"].get("ocrText", "")[:1800]
                })
    print(json.dumps({
        **{k: result[k] for k in ("lowConfidenceSkillKinds", "targetCardIds",
            "imagesOcrProcessed", "skillsWithOcrNameMatch", "skillsWithFuzzyOcrCandidate",
            "skillImageEvidenceRows", "skillImageEvidenceStatusCounts")},
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
