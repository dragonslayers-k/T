# FM1 Manual Skill1 — rule-by-rule APK coverage ledger (initial source audit)
Date: 2026-11-06

## Scope and control

This is an initial source inspection of the APK branch and a test-title/assertion-oriented inventory. It is not a runtime promotion decision and not a complete assertion-level proof for every rule.

- CardDB: `dragonslayers-k/T`, branch `feat/carddb-effect-semantic-pass`, HEAD `026bd1edc731fb65929b802ba98d81eafb76b008`
- APK: `dragonslayers-k/FM-OFFLINE`, branch `feat/combat-event-foundation`, inspected HEAD `4033c1ab84c054c070ad187106a577600585503a`
- Inspected APK source: `app/src/main/assets/game/rules.js`, `tests/rules.test.cjs`
- DB29 immutable; DB30 not issued. PR #9 and #28 remain open/unmerged.
- Mapping guard: only `manual_verified` + `manual` authority + a known Manual rule ID is eligible in the compact DB29 path. Community/inferred candidate records remain fail-closed.
- Main combat handler: `resolveUnitAttack` (source lines around 1260–1417 at inspected SHA).

## Coverage interpretation

- **Focused**: a test title indicates a specific mechanic/card outcome or a targeted boundary.
- **Aggregate/card-group**: an assertion is grouped with other mechanics or several examples; this is not independent four-way coverage.
- **No dedicated test title identified**: title scan alone cannot establish absence; inspect assertions before assigning a definitive gap.
- **Handler branch**: the source contains an explicit implementation branch. This alone does not prove rule fidelity.

## 27-rule initial ledger

