# Runtime Profile Contract — DB29 to FM-OFFLINE

- Date: 2026-11-06 (KST)
- Scope: T PR #9 and Android FM-OFFLINE PR #28
- Source baseline: DB29 `fm1-carddb-29` (read-only)
- Governing policy: `docs/GAMEPLAY_COMPLETION_POLICY_2026-11-06.md` and Library master v4.9, Appendix 29

## 1. Two independent completion axes

The source/provenance axis records what the original site, DB, Manual, or other evidence verifies. The runtime/playability axis records whether the Android engine can complete a legal card action. A pending source review must never be interpreted as a card-wide usability block.

Preserve the original source fields and review flags. Never overwrite them with inferred values. The Android pack validator must report source-verified coverage and runtime-ready coverage separately.

## 2. Runtime cost contract

Every card must receive a valid, payable runtime cost object. Valid keys are `dark`, `fire`, `water`, `forest`, `metal`, `earth`, `light`, and `neutral`. Negative, non-integer, unsupported, or missing values are invalid.

- `candidateCost` preserves source token distinctions and parsed candidate components.
- `runtimeCost` is the normalized cost passed to the engine.
- `runtimeCostStatus` is `implemented_verified`, `implemented_inferred`, or `fallback_payable`.
- `runtimeCostInference` records why an inferred/fallback value was selected.
- `runtimeUpkeepCost.neutral` records only recurring NCS upkeep for units.

Special soul handling:
- NCS is generic payment from any generated colored or neutral soul; for units only, its amount is recurring neutral upkeep.
- BONUS is normalized to generic `neutral` payment at card use. Its original BONUS identity remains in `candidateCost`; it is a one-time requirement and is excluded from recurring unit upkeep.
- Hybrid tokens require every inferred component color.
- Unknown or unparseable tokens receive a conservative payable neutral fallback; they are not silently treated as free.
- Explicit source no-cost is represented as `{ "neutral": 0 }`, never as a missing or empty object.

## 3. Runtime card-action disposition

- Unit AP/DP/HP use source values when valid. A nonpositive/missing HP uses a tagged minimum-one runtime fallback while source values remain preserved.
- An item whose native target condition cannot be mapped receives `runtimeItemConditionStatus: fallback_any_unit`. Keep a parsed own/enemy owner restriction where available; do not block the item solely because race/affiliation wording is unresolved.
- Standard lands use decoded source production. MagicLand retains its unresolved source effect but installs with zero invented ordinary production and `runtimeLandProductionStatus: fallback_noop`.
- A single exact simple-text spell effect with a supported attack/defend/battle-start trigger may use a tested inferred handler. Unsupported spell clauses use deterministic no-op. Enchants remain fallback_noop until the Android engine has a correct event/duration-bound slot handler; the card still pays its runtime cost, leaves the hand, enters its terminal zone, and marks the action complete.
- Unit Skill1/Skill2 handlers use only source/manual-verified or tested inferred mappings. Unmapped individual clauses use fallback; provenance does not disable the unit.
- Upkeep must always be finite. Missing legacy upkeep metadata must never become positive Infinity or automatically end a match.

## 4. Engine and validator requirements

The resolver must select runtime values before source-review flags. A source-review flag is not a reason to reject a card. Actual invalid player actions remain rejected: insufficient resources, illegal phase, exhausted LP/deploy capacity, invalid ownership, invalid zone transfer, or an invalid target when no fallback target policy exists.

The pack validator must verify:
1. Exactly 15,350 unique card IDs and expected category totals.
2. A valid runtime cost for all 15,350 cards, with no unsupported `bonus` key.
3. A finite runtime upkeep profile for all 8,633 units.
4. Every spell/enchant clause has a terminal effect disposition.
5. All 15,350 cards pass the runtime action-readiness validation; blocked count is zero.
6. Source review counts remain visible and unchanged; they are not rewritten as source-verified.
7. MagicLand has no invented normal production.
8. Source image/card identity hashes and DB29 SQLite integrity remain intact.

## 5. Validation and workflow discipline

