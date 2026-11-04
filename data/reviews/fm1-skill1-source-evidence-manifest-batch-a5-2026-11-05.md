# Skill1 source evidence index — Batch A5 (DB29)

**Verified against:** Actions #430 artifact `gap-reports/inferred-skill-report.jsonl`.
**Skill:** 투척공격 (`Skill1`; 41 candidate card rows; 40 mechanic excerpts; 4 exact wording variants).
**State:** inferred; no authority promotion or runtime implementation.

## Exact source variants

| Count | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 29 | 적 1파괴시, 적 필드 행동가능 다음 유닛 AP/DP/HP -1 | 10033124766 켄드데이샤; 10040724777 케이브텐타클; 10080425061 스플릿포스; 10120125459 정글버서커 |
| 5 | 적 1 파괴시, 적 필드 행동가능 다음 유닛 1의 AP/DP/HP를 1씩 감소시킨다. | 15010727791 세이사린; 16020328256 트론; 16032328282 연장사; 16040641688 정크슈티 |
| 3 | 적 1파괴시, 적 필드 행동가능 다음 유닛 AP/DP/HP -1. | 10080425087 은룡섬의주인; 11010525541 광산지배자; 11020125594 불의조언자 |
| 3 | 적 1 파괴시, 적 필드 행동가능 다음 유닛 AP/DP/HP -1. | 15040127895 이에디오; 15060327954 미노타도끼병; 16050428334 어린파소에 |

One of the 41 Skill1 rows has no `additional_text` mechanic reference in this group. Do not infer missing wording.

## Semantic questions

1. Does “적 1 파괴시” mean this unit must cause the destruction, or any enemy unit destruction during the effect window?
2. “행동가능 다음 유닛” — next by field index, next currently actionable unit, or next unit after skipping non-actionable/empty slots?
3. If no next actionable unit exists, is the effect lost or does it wrap around?
4. Are AP, DP, and HP reduced independently, and how do ▲/▼/* stat markers affect each change?
5. Does the effect resolve before/after destruction cleanup and other death triggers?
6. Are all three stats reduced by 1 even when one is already 0 or negative?

## Required test plan after semantics are sourced

- Positive: destroy an enemy and confirm next actionable enemy unit receives AP/DP/HP -1.
- Negative: no enemy destroyed; attacker does not cause destruction if the trigger is causation-specific.
- Boundary: next field slot empty; next unit non-actionable; no remaining actionable enemy unit; field wrap boundary.
- Interaction: each stat marker independently protects or allows decrease; target at AP/DP/HP 0; simultaneous destruction triggers.
- Provenance: each fixture must include card ID, exact source excerpt, source URL, and DB29 snapshot version.

## Disposition

- Card-text evidence only; not in the 27-entry Manual.zip list checked in the current work.
- Keep `inferred` and non-executable.
- Do not change DB29, create DB30, or merge to main based on this candidate.