| Manual rule ID | Canonical Skill1 label | Handler branch found | Test evidence located in inspected suite | Initial gap / caution |
|---|---|---|---|---|
| normal_attack | 일반공격 | Yes; default AP−DP path and Manual baseline mapping | DB29 source card 은룡의검 ordinary-attack baseline | Add direct negative/threshold test; avoid treating default path as full independent test coverage |
| defense_bypass | 방어무시 | Yes; damage=AP, DP bypass | Focused: compact DB29 defense-bypass clamp; source card 카오틱비스트 positive/negative DP | Review HP marker and AP=0 cases independently |
| fatal_attack | 치명공격 | Yes; HP-to-1 floor, requires rolled AP≥1 | Focused: lethal one-HP floor and already-zero-HP no-revive tests | Verify marker interactions and AP=0 trigger explicitly |
| piercing_attack | 관통공격 | Yes; consumes positive DP up to attack power | Aggregate: Manual piercing/weaken test group | Separate positive/negative DP, DP marker and remaining-damage boundary tests |
| weaken_attack | 약화공격 | Yes; AP−1 and DP−1 on eligible attack | Aggregate: Manual piercing/weaken test group | Independent AP/DP marker direction and zero-AP trigger assertions needed |
| petrify_attack | 석화공격 | Yes; AP=0 and DP+1 | Aggregate: source-backed petrify/aging/charge group | Isolate DP marker, AP marker, AP=0 trigger and resulting values |
| vampiric_attack | 흡혈공격 | Yes; heals ceil(actual HP damage/2) | Focused: actual HP damage, round-up, HP marker | Add lethal/zero-damage and healing cap/marker cases if Manual requires |
| aging_attack | 노화공격 | Yes; target AP−2 | Focused: source card 타락자 applies full AP−2 below zero | Add zero-AP trigger and AP marker/negative stat boundary |
| charge_attack | 돌진공격 | Yes; attack AP + attacker DP − defender DP | Aggregate: source-backed charge group | Isolate signed DP and stat-marker cases |
| beast_tamer | 야수조련 | Yes; exact target ability contains 야수, then AP=0 | Focused/aggregate: exact target ability test with suppression skills | Ensure non-beast target negative and ability-tag precedence |
| bravery_attack | 용맹공격 | Yes; +1 attack power when defender level≥attacker | Focused aggregate: bravery/fear level relation, AP=0 behavior | Separate own/target level below/equal/above and AP=0 checks |
| regeneration | 재생능력 | Yes; +1 HP on attack | Focused: even if defender DP blocks all damage; max-HP handling | Check HP marker direction, cap, attack trigger negative |
| frenzy_attack | 광분공격 | Yes; attacker HP sacrifice to 1, bonus added | Focused: source card 다크퍼밀리어 leaves attacker at 1 HP | Add low-HP/HP-marker and no-sacrifice boundary cases |
| consecutive_attack | 연속공격 | Yes; (AP−1)×2−DP | Focused: DP and boundary clamps | Check AP 0/1 and signed DP independent assertions |
| fear_attack | 공포공격 | Yes; +1 attack power when defender level≤attacker | Focused aggregate: bravery/fear level relation, AP=0 behavior | Separate own/target level below/equal/above |
| charm_attack | 매료공격 | Yes; target AP=0 only if resulting damage is 0 | Focused: AP disabled only when DP blocks all HP damage | Test positive damage negative case, AP/marker direction |
| ability_seal | 기술봉쇄 | Yes; resets Skill1 to ordinary attack | Focused: 환상낚시꾼 Skill1-only change preserving Skill2 | Add duration/persistence and already-normal Skill1 cases |
| spell_suppression | 주문봉쇄 | Yes; exact target ability contains 마법, AP=0 | Aggregate: exact target ability grouped test | Independent spell target positive/non-spell negative and marker |
| weapon_suppression | 무기봉쇄 | Yes; exact target ability contains 장비, AP=0 | Aggregate: exact target ability grouped test | Independent equipped/non-equipped and tag semantics |
| copy_attack | 공격복제 | Yes; uses defender effective AP minus defender DP | Focused: 진실의거울 copies effective AP; AP=0 produces no damage | Add copied AP boundary and DP signed interactions |
| shield_break | 방패파괴 | Yes; target DP=0 when rolled DP≥0 | Aggregate: Manual shield-break and curse stat-change test | Test negative DP, DP marker, AP=0 and target DP state |
| curse_attack | 저주공격 | Yes; target AP−2, DP−2 | Focused/aggregate: Manual shield-break and curse stat-change test | Separate each stat marker and below-zero boundaries |
| defensive_use | 방어이용 | Yes; damage=attack AP + defender rolled DP, gated AP≥1 | Focused: source card 포춘텔러 signed DP | Add AP=0 negative and DP sign boundary with exact source card |
| taunt_attack | 조롱공격 | Yes; defender HP to 1, lost HP becomes attacker AP | Focused: 다크조커 HP floor and AP transfer; no transfer at 1 HP | Add HP marker, lethal target and attacker AP marker checks |
| confusion_attack | 혼란공격 | Yes; target AP/remaining HP exchange logic | Focused: 견습수도사 swaps target AP and remaining HP | Add AP/HP marker and zero/negative boundary assertions |
| stealth_attack | 은폐공격 | Yes; attacker DP+1 | Focused: 블라인드랩터 gain even if damage blocked; DP-increase prohibition marker | Check DP marker direction and repeat-trigger boundaries |
| defense_convert | 방어변환 | Yes; positive rolled DP becomes negative absolute value | Aggregate: Manual defense-convert attack makes positive target DP negative | Isolate DP=0/negative no-change cases and DP marker interaction |

## Source-level findings

1. The APK’s normalization path is fail-closed for compact DB29 Manual Skill1 metadata. A community/inferred candidate cannot execute merely because its Korean label resembles a Manual name.
2. The core combat handler explicitly contains the 27 mechanic branches or the default ordinary-attack path. Source presence is not the same as independently verified behavior.
3. The suite has useful focused tests, including source-card examples, marker-direction checks, AP=0 special cases, and several boundaries. Coverage is uneven and multiple rules share aggregate test titles.
4. The 27-rule spec currently reports 108 test designs but 0 rules promoted to executable status in that specification. Keep this formal gate intact.
5. Test title scanning has false negatives because titles may use source card names or group several mechanics. The “no dedicated title” labels above are deliberately not final missing-test declarations.

## Next concrete audit step

Inspect the assertion bodies and actual handler conditions for the first priority cluster:
- shield_break
- defense_convert
- weaken_attack
- petrify_attack
- piercing_attack
- normal_attack

For each, record exact Manual clause, exact representative DB29 card ID/source URL, handler excerpt, existing assertion excerpt, and independent positive/negative/boundary/interaction case status. Add tests only where source-backed semantics establish expected results. No broad status promotion, speculative code changes, DB30 release, or merge.

## Acceptance

A rule remains pending until exact Manual authority and DB29 source matching are connected to the actual implementation and the dedicated assertions pass. Successful CI alone is not a blanket promotion.
