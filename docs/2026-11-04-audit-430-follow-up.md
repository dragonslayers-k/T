# Audit #430 follow-up — semantic review next steps

Date: 2026-11-04  
Branch: `feat/carddb-effect-semantic-pass`  
Baseline: immutable `fm1-carddb-29`

## Latest full audit

- Actions run: [#430](https://github.com/dragonslayers-k/T/actions/runs/41810552771), run ID `41810552771`.
- Cards: 15,350; source fields: 55; effect clauses: 48,281; images: 30,700.
- SQLite integrity: `ok`; foreign-key errors: 0; unmapped skills: 0.
- Remaining semantic review: 206 low-confidence effect interpretations, 52 hybrid-cost mappings, and 779 special-soul semantics.
- Artifact IDs: full audit `13311584435`; semantic review `13312586416`.
- The audit is not a claim that semantic review is complete. No new release was published.

## Effect review queue fixes after #430

The grouped queue now preserves classification and confidence variants. If one normalized phrase has conflicting classifications, its representative classification is `mixed`; confidence conflicts select the conservative lower-confidence value. Regression coverage was added.

Commits:
- `3e2ad22` — preserve variants within grouped effect review queue.
- `dc6a4a4` — classify conflict groups as mixed and conservative confidence.
- `96d1fc7` — add classification-conflict regression test.

These commits have not been validated by a new full audit. Tests were not run as part of these commits; do not report them as passing.

## Next data work

1. Rebuild and inspect the 206 low-confidence effect review rows from the #430 source artifact. Prioritize classification conflicts and repeated patterns; preserve all original text variants and card/source references.
2. Keep 52 hybrid and 779 NCS/BONUS rows distinct from parser failures. Preserve token identity; do not invent payment rules or mark them verified without evidence.
3. Review card-local Skill2 evidence and named-effect references. Evidence from one card must not be copied as evidence for another.
4. Batch code changes, run focused regression tests once, then request one manual full DB29 audit. Documentation-only changes must not trigger full audits.
5. Keep `fm1-carddb-29` immutable; no release tag until the quality gate is met and explicitly approved.

## Verification status

- #430 full audit: successful for its stated structural and semantic-audit scope.
- Post-#430 review-queue commits: committed; focused tests not yet run.
- Full semantic completion / next release: not complete.
