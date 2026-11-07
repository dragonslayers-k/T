# Skill1 A41–A45 source-to-APK gap review — 2026-11-06

## Scope and repository snapshot
- CardDB branch: `feat/carddb-effect-semantic-pass`; baseline HEAD `4308cd776c2942703eb77f5b263e36dc651bd3e5`.
- APK branch: `feat/combat-event-foundation`; inspected HEAD `4033c1ab84c054c070ad187106a577600585503a`.
- Inspected APK files: `app/src/main/assets/game/rules.js`, `tests/rules.test.cjs`.
- A41–A45: 50 candidate groups, 50 unique exact labels. Exact-name text comparison, not behavior proof.

## APK literal-name comparison
All 50 labels were checked against the inspected APK rules source and test file. Every label had 0 literal occurrences in `rules.js` and 0 in `rules.test.cjs`.

## Unavailable or qualified source evidence
- A42: `매직펌프킨` (`16101928562`) has zero effect excerpts.
- A43: `메탈아레아` (`16113028637`) has zero effect excerpts.
- A45: `배틀타워` (`13010226609`) has zero effect excerpts.
- A44: `무지개발산` descriptive `card_text` must be separated from its source effect excerpt.
- A41: `레드랜드` contains an explicit future tooltip correction note; treat as stale/qualified until corroborated.
- Other excerpts do not by themselves grant execution approval; preserve card-specific unresolved conditions from the manifests.

## Semantic clusters to keep distinct
- Hero counters, hero-point counters, and hero ability activations (A41, A43–A44).
- Coin sign/value mutations and ordinary stat changes (A41, A43, A45).
- Hand replacement/creation, graveyard deletion/movement, and unit recreation (A41–A45).
- Skill1 versus attack/defense techniques and unique card-bound handlers (A41, A44–A45).
- Equipment selection/mapping, field position, target scopes, and AP/HP comparison (A42–A45).
- Triggered status removal/destruction and status durations (A42–A43).
- Descriptive text and stale tooltip notes versus executable text (A41, A44).

## Disposition
- All 50 groups remain `pending/non_executable` until card-specific semantics and regression tests are verified.
- No APK code changed in this evidence-only pass.
- DB29 immutable; DB30 not issued; PR #9 remains open; no merge.
- Cumulative Skill1 evidence inventory after A45: 2,358 candidate rows / 2,405 excerpts / 649 exact text variants. Inventory counts, not implementation-complete counts.
