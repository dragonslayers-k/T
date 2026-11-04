# Semantic backlog work after audit #432

Date: 2026-11-04  
Active branch: `feat/carddb-effect-semantic-pass`  
Immutable source release: `fm1-carddb-29`  
Audit baseline: Actions #432, commit `fb3647896029bf06452e34df3eb826f2524d45b1`

## Verified #432 backlog baseline

| Review domain | Pending |
|---|---:|
| Low-confidence effect interpretations | 206 |
| Name-only low-confidence skill rules | 26 |
| Hybrid soul payment rules | 52 |
| NCS/BONUS special soul semantics | 779 |
| Manual rule conflicts | 1 |
| Manual rules pending engine verification | 42 |

These are review/verification items, not missing parser rows. The audit passed structural checks but did not complete semantic verification.

## Source finding: what the current Manual.zip does and does not establish

The repository's extracted `data/rules/manual-global-gameplay-source.txt` includes the complete `soulcost.htm` extract. It explicitly establishes:
- Soul-cost maintenance applies only to units with neutral (MU) summon symbols.
- Those units pay the neutral amount each preparation phase.
- A shortfall destroys that many deck cards.
- At initial summon, neutral symbols can be paid with any color.

A full text scan of that extracted manual source found no occurrences of `NCS`, `BONUS`, `하이브리드`, or `혼합 소울`. Therefore the existing Manual.zip evidence cannot justify assigning hybrid tokens to a final payment rule or treating NCS/BONUS as neutral/ordinary colors. Keep all 831 records pending and non-executable until an independent source or reproducible game test establishes the rule.

The same source extract contains one genuine global-rule conflict: `gamerule.htm` describes terrain placement up to LP, while `ready.htm` says one terrain card per turn. The conflict is retained; do not choose one statement without a version or priority source.

## Changes added to the active branch

1. `data/semantic-backlog-baseline-fm1-carddb-29.json` records the immutable #432 counts.
2. `scripts/semantic_backlog_progress.py` compares the next audit report with that baseline and classifies each domain as reduced, unchanged, or increased. It never treats a lower count as proof of correctness.
3. `scripts/build_gap_reports.py` now emits `soul-semantic-review-queue.json`, grouping hybrid/special token identities while preserving every token occurrence, card ID, card name/type, original RequireSoul source value, and source card URL.
4. The queue uses token-level status, not card-level flags, so a hybrid token on a card that also contains a special token is not mislabeled as both.
5. The queue explicitly keeps `executable=false` and `pending_source_and_engine_verification`.
6. Regression cases were added to `tests/test_cost_decoding.py`.

## Next semantic work — not another whole-database audit

- Resolve the 52 hybrid records only from enum definitions, original card UI/source evidence, or controlled game tests. Validate whether the displayed pair means both colors, either color, or another rule; do not assume.
- Resolve the 779 special records by exact token identity and observed payment behavior. Keep NCS and BONUS separate until proven otherwise.
- Review the 206 effect patterns against all preserved source variants and their card-local contexts; classify metadata/reference/condition/effect without deleting or rewriting source text.
- Trace the 26 name-only skills to card-local definitions or reliable source documents. A name match or OCR label alone is not a definition.
- Reconcile the single terrain-placement conflict with authoritative versioned evidence.
- Implement and run the 42 pending engine tests in the engine repository before marking manual rules executable.

## Execution policy

- Do not rerun the full DB29 audit merely to reproduce the same counts.
- The next full audit should occur only after a substantive batch of source-backed decisions or parser changes is ready; it will then produce a per-domain delta from #432.
- Do not merge PR #9 into main, publish DB30, or change immutable Release `fm1-carddb-29` as part of this work.


## Full-audit measurements after parser work

### Actions #435 — first source-note pass
- Run: https://github.com/dragonslayers-k/T/actions/runs/41828854741
- Low-confidence effect rows/patterns: 206 → 150.
- Reduction: 56.
- Other baseline counts unchanged: name-only skills 26; hybrid soul 52; special soul 779; manual conflicts 1.

### Actions #437 — second rule-note and legacy-action pass
- Run: https://github.com/dragonslayers-k/T/actions/runs/41829985712
- Low-confidence effect rows/patterns: 206 → 86.
- Reduction: 120 (58.3%).
- Breakdown at #437: 8 conditional/reference candidates, 78 unparsed effect-text candidates.
- Other baseline counts unchanged: name-only skills 26; hybrid soul 52; special soul 779; manual conflicts 1.

### Actions #444 — latest full audit
- Run: https://github.com/dragonslayers-k/T/actions/runs/41831469993
- Low-confidence effect rows/patterns: 206 → 67.
- Reduction: 139 (67.5%).
- Breakdown at #444: 8 conditional/reference candidates, 59 unparsed effect-text candidates.
- Name-only low-confidence skills: 26 (unchanged).
- Hybrid soul payment rules: 52 (unchanged).
- NCS/BONUS special-soul semantics: 779 (unchanged).
- Manual rule conflicts: 1 (unchanged).
- Manual engine verification pending: 42 (27 manual skill rules + 15 global rules).
- Structural gates, image validation (30,700/30,700), SQLite integrity and FK checks passed.
- Release publication was skipped; DB29 remains immutable.

The effect count reduction reflects source-marker, metadata, calculation/scope-note, named-ability-reference and legacy-action candidate classification. It does not make those candidates executable. The remaining 67 must be reviewed against their original card IDs, full text and source pages; the 59 unparsed candidates include genuine formula-heavy effects and must not be hidden by generic metadata classification.
