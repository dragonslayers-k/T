# Skill1 candidate inventory exhaustion and next-stage gate — 2026-11-06

## Decision

The A1–A75 candidate inventory is exhausted at the current DB29 source artifact. Do **not** fabricate A76–A80 batches. Move the next workstream from enumerating Skill1 candidate labels to source-card-backed semantic adjudication and APK test coverage, using the existing 27-rule Manual Skill1 crosswalk as the authoritative anchor.

## Repository snapshot checked

- CardDB repository: `dragonslayers-k/T`
- CardDB branch: `feat/carddb-effect-semantic-pass`
- CardDB HEAD at audit: `0793ebf117a6593b00a052d600128ec794487751`
- APK repository: `dragonslayers-k/FM-OFFLINE`
- APK branch: `feat/combat-event-foundation`
- APK HEAD at audit: `4033c1ab84c054c070ad187106a577600585503a`
- DB29 remains immutable; DB30 is not issued.
- PR #9 and PR #28 remain open/unmerged.

## Evidence for ending A1–A75 enumeration

The final A75 manifest explicitly filters the source artifact to `source_field == "Skill1"`, identifies 704 distinct Skill1 groups, and records the last three groups at ranks 702–704 (히든레인져, 히어로캔슬, 히트웨이브). Its direct recount establishes the cumulative source-inventory totals:

| Measure | Total |
|---|---:|
| Distinct Skill1 candidate groups | 704 |
| Candidate card rows | 2,655 |
| Exact source excerpts | 2,767 |
| Exact phrase variants | 1,004 |

These are inventory counts only. They do not mean the rules are interpreted, verified, implemented, or tested.

## Next-stage authoritative anchor

The Manual Skill1 engine test specification reports:

- 27/27 Manual Skill1 names exact-matched to DB29 labels.
- 3,158 DB29 card rows mapped across those rule groups.
- 108 test designs (four intended classes per rule).
- 0 rules promoted to executable status in that specification.

The next pass must use the exact `rule_id`, representative DB29 card ID, source field/value, source URL, Manual clause, and the APK implementation/tests together. It should build a per-rule evidence ledger and then prioritize independently missing positive, negative, boundary, and interaction tests. Aggregate tests or keyword matches are not enough to promote a rule.

## APK inspection note (heuristic, not a coverage verdict)

The current APK test suite contains multiple source-backed Skill1-focused tests, including tests for defense bypass, fatal attack, stat markers, bravery/fear at AP zero, vampiric attack, regeneration, consecutive attack, ability seal, and several card-specific examples. A simple test-title-to-rule-ID scan produces false negatives because tests use aliases, card names, and aggregate titles. Therefore this scan is not a rule-coverage score and must not be used to mark any rule uncovered without inspecting the actual assertions and handlers.

## Controlled next action

1. Do not create an A76–A80 manifest from invented names.
2. Generate a 27-rule coverage ledger by inspecting actual APK handlers and assertions, not only test titles.
3. For each rule, attach a Manual clause and exact DB29 representative card evidence where available.
4. Add only source-supported tests/implementation; leave unresolved semantics pending and fail-closed.
5. Keep the immutable DB29 and PR/main/release controls unchanged.

## Acceptance boundary

A successful Actions run validates only the checked workflow. It does not by itself establish full CardDB completion or promote a source observation to executable game semantics.