Lightweight JavaScript/Python tests run on ordinary PR synchronization. The large DB29-to-Android pack build and emulator smoke are separate expensive gates and must run only when explicitly requested via workflow_dispatch inputs or explicit `[build-card-pack]` and `[run-emulator]` markers. Do not re-run a successful validation on the same SHA.

## 6. Immutable boundaries

- DB29 tag, release, SQLite, and source records remain unchanged.
- DB30 is not published without separate explicit approval.
- T PR #9/#12/#13 and APK PR #28/#26/#25/#9 remain open and unmerged unless the user separately authorizes a merge.
- This contract is a development/validation rule; it does not itself certify the app or a complete original-rule implementation.

## 7. Current implementation work

APK PR #28 now has a DB29 SQLite converter that creates a runtime cost profile, a runtime cost resolver in the rules engine, finite upkeep handling, item target fallback, and deterministic terminal spell/enchant fallbacks. The validator has been changed to distinguish source review from runtime readiness. Final DB29 pack validation and emulator smoke passed on APK code HEAD `60681acc02974f6f6e8721def63b24f0823a6d6e` in Actions #325. Later app.js/UI and workflow-only commits are recorded separately; the final current branch status must be rechecked before additional claims.


## 8. Integrated verification checkpoint — 2026-11-06

- T PR #9 HEAD `2aad86adf76a823446296f6754181b1cdb4da294` passed Actions #716 / run `42191294766`. Scope: lightweight regression tests, runtime overlay self-test and Python compile. This was not a new full DB29 audit or release.
- APK PR #28 code HEAD `60681acc02974f6f6e8721def63b24f0823a6d6e` passed Actions #325 / run `42192845020`: DB29 SQLite integrity/source checks, 15,350-card pack conversion and manifest validation, runtime profile/action audit, Debug APK packaging/signature/ZIP validation, emulator install/import, and WebView load of 15,350/15,350.
- At that exact SHA, the validator measured 15,350 runtime cost profiles ready / 0 blocked and 15,350 runtime action attempts / 15,350 completed / 0 blocked. Per-card terminal action probe is an execution-readiness check, not proof that every original semantic clause behaves identically in a full match.
- The action audit reported 48,281 effect clauses: 18 `implemented_inferred`, 48,263 `fallback_noop`; unsupported effects close only the affected clause while payment/action terminal state proceeds. Source review remains a separate axis. Do not describe this as full original effect semantics.
- CI-cost gate commit `0be807b9dd3b67e5555ea9140e9083d698301bf5` passed #327 / run `42197420334`; only JS/Python checks ran, while DB29 pack, JDK/SDK/Gradle/APK/emulator were skipped.
- UI/CI clarification SHA `77e1ee9723d6c10263498c68e8b65342fa28646f` passed #328 / run `42199670675`; lightweight JS/Python only. It did not rebuild APK.
- The card-detail UI warning mismatch was corrected on APK PR #28 commit `6dbdcf7ecabd645f20dd0073435999468409ff4a`. Source-review state now explains the actual runtime cost path where available; unsupported spell/enchant clause copy states that only the effect falls back and card payment/action/turn completion remains normal. Actions #329 / run `42202046670` succeeded with JS/Python checks and Debug APK build/application-ID/signature/ZIP integrity; DB29 pack and emulator were skipped.
- Remaining semantic work is evidence-linked triage of 48,263 fallback clauses and 1,249 low-confidence source rows, plus a fixed-seed end-to-end combat/turn scenario. Do not promote a clause without its evidence, guardrails and focused engine test.
- DB29 remains read-only and preserved; DB30 is not published; T PR #9/#12/#13 and APK PR #28/#26/#25/#9 stay open and unmerged.


## 9. Seeded battle-cycle and terminal victory regression — 2026-11-06

