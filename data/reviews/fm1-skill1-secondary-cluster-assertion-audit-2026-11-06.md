# FM1 Manual Skill1 secondary cluster — source and assertion boundary audit
Date: 2026-11-06

## Scope

This pass follows the earlier six-rule audit and covers the next Manual Skill1 cluster: fatal attack, charge attack, bravery, fear, regeneration and frenzy. Primary source: Dropbox `/판마/Manual.zip`, `specialability.htm` and `cardability.htm`. The tests are source-backed handler fixtures; this audit does not upgrade pack mappings or claim the fixture rows are a full release-lineage check.

## Manual definition and current test coverage

| Rule | Manual source meaning | DB29 card / fixture | Assertions found or added | Remaining caution |
|---|---|---|---|---|
| `fatal_attack` | Fatal Attack sets the target's HP to 1; an already-destroyed unit at HP 0 must not be revived | compact Manual fixture; the lethal-boundary test does not include a card ID in its fixture constructor | Target HP 1, 2, and 5 all finish at 1 HP; zero rolled AP does not trigger opponent-facing effects; a zero-HP target remains destroyed | Keep this separated from exact DB29 card mapping until a card-ID/SQLite/pack lineage fixture is attached |
| `charge_attack` | §9: attack with the unit's AP and DP; DP can still produce attack damage when AP is 0 or marked *0 | Pathfinder / `10010624588` / 돌진공격 | Existing AP2 + own DP3 − defender DP1 = 4; added AP0 + own DP3 − defender DP2 = 1; added AP0 + own DP1 − defender DP3 = 0 | Current tests establish arithmetic at these boundaries; do not infer additional target/phase exceptions not present in Manual |
| `bravery_attack` | §11: +1 damage against equal-or-higher level targets, even when AP is 0; no effect against lower level | Tattoo Fighter / `10010624545` / 용맹공격 | Equal level at AP0 gives 1; lower target gives 0 | Test uses exact DB29 card ID in fixture comments; source mapping provenance stays distinct |
| `fear_attack` | §15: +1 damage against equal-or-lower level targets, even when AP is 0; no effect against higher level | Dark Priest / `10050424835` / 공포공격 | Lower/equal target at AP0 gives 1; higher target gives 0 | Same fixture-vs-release lineage distinction |
| `regeneration` | §12: unconditional HP +1 on attack | Wolf Rider / `10010624560` / 재생능력 | HP +1 at printed maximum HP even when defender DP blocks all damage; HP-increase protection marker prevents increase | Existing marker-direction test remains a separate guard; do not cap at max HP because Manual says +1 |
| `frenzy_attack` | §13: set own HP to 1, and add the sacrificed HP to attack damage | Dark Familiar / `10010624538` / 광분공격 | AP0, HP4 becomes HP1 and adds 3 damage; one-HP floor sacrifices none; added AP0 + sacrificed HP3 − defender DP2 = 1 | Exact DB29 card ID is present; do not change the one-HP floor |

## New focused assertions — Actions #350

- Test commit: `9575dcd77738daacd0d57ede0baa6e6f9fc928c2`
- Actions #350 / run `42217090860`: success.
- Node suite: 236 tests / 0 failures.
- Python converter tests: 13 passed.
- Added only test assertions; no `rules.js`, data converter, DB29 source or rule-mapping promotion was included in this test commit.
- The test log explicitly confirms:
  - `DB29 Manual source-backed Skill1 cards preserve petrify, aging and charge attack rules`
  - `DB29 source card 다크퍼밀리어 uses Manual frenzy attack and leaves the attacker at one HP`

## Conclusion and guardrails

The six-rule secondary cluster now has Manual-linked assertions for its major trigger/level/HP/stat boundaries. Charge and frenzy gained new defender-DP arithmetic cases at AP0. This is not a complete audit of all 27 Skill1 rules, not a database pack/import test, and not proof that all source rows are approved for execution. Keep fixture evidence, card-local source verification, converter/SQLite/pack lineage and actual runtime execution as separate axes. DB29 remains preserved; DB30 is not published; designated PRs remain open/unmerged.
