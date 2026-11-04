# Skill1 source evidence index — Batch A3 (DB29)

**Source basis:** CardDB Actions #430 `gap-reports/inferred-skill-report.jsonl`; Batch A source review queue.  
**State:** inferred; semantic review pending.  
**Scope correction:** this file originally grouped 환상폭발 with Skill1, but Actions #430 source rows show 환상폭발 is `Skill2`, not `Skill1`. This file therefore covers only the Skill1 candidates 음파공격 and 마법숙련; 환상폭발 is a separate Skill2 review item.  
This is a prioritization and evidence-tracking document only. It does not establish Manual authority, approve rule promotion, enable runtime behavior, or alter DB29.

## Evidence handling
- Sample card IDs and URLs below are preserved from the DB29 review queue.
- Exact card excerpts must be retrieved from the archived #430 artifact or verified source snapshot before they become executable test fixtures.
- Candidate counts and repeated phrasing are evidence of prevalence, not proof of semantics.
- Keep wording variants separate when trigger, target selection, or timing differs.

## 환상폭발 — 48 candidate rows (Skill2; excluded from Skill1 batch)

| Sample card ID | Card source |
|---|---|
| 10110325335 | https://fmlunatic.com/card/10110325335 |
| 10110325342 | https://fmlunatic.com/card/10110325342 |
| 10110325349 | https://fmlunatic.com/card/10110325349 |

**Observed summary (Skill2):** when the source unit is destroyed, destroy an opposing unit that has a status. This section is retained for traceability but must not be counted as Skill1 coverage.

**Pending semantic decisions:** “destroyed” event vs. HP reaching zero; whether this is a death trigger or any removal; target choice and timing; whether status is checked at trigger time or resolution; prevention, replacement, and simultaneous destruction interactions.

## 음파공격 — 46 candidate rows

| Sample card ID | Card source |
|---|---|
| 10010624554 | https://fmlunatic.com/card/10010624554 |
| 10030324722 | https://fmlunatic.com/card/10030324722 |
| 10050424848 | https://fmlunatic.com/card/10050424848 |

**Observed summary:** AP 1 이상으로 공격할 때 적 필드의 다음 유닛 AP/DP를 각각 2 감소시키는 패턴. A separately observed wording explicitly identifies the next unit as field position +1; do not assume that applies to every candidate.

**Pending semantic decisions:** field order and “next” definition; empty slot/end-of-field; attack canceled or misses; AP/DP floor; protective markers; whether repeated applications stack and duration.

## 마법숙련 — 43 candidate rows

| Sample card ID | Card source |
|---|---|
| 10010624561 | https://fmlunatic.com/card/10010624561 |
| 10012024610 | https://fmlunatic.com/card/10012024610 |
| 10020324641 | https://fmlunatic.com/card/10020324641 |

**Observed summary:** AP 1 이상 attack against a target classified as “magic” gains +2 damage.

**Pending semantic decisions:** “magic” classification (card type, unit subtype, or ability); where the bonus is applied relative to DP; attack threshold; whether copied/temporary classifications count; and whether the modifier persists or is attack-local.

## Evidence gate

1. Verify exact source excerpts for the listed IDs from #430 or a preserved source snapshot.
2. Find Manual/version-specific documentation for terms and timing; if absent, keep the interpretation explicitly unverified.
3. Write distinct positive, negative, boundary, and interaction cases only after the semantics are resolved.
4. Tie any future fixture to card ID, URL, exact excerpt, and evidence provenance.
5. Keep all three inferred and disabled until review and runtime tests are complete.

**Disposition:** no executable engine assertions in this batch. No inferred-to-verified promotion, no DB29 edits, no DB30, and no main-branch merge.
