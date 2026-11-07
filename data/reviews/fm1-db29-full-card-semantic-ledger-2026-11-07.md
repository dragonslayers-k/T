# DB29 full-card semantic evidence ledger — 2026-11-07

## Source and validation lineage

- Source Release: `fm1-carddb-29` (read-only; no DB mutation).
- Source SQLite SHA-256: `56fb56c491c1049a09ff71c77b10557f750dd32490ca55bcbb93f1379548ebde`.
- Builder commit: `3da860c6c99da86b0af23a6791133c60c1f7a73e`.
- Actions #811 / run `42376614515`: success on that exact SHA.
- Artifact: `fm1-db29-runtime-source-inventory-811`, artifact ID `13576145880`.
- PR #9 branch follow-up commits: `c4bbbd40d78ed885cde823153f9ebf78569195d3` added candidate-summary linkage; `d82cdda1f3f45acce61c8f0dd45a492e8e0218ab` fixed the CSV index schema to include the candidate-summary count. The first follow-up test runs #812 / #813 failed because the CSV DictWriter received `effect_candidate_summary_rows` absent from its header. The d82cdda fix adds that header field and a regression assertion; its exact-SHA CI validation is pending.

## Full population

| Metric | Result |
|---|---:|
| Expected cards | 15,350 |
| Ledger rows | 15,350 |
| Unique card IDs | 15,350 |
| Individual source URLs | 15,350 |
| Source field rows | 613,435 |
| Distinct source field keys | 55 |
| Card × field coverage matrix | 844,250 |
| Missing-on-card cells | 0 |
| Raw-payload mismatches | 0 |

Card types: Unit 8,633; Magic 3,857; Item 1,748; Enchant 823; Land 289.

## 55-field coverage matrix

The matrix is deterministically expanded from each card's immutable `raw_payload` and normalized `source_fields`. Every card has 55 field entries.

| Status | Cells |
|---|---:|
| `source_snapshot_verified` | 600,142 |
| `source_absent_confirmed` | 230,815 |
| `source_empty_confirmed` | 13,293 |
| `missing_on_card` | 0 |
| Payload mismatch | 0 |
| **Total** | **844,250** |

A source snapshot match proves that the normalized row matches the raw payload; it does not prove the field's game meaning.

## Other evidence axes

- Images: 30,700 rows; 30,700 archive-verified.
- Costs: 15,350 source rows; 15,350 syntactically parsed; 779 special semantic review rows; 52 hybrid mapping review rows; 24,166 token rows.
- Skills: 20,762 mapping rows; 3,158 Manual-verified mapping rows.
- Effects: 17,407 source rows; 48,281 clause rows. Clause extraction is not semantic verification or executable runtime behavior.

## Output package

The Actions artifact contains the base per-card JSONL, compact card index, source-cost inventory and runtime overlay. A separate coverage expansion adds a 55-field matrix inside each JSONL card record and a standalone 844,250-row CSV.GZ matrix. The resulting package is retained locally for Library upload:

- `cards.jsonl.gz` SHA-256: `de3cb3f26557d2d433856e839093ab47f9235f9b7ee44ebf2cc70515cf95ca8a`
- `card-index.csv` SHA-256: `da8e23b09e141711cded16a78808cc967ba0a51c5ff8a7b11d4022f9baec69b1`
- `card-field-coverage.csv.gz` SHA-256: `17d0e432b582eb3d17e99e9fb4cd28980a9cea7f7a0df72727d75e046dd7b2e6`
- `summary.json` SHA-256: `b853562e913cc31cd1741efc9226a2089bd73492271ee571bcbfa86250c5ed8e`

## Completion boundary

This is a complete card-level source/evidence inventory for the 15,350-card DB29 population, not a complete semantic adjudication. Every card remains pending card-level semantic review until cost, Skill1, Skill2, effect, visual/OCR and runtime evidence are separately resolved. The existing 831-card RequireSoul census is a completed subgroup and must be linked, not counted as additional cards.

DB29 remains unchanged. DB30 is not created. PR #9 remains open/unmerged. No APK Release or seeded full-game certification is claimed.


## Follow-up test failure and correction

- Actions #812 / run `42376736039` failed on the card ledger unit test with `ValueError: dict contains fields not in fieldnames: 'effect_candidate_summary_rows'`.
- Actions #813 / run `42376960319` repeated the same failure on the preceding report commit; it did not validate the correction commit.
- Fix commit: `d82cdda1f3f45acce61c8f0dd45a492e8e0218ab`; adds `effect_candidate_summary_rows` to the CSV fieldnames and asserts that the column is present.
- A follow-up PR synchronization check is required before this corrected code is considered validated. The already-generated #811 artifact remains valid for its exact SHA and the DB29 SQLite source hash; it predates the candidate-summary addition.
