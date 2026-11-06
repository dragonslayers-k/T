# FM1 Manual Skill1 target-ability gate boundary audit — 2026-11-06

## Manual clauses

- `specialability.htm` §10 — Beast Tamer: attacking a unit with Beast ability sets target AP to 0.
- §18 — Magic Suppression: on attack against a Magic-ability unit, target AP becomes 0.
- §19 — Weapon Suppression: on attack against an Equipment-ability unit, target AP becomes 0.
- Shared stat-marker rules are from `cardability.htm`: `△` blocks decrease; `▽` allows decrease and blocks increase.

## Representative DB29 exact Skill1 fixtures

| Rule | Card | ID | Skill1 | Matched rows in T spec |
|---|---|---|---|---:|
| `beast_tamer` | 네추럴마스터 | `11011925567` | 야수조련 | 63 |
| `spell_suppression` | 혼드비스트 | `10010624550` | 주문봉쇄 | 56 |
| `weapon_suppression` | 데크라프 | `10010624543` | 무기봉쇄 | 48 |

These are exact Skill1-label matches. The formal spec still keeps card-local effect excerpts pending; do not claim exact TextBase/TextExtra evidence or SQLite→Android pack lineage.

## Previous coverage

The existing test checked one matching target ability for each rule and one nonmatching ability. It did not test the AP=0 trigger guard or the common AP marker directions for these rule-specific set-to-zero effects.

## Added tests

- APK test commit: `7c18d444f0b9d1e852abb7a8cef49dc0b0dec84c`.
- Actions #369 / run `42231717568`: success; 236 JS tests / 0 failures; Python converter 13 tests / OK.
- For each of the three rules:
  - AP=0 does not trigger; target AP is unchanged.
  - With the correct target ability and AP>0, target AP `△` blocks the decrease to zero.
  - With the correct target ability and AP>0, target AP `▽` allows the decrease to zero.
- Existing assertions remain: the exact target ability is affected; a different ability is not affected.

## Interpretation and promotion boundary

- Test-only change to `tests/rules.test.cjs`; no runtime code, mapping, converter, DB29 SQLite, card pack, tag or Release changed.
- Actions #369 ran JS/Python lightweight gates only. DB29 pack, JDK/SDK/Gradle, APK and emulator were skipped.
- Formal T test-spec stays design-only until its explicit promotion gate is met. Card-local source text and release pack lineage remain independent pending evidence.
- DB29 preserved; DB30 unpublished; designated PRs remain open/unmerged.
