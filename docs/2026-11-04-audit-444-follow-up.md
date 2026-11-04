# Audit #435–#444 history and next work order

Date: 2026-11-04  
Branch: `feat/carddb-effect-semantic-pass`  
Immutable source baseline: `fm1-carddb-29`  
Latest full audit: Actions [#444](https://github.com/dragonslayers-k/T/actions/runs/41831469993)  
Latest tested commit: `b4191d060eba3ef809d487ddabd266cbc60e0132`

## 1. Actions history

| Run | Commit | Mode / purpose | Result |
|---|---|---|---|
| #435 | `c6376be5` | Full DB29 audit after first legacy-effect parser batch | Success; low-confidence effects 150 |
| #436 | `40de8b8f` | Pull-request regression tests | Success |
| #437 | `7ee88a5f` | Full DB29 audit after next parser batch | Success; low-confidence effects 86 |
| #438 | `452c489b` | Regression tests | Failed: 3 assertions (named ability/card-list overlap; grouped AP/DP/HP delta; AP assignment to zero) |
| #439 | `2ee94293` | Regression tests after partial correction | Failed: 2 assertions (grouped AP/DP/HP delta; AP assignment to zero) |
| #440 | `cc7f0a69` | Regression tests after correction | Success |
| #441 | `0b5370d0` | Regression tests for passive/counter conversion | Failed: kill-count-to-LP clause classified only as generic effect |
| #442 | `e29a150f` | Regression tests after counter-conversion correction | Failed: same counter-conversion assertion |
| #443 | `863336fc` | Regression tests after sequential counter-conversion correction | Success |
| #444 | `b4191d06` | Full DB29 audit of accumulated parser changes | Success; low-confidence effects 67 |

The four failed test runs exposed concrete parser overlaps or missed legacy phrases. They were corrected before #443 passed. #444 tested the accumulated changes against the immutable DB29 snapshot.

## 2. #444 verified structural results

- Cards: 15,350 required / 15,350 source / 15,350 unique; duplicate IDs 0.
- Source fields: 55; complete card-field matrix: 844,250 rows.
- Field coverage: 600,142 source-verified, 230,815 source-absent/not-applicable, 13,293 source-empty, 0 source-null.
- Field applicability candidates: 0; applicable-but-source-absent: 0; missing field cells: 0; payload mismatches: 0.
- Card image records: 30,700; large/small downloads: 15,350 each; failures: 0.
- Effect source rows: 17,407; normalized effect clauses: 48,281; interpretation rows: 48,281; missing interpretations: 0; source mismatches: 0.
- Soul costs: all 15,350 cards parsed; parse-level needs-review 0; 24,166 soul tokens.
- Skills: 20,762 source/mapping rows; unmapped 0. Card-local inferred evidence: 3,893 rows; missing card-local evidence: 123 rows.
- SQLite/integrity and source snapshot checks passed; the Actions job completed successfully.
- No Release was published: `PUBLISH_RELEASE=false`. `fm1-carddb-29` remains unchanged.

Important distinction: the 844,250-row matrix is the full card × field coverage matrix. The 613,435 `card_field_rows` metric is the number of stored source field rows, not the size of the coverage matrix. Do not report 613,435/844,250 as complete.

## 3. Semantic backlog after #444

The progress report compares #444 against the immutable baseline captured by #432:

| Review category | #432 baseline | #444 current | Net reduction |
|---|---:|---:|---:|
| Low-confidence effect interpretations | 206 | 67 | 139 |
| Name-only skill rules | 26 | 26 | 0 |
| Hybrid-soul payment rules | 52 | 52 | 0 |
| Special-soul payment rules | 779 | 779 | 0 |
| Manual rule conflicts | 1 | 1 | 0 |

The effect backlog fell by 139 (67.5%). This is parser classification progress, not proof that 139 game rules were independently verified. The progress report explicitly forbids promoting a rule to verified/executable from a count reduction alone.

The remaining 67 low-confidence rows comprise 67 unique text patterns: 8 `conditional_or_reference_candidate` and 59 `unparsed_effect_text`. This is a mixed queue: actual effect fragments, activation conditions, named-ability/card references, collection/deck restrictions, category/rarity notes, historical/event metadata, and source fragments. Triage by meaning and source card; do not blanket-reclassify as effects or metadata.

Additional pending items:
- 26 name-only skill rules.
- 52 hybrid-soul payment semantics and 779 special-soul (NCS/BONUS) payment semantics. Token parsing is complete; payment meaning is not.
- 42 engine-verification cases: 27 manual skill rules + 15 global gameplay rules.
- 1 manual-rule conflict.
- Skill image OCR evidence: 32 rows (14 exact, 5 fuzzy candidates, 5 name collisions, 8 not found); 0 OCR promotions were accepted in #444.

## 4. Next work order

### Batch A — adjudicate the 67 effect rows
1. Preserve the #444 semantic-review artifact as the fixed input. Do not re-crawl or re-download images.
2. For every row, retain card ID, exact source text, source URL, original marker, and adjacent TextBase/TextExtra context.
3. Assign a review disposition: (a) actual effect operation, (b) activation/branch condition, (c) named ability/status/card reference, (d) deck/collection/category metadata, (e) historical/lore/source artifact, or (f) incomplete/ambiguous fragment.
4. For actual effects, record actor, target, trigger, condition, operation, numeric formula, duration, and source evidence. If any element is unknown, retain a non-executable candidate.
5. Add regression cases from exact #444 rows. Run focused tests once after batching; only then run one full DB29 audit to measure the real change.

### Batch B — skill semantics
1. Resolve the 26 name-only skill rules against each card's own detail page and image evidence.
2. Review the 5 fuzzy OCR candidates and 5 name collisions separately; do not promote ambiguous OCR.
3. Inspect the 123 card-local evidence-missing rows. Never copy another card's skill meaning without a source link proving the relationship.
4. Verify the 27 manual skill rules and 15 global rules against engine behavior or authoritative source rules.

### Batch C — soul payment semantics
1. Work from the card-linked 52 hybrid and 779 special-soul occurrence queue.
2. Preserve each token occurrence and its card/source provenance.
3. Determine whether each token means a fixed payment, selectable payment, wildcard/any-soul payment, bonus/NCS condition, or another rule only where evidence establishes it.
4. Keep unresolved items explicitly pending; do not force a mapping merely to reduce the counter.

### Release gate
No merge or `fm1-carddb-30` publication until effect review, skill/soul semantic review, manual-rule conflict resolution, and engine verification pass. Keep DB29 immutable.

## 5. #444 artifacts

- Full audit: [artifact 13323600415](https://github.com/dragonslayers-k/T/actions/runs/41831469993/artifacts/13323600415)
- Semantic review queue: [artifact 13323730248](https://github.com/dragonslayers-k/T/actions/runs/41831469993/artifacts/13323730248)
- Semantic backlog progress: [artifact 13323595391](https://github.com/dragonslayers-k/T/actions/runs/41831469993/artifacts/13323595391)

## 6. Post-#444 parser batch validation

- The follow-up parser batch adds non-executable candidates for hero-power deltas, spell target-count deltas, grouped AP/DP/HP changes, formula-based HP changes, level-count tie-breaks, and conditional effect branches.
- Regression tests were added from #444 queue examples.
- Actions [#445](https://github.com/dragonslayers-k/T/actions/runs/41833512404) on commit `15958f161703d156fc0d60e222aa175206ce561d` completed successfully. All lightweight test suites passed, including 16 effect-interpretation tests.
- #445 was a test-only run. It did not rebuild the DB29 SQLite file or recalculate the 67-row full-audit backlog. Do not claim a new backlog count until a deliberate full audit is run after a complete source-backed batch.
