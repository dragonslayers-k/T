# Skill1 A24–A25 source-to-APK gap audit — 2026-11-06

## 검증 기준

- CardDB parent HEAD: `40df5e3d150c39dea471da8df25d65a2ba0ffcfd` (Actions #632 success)
- APK branch: `feat/combat-event-foundation`
- APK `rules.js`: `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`
- APK `rules.test.cjs`: `212a8d2c098116349b58cc47871207d3af064346`
- Immutable DB29 preserved; DB30 not issued; PR #9/#28 not merged.

This audit checks source inventory and exact Korean skill-label occurrences in the two APK files. Zero direct label occurrences do not rule out generic reusable primitives, but do not establish a named handler or regression fixture either.

## A24 evidence inventory

A24 contains 10 Skill1 groups, 20 candidate rows, 22 excerpts, and 15 expression variants. Two groups have only one excerpt for two candidates:

- **사자부활**: 에봉파항아리 (`16101941731`) excerpt is missing; 파라오의관 (`3111440368`) is the only row with text. Do not infer the missing card effect from the name.
- **생명약화**: 창조주 (`16102628564`) excerpt is missing; 천화 (`16121528672`) has the source text. The missing row must not inherit the other card's rule.

Other A24 groups and their principal gates:

| Skill1 | Main source-backed operation | Unresolved gate |
|---|---|---|
| 사기증진 | own destruction; apply 2-turn training status to allied field units at/below own level | exact target snapshot, status refresh and immediate timing |
| 샌드웜소환 | hero counter increment; separate 2-counter hero activation transforms hand unit | distinguish attack Skill1 from hero activation; exact target/card ID |
| 서먼라이팅 | enemy destruction; create Lightning Bolt at next allied field position | card ID, slot and action-ready state |
| 서먼레전드 | AP≥1 attack; attach item selected by opponent soul | soul lookup table and skill-attached item interaction |
| 서먼매직 | AP≥1 attack; replace a hand card with random neutral-soul spell | candidate pool, deterministic RNG and empty-pool behavior |
| 서먼빅버드 | own destruction; summon Big Bird at next allied position | card ID, slot and readiness |
| 서먼익스플로 | enemy destruction; summon Magic Explo at allied field end, disabled | distinct end-placement and disabled-state timing |
| 섬광의검술 | AP comparison chooses attack-copy skill or own-AP attack | AP snapshot, equality branch and recursion guard |

## A25 evidence inventory

A25 contains 10 groups, 20 candidate rows, 23 excerpts, and 15 expression variants. Two explicit evidence limitations:

- **수호일격**: the manifest has 2 candidates but only a short “attack skill (before skill defense)” excerpt for 아스트라나간 (`16090728486`); effect body is absent. Do not implement.
- **수문장출현**: the manifest distinguishes the attack-triggered summon/stat effect from a separate ★ area-defense text. Keep the channels separate; absence of the defense text in the second card is not evidence that the effect is absent.

Other A25 groups and principal gates:

| Skill1 | Main source-backed operation | Unresolved gate |
|---|---|---|
| 세계수의아이 | attack; summon Mandrarose B based on allied forest terrain count | exact generated card ID, coin type and duplicate guard |
| 세인트콜링 | hero counter increment; separate hero activation grants light soul and modifies counters | attack/hero channel separation and counter order |
| 소울컨슘 | AP≥1 attack; gain stats based on target's colored souls | colored soul aggregation, rounding and temporary/permanent duration |
| 소울컨퓨젼 | AP≥1 attack; compare next enemy unit AP and allied neutral-soul parity | neutral soul snapshot and target eligibility |
| 솔리스톨 | own destruction; add summon-soul amount to next turn soul generation | colored/neutral split and accumulation |
| 수집능력 | attack; copy enemy hand card whose level matches coin heads | coin-roll scope, tie selection and hand capacity |
| 숲의분노 | own destruction; conditional enemy terrain removal and allied terrain creation | terrain selection, slot and soul recalculation |
| 숲의연합 | AP≥1 attack; buff self by count of other allied forest units | attribute count snapshot and HP persistence |

## APK direct-label cross-check

All 20 A24/A25 labels occur zero times in the inspected APK `rules.js` and `rules.test.cjs`.

**Disposition:** A24/A25 remain source-evidence-only / non-executable. No handlers were added and no missing text was filled by analogy.

## Consolidated next gates

1. Recover the three incomplete candidate records across A21/A24/A25 from immutable DB29 source data or independently accessible original card pages: A21 돌연변이확산, A24 사자부활, A24 생명약화. A25 수호일격 needs the full effect body, not merely its trigger heading.
2. Separate hero activation from Skill1 attack triggers (샌드웜소환, 세인트콜링).
3. Implement deterministic card lookup, copy/replace semantics, slot behavior and event-cause attribution as distinct primitives, not one generic “summon/copy” operation.
4. Add source-backed positive, negative, boundary and interaction tests before execution promotion.

## Non-actions

- No DB29 data was modified.
- No DB30 was created or published.
- No PR was merged.
- No A24/A25 runtime rule was activated.
- No undocumented status, soul, coin, random-selection or card-copy semantics were inferred.
