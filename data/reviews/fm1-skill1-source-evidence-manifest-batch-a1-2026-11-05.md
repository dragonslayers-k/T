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


## Manual.zip cross-check — general rules only; no direct mechanic match

The captured specialability.htm source in Manual.zip contains a 27-entry special-skill list. The current Manual-authority catalogue names are:

일반공격, 방어무시, 치명공격, 관통공격, 약화공격, 석화공격, 흡혈공격, 노화공격, 돌진공격, 야수조련, 용맹공격, 재생능력, 광분공격, 연속공격, 공포공격, 매료공격, 기술봉쇄, 주문봉쇄, 무기봉쇄, 공격복제, 방패파괴, 저주공격, 방어이용, 조롱공격, 혼란공격, 은폐공격, 방어변환.

The three indexed Skill1 mechanics—화염공격, 환상봉인, 연합공격—do not appear as entries in that 27-item list. Therefore Manual.zip does not directly confirm their individual effects in this captured section. Keep them inferred/card-source based and do not grant Manual authority.

Manual does provide shared context that can inform future test design, without resolving these skills:
- “추가공격데미지” is added to the attacker’s AP from AP/DP/HP/level and is described as damage of the same kind as a normal attack.
- A special attack effect that affects the opponent generally requires the attacker’s AP to be at least 1.
- An exception is an effect that changes the attacker’s own stats.
- Special attack skills apply when coins are tossed and the unit attacks.

These shared principles are not enough to decide the disputed mechanics:
- For 화염공격, the source does not state whether the DP/HP reduction is itself additional attack damage or a separate post-attack effect.
- For 환상봉인, the state-bearing target and timing of setting AP/DP to zero are not specified by this general section.
- For 연합공격, the phrase “same ability” and whether the attacker is included in the count remain unspecified.

**Evidence conclusion:** retain each mechanic as inferred, keep the source excerpts and variants, and pursue card/version-specific or reliable historical documentation. Do not implement or promote these three skills solely from the Manual’s general attack rules.