- APK PR #28 HEAD `be42ec585f6b124ceb310b875f7f08ae0d12b155`, Actions #341 / run `42206456060`: deterministic player+AI preparation, paid land installation, unit summon, paired battle/counter, round-2 transition and attacker rotation passed (233 JS tests, 0 failures; Python 13 passed).
- APK PR #28 test HEAD `3837301571449a17e28a09d08911cd5ce87f3336`, Actions #342 / run `42214419550`: direct deck-depletion terminal path through `resolveBattle()` passed. Two-soul direct attack removes the defender's final two cards; player wins and the round/attacker/preparation state does not advance (234 JS tests, 0 failures; Python 13 passed).
- Both are lightweight deterministic fixture tests; DB29 pack/APK/emulator were skipped. They prove the tested state transitions, not all card-effect semantics or a full match from the production 15,350-card deck. Retain #325 as the separate full DB29 pack/APK/emulator evidence.


## 10. AI draw-to-six terminal transition — 2026-11-06

- APK PR #28 test commit `de07a48573b8752a635e81667e5d905614c19550`, Actions #345 / run `42215759449`, initially failed one new assertion (234/235 pass). The test incorrectly hardcoded `AI` in the expected log while the test fixture's player name is `ai`; match state and winner assertions had already passed.
- Fix commit `59384b9381cad328ed60801895635077ecdeefba` compares the terminal log with the actual fixture `ai.name`. Actions #346 / run `42215917221` passed: 235 JS tests / 0 failures; Python converter 13 / OK.
- The test executes `FM.endPhase()` → opponent AI `beginPhase()` → `drawToSix()` with five cards in hand and an empty AI deck. It verifies no phantom draw, the player wins, state becomes finished, round does not advance, and `runAIPhase()` does not start after the terminal state.
- This covers a second terminal route distinct from #342's direct deck attack: preparation draw exhaustion. This is still fixture-level lightweight integration; DB29 pack/APK/emulator skipped and no full 15,350-card match is certified.


## 11. NCS upkeep deck-exhaustion terminal transition — 2026-11-06

- APK PR #28 test HEAD `c4bb96875778d3a038fba6e3a058191e943fa4a4`, Actions #348 / run `42216514570`: success; 236 JS tests / 0 failures, 13 Python converter tests / OK.
- The test traverses `FM.endPhase()` → AI `beginPhase()` → `payNeutralUpkeep()`. A single NCS upkeep remains unpaid because the AI has no available souls; the final deck card is destroyed; the human wins; AI hand refill/card review/action and round transition are prevented.
- Source basis: Dropbox Manual.zip `soulcost.htm` rules for neutral-cost units, upkeep each preparation turn, and deck-card destruction equal to unpaid amount. The test verifies the terminal boundary without modifying upkeep logic.
- The distinct terminal paths now have focused integration tests: #342 direct deck hit, #346 draw-to-six exhaustion, #348 unpaid NCS upkeep. These are fixtures and do not equal a full DB29 production-deck match. DB29 pack/APK/emulator remain separately evidenced by #325.


## 12. Manual Skill1 secondary cluster — charge/frenzy AP-zero DP boundaries

- APK PR #28 test commit `9575dcd77738daacd0d57ede0baa6e6f9fc928c2`, Actions #350 / run `42217090860`: success; 236 JS tests / 0 failures; Python converter 13 / OK.
- Manual `specialability.htm` §9: charge attacks with own AP and DP, including AP 0 / *0. DB29 Pathfinder `10010624588`: AP0 + own DP3 − defender DP2 = 1; AP0 + own DP1 − defender DP3 = 0.
- Manual §13: frenzy sets own HP to one and adds sacrificed HP to attack damage. DB29 Dark Familiar `10010624538`: AP0, HP4 sacrifices 3; defender DP2 reduces resulting damage to 1; attacker stays at 1 HP.
- The remaining secondary cluster review also checked Fatal Attack HP=1 floor/no-revive, Bravery/Fear equal-level thresholds at AP0, and Regeneration +1 at printed max HP / HP marker boundary. These tests were already present; no duplicate tests were added.
- #350 adds assertions only; no runtime code or source mappings were changed. This is not a full DB29 pack/emulator revalidation or full original-rules certification.


## 13. Manual Skill1 piercing attack — AP limit and zero-DP boundary

