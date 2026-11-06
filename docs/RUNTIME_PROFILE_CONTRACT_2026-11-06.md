# Runtime Profile Contract — DB29 to FM-OFFLINE

- Date: 2026-11-06 (KST)
- Scope: T PR #9 and Android FM-OFFLINE PR #28
- Source baseline: DB29 `fm1-carddb-29` (read-only)
- Governing policy: `docs/GAMEPLAY_COMPLETION_POLICY_2026-11-06.md` and Library master v4.9, Appendix 29

## 1. Two independent completion axes

The source/provenance axis records what the original site, DB, Manual, or other evidence verifies. The runtime/playability axis records whether the Android engine can complete a legal card action. A pending source review must never be interpreted as a card-wide usability block.

Preserve the original source fields and review flags. Never overwrite them with inferred values. The Android pack validator must report source-verified coverage and runtime-ready coverage separately.

## 2. Runtime cost contract

Every card must receive a valid, payable runtime cost object. Valid keys are `dark`, `fire`, `water`, `forest`, `metal`, `earth`, `light`, and `neutral`. Negative, non-integer, unsupported, or missing values are invalid.

- `candidateCost` preserves source token distinctions and parsed candidate components.
- `runtimeCost` is the normalized cost passed to the engine.
- `runtimeCostStatus` is `implemented_verified`, `implemented_inferred`, or `fallback_payable`.
- `runtimeCostInference` records why an inferred/fallback value was selected.
- `runtimeUpkeepCost.neutral` records only recurring NCS upkeep for units.

Special soul handling:
- NCS is generic payment from any generated colored or neutral soul; for units only, its amount is recurring neutral upkeep.
- BONUS is normalized to generic `neutral` payment at card use. Its original BONUS identity remains in `candidateCost`; it is a one-time requirement and is excluded from recurring unit upkeep.
- Hybrid tokens require every inferred component color.
- Unknown or unparseable tokens receive a conservative payable neutral fallback; they are not silently treated as free.
- Explicit source no-cost is represented as `{ "neutral": 0 }`, never as a missing or empty object.

## 3. Runtime card-action disposition

- Unit AP/DP/HP use source values when valid. A nonpositive/missing HP uses a tagged minimum-one runtime fallback while source values remain preserved.
- An item whose native target condition cannot be mapped receives `runtimeItemConditionStatus: fallback_any_unit`. Keep a parsed own/enemy owner restriction where available; do not block the item solely because race/affiliation wording is unresolved.
- Standard lands use decoded source production. MagicLand retains its unresolved source effect but installs with zero invented ordinary production and `runtimeLandProductionStatus: fallback_noop`.
- A single exact simple-text spell effect with a supported attack/defend/battle-start trigger may use a tested inferred handler. Unsupported spell clauses use deterministic no-op. Enchants remain fallback_noop until the Android engine has a correct event/duration-bound slot handler; the card still pays its runtime cost, leaves the hand, enters its terminal zone, and marks the action complete.
- Unit Skill1/Skill2 handlers use only source/manual-verified or tested inferred mappings. Unmapped individual clauses use fallback; provenance does not disable the unit.
- Upkeep must always be finite. Missing legacy upkeep metadata must never become positive Infinity or automatically end a match.

## 4. Engine and validator requirements

The resolver must select runtime values before source-review flags. A source-review flag is not a reason to reject a card. Actual invalid player actions remain rejected: insufficient resources, illegal phase, exhausted LP/deploy capacity, invalid ownership, invalid zone transfer, or an invalid target when no fallback target policy exists.

The pack validator must verify:
1. Exactly 15,350 unique card IDs and expected category totals.
2. A valid runtime cost for all 15,350 cards, with no unsupported `bonus` key.
3. A finite runtime upkeep profile for all 8,633 units.
4. Every spell/enchant clause has a terminal effect disposition.
5. All 15,350 cards pass the runtime action-readiness validation; blocked count is zero.
6. Source review counts remain visible and unchanged; they are not rewritten as source-verified.
7. MagicLand has no invented normal production.
8. Source image/card identity hashes and DB29 SQLite integrity remain intact.

## 5. Validation and workflow discipline

Lightweight JavaScript/Python tests run on ordinary PR synchronization. The large DB29-to-Android pack build and emulator smoke are separate expensive gates and must run only when explicitly requested via workflow_dispatch inputs or explicit `[build-card-pack]` and `[run-emulator]` markers. Do not re-run a successful validation on the same SHA.

## 6. Immutable boundaries

- DB29 tag, release, SQLite, and source records remain unchanged.
- DB30 is not published without separate explicit approval.
- T PR #9/#12/#13 and APK PR #28/#26/#25/#9 remain open and unmerged unless the user separately authorizes a merge.
- This contract is a development/validation rule; it does not itself certify the app or a complete original-rule implementation.

## 7. Current implementation work

APK PR #28 now has a DB29 SQLite converter that creates a runtime cost profile, a runtime cost resolver in the rules engine, finite upkeep handling, item target fallback, and deterministic terminal spell/enchant fallbacks. The validator has been changed to distinguish source review from runtime readiness. Final DB29 pack validation and emulator smoke must still be completed on the final combined HEAD before claiming the 15,350-card runtime gate passes.
