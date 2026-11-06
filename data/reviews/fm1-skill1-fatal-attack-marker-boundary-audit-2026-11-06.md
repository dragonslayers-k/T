# FM1 Manual Skill1 — Fatal Attack HP stat-marker boundary audit (2026-11-06)

## Source rule and representative DB29 row

- Manual archive: `/판마/Manual.zip`, `specialability.htm` §3, Fatal Attack: target HP is set to 1.
- Exception: an already-destroyed target at HP 0 is not revived.
- Shared HP stat-marker behavior is defined in `cardability.htm`: `△` blocks decreases; `▽` permits decreases and blocks increases; `*` blocks all stat changes.
- Exact DB29 Skill1 match: 선더골렘 / `10012024612` / `치명공격` / source value 643. The T formal spec lists 153 exact-label rows, but this is not card-local TextBase/TextExtra evidence; its source excerpt remains pending.

## Existing coverage and gap

The APK suite already checks the Fatal Attack one-HP floor for target HP 1, 2, and 5, and separately guards against reviving a target whose HP is already 0. Those tests did not use the representative DB29 card ID for the one-HP floor scenario and did not assert HP decrease-marker interaction.

## Added focused assertion

- APK test commit: `7395be721af431753ebfa96ff0e8f17ae8402a1e`.
- Test: `DB29 Manual Fatal Attack source card respects HP decrease markers`.
- The fixture is linked to 선더골렘 / `10012024612` / `치명공격`.
- Assertions:
  - no marker: HP 5 → 1;
  - HP `▽`: decrease is allowed, HP 5 → 1;
  - HP `△`: decrease is blocked, HP remains 5;
  - HP `*`: all changes are blocked, HP remains 5.
- This is test-only. No combat handler, source mapping, converter, SQLite row, DB29 pack, tag, or Release was changed.

## Verification state

- APK PR #28 Actions #371 / run `42235607730`: success on exact test SHA `7395be721af431753ebfa96ff0e8f17ae8402a1e`. Node suite: 237 passed / 0 failed; Python converter tests: 13 passed; converter and enchant audit self-tests passed. DB29 pack, Gradle/APK build and emulator steps were skipped by the lightweight PR gate.
- DB29 remains immutable; DB30 is not issued.
- PR #9 and PR #28 remain open/unmerged.
- This test does not complete the formal T Skill1 promotion gate, card-local source packet, or SQLite → converter → Android import lineage.

## Next

After the lightweight Actions result is confirmed, continue the per-rule ledger only where a source-backed assertion gap remains. Do not repeat the HP 1/2/5 floor or HP=0 no-revive assertions. The production DB29 source-to-pack lineage gate remains a separate, higher-value integration task.
