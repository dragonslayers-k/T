# Skill1 source-to-APK gap review — A51–A55 (2026-11-06)

## Scope and verification method

This review covers source-evidence manifests A51–A55 (candidate ranks 462–511, 50 Skill1 labels, Skill2 excluded). The DB29 source manifests were inspected as evidence. The APK comparison inspected `app/src/main/assets/game/rules.js` and `tests/rules.test.cjs` on branch `feat/combat-event-foundation` at HEAD `4033c1ab84c054c070ad187106a577600585503a`.

Exact-label search was performed for all 50 candidate Skill1 names across both inspected APK files. **No exact candidate labels were present in either file.** This is a bounded source/test comparison, not a claim that every feature is absent from every APK resource or runtime surface. No APK code was changed in this evidence-only pass.

## Batch-level findings

| Manifest | Candidate ranks | Candidate rows | Source excerpts | Exact text variants | Main unresolved evidence / semantic areas |
|---|---:|---:|---:|---:|---|
| A51 | 462–471 | 10 | 11 | 11 | Incomplete effect fragments (성실한준비, 성지화), missing evidence (성화전달); hero counter vs ability; next-turn 무소울 modifiers; soul delta damage; copy/summon semantics |
| A52 | 472–481 | 10 | 12 | 12 | Status definition and duration; target-selection ties; effect override; full status removal; summon/recreate; deck-top movement; poison rank escalation |
| A53 | 482–491 | 10 | 11 | 11 | Random special-skill pool/RNG; opponent skill copying; temporary stat markers; multi-summon/hand replacement; opponent graveyard transfer and ownership |
| A54 | 492–501 | 10 | 13 | 13 | Corrected tooltip vs actual behavior; hero counter vs hero point; cost/soul conversion; level reduction boundaries; recreate/replace identity; stat snapshot |
| A55 | 502–511 | 10 | 13 | 13 | Global status and HP-direct damage; AP/DP marker alteration; resource conversion; delayed status; multiple trigger stages and summon ordering |

## Cross-batch classification

The manifests repeatedly identify these distinct mechanics. They must remain separate rule primitives rather than being inferred from similar wording:

1. **Hero accounting:** attack-triggered hero counters, named hero points, and thresholded hero abilities are separate fields/triggers.
2. **Resource economy:** generated un-soul / elemental soul, maintenance-cost conversion, next-turn soul deltas, and “remaining soul” arithmetic have distinct pools and timing.
3. **Combat resolution:** HP-direct damage, DP bypass, HP damage multipliers, stat changes, attack-value changes, and permanent marker replacement are not interchangeable.
4. **Zone and identity operations:** copy/create/summon, recreate, replace, transform, deck-top generation, hand replacement, and graveyard transfer each need explicit ownership, identity, ordering, and preservation rules.
5. **Statuses and duration:** status names alone do not establish effect, stack/refresh, tick boundary, removal, immunity, or delayed activation.
6. **Selection and failure:** highest-AP/level ties, “next actionable” selection, missing targets, full field/hand, and partial multi-effect failure require documented behavior.
7. **Text authority:** tooltip correction notes, customer-service announcements, descriptive card text, and truncated lead-in fragments are not executable effect evidence.

## Card-specific evidence blockers

The inspected manifests flag the following high-risk incomplete/qualified cases:
- A51: 성화전달 has zero effect excerpts; 성실한준비 and 성지화 only provide incomplete condition/lead-in text.
- A52: all status names referenced by these cards need their authoritative status definitions and duration rules.
- A53: random ability pools and RNG distribution, plus opponent-side source skill and graveyard ownership semantics, are unresolved.
- A54: 신검의보호 has a tooltip correction/customer-support note; 실버랜드 includes a “tooltip update planned” qualification. Such notes must not be treated as final mechanics.
- A55: 악마의분노’s Skill1 spawn and separate spell definition must not be conflated; 알파게놈 has a delayed status trigger; 아이컨택 has a status definition requiring precise HP-damage timing.

These are evidence gates, not conclusions that a proposed mechanic is correct.

## Cumulative inventory

- A1–A50: 2,408 candidate rows / 2,463 source excerpts / 707 exact text variants.
- A51–A55: 50 candidate rows / 60 source excerpts / 60 exact text variants.
- **A1–A55 total: 2,458 candidate rows / 2,523 source excerpts / 767 exact text variants.**

The inventory measures extracted Skill1 source candidates, not verified semantics, executable rules, APK implementation, or completion of the full 15,350-card / 55-field database.

## Next safe step

Continue evidence-only batches and source cross-checks. Promote a rule only after card ID and authoritative effect text, trigger/target/snapshot timing, ownership/zone behavior, boundaries/failure paths, and regression tests are confirmed. Keep DB29 immutable, do not issue DB30, and leave PR #9 and the APK PR #28 open/unmerged absent explicit approval.
