# Skill1 source evidence index — Batch A1 (DB29)

**Source snapshot:** CardDB Actions #430, gap-reports/inferred-skill-report.jsonl  
**State:** inferred; card text indexed; semantic review pending.  
**Scope:** 화염공격, 환상봉인, 연합공격.  
This index records card-source observations only. It does not approve Manual authority, rule promotion, runtime implementation, or DB29 modification.

## Evidence policy
- Preserve card IDs and URLs from the artifact.
- Separate mechanic text from rename notices, lore, and supplemental notes.
- Do not merge distinct wording variants without resolving trigger/timing differences.
- Frequency prioritizes review but does not establish accuracy.
- Unresolved interpretations remain pending.

## 화염공격 — 127 candidate rows

| Card ID | Name | Exact effect excerpt | Card source |
|---|---|---|---|
| 10010624547 | 타투파이터 | AP1 이상으로 공격시 상대는 DP-1, HP-1(DP에 막힐 시 무효) | https://fmlunatic.com/card/10010624547 |
| 10012024608 | 루베릭 | AP1 이상으로 공격시 상대는 DP-1, HP-1(DP에 막힐 시 무효) | https://fmlunatic.com/card/10012024608 |
| 10020324636 | 데몬 | AP1 이상으로 공격시 상대는 DP-1, HP-1(DP에 막힐 시 무효) | https://fmlunatic.com/card/10020324636 |
| 10022424696 | 히드라 | AP1 이상으로 공격시 상대는 DP-1, HP-1(DP에 막힐 시 무효). | https://fmlunatic.com/card/10022424696 |

#430 records a separate 15-row variant: “자신 AP가 상대 DP보다 높으면 공격 후 DP/HP를 1 감소.” Keep separate until condition, timing, and “DP에 막힐 시 무효” are resolved.

**Required post-confirmation tests:** AP 0/1 threshold; attacker AP below/equal/above defender DP; DP protection; DP-vs-HP order; whether HP decrement is prevented if DP decrement is blocked.

## 환상봉인 — 85 candidate rows

| Card ID | Name | Exact effect excerpt | Card source |
|---|---|---|---|
| 10042124827 | 메탈키메라 | AP 1이상으로 공격시, 적 유닛이 상태보유 유닛이면 AP/DP=0. | https://fmlunatic.com/card/10042124827 |
| 10080425079 | 리아 | AP 1이상으로 공격시, 적 유닛이 상태보유 유닛이면 AP/DP=0. | https://fmlunatic.com/card/10080425079 |
| 10090125163 | 하이엘프 | AP 1이상으로 공격시, 적 유닛이 상태보유 유닛이면 AP/DP=0. | https://fmlunatic.com/card/10090125163 |
| 11040625663 | 신록의지도자 | Mechanic text is followed by a 2012 rename notice; exclude the notice from the effect. | https://fmlunatic.com/card/11040625663 |

**Open questions:** define “상태보유” using actual state markers; confirm AP/DP zeroing timing; protections and already-zero stats; confirm HP unaffected; exclude rename/history text. These are card-text observations, not Manual verification.

## 연합공격 — 70 candidate rows

| Card ID | Name | Exact effect excerpt | Card source |
|---|---|---|---|
| 10010624559 | 울프라이더 | AP 1이상으로 공격시, 아군 필드내 자신과 동일한 능력의 유닛수만큼 AP에추가데미지. | https://fmlunatic.com/card/10010624559 |
| 10020324681 | 호기심요정 | AP 1이상으로 공격시, 아군 필드내 자신과 동일한 능력의 유닛수만큼 AP에추가데미지. | https://fmlunatic.com/card/10020324681 |
| 10030324728 | 볼드리솔져 | AP 1이상으로 공격시, 아군 필드내 자신과 동일한 능력의 유닛수만큼 AP에추가데미지. | https://fmlunatic.com/card/10030324728 |
| 10102025311 | 금속길드전사 | Same representative text; a separate unit is needed to test count semantics. | https://fmlunatic.com/card/10102025311 |

**Open questions:** whether “same ability” compares Skill1, Skill1+Skill2, or the full ability tuple; whether attacker counts itself; copied/temporary abilities; whether bonus damage joins AP before DP or applies after calculation; zero and multiple match boundaries.

## Disposition

| Skill | Evidence | Authority | Runtime |
|---|---|---|---|
| 화염공격 | exact card excerpts from #430 artifact | card text observation, not Manual | blocked pending semantics |
| 환상봉인 | exact card excerpts from #430 artifact | card text observation, not Manual | blocked pending semantics |
| 연합공격 | exact card excerpts from #430 artifact | card text observation, not Manual | blocked pending semantics |

Next: compare relevant Manual.zip material and reliable historical/version-specific evidence. If Manual does not define a mechanic, retain card text as versioned evidence and do not implement until authoritative evidence resolves semantics. Only then turn design questions into executable engine assertions.