- APK PR #28 test HEAD `d95bbed32445de4b6577efe4600a0fa3cc0abb46`, Actions #352 / run `42218090054`: success; 236 JS tests / 0 failures; Python converter 13 / OK.
- Manual `specialability.htm` §4: destroy defender DP by own AP; when defender DP reaches zero, remaining AP causes HP damage. DB29 Manual card fixture Black Unicorn `10091525214` now tests AP2 vs DP4 (DP2 remains, no HP damage) and AP3 vs DP0 (3 HP damage). Prior AP4 vs DP2 (2 HP damage) remains.
- Negative target DP is not explicitly defined by this special-attack clause. Keep review-only and do not assume the general AP-minus-DP formula transfers to piercing.
- This is a test-only boundary addition, not a source mapping promotion or full data-pack/runtime validation.


## 14. Manual Skill1 piercing — stat-marker protected DP overflow

- Manual.zip `specialability.htm` §4: attacker AP destroys target DP; only the AP left after defender DP reaches zero becomes HP damage. The Manual's shared stat-marker paragraph says `△` prevents decreases and `▽` prevents increases.
- T specification `fm1-manual-skill-engine-test-spec-2026-11-05.json` identifies `piercing_attack` / `관통공격`, 172 exact DB29 Skill1 label rows, representative 블랙유니콘 `10091525214`, source value 51 and a recorded card URL. It still marks card-local effect text pending and has no exact card-local source text packet. This is label identity, not semantic approval.
- APK test commit `c665a105de796bb4eb10a60bdf1650990e52f2bd`, Actions #356 / run `42221573459`: one assertion failed (236 tests, 1 failure). With `△`, DP reduction was blocked but old logic incorrectly caused 4 HP damage.
- APK fix commit `6d736aa9e56c677aa7f2dcbfe94571b9a54d818b`, Actions #357 / run `42221699683`: success, 236 JS tests / 0 failures, Python converter 13 / OK. HP overflow now occurs only when positive DP was actually reduced to zero or defender DP was already <=0. `△` blocks both DP decrease and HP overflow; `▽` permits decrease and normal overflow.
- #355 / run `42221259328` also passed exact AP=DP and pre-existing negative-DP conservative cases. Negative DP is treated as already exhausted and never adds its magnitude as bonus damage; Manual §4 does not explicitly define that case.
- #357 was lightweight JS/Python only. DB29 pack, APK, emulator and source-row→pack→Android import lineage were not run. No mapping/data promotion is authorized by these tests.


## 13. Manual Skill1 shield-break DP boundary and marker interactions — 2026-11-06

- APK PR #28 test commit `74ce501d4b97081ad4223b9868eb9bb26711ea68`, Actions #361 / run `42223636601`: success; JS 236 tests / 0 failures; Python converter success.
- Exact Skill1 label fixture is DB29 해적전투원 `10010624551` / `방패파괴`; the Manual.zip source is `specialability.htm` §21: after an attack set target DP to zero; if target DP is negative, no effect. T spec records 96 exact label matches, but exact card-local effect excerpt remains pending; the test is Manual-rule fixture evidence only.
- Added boundaries: AP0 no-trigger; DP0 leaves ordinary AP damage active; negative DP unchanged; positive DP set to zero post-attack; `△` blocks the DP decrease, and no AP spillover is created; `▽` permits reduction. The skill's post-attack DP change does not create extra HP damage.
- Runtime code/source mapping/DB29 data were not changed. `implementation_status=pending_engine_test` in the T spec has not yet been revised because its accepted status vocabulary was not established here; track the new focused test evidence separately and resolve the schema/status field in a later explicit spec update. This avoids inventing an enum.


## 14. Manual Skill1 shield-break and curse marker boundaries — 2026-11-06

