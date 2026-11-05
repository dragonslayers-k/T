# Cross-repository Skill1 evidence / APK validation checkpoint — 2026-11-05

## Repository snapshot
- Card database: [T](https://github.com/dragonslayers-k/T), PR #9, branch `feat/carddb-effect-semantic-pass`.
- APK/runtime: [FM-OFFLINE](https://github.com/dragonslayers-k/FM-OFFLINE), PR #28, branch `feat/combat-event-foundation`.
- DB29 is immutable. No DB30 release, `main` merge, or PR merge.

## DB29 exact source match findings
Source: immutable DB29 artifact from T Actions #558, artifact `13384922100`, `fm1-manual-skill-db29-source-match-2026-11-05.json`.

- 27/27 Manual-authority rules have exact Skill1 rows.
- Total matched rows: 3,158.
- All 3,158 matched rows use exact canonical labels (0 catalog-alias matches).
- Unique card IDs: 3,158; cross-rule duplicate card IDs: 0.
- Missing source detail URLs: 0.
- Matching is normalized exact equality only (Unicode NFKC + whitespace removal); substring/name inference is excluded.
- This proves label-to-source-card presence, not semantic correctness or engine readiness. Runtime-executable rules remain 0 in the audit.

A 3-sample-per-rule source ID/name index is recorded at:
`data/reviews/fm1-manual-skill1-db29-source-card-evidence-sample-2026-11-05.md`.
The complete 3,158-row JSON remains in the Actions artifact rather than duplicating a large export into the repository.

## APK runtime/test findings
- PR #28's previous latest successful run #175: [Actions](https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41964416258).
- Retrieved build artifact `13387431254`: debug APK present (86,698 bytes), emulator screenshot/log and build status included.
- Build status records emulator install/launch success, card pack from immutable DB29, data pack version 1.3.0, and 15,350 card rows / 15,350 images.
- Emulator log confirms `WEBVIEW_CARDS_LOADED=15350/15350`. This confirms the import/listing path in the emulator; it does not validate every gameplay rule.
- Enchant inventory audit in that artifact: 823 expected/actual/unique IDs, no duplicate IDs, no missing required fields, `auditPass=true`; execution mapping explicitly remains unimplemented.
- APK test suite contains a table-driven baseline test covering the 27 Manual Skill1 behavior branches plus separate AP-zero, alias and source-authority tests. The test structure is broad but still needs additional per-rule edge/marker/order tests.
- The latest #174 failure was an assertion expecting sequence 12 on events dispatched directly; actual contract was null until queue sequencing. #175 corrected that assertion and passed.
- Follow-on APK commit [`c2c93fa`](https://github.com/dragonslayers-k/FM-OFFLINE/commit/c2c93fa6fcb94d345dbb755854d1ada6048b2b4d) adds a runtime test for compact DB29 Skill1 mapping: manual authority should activate the defense-bypass rule; community or community-candidate metadata must fail closed. Its CI result is pending at the time this checkpoint was authored.

## Next evidence-driven work
1. Validate the compact DB29 mapping test in APK Actions; do not report it green until the job completes.
2. Start a dedicated edge-case batch for source-matched Manual rules: defense markers, AP-zero boundaries, HP=0 fatal behavior, and target-type gates.
3. Keep per-rule source IDs, Manual clauses, expected outcomes, and test evidence linked. Avoid promoting a rule solely because a generic test passed.
4. Update the full audit only after meaningful batches, not on every test/doc commit.

## Guardrails
Skill1 and Skill2 remain separate. Unknown or community-only mappings fail closed. Preserve all source text, IDs, URLs, and DB29 immutability. No DB30 or merge actions.