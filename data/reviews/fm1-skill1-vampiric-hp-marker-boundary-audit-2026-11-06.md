# FM1 Manual Skill1 — Vampiric Attack HP marker-direction boundary audit (2026-11-06)

## Source and representative card

- Manual.zip `specialability.htm` §7: Vampiric Attack heals the attacker by 50% of HP actually removed from the defender; odd damage rounds half-up (Manual example: HP−5 gives HP+3).
- Manual.zip `cardability.htm` §6(b): `*` blocks any stat change; `△` blocks decreases but allows increases; `▽` blocks increases but allows decreases.
- Exact DB29 Skill1 label fixture: Dark Countess / `10010624542` / `흡혈공격` / source value 788; exact-label group has 115 rows in the T spec. This does not claim card-local TextBase/TextExtra was recovered.

## Existing and newly added assertions

Existing focused test already verifies actual HP damage (not nominal AP), half-up healing for 1/2/5 damage, zero heal when DP blocks all HP damage, and HP increase blocked by `▼`.

New assertions add:
- HP `△`: with 3 actual HP damage, half-up vampiric heal is +2 (attacker HP 2→4).
- HP `▽`: positive healing is blocked (HP remains 2; no tempHP delta).
- HP `*`: all stat changes are blocked (HP remains 2; no tempHP delta).

## CI evidence

- APK PR #28 test commit `15162b6d46043e9e297392feecf48bc40d3bacce`.
- Actions #365 / run `42228582000`: success; 236 JavaScript tests / 236 pass / 0 fail; Python converter tests 13 passed.
- This was the lightweight PR gate. DB29 pack conversion, Gradle/APK build and emulator were not run.

## Evidence boundary

- Test-only change in `tests/rules.test.cjs`; no `rules.js` handler, mapping, SQLite source row, DB29 asset, converter or Release changed.
- The assertion proves the fixture's Manual marker interaction path, not the representative card's card-local effect text or SQLite→converter→Android pack/device lineage.
- Formal T spec remains design-only: its `test_design.executable=false` and cases `design_only` are unchanged. Do not promote `implementation_status` or `card_source_matching` based solely on this test.
- DB29 preserved; DB30 unpublished; PR #9/#28 remain unmerged.

## Next action

Continue with an existing source-linked Skill1 rule only where a concrete missing assertion is found in the crosswalk. Do not duplicate existing vampiric damage/rounding tests; this addition specifically closes HP `△`/ `▽`/ `*` direction coverage.