- Shield Break: APK PR #28 test commit `74ce501d4b97081ad4223b9868eb9bb26711ea68`, Actions #361 / `42223636601`, passed 236 JS / 0 fail and Python converter. DB29 exact label fixture Pirate Combatant `10010624551`; Manual `specialability.htm` §21 says target DP becomes zero after attack unless it is already negative. AP0 no-trigger, DP0, negative DP, positive DP, `△` (blocks decrease), and `▽` (allows decrease) are covered.
- Curse Attack: APK PR #28 test commit `51222519ffa6f22b015bf0cea9ef16829b92ea73`, Actions #363 / `42224203597`, passed 236 JS / 0 fail and Python converter. DB29 exact label fixture Dark Joker `10030324708`; Manual §22 says target AP/DP −2. Tests verify zero-AP no-trigger and the AP/DP marker directions independently (AP △ with DP ▽, and AP ▽ with DP △).
- Shared marker source is Manual `cardability.htm`. Both tests are fixture-level Manual rule evidence, not SQLite→converter→Android pack or actual device execution. No source mapping/data was promoted.
- The T Skill1 spec currently labels shield_break `pending_engine_test` while focused fixture assertions now exist; exact card-local effect packet remains pending. Do not invent a new status enum or treat exact Skill1 label identity as a recovered card-local effect excerpt.


## 15. Manual Skill1 Vampiric Attack HP marker directions — 2026-11-06

- Manual `specialability.htm` §7: restore 50% of actual HP damage, odd values round half-up. `cardability.htm` §6(b): `*` prohibits all stat changes, `△` prohibits decreases but allows increases, `▽` prohibits increases but allows decreases.
- DB29 exact Skill1 label representative: Dark Countess `10010624542` / `흡혈공격`, source value 788; exact-label group 115 rows. Card-local source packet remains a separate gate.
- APK PR #28 test commit `15162b6d46043e9e297392feecf48bc40d3bacce`, Actions #365 / `42228582000`: 236 JS / 0 fail, Python converter 13 passed. Adds HP `△` permits half-up +2 healing on 3 actual damage, HP `▽` blocks positive healing, and HP `*` blocks all healing. Existing tests cover 1/2/5 actual damage, blocked damage and `▼`.
- Lightweight test only; DB29 pack/APK/emulator skipped. No runtime mapping/source/DB29 mutation. Formal test spec remains design-only and must not be promoted based on fixture alone.


## 15. Manual Skill1 Aging Attack AP boundary evidence — 2026-11-06

- Manual.zip `specialability.htm` §8 defines Aging Attack as applying AP−2 to the attacked target. Common AP marker directions follow `cardability.htm`: `△` prevents decrease; `▽` permits decrease.
- Representative DB29 exact Skill1 label row: 타락자 `13020626691` / `노화공격`; T spec records 53 exact label matches. Card-local `exact_db29_source_text` remains null and `effect_excerpt_status=pending_card_local_semantic_packet`.
- APK PR #28 test commit `b88db5b55576854a2f8fe94ec5b72d2f078b66f6`, Actions #367 / run `42229779160`: success, 236 JS / 0 failures, Python converter 13 / OK.
- Added test cases: AP0 no-trigger; AP1 against defender DP2 where HP damage is 0 but the attack still applies AP−2; AP `△` blocks decrease; AP `▽` allows decrease; target AP1 receives full −2 and reaches −1.
- Fixture-level engine test only. Formal test-spec remains design-only (27 rules, 108 cases, zero executable rules); card-local source and data-pack lineage are separate gates. No mapping or DB29 data promotion.


## 16. Manual Skill1 target-ability AP marker boundaries — 2026-11-06

- Manual `specialability.htm` §§10/18/19: Beast Tamer, Magic Suppression and Weapon Suppression set target AP to zero only for the respective target ability. Common AP markers: `△` prevents decrease; `▽` permits decrease.
- Representative DB29 exact Skill1 label fixtures: 네추럴마스터 `11011925567` (63 matching rows), 혼드비스트 `10010624550` (56), 데크라프 `10010624543` (48). Exact card-local effect packet/runtime data-pack provenance remain separate from exact Skill1 label matching.
- APK PR #28 test commit `7c18d444f0b9d1e852abb7a8cef49dc0b0dec84c`, Actions #369 / run `42231717568`: success; 236 JS / 0 failures; Python converter 13 / OK.
- Each rule now covers AP0 no-trigger; matching target + AP `△` blocks AP=0; matching target + AP `▽` permits AP=0. Existing matching/nonmatching target ability checks remain.
- Fixture-level test only. No runtime code/source mapping/DB29 data change. The formal engine test spec remains 27 rules / 108 design-only cases / 0 executable pending its separate promotion contract.
