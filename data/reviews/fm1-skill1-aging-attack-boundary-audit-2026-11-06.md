# FM1 Manual Skill1 Aging Attack boundary audit — 2026-11-06

## Primary rule source

- Dropbox `/판마/Manual.zip`, `specialability.htm` §8, 노화공격기술: when the unit attacks, the target receives AP−2.
- The current formal T spec describes `aging_attack` with trigger `unit_attack`, `attackerRolledAPMin=1`, effect `modify_target_stats(ap=-2)`.
- Common AP stat-marker semantics come from Manual `cardability.htm`: `△` prohibits decreases; `▽` permits decreases and prohibits increases.

## Representative DB29 card row

- 타락자 / card ID `13020626691` / Skill1 `노화공격`.
- T spec reports 53 exact label-matched rows for this Skill1 name.
- This is an exact Skill1 label match only. The spec still has `exact_db29_source_text=null` and `effect_excerpt_status=pending_card_local_semantic_packet`; do not claim the card-detail TextBase/TextExtra effect passage has been recovered.

## Existing coverage before this pass

The APK test already checked one positive case: AP1 attacker, target AP4/DP0, target HP decreases by one and target AP becomes 2. It did not separately assert AP=0 no-trigger, AP reduction when all HP damage is absorbed by DP, marker protection, or the negative-AP boundary.

## Added assertions

- Test commit: `b88db5b55576854a2f8fe94ec5b72d2f078b66f6`.
- Actions #367 / run `42229779160`: success; 236 JS tests / 0 failures; Python converter 13 tests / OK.
- AP=0: no attack and no AP decrease.
- AP=1 against defender DP=2: actual HP damage is zero, but the attack has occurred and aging still applies AP−2.
- Defender AP marker `△`: blocks the AP decrease.
- Defender AP marker `▽`: allows the AP decrease.
- Target AP=1: the full Manual AP−2 results in AP=−1; no undocumented zero clamp is introduced.

## Interpretation and promotion boundaries

- The commit changes `tests/rules.test.cjs` only. It does not change `rules.js`, the converter, DB29 SQLite, source mapping, card pack, tag or Release.
- The focused fixture test is engine evidence, not a formal spec promotion. The T test-spec remains at 27 rules / 108 design-only cases / 0 executable rules until its formal gate is independently satisfied.
- Card-local source evidence and SQLite→converter→APK pack lineage remain separate and pending. Exact Skill1 label matching is not card-local semantic evidence.
- Actions #367 ran the lightweight JS/Python PR checks. DB29 pack, JDK/SDK/Gradle, APK and emulator steps were skipped by the PR gate.
- DB29 remains preserved; DB30 unpublished; designated PRs remain open and unmerged.
