# Skill2 source evidence adjudication — pass 2 (DB29 / 2026-11-05)

## Scope
This pass uses the DB29 semantic-review artifact from audit #573 and the pass-1 evidence audit. It resolves the *evidence status* of the eight rows that lack card-local Skill2 excerpts; it does not infer the skill's behavior from enum labels.

- Candidate set: 377 card rows / 8 inferred Skill2 rule groups.
- Card-local evidence: 369 rows; 368 have actual `additional_text` excerpts.
- Missing card-local excerpt: 8 rows.
- All rows remain inferred. This file does not promote a mapping to source-verified or executable.
- DB29 remains immutable; no DB30 release or main merge.

## Eight missing rows: disposition
| Card ID | Name | Skill2 | Enum | Evidence observation | Disposition |
|---|---|---|---:|---|---|
| 12111426500 | 신비의바다 | 기선제압 | 18 | No matched card-local Skill2 excerpt in #573 review payload | pending; source excerpt recovery needed |
| 16102628565 | 마왕 | 기선제압 | 18 | TextBase/TextExtra reported empty in pass 1 | pending; empty text is not proof of absent behavior |
| 16110928590 | 불의정령여왕 | 기선제압 | 18 | TextBase/TextExtra reported empty in pass 1 | pending; empty text is not proof of absent behavior |
| 6121340763 | 고대나무뿌리 | 기선제압 | 18 | Item; TextExtra reported empty, no matched excerpt | pending; seek original enum/source or trusted manual evidence |
| 8080640943 | 용기의정령 | 기선제압 | 18 | Item; TextExtra reported empty, no matched excerpt | pending; seek original enum/source or trusted manual evidence |
| 14031227302 | 순수한레비 | 헌신방어 | 175 | TextBase empty; no matched Skill2 excerpt | pending; recover card-local source evidence |
| 16110228578 | 설원고양이 | 헌신방어 | 175 | TextBase/TextExtra reported empty in pass 1 | pending; empty text is not proof of absent behavior |
| 16112328609 | 어둠기사 | 헌신방어 | 175 | TextBase empty; no matched Skill2 excerpt | pending; recover card-local source evidence |

## Evidence policy and next resolution
1. The #573 review artifact is a generated analysis snapshot, not a substitute for the original source payload.
2. An empty TextBase/TextExtra does not establish that the enum is erroneous or that the skill is inactive.
3. For these eight IDs, inspect the preserved Firestore source record, original card detail page, and available Manual/source archives. If no authoritative card-local description exists, record the rule-level evidence and keep the per-card mapping pending.
4. Do not copy a neighboring card's description solely because the enum/name matches.
5. Do not enable runtime behavior based on this adjudication.

## Related semantic boundaries retained
- Tactical Initiative (기선제압): source variants differ on whether reduction covers all damage or only opponent-AP damage, and on strict vs inclusive level comparisons.
- Devoted Defense (헌신방어): “next friendly field unit” still requires engine ordering/gap/wrap tests.
- Source excerpt availability is not equivalent to semantic approval.

## Traceability
- DB29 semantic-review artifact: T Actions #573, run 41970905894.
- Pass 1 source evidence audit: `data/reviews/fm1-skill2-source-evidence-audit-pass-1-2026-11-05.md`.
- Baseline guard: DB29 immutable; no DB30, no main merge.
