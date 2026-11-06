# Skill1 A23 source-to-APK gap audit — 2026-11-06

## 기준 및 검증 범위

- CardDB branch: `feat/carddb-effect-semantic-pass`
- CardDB parent HEAD: `f4f9c08e4081931058b1be1194d9e1c484a1e973` (Actions #631 success)
- APK branch: `feat/combat-event-foundation`
- APK source: `app/src/main/assets/game/rules.js` (`d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`)
- APK tests: `tests/rules.test.cjs` (`212a8d2c098116349b58cc47871207d3af064346`)
- Immutable baseline: `fm1-carddb-29`. No DB29 edits, no DB30 release, no PR merges.

This is a source-evidence inventory and direct-label cross-check. A missing direct Korean label does not prove that no reusable generic primitive exists. It does mean no direct named handler or named regression fixture was found in the two inspected APK files.

## A23 inventory

A23 covers Skill1 frequency ranks 182–191: 10 groups, 20 candidate rows, 21 excerpts, 14 expression variants. The extra excerpt in 바다의지원 is an equipment description and is explicitly excluded from its Skill1 rule semantics.

| Skill1 | Trigger and operation evidenced in the manifest | Main unresolved gate |
|---|---|---|
| 바다의지원 | own field removal; summon separate allied water-soul and enemy neutral-soul producers | exact summon card IDs, side/slot and soul payload |
| 복사공격 | AP≥1 attack; replace self with unit matching opponent card number | copy vs identity replacement; preserve HP/equipment/status/owner |
| 복수공격 | enemy removal; reduce next eligible enemy stats by removed unit kill count and increase own stats | zero-kill behavior, exact stat mapping and duration |
| 본그로잉 | attack; create Bone Tower in graveyard and replace a hand card with Bone Mammoth | generated IDs, hand selection, temporary level vs permanent stats |
| 분노의폭풍 | enemy removal; exchange an enemy hand spell with an allied hand card | target selection, hand slots, full/empty-hand behavior |
| 분투공격 | AP≥1 attack; +2 damage if own AP is lower than opponent AP | compare base/current/rolled AP; damage-vs-DP order |
| 브레인스톰 | own field removal; copy highest-level enemy hand card into allied hand after level/NCS transformation | tied highest cards, NCS meaning, original preservation, full hand |
| 브루탈비스트 | enemy removal; conditional HP gain and permanent upkeep/soul-cost adjustment | HP cap, upkeep floor, soul cap and boundary |
| 블러드스웜 | own field removal; remove cause enemy unit and one allied terrain | cause attribution, terrain selection, soul recomputation |
| 사기고취 | enemy removal; alter positive/negative coin counts on allied field/hand units | coin metadata arithmetic, persistence, hand target |

## APK direct-label cross-check

All 10 A23 Skill1 labels occur zero times in the inspected APK `rules.js` and `rules.test.cjs` files.

Therefore A23 is **source-evidence-only / non-executable**. No handlers were added, no behavior was inferred from label similarity, and no effect was promoted.

## Reusable engine primitives vs. rule completion

The APK branch already has combat event/queue foundations and validated zone-transfer primitives. These are not sufficient by themselves to claim A23 rules are implemented:

- field-removal events must retain the exact cause unit and distinguish destruction from other removals;
- card identity replacement, clone/copy, and generated-card creation are distinct operations;
- hand and field slot placement need deterministic full/empty behavior;
- coin counters and soul/upkeep values require explicit persistence and caps;
- multi-step effects need ordering and rollback/atomicity tests.

## Required test gates before any A23 execution

For each card-backed expression, add independent positive, negative, boundary, and interaction tests. At minimum:

1. removal-cause identity and non-destruction field exits;
2. copy vs. replacement with ownership, card number, equipment, status, current/max HP;
3. full/empty hand and field slots;
4. AP equality and zero-kill boundaries;
5. permanent upkeep/soul/coin mutations and all documented floors/caps;
6. multi-target ordering and terrain-driven soul recomputation.

## Non-actions

- No DB29 asset or release was changed.
- No DB30 was issued.
- PR #9 and PR #28 remain unmerged.
- No A23 Skill1 runtime handler was activated.
- No status, stacking, ticking, or field-removal semantics were guessed.
