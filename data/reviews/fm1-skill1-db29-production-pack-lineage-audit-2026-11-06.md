# DB29 Skill1 production-pack lineage audit — 2026-11-06

## Scope and immutable boundaries

This audit follows four Manual Skill1 examples already represented in the APK rules test suite:

- 네추럴마스터 / `11011925567` / 야수조련 / `beast_tamer`
- 혼드비스트 / `10010624550` / 주문봉쇄 / `spell_suppression`
- 데크라프 / `10010624543` / 무기봉쇄 / `weapon_suppression`
- 환상낚시꾼 / `10020324644` / 기술봉쇄 / `ability_seal`

DB29 remains immutable. This is a lineage audit, not authorization to publish DB30, merge PR #9 or #28, or change the master reference.

## APK path observed at branch HEAD

APK branch inspected: `feat/combat-event-foundation`, HEAD `4033c1ab84c054c070ad187106a577600585503a`.

1. `scripts/fm1-offline/build-firestore-card-pack.py` reads the canonical T SQLite records and produces card JSON. For Skill1 it emits the source enum label, `specialSkillMappingStatus`, Manual authority, rule IDs, and `specialSkillExecutionStatus` only when a source mapping has `mappingStatus=manual_verified` and `ruleAuthority=manual`.
2. `app/src/main/assets/game/app.js` obtains the installed authoritative card pack through the native data-pack bridge, reads it in pages (250 records per page when the paged API exists), and normalizes cards with `FMCardSchema.normalizeMany`. The installed imported dataset is designated the sole playable-card source; demo `extraCards` are cleared.
3. `tests/rules.test.cjs` contains source-ID-labelled rule behavior tests for the first three listed cards. Those tests construct attacker and defender fixtures in JavaScript and supply Manual mapping fields directly. They verify rule behavior and matching/nonmatching synthetic target abilities, but do not demonstrate that the four cards' fields survive the actual T SQLite → release pack → Android import → WebView normalization path.
4. The ability-seal source test for 환상낚시꾼 also supplies its Manual mapping directly. It verifies that the special attack skill is suppressed/normalized and a separate Skill2 tuple remains distinct; it is not an end-to-end imported-pack test.

## What is established versus not established

Established from repository code:
- The converter has an explicit Manual-only Skill1 rule-ID selection gate.
- The WebView consumes the installed data pack through the native bridge and schema normalizer.
- The APK test suite already has focused rule-behavior coverage for these source-card IDs.

Not established by the inspected code/tests alone:
- Exact DB29 release SQLite rows for these four IDs have the expected mapping status, authority, canonical rule ID, and Skill1 label.
- Those values persist unchanged in the generated package and installed SQLite/data-pack payload.
- The native importer and WebView normalize the real package into executable rule metadata.
- A full Android emulator import test for this exact release/source revision passed.

No APK test suite, Android build, emulator import, or CI run was executed during this audit.

## Next implementation gate (do not substitute synthetic fixtures)

Add a release-bound integration test that consumes the actual immutable DB29 release artifact and generated card pack, and asserts for each listed ID:
- source name and Skill1 label match the DB29 source row;
- mapping status and authority are Manual-verified;
- the canonical rule ID is the expected ID;
- Skill1 and Skill2 are not conflated;
- normalized runtime card retains the verified fields;
- the existing rules behavior test runs using that normalized source card where practical.

The test must fail closed if the DB29 artifact, release manifest, source mapping, or generated package is unavailable or mismatched. Record artifact tag, commit, and checksums in its output. Keep source rows and card values unchanged; use this as a validation layer, not a data rewrite.

## References inspected

- APK `scripts/fm1-offline/build-firestore-card-pack.py` (Skill1 field emission)
- APK `app/src/main/assets/game/app.js` (installed pack bridge/import normalization)
- APK `tests/rules.test.cjs` (source-labelled fixture tests)
- APK `docs/DB29-INTEGRATION-VALIDATION.md` (required release/emulator gates)
