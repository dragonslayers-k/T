# FM-OFFLINE Skill1 engine gap audit — 2026-11-05

## Audited revisions
- FM-OFFLINE main `rules.js`: `a98064062e95037e6c36abd1ceb4fadc36736975`
- FM-OFFLINE main `tests/rules.test.cjs`: `7a91dbf5ea0af3b2666aeb75b0636a596404c818`
- CardDB review branch: `feat/carddb-effect-semantic-pass`, head at audit time `95a80d1e788b68e33b55d174d505cc51d4528ffa` (PR #9, open).

## Confirmed engine architecture
- Skill1 normalization is in `normalizeSpecialSkillForEngine` (rules.js around line 132). For DB29 records with mapping metadata, execution is allowed only for `specialSkillMappingStatus=manual_verified` and `specialSkillRuleAuthority=manual`; other statuses return an empty skill.
- Skill1 execution itself is embedded in `resolveUnitAttack` (around line 846), primarily as explicit name checks for the already implemented manual rules.
- Skill2 has a separate allowlist and source-card verification gate in `normalizeSpecialSkill2ForEngine` (around line 176); its effects are resolved in separate defensive/destruction branches.
- Destruction processing is centralized in `destroyUnit` (around line 705), which currently contains explicit Skill2 destruction effects for 헌신방어 and 강한헌신방어.
- Stat mutation uses `changeUnitStat` and marker checks; changes are temporary stat deltas. Coin profiles are rolled once and shared across AP/DP/HP in a combat exchange.

## Verified gap for Skill1 batches A17–A20
The following 40 exact Skill1 names were checked literally against both audited files. None appears in either runtime `rules.js` or `tests/rules.test.cjs`. This is a source-name presence check, not proof that no lower-level primitive can be reused.

길티컨션스, 나락의화염, 더블디펜스, 동아리모집, 소울증오, 시간차공격, 시체폭발, 심판, 어둠의부름, 용의권능,
기술무력화, 눈덩이제작, 더블소울, 데스브레스, 디바이드어택, 버닝퓨리, 블레스, 빙결공격, 선물하기, 솔카운터,
아이언클래드, 야수강타, 에코카피, 자연의경고, 천상의벼락, 초음파, 칠색음, 켄드드레인, 코인적중, 클리브,
플라잉샷, 행운훔치기, 혼령흡수, 고대의힘, 고블린어설트, 기계배치, 눈덩이던지기, 달부수기, 대지의역사, 데스메모리.

## Implementation priority — do not promote without source-card tests

| Priority | Mechanic family | Candidate rules | Required engine work |
|---|---|---|---|
| P0 | Event lifecycle | 시체폭발, 데스브레스, 어둠의부름, 용의권능, 버닝퓨리, 자연의경고, 에코카피 | Add typed destruction events with pre-removal snapshot, event owner, cause, and stable slot/order. Distinguish 파괴 from 소멸. |
| P0 | Zone/card operations | 눈덩이제작, 선물하기, 고블린어설트, 기계배치, 나락의화염, 고대의힘 | Add validated card-ID lookup, hand/field/graveyard capacity rules, exact replacement/copy semantics, item attachment, and no-space behavior. |
| P0 | Damage routing | 더블디펜스, 디바이드어택, 시체폭발, 야수강타 | Separate base combat damage, direct damage, redirected damage, and multi-target damage; define DP interaction and damage snapshots. |
| P1 | Persistent/temporary stat or skill changes | 기술무력화, 동아리모집, 아이언클래드, 블레스, 클리브, 초음파, 칠색음, 혼령흡수 | Preserve stat markers and duration/ownership; avoid conflating Skill1 and Skill2 or permanent changes with battle-only temp deltas. |
| P1 | Soul/coin/turn calculations | 더블소울, 솔카운터, 켄드드레인, 플라잉샷, 행운훔치기, 시간차공격, 눈덩이던지기 | Add deterministic calculation inputs, timing snapshots, bounded probability modifiers, and explicit soul-pool/coin definitions. |
| P2 | Special condition / sparse evidence | 천상의벼락, 클리브 variants, 초음파 sparse row, 켄드드레인 sparse rows | Recover full card-local source text and exact generated-card/hero lookup before implementation. |

## Existing reusable primitives and limitations
- `changeUnitStat` respects immutable/up-only/down-only stat markers and adjusts temporary AP/DP/HP deltas. It does not itself encode permanent card changes.
- `destroyUnit` removes a unit and attached equipment to the owner's graveyard, then applies currently implemented Skill2 destruction effects. It has no typed event payload for other cards to subscribe to.
- `resolveUnitAttack` calculates a single attacker/defender exchange and applies defensive Skill2 damage reductions before HP loss. It has no general post-attack event queue or multi-target damage router.
- `coinProfile` provides deterministic injectable RNG and shared toss outcomes, but there is no generic per-player probability modifier layer for coin outcomes.
- Existing spell parsing intentionally rejects ambiguous/random/conditional/replacement text. New Skill1 effects must not be smuggled through the generic spell parser.

## Safe next implementation sequence
1. Add a typed, side-effect-free combat event description and tests for event timing/attribution; do not change card behavior yet.
2. Add exact card lookup and zone-operation helpers with capacity/ownership tests; do not bind any candidate rule until its generated card IDs are verified.
3. Add a deterministic post-combat event queue, keeping Skill1 and Skill2 handlers isolated.
4. Promote one mechanic at a time only when card-local source text, expected outputs, and regression tests agree.
5. Run the existing APK test suite once after a coherent batch, not after every small file edit.

## Decision
No runtime behavior was changed by this audit. The 40 candidates remain evidence-only. DB29 remains immutable; no DB30 was created; PR #9 remains open and unmerged.
