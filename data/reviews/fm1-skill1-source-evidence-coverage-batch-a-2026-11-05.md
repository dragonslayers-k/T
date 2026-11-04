# Skill1 inferred-source review coverage — Batch A consolidated (DB29)

**Source artifact:** CardDB Actions #430, `fm1-carddb-semantic-review-fm1-carddb-29-430/gap-reports/inferred-skill-report.jsonl`.  
**Policy:** all ten entries remain inferred/card-text observations. Candidate frequency does not establish authority or engine semantics.

## Coverage summary

| Skill1 | Candidate card rows | Mechanic excerpts | Exact wording variants | Review batch |
|---|---:|---:|---:|---|
| 화염공격 | 127 | 120 | 7 | A1 |
| 환상봉인 | 85 | 86 | 7 | A1 |
| 연합공격 | 70 | 66 | 7 | A1 |
| 환상제어 | 68 | 67 | 6 | A2 |
| 약탈공격 | 61 | 60 | 3 | A2 |
| 컨슘 | 50 | 49 | 2 | A2 |
| 환상폭발 | 48 | 47 | 2 | A3 |
| 음파공격 | 46 | 45 | 4 | A3 |
| 마법숙련 | 43 | 43 | 3 | A3 |
| 기술감지 | 42 | 42 | 3 | A4 |
| **Total** | **640** | **615** | — | **A1–A4** |

Candidate card rows count Skill1 assignments; mechanic excerpts count individual `additional_text` references. Counts can differ where one row has multiple references or includes non-mechanic card text.

## Batch disposition

- **A1 — 화염공격·환상봉인·연합공격:** exact card-text samples indexed; Manual.zip cross-check found only general attack rules, not direct definitions for these mechanics. Keep inferred/non-executable.
- **A2 — 환상제어·약탈공격·컨슘:** source triage exists. HP/AP/DP timing, coin-difference formula, and HP absorption timing/recipient remain unresolved. Exact excerpt expansion is still required before executable fixtures.
- **A3 — 환상폭발·음파공격·마법숙련:** source triage exists. Death-trigger semantics, next-field-unit selection, and “magic” classification remain unresolved.
- **A4 — 기술감지:** exact artifact excerpts indexed. 38 references use “not a normal-attack unit”; 4 use “has a special skill”. Do not merge these definitions without proof.

## Highest-priority evidence gaps

1. Retrieve exact source excerpts for all candidate rows in A2 and A3 from the preserved #430 artifact, not just sample cards.
2. Reconcile the Skill1 source-name/enum mapping with the card DB and engine catalog, preserving unresolved aliases.
3. Locate version-specific rule definitions for status-bearing targets, field order, coin count, magic classification, and non-normal-attack classification.
4. Convert only resolved semantics into positive, negative, boundary, and interaction tests linked to card IDs and exact source excerpts.

## Change controls

- No inferred skill is promoted to Manual authority or playable status by this report.
- No runtime rule is implemented solely from repeated card text.
- DB29 remains immutable; no DB30 generation, release update, or main-branch merge.
- Keep evidence provenance, source variants, and unresolved questions in each batch file.
