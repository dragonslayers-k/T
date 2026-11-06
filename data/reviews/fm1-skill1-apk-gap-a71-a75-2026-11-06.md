# Skill1 APK exact-label gap audit — A71–A75

- Date: 2026-11-06 (KST)
- CardDB branch: `dragonslayers-k/T` / `feat/carddb-effect-semantic-pass`
- Baseline CardDB HEAD: `4203a6f6dfd1d1772b45fdb393d778e205ac7d49` (A66–A70 report commit)
- APK branch: `dragonslayers-k/FM-OFFLINE` / `feat/combat-event-foundation`
- APK HEAD checked: `4033c1ab84c054c070ad187106a577600585503a`
- Files: `app/src/main/assets/game/rules.js` and `tests/rules.test.cjs`
- File blob SHAs: rules.js `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`; tests `212a8d2c098116349b58cc47871207d3af064346`

## Exact-label check

A bounded exact-text search was performed for the 43 candidate Skill1 labels in A71–A75 against the two APK files above.

- Candidate labels checked: **43**
- Found in either inspected file: **0**
- Absent from both inspected files: **43**
- APK code/tests changed: **No**

This result applies only to the exact labels and files inspected; it is not a comprehensive claim about every APK implementation surface.

## Batch findings

- **A71 (ranks 662–671):** 10 candidate rows / 12 excerpts / 12 exact variants. 포레스아레아 has 0 source excerpts. Distinct gates: hero-counter versus activated ability, destruction-source status, item stat changes, whole enemy-field AP reduction, conditional summon and hand/yard consumption.
- **A72 (ranks 672–681):** 10 / 11 / 11. Requires clarification of target scope, hand+field population, state duration, marker removal, HP=1 semantics, coin-probability formula, and summon-vs-create distinction.
- **A73 (ranks 682–691):** 10 / 10 / 10. 홀리아레아 has 0 source excerpts. Important blockers include terrain replacement/summon atomicity, defense damage reduction, name-based lookup, hand card transformation, and yard-wide consumption with next-turn resource.
- **A74 (ranks 692–701):** 10 / 11 / 11. 화분's item-build-up commentary is kept separate from Skill1. Need exact calculations/order for stat changes, HP effects, image-only change, graveyard additions before damage, and self-stat reductions before extra damage.
- **A75 (ranks 702–704; last 3 groups):** 3 / 3 / 3. 히어로캔슬 requires an authoritative definition of the “first hero ability” and removal target; other cards require exact replacement ID, level/tie rules, and status duration.

## Corrected full-inventory totals

A75 manifest reports a direct re-count of the DB29 source artifact and explicitly corrects the earlier cumulative totals, which undercounted some early multi-card groups. Use this artifact-level re-count as the current source inventory baseline:

| A1–A75 | Skill1 groups | Candidate card rows | Source excerpts | Exact phrase variants |
|---|---:|---:|---:|---:|
| Full artifact re-count | **704** | **2,655** | **2,767** | **1,004** |

A71–A75 additions are **43 candidate rows / 47 excerpts / 47 exact variants**. The prior A1–A70 running values were 2,608 / 2,694 / 938; do not extend those mechanically because the original cumulative tally omitted some earlier multi-card rows. The directly re-counted A1–A75 totals supersede that running sum.

These figures represent source-candidate inventory only—not semantic adjudication, runtime-ready rules, APK implementation coverage, or CardDB completion.

## Runtime gate and project guardrails

Keep source excerpt, interpretation, confidence, and executable status separate. Until target selection/ties, card IDs, conditions, state timing, ownership, permanence, event order, resource timing, and failure/atomicity tests are established, candidates remain `pending/non_executable`.

- DB29 / `fm1-carddb-29` remains immutable.
- DB30 is not issued.
- CardDB PR #9 and APK PR #28 remain open and unmerged.
- No release, runtime promotion, or APK source change is made by this audit.
