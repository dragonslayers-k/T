# DB29 full-population visual/OCR census — stage definition (2026-11-07)

## Purpose
Create a reproducible, read-only machine-observation inventory for all 15,350 DB29 cards and their 30,700 archived images. This is the first full-population visual/OCR pass after the card-level source/evidence ledger.

## Inputs
- Immutable source Release: `fm1-carddb-29`
- `cards.jsonl.gz` source records
- `images.tar.gz.part-aa` archived image bundle
- Expected population: exactly 15,350 unique card IDs and one `small` plus one `large` WebP per ID.

## Outputs
- `image-visual-ocr.csv`: one row per image with SHA-256, image dimensions, aspect ratio, grayscale statistics, entropy, perceptual dHash, OCR text/confidence, and observation-only status.
- `card-visual-ocr-index.csv`: one row per card, joined by card ID, with both image hashes/dimensions and OCR text.
- `visual-ocr-summary.json`: population, completeness, errors, and policy boundaries.

## Guardrails
- Read-only against DB29; no source card values or image archive records are modified.
- OCR output is a machine observation, not source truth or a semantic adjudication.
- No cost/skill/effect rule is approved from OCR alone.
- No DB30 creation, Release publication, or PR merge.
- The existing 831-card RequireSoul image subgroup is linked, not counted as a second card population.

## Completion gate
The image pass is complete only if exactly 30,700 unique image records are processed with zero missing or invalid entries. Semantic review remains pending until card-level source text, manual authority, visual confirmation, inference status, and tests are joined in a subsequent adjudication ledger.
