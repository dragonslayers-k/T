#!/usr/bin/env python3
"""Full-population visual/OCR inventory for immutable DB29 card images.
OCR output is evidence for review only and is never promoted to source fact.
"""
from __future__ import annotations
import argparse, csv, hashlib, io, json, math, re, subprocess, tarfile
from collections import Counter
from pathlib import Path
from PIL import Image, ImageOps, ImageStat
EXPECTED_CARDS=15350
IMAGE_TYPES={"small","large"}
def normalize_text(value): return re.sub(r"\s+"," ",value or "").strip()
def parse_member(name, expected_ids):
    normalized=name.replace("\\","/")
    parts=[part.lower() for part in Path(normalized).parts]
    kind="small" if "small" in parts else ("large" if "large" in parts else None)
    card_id=Path(normalized).stem
    return (card_id,kind,normalized) if kind in IMAGE_TYPES and card_id in expected_ids else None
def ocr_image(data,language,psm=11):
    cmd=["tesseract","stdin","stdout","-l",language,"--psm",str(psm),"tsv"]
    result=subprocess.run(cmd,input=data,stdout=subprocess.PIPE,stderr=subprocess.PIPE,check=True)
    words=[]; confidences=[]
    for line in result.stdout.decode("utf-8",errors="replace").splitlines()[1:]:
        cols=line.split("\t")
        if len(cols)>=12 and cols[11].strip():
            words.append(cols[11].strip())
            try:
                confidence=float(cols[10])
                if confidence>=0: confidences.append(confidence)
            except ValueError: pass
    return normalize_text(" ".join(words)),round(sum(confidences)/len(confidences),2) if confidences else 0.0
def analyze_image(data,card_id,kind,path,language,do_ocr):
    digest=hashlib.sha256(data).hexdigest()
    with Image.open(io.BytesIO(data)) as im:
        im.load(); image=ImageOps.exif_transpose(im).convert("RGB"); width,height=image.size
        gray=ImageOps.grayscale(image); stats=ImageStat.Stat(gray); extrema=gray.getextrema()
        hist=gray.histogram(); total=sum(hist)
        entropy=-sum((n/total)*math.log2(n/total) for n in hist if n)
        thumb=image.resize((9,8),Image.Resampling.LANCZOS); pixels=list(thumb.getdata())
        dhash="".join(f"{sum(1<<bit for bit in range(8) if pixels[y*9+bit][0]>pixels[y*9+bit+1][0]):02x}" for y in range(8))
    text,conf=ocr_image(data,language) if do_ocr else ("",0.0)
    return {"card_id":card_id,"image_type":kind,"archive_path":path,"byte_size":len(data),"sha256":digest,
      "width":width,"height":height,"aspect_ratio":round(width/height,6) if height else None,
      "grayscale_mean":round(stats.mean[0],3),"grayscale_stddev":round(stats.stddev[0],3),
      "grayscale_min":extrema[0],"grayscale_max":extrema[1],"grayscale_entropy":round(entropy,4),
      "dhash":dhash,"ocr_text":text,"ocr_confidence_mean":conf,"ocr_status":"processed" if do_ocr else "metadata_only",
      "review_status":"machine_observation_only_not_semantically_verified"}
def load_cards(path,expected):
    rows={}; names={}
    with path.open(encoding="utf-8") as stream:
        for line_no,line in enumerate(stream,1):
            if not line.strip(): continue
            row=json.loads(line); raw=row.get("raw_payload") if isinstance(row.get("raw_payload"),dict) else row
            cid=str(row.get("card_id") or row.get("id") or raw.get("ID") or "").strip()
            if not cid: raise ValueError(f"{path}:{line_no}: card ID absent")
            if cid in rows: raise ValueError(f"duplicate card ID: {cid}")
            rows[cid]=row; names[cid]=str(row.get("name") or raw.get("Name") or "")
    if len(rows)!=expected: raise ValueError(f"expected {expected} unique cards, found {len(rows)}")
    return rows,names
