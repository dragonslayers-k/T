# Skill1 A46–A50 source-to-APK gap review — 2026-11-06

## Scope and repository snapshot
- CardDB branch `feat/carddb-effect-semantic-pass`, parent `f7a8d9740f598c5a485de188e3f1da81dabeb6c7`.
- APK branch `feat/combat-event-foundation`, inspected HEAD `4033c1ab84c054c070ad187106a577600585503a`.
- Inspected APK paths: `app/src/main/assets/game/rules.js`, `tests/rules.test.cjs`.
- A46–A50 cover Skill1 frequency ranks 412–461: 50 candidate groups, 50 distinct labels.
- Exact-name comparison only; absence of literal names is not a claim about all generic handler capability.

## APK exact-name comparison
All 50 candidate labels from A46–A50 were checked in the inspected `rules.js` and `rules.test.cjs`. Every label had zero literal occurrences in both files. Therefore no exact-label-linked implementation or regression test was found in this inspected source snapshot.

## Source evidence gaps / qualification
- A48: `빅샌드트랩` (`13010226610`) has zero source effect excerpts.
- A49: `샤이닝스파크` (`13010226611`) has zero source effect excerpts.
- A50: `서먼헌트` (`13010241409`) has zero source effect excerpts.
- A49: `생명의꽃` passage is flavor/descriptive `card_text`, not effect semantics.
- A47: `브라운랜드` and `블루랜드` source lines include future tooltip correction notes; require current corroboration before executable promotion.
- A46–A50 other source excerpts still carry unresolved card-specific rules; excerpts alone do not establish runtime semantics.

## Critical semantic distinctions
- Hero counter accumulation vs hero ability activation; hero-point counter vs ordinary counters (A46–A47).
- Source target card/AP/DP/HP snapshots, order of damage, damage type, and sequential target resolution (A46–A47).
- Hand/field/graveyard card movement, replacement, creation, summon, and deletion as distinct actions (A46–A50).
- Coin front count, coin-rate modification, coin types/signs, NCS/elemental soul, and cost mutation (A46–A50).
- Random pool / distribution / seed / candidate list and slot-space failure behavior (A48–A50).
- Item attachment, ownership, target filters, and attachment constraints (A46, A48–A50).
- Status duration, status activation, removal, and status-removal-triggered destruction (A46).
- Descriptive text and possibly stale tooltip content versus confirmed effect text (A47, A49).

## Disposition
- All 50 groups remain `pending/non_executable` until authoritative card-local meaning, all target/timing/cost/failure cases, and card-specific regression tests are verified.
- No APK code changed in this evidence-only review.
- DB29 immutable; DB30 not issued; no PR merge or branch cleanup.
- Cumulative Skill1 evidence inventory through A50: 2,408 candidate rows / 2,463 source excerpts / 707 exact text variants. These are source inventory counts, not verified or implemented effect totals.
