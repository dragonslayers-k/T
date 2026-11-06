# Skill1 source-to-APK gap review — A61–A65 (2026-11-06)

## Scope and APK comparison

This pass reviews source manifests A61–A65, candidate ranks 562–611 (50 Skill1 labels; Skill2 excluded). Exact-label search was performed across APK branch `feat/combat-event-foundation` in:
- `app/src/main/assets/game/rules.js`
- `tests/rules.test.cjs`

No exact candidate labels were found in either inspected file. This is a bounded exact-text comparison, not a statement about every APK asset or runtime surface. This evidence-only review did not modify APK source.

## Batch summary

| Batch | Rank span | Candidate rows | Excerpts | Exact variants | Main evidence gaps |
|---|---:|---:|---:|---:|---|
| A61 | 562–571 | 10 | 11 | 11 | Zero-evidence labels, terrain replacement, item destruction/copy/equip, hero rank promotion, defense skill hand replacement |
| A62 | 572–581 | 10 | 12 | 12 | Graveyard consumption and summon, permanent race/affiliation changes, status stacking, random item/unit pools, action availability |
| A63 | 582–591 | 10 | 11 | 11 | Delayed status tick, conditional resurrection, maximum-stat target ties, status purge, maintenance-cost damage |
| A64 | 592–601 | 10 | 14 | 14 | Hero ability/equip delay, coin-value vs coin-count, deck-top recreation, level bands, status-release chain damage |
| A65 | 602–611 | 10 | 14 | 14 | Ownership transfer from enemy graveyard, item/image transformations, magic-land aura, rank promotion, unclear target-scope wording |

## Source-specific blockers

- **Zero effect excerpts:** A61 워터아레아 and 은폐능력. Keep them label-only and non-executable.
- **Text authority and separation:** A63 저주받은영혼 requires precise 2-turn HP tick; A64 정령부활’s Skill1 deck recreation must remain distinct from card_text upgrade commentary; A65 지니스화 image effect is distinct from flavor text. Do not infer from narrative descriptions.
- **Ambiguous wording:** A65 지니’s first word needs source corroboration; 질서’s “상대 제외한 적 필드” scope needs clarification. A63 전투의함성 must distinguish highest-AP and highest-DP targets, including ties.
- **Distinct implementation primitives:** status tick/stack/remove, conditional resurrection and deferred triggers, permanent versus temporary stats, coin value versus number of coins, copy versus move/replace, equip compatibility, image/card identity, rank upgrade, field terrain swap/aura, staged HP/DP damage, and ownership conversion.
- **Atomicity and bounds:** Every effect involving multiple cards, resource costs, a summon/equip, or a terrain swap needs documented missing-target/space/cost failure semantics before runtime promotion.

## Cumulative inventory

- A1–A60: 2,508 candidate rows / 2,578 excerpts / 822 exact text variants.
- A61–A65: 50 candidate rows / 62 excerpts / 62 exact text variants.
- **A1–A65: 2,558 candidate rows / 2,640 excerpts / 884 exact text variants.**

These figures describe extracted Skill1 source candidates only. They do not represent semantic verification, executable rule coverage, APK completion, or completion of the 15,350-card / 55-field database.

## Next safe gate

Continue source-backed reviews and compare each candidate against the APK. Promote only after exact card identity/effect, trigger timing, target and ownership, duration/permanence, formula boundaries, resource/space failure, and card-specific regression tests are grounded. Keep DB29 immutable, do not issue DB30, and do not merge PR #9 or APK PR #28 without explicit approval.
