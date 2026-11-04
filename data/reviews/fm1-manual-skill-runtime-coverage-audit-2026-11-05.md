# FM1 Manual Skill Runtime Coverage Audit — 2026-11-05

## Scope and safety

- Immutable card-data baseline: DB29. No DB30 issued; no merge to `main`.
- Runtime repository inspected: `dragonslayers-k/FM-OFFLINE`, branch `main`.
- CardDB work branch inspected: `feat/carddb-effect-semantic-pass`.
- This audit does not promote any rule, change source card data, or authorize an inferred effect.

## Verified current state

The CardDB test-design specification `data/reviews/fm1-manual-skill-engine-test-spec-2026-11-05.json` declares:

- 27 Manual-backed Skill1 definitions preserved.
- 0 executable rules in the specification.
- 0 card-specific source matches.
- 108 test cases are design-only (4 per rule).
- All 27 definitions remain `pending_engine_test`.
- Card matching remains `pending_db29_raw_inventory`.

The APK test file `tests/rules.test.cjs` currently contains 71 top-level tests. This includes meaningful runtime tests for a subset of Skill1 mechanics and eight separately gated Skill2 mechanics. The test suite's existence must not be confused with promotion of all 27 Manual definitions.

## Existing Skill1 runtime coverage observed

The test suite contains focused or aggregate assertions for at least these Skill1 mechanics:

- Defense bypass, fatal attack, piercing attack, beast tamer, bravery, frenzy, fear, copy attack, shield break, confusion, and defense conversion.
- Aggregate tests for manual special-attack stat conditions, source-name aliases, and compact DB29 mapping metadata.
- Existing tests include level-boundary checks for bravery/fear, AP-zero exceptions for bravery/fear, and canonical shield-break alias normalization.

This is partial implementation evidence only. It does not establish complete positive/negative/boundary/interaction coverage for every Manual rule. In particular, rule-by-rule coverage must be matched by exact `rule_id`, not inferred from a nearby Korean keyword or a broad aggregate test title.

## Separate Skill2 lane

The APK currently has eight source-card-gated Skill2 rules. Normalization requires the exact tuple:
- `specialSkill2MappingStatus = source_card_verified`
- `specialSkill2RuleAuthority = card_source`
- `specialSkill2ExecutionStatus = source-card-rule-implemented`
- known `specialSkill2RuleId` and exact matching Skill2 name

The Skill2 tests cover the eight implemented rules, with additional boundary tests for Pressure, Alliance/Racial Defense, Tactical Initiative, and Devoted Defense. Skill2 must remain separate from the Manual Skill1 lane.

## Required next work before any promotion

1. Inventory DB29 Skill1 rows by exact `specialSkillRuleId`, source label, card ID, exact card text, and source URL.
2. For each of the 27 rules, map the manual clause to at least one exact DB29 card-source example where available. Keep unmatched rules explicitly pending.
3. Compare each rule definition to the actual APK handler and add independent positive, negative, boundary, and interaction assertions.
4. Add source-backed cases for stat markers, HP destruction/retention, AP-zero triggers, target eligibility, and ordering where the manual clause requires them.
5. Only after source matching and tests pass, update the rule's implementation status. Do not bulk-promote from the existence of aggregate tests.

## Decision

No rule is promoted by this audit. The current state is a mixed runtime: selected Skill1 mechanics have tests, eight Skill2 mechanics are source-gated and tested, while the 27-rule Manual catalogue remains formally pending at the CardDB promotion gate. The next implementation batch should target the highest-risk gaps revealed by the exact DB29 card inventory, not add speculative handlers.
