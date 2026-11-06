# FM1 Manual Skill1 debuff-rule boundary audit — 2026-11-06

## Scope and source

This focused review follows Manual.zip (Dropbox `/판마/Manual.zip`) and the current APK engine tests for two neighboring Skill1 rules. It does not approve card-local semantic packets or change source mappings.

## 1. Shield Break — `shield_break`

**Manual source:** `specialability.htm` §21. After the attack, target DP becomes 0. If target DP is negative, the effect does not occur.

**DB29 exact Skill1 label:** 해적전투원 / `10010624551` / `방패파괴` / source value 249. The T spec reports 96 exact Skill1 label matches. The representative row still has `exact_db29_source_text=null` and `effect_excerpt_status=pending_card_local_semantic_packet`; exact label identity is not card-local effect text.

**Assertions:** APK PR #28 test commit `74ce501d4b97081ad4223b9868eb9bb26711ea68`, Actions #361 / run `42223636601`, success (236 JS tests / 0 fail; Python converter passed).

- AP=0: no trigger; positive DP remains.
- DP=0: ordinary attack can damage HP; DP remains zero.
- DP<0: special effect has no effect; negative DP remains unchanged.
- DP>0: DP becomes zero after the attack.
- DP `△`: decrease is prohibited, so positive DP remains and there is no HP spillover from the shield-break action.
- DP `▽`: decrease is permitted and DP becomes zero.
- The DP-setting effect is post-attack and does not itself add damage to HP.

## 2. Curse Attack — `curse_attack`

**Manual source:** `specialability.htm` §22. The attacked target receives AP−2 and DP−2.

**DB29 exact Skill1 label:** 다크조커 / `10030324708` / `저주공격`.

**Assertions:** APK PR #28 test commit `51222519ffa6f22b015bf0cea9ef16829b92ea73`, Actions #363 / run `42224203597`, success (236 JS tests / 0 fail; Python converter passed).

- AP=0: the effect does not trigger; target AP/DP remain unchanged.
- AP marker `△` blocks AP−2 while DP marker `▽` allows DP−2.
- AP marker `▽` allows AP−2 while DP marker `△` blocks DP−2.

## 3. Test-only change and status separation

- The APK runtime handler and data converter were not changed by #361/#363; the commits only expanded `tests/rules.test.cjs`.
- No SQLite row, DB29 asset, tag or Release was changed. DB29 stays preserved; DB30 remains unpublished.
- These tests prove fixture-level Manual rule interactions, not that the representative card's HTML details were recovered or that the row has been traced through SQLite→converter→Android pack→device import.
- The T machine-readable spec still lists `implementation_status=pending_engine_test` for `shield_break` while fixture tests now exist. Its accepted enum/schema was not verified, so no new status value was invented. Keep the card-local effect packet pending until that evidence is recovered.
- Actions #361/#363 are lightweight JS/Python checks; DB29 pack/APK/emulator were skipped.

## Remaining action

Verify the T spec validator/consumer's allowed status vocabulary, then update the `shield_break` machine-readable status without changing `card_source_matching.effect_excerpt_status` or `exact_db29_source_text`. Separately recover the card-local source packet for `10010624551` if possible. Do not conflate focused test completion with production DB29 pack lineage.
