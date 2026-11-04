# Skill1 inferred-source review coverage — Batch A consolidated (DB29)

**Source artifact:** CardDB Actions #430, `fm1-carddb-semantic-review-fm1-carddb-29-430/gap-reports/inferred-skill-report.jsonl`.  
**Policy:** all ten Skill1 entries indexed through A5 remain inferred/card-text observations. One originally grouped entry (환상폭발) was confirmed to be Skill2 and is reported separately. Candidate frequency does not establish authority or engine semantics.

## Coverage summary

| Skill1 | Candidate card rows | Mechanic excerpts | Exact wording variants | Review batch |
|---|---:|---:|---:|---|
| 화염공격 | 127 | 120 | 7 | A1 |
| 환상봉인 | 85 | 86 | 7 | A1 |
| 연합공격 | 70 | 66 | 7 | A1 |
| 환상제어 | 68 | 67 | 6 | A2 |
| 약탈공격 | 61 | 60 | 3 | A2 |
| 컨슘 | 50 | 49 | 2 | A2 |
| 환상폭발 (Skill2) | 48 | 47 | 2 | 별도 Skill2 큐 |
| 음파공격 | 46 | 45 | 4 | A3 |
| 마법숙련 | 43 | 43 | 3 | A3 |
| 기술감지 | 42 | 42 | 3 | A4 |\n| 투척공격 | 41 | 40 | 4 | A5 |
| **Skill1 total** | **633** | **608** | **46** | **A1–A5** |

Candidate card rows count source-field assignments; mechanic excerpts count individual `additional_text` references. Counts can differ where one row has multiple references or includes non-mechanic card text.

## Batch disposition

- **A1 — 화염공격·환상봉인·연합공격:** exact card-text samples indexed; Manual.zip cross-check found only general attack rules, not direct definitions for these mechanics. Keep inferred/non-executable.
- **A2 — 환상제어·약탈공격·컨슘:** source triage exists. HP/AP/DP timing, coin-difference formula, and HP absorption timing/recipient remain unresolved. Exact excerpt expansion is still required before executable fixtures.
- **A3 — 음파공격·마법숙련:** source triage exists. Next-field-unit selection and “magic” classification remain unresolved. 환상폭발은 원본 보고서상 `Skill2`이므로 Skill1 집계에서 제외하고 별도 Skill2 큐로 이동.
- **A4 — 기술감지:** exact artifact excerpts indexed. 38 references use “not a normal-attack unit”; 4 use “has a special skill”. Do not merge these definitions without proof.\n- **A5 — 투척공격:** exact artifact variants indexed. The next actionable enemy unit, destruction causation, stat-marker behavior, and trigger ordering remain unresolved.

**Field-separation correction:** the earlier 640/615 totals incorrectly included 환상폭발 from Skill2. After adding A5 투척공격, the current Skill1 review coverage is 633 candidate card rows and 608 mechanic excerpts. 환상폭발 remains 48 Skill2 rows and 47 excerpts.\n\n## Highest-priority evidence gaps

1. Retrieve exact source excerpts for all candidate rows in A2 and A3 from the preserved #430 artifact, not just sample cards.
2. Reconcile the Skill1 source-name/enum mapping with the card DB and engine catalog, preserving unresolved aliases.
3. Locate version-specific rule definitions for status-bearing targets, field order, coin count, magic classification, and non-normal-attack classification.
4. Convert only resolved semantics into positive, negative, boundary, and interaction tests linked to card IDs and exact source excerpts.

## Change controls

- No inferred skill is promoted to Manual authority or playable status by this report.
- No runtime rule is implemented solely from repeated card text.
- DB29 remains immutable; no DB30 generation, release update, or main-branch merge.
- Keep evidence provenance, source variants, and unresolved questions in each batch file.
