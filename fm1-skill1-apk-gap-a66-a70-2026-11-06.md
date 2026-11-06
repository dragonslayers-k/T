# Skill1 APK exact-label gap audit — A66–A70

- Date: 2026-11-06 (KST)
- CardDB repository/branch: `dragonslayers-k/T` / `feat/carddb-effect-semantic-pass`
- Baseline CardDB HEAD: `57a9579714afe8ae0005dd98a614ebf84757c389`
- APK repository/branch: `dragonslayers-k/FM-OFFLINE` / `feat/combat-event-foundation`
- APK HEAD checked: `4033c1ab84c054c070ad187106a577600585503a`
- APK source files checked: `app/src/main/assets/game/rules.js`, `tests/rules.test.cjs`
- APK file blob SHAs: rules.js `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`; rules.test.cjs `212a8d2c098116349b58cc47871207d3af064346`

## Scope and result

A bounded exact-label text search was performed for the 50 Skill1 candidate labels listed in manifests A66–A70 against the two APK files above.

- Candidate rows checked: **50**
- Exact candidate labels found in either inspected APK file: **0**
- Exact candidate labels absent from both inspected files: **50**
- APK runtime source/tests changed by this evidence audit: **No**

This result means only that the candidate labels are not present as exact text in these two inspected files. It does not prove that every effect surface or implementation path in the APK is absent.

## Candidate batches

- **A66 (ranks 612–621):** 질주능력, 집행, 차원붕괴, 차원의번개, 착란의춤, 찰나의승부, 창조의오른손, 천리안, 천부적재능, 천사의보호.
  - Manifest: 10 candidate rows / 11 excerpts / 11 exact variants.
  - Distinct unresolved primitives include hand-to-backfield land transfer; delayed status first tick; card replacement preserving a selected field; AP<=0 attack destruction; AP-threshold damage exceptions; hero counters and spell override.
- **A67 (ranks 622–631):** 천의, 청록의자손, 체인웨폰, 체인징밸류, 체인징어택, 초자연화, 축복수업, 치명능력, 침투확산, 카오스데드.
  - Manifest: 10 / 11 / 11.
  - Requires source-grounded branches for hand costs, hero counters, item copy/fallback, stat-sum comparison, enemy hand-to-field transfer, RNG distinct status selection, and status-field semantics. 침투확산 is marked as a defense-skill trigger axis, not conflated with Skill1.
- **A68 (ranks 632–641):** 캣송, 코스튬, 코인순화, 퀵폴리모프, 크로스카운터, 크로스카운트, 클로버, 킬링어택, 킬어설트, 타임리커버.
  - Manifest: 10 / 11 / 11.
  - 퀵폴리모프 has 0 source excerpts; keep pending. Separate same-text card mappings for 크로스카운터 and 크로스카운트. Additional gates: coin-side snapshot/card replacement, attribute-to-item mapping, physical damage, kill-count stat increase, conditional summon.
- **A69 (ranks 642–651):** 타임슬래시, 탈렌적성자, 탈부수기, 탐험정보수집, 태양신의강림, 태양의일격, 태초의힘, 태풍의눈, 통찰의눈, 트레져헌팅.
  - Manifest: 10 / 11 / 11.
  - Needs exact turn-digit branches, attack-skill mutation, land filter, hand/field/battlefield scopes, next-turn soul generation, status removal/re-application timing and slot-1 replacement.
- **A70 (ranks 652–661):** 트루블러드, 튼튼한논리, 파소에제련술, 파이어데몬, 파이어아레아, 파이어파워, 파인딩레거시, 펌프킨크래쉬, 페이트, 평화의갈구.
  - Manifest: 10 / 10 / 10.
  - 파이어아레아 and 펌프킨크래쉬 have 0 source excerpts; keep non-executable. Other open gates include damage/soul snapshots, DP assignment, skill mutation, deck/hand definition changes, attribute-based item assignment and level-branch summons.

## Evidence and runtime gate

The manifest excerpts are evidence candidates, not adjudicated semantics or executable approvals. Do not promote any candidate based solely on exact label presence or a source excerpt. Keep unresolved target selection, ties, card IDs, random pools, status duration/tick timing, ownership transfer, permanent-vs-temporary stats, slot constraints, and failure atomicity as explicit test gates.

## Cumulative inventory

- A1–A65 baseline: 2,558 candidate rows / 2,640 excerpts / 884 exact variants.
- A66–A70 addition: **50 / 54 / 54**.
- A1–A70 total: **2,608 candidate rows / 2,694 excerpts / 938 exact variants**.

These are Skill1 source-candidate inventory totals only—not semantic adjudication, runtime-ready rules, APK implementation coverage, or overall CardDB completion.

## Guardrails

- DB29 / `fm1-carddb-29` remains immutable.
- DB30 is not issued.
- CardDB PR #9 and APK PR #28 remain open and unmerged.
- No release, runtime promotion, or APK source change is made by this audit.
