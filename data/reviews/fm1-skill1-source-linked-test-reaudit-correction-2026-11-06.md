# Re-audit: source-linked Skill1 assertions already present in APK tests (2026-11-06)

## Purpose
Correct and refine the preceding gap note. The APK branch test file was read in full during this pass; it already contains focused tests that the previous note did not account for. Therefore, the prior statement that the three rules only had aggregate fixture assertions was too broad.

## Inspected branch snapshots
- CardDB branch: `feat/carddb-effect-semantic-pass`, HEAD at review start `473329a6d62badd6cc5907e694532bc5cb6d2783`.
- APK branch: `feat/combat-event-foundation`, HEAD `4033c1ab84c054c070ad187106a577600585503a`.
- APK test file: `tests/rules.test.cjs`, blob SHA `212a8d2c098116349b58cc47871207d3af064346`.
- APK rules engine: `app/src/main/assets/game/rules.js`, blob SHA `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`.

## Existing focused assertions found

### 1. Beast-tamer, spell suppression, weapon suppression
Test name:
`DB29 Manual beast tamer, spell suppression and weapon suppression require the exact target ability`

The fixture carries source card ID, name, Skill1 label, canonical rule ID, and Manual mapping authority. It directly resolves an attack and asserts both matching and non-matching target categories:
- Beast-tamer: 네추럴마스터 / `11011925567` / `야수조련`; 야수능력 target AP becomes 0; 장비능력 target remains AP 4.
- Spell suppression: 혼드비스트 / `10010624550` / `주문봉쇄`; 마법능력 target AP becomes 0; 야수능력 target remains AP 4.
- Weapon suppression: 데크라프 / `10010624543` / `무기봉쇄`; 장비능력 target AP becomes 0; 마법능력 target remains AP 4.

This is a card-ID-linked and rule-ID-linked positive/negative fixture, more specific than a generic tag-only test. It still uses synthetic target fixtures and a test-supplied Manual-authority mapping; it does not by itself validate the production card package's actual parsed row or source-text-to-mapping pipeline.

### 2. Ability seal
Existing focused test:
`DB29 source card 환상낚시꾼 uses Manual ability-seal mapping to suppress a target special skill`
- Source card: 환상낚시꾼 / `10020324644` / `기술봉쇄`.
- Test asserts the target's special attack skill changes to ordinary attack and its normalized skill is `일반공격`.
- Another adjacent test checks Skill1 sealing does not erase a separate Skill2 tuple.

This tests the behavior after Manual mapping is supplied. It does not independently prove that the card data import/normalization binds all source rows or that all possible Skill1/Skill2 seal interactions are covered.

## Corrected disposition
- Remove the categorical claim that there are no dedicated source-linked tests for beast-tamer, spell suppression, weapon suppression, and ability seal.
- Treat the above as existing focused test coverage.
- Remaining work is now **production-data integration and edge-case/Manual coverage**, not a duplicate test addition:
  1. Trace source card record -> imported runtime fields -> canonical rule ID/authority for these exact IDs.
  2. Confirm test fixtures are loaded from the actual DB29 asset, or identify where manual fixture construction bypasses that path.
  3. Add only uncovered boundary cases supported by the Manual (target category edge, timing/expiration, slot/trigger sequencing).
  4. Run the APK test suite on the current branch and report exact test output; this review did not execute the suite.

## Guardrails
- No APK source or tests changed in this review.
- No DB30 release; DB29 remains immutable.
- PR #9 and PR #28 remain unmerged.
- No Actions or test success is claimed.