def run(archive,cards_path,out,expected,language,do_ocr):
    rows,names=load_cards(cards_path,expected); ids=set(rows); out.mkdir(parents=True,exist_ok=True)
    seen=set(); bad=[]; counts=Counter(); by_card={}; image_csv=out/"image-visual-ocr.csv"
    fields=["card_id","name","image_type","archive_path","byte_size","sha256","width","height","aspect_ratio",
      "grayscale_mean","grayscale_stddev","grayscale_min","grayscale_max","grayscale_entropy","dhash",
      "ocr_text","ocr_confidence_mean","ocr_status","review_status"]
    with tarfile.open(archive,mode="r|gz") as tf,image_csv.open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=fields); writer.writeheader()
        for member in tf:
            if not member.isfile() or not member.name.lower().endswith((".webp",".png",".jpg",".jpeg")): continue
            parsed=parse_member(member.name,ids)
            if not parsed: continue
            cid,kind,path=parsed; key=(cid,kind)
            if key in seen: bad.append({"card_id":cid,"image_type":kind,"error":"duplicate_image_path","path":path}); continue
            source=tf.extractfile(member)
            if source is None: bad.append({"card_id":cid,"image_type":kind,"error":"unreadable_member","path":path}); continue
            data=source.read()
            try:
                record=analyze_image(data,cid,kind,path,language,do_ocr)
                with Image.open(io.BytesIO(data)) as im:
                    if im.format!="WEBP": raise ValueError("not_webp:"+str(im.format))
            except Exception as exc: bad.append({"card_id":cid,"image_type":kind,"error":str(exc),"path":path}); continue
            record["name"]=names.get(cid,""); writer.writerow(record); seen.add(key); counts[kind]+=1
            by_card.setdefault(cid,{})[kind]=record
    missing=[{"card_id":cid,"image_type":kind} for cid in sorted(ids) for kind in ("small","large") if (cid,kind) not in seen]
    card_rows=[]
    for cid in sorted(ids):
        pair=by_card.get(cid,{}); small=pair.get("small",{}); large=pair.get("large",{})
        card_rows.append({"card_id":cid,"name":names.get(cid,""),"small_sha256":small.get("sha256"),"large_sha256":large.get("sha256"),
          "small_dimensions":f'{small.get("width")}x{small.get("height")}' if small else "",
          "large_dimensions":f'{large.get("width")}x{large.get("height")}' if large else "",
          "small_ocr":small.get("ocr_text",""),"large_ocr":large.get("ocr_text",""),
          "image_pair_status":"both_images_processed" if small and large else "image_pair_incomplete",
          "semantic_review":"pending_card_level_adjudication"})
    with (out/"card-visual-ocr-index.csv").open("w",encoding="utf-8-sig",newline="") as stream:
        writer=csv.DictWriter(stream,fieldnames=list(card_rows[0].keys())); writer.writeheader(); writer.writerows(card_rows)
    summary={"source_release_tag":"fm1-carddb-29","expected_cards":expected,"expected_images":expected*2,
      "processed_images":sum(counts.values()),"small_images":counts["small"],"large_images":counts["large"],
      "ocr_enabled":do_ocr,"ocr_language":language if do_ocr else None,"missing_images":len(missing),
      "invalid_or_duplicate_images":len(bad),"complete":len(missing)==0 and not bad and sum(counts.values())==expected*2,
      "semantic_adjudication_complete":False,"policy":{"source_db_modified":False,"db30_published":False,
      "source_fields_overwritten":False,"machine_ocr_is_not_source_fact":True},"missing":missing,"invalid":bad}
    (out/"visual-ocr-summary.json").write_text(json.dumps(summary,ensure_ascii=False,indent=2),encoding="utf-8")
    if not summary["complete"]: raise SystemExit("Visual/OCR image census incomplete; inspect summary.")
    return summary
def self_test():
    assert normalize_text("  FM1  \n card ")=="FM1 card"
    assert parse_member("images/large/123.webp",{"123"})==("123","large","images/large/123.webp")
    assert parse_member("images/large/999.webp",{"123"}) is None
    im=Image.new("RGB",(20,30),(255,255,255)); buff=io.BytesIO(); im.save(buff,format="WEBP")
    rec=analyze_image(buff.getvalue(),"123","large","images/large/123.webp","eng",False)
    assert rec["width"]==20 and rec["height"]==30 and rec["ocr_status"]=="metadata_only"
    print("full image OCR inventory self-test: PASS")
def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--archive",type=Path); ap.add_argument("--cards-jsonl",type=Path)
    ap.add_argument("--output-dir",type=Path); ap.add_argument("--expected-cards",type=int,default=EXPECTED_CARDS)
    ap.add_argument("--language",default="eng+kor"); ap.add_argument("--no-ocr",action="store_true"); ap.add_argument("--self-test",action="store_true")
    args=ap.parse_args()
    if args.self_test: self_test(); return
    if not args.archive or not args.cards_jsonl or not args.output_dir: ap.error("archive, cards-jsonl and output-dir required")
    result=run(args.archive,args.cards_jsonl,args.output_dir,args.expected_cards,args.language,not args.no_ocr)
    print(json.dumps({k:v for k,v in result.items() if k not in ("missing","invalid")},ensure_ascii=False))
if __name__=="__main__": main()
