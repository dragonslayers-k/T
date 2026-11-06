# Skill1 A21–A22 source-to-APK gap audit — 2026-11-06

## 기준과 범위

- CardDB branch: `feat/carddb-effect-semantic-pass`
- CardDB inspected HEAD: `b663bdc64fe5b760875cfd1dd4bb36b932c996bb` (Actions #630 success)
- APK branch: `feat/combat-event-foundation`
- APK inspected HEAD: `4033c1ab84c054c070ad187106a577600585503a` (Actions #238 success)
- Immutable baseline: `fm1-carddb-29`; DB29 is not modified, DB30 is not issued.
- PR #9 and PR #28 remain open and unmerged.

This is a source-to-runtime gap inventory only. It does not authorize inferred effects, handler activation, or semantic promotion.

## A21 source evidence status

A21 contains 10 Skill1 groups, 20 candidate rows, 19 exact text excerpts, and 13 expression variants. The only explicitly incomplete group is **돌연변이확산**: 2 candidate rows but 1 excerpt.

The known excerpt is associated with 크로우어세신 (`11092125892`) and describes a field-removal trigger that applies a two-turn mutation status to the next friendly unit. The source card page could not be retrieved during this review. The available Manual Skill1 DB29 exact-label artifact does not contain this card ID because that artifact covers the separate 27-rule Manual catalogue, not this custom Skill1 candidate inventory.

**Disposition:** keep the second candidate row unidentified and its source text missing. Do not copy the known excerpt onto the second row, infer its card ID, or promote the effect. The status duration/tick/stacking semantics and “next friendly unit” slot rule remain unresolved.

## A22 source evidence status

A22 contains 10 groups, 20 candidate rows, 24 excerpts, and 13 expression variants. All listed candidates have excerpts in the manifest.

| Skill1 | Main unresolved semantic dependency |
|---|---|
| 리플렉션실드 | defensive trigger timing; stat persistence; regeneration conversion |
| 마그마플레어 | DP-block condition timing; DP/HP marker interaction |
| 마법화살 | enemy-wide DP floor exception; ally recovery and field reorder |
| 매직체인지 | MagicLand identification/removal; next-turn neutral soul |
| 맹약이행 | summon card identity; hand capacity; permanent upkeep modification |
| 메탈콜링 | hero counter vs. Skill1 trigger separation; metal-soul activation |
| 명철한이성 | hero counter initialization, threshold, consumption and soul payload |
| 모랄라이징 | self-AP reduction vs. permanent ally AP increase ordering |
| 무적의철갑 | kill-count item lookup; next eligible ally selection |
| 미러이미지 | clone identity/data; soul snapshot; duplicate-card and disabled-state rules |

## APK cross-check

At APK HEAD `4033c1a`, the exact Korean labels for all 10 A22 groups occur **zero** times in both `app/src/main/assets/game/rules.js` and `tests/rules.test.cjs`.

This string check is not proof that no equivalent low-level primitive exists. It does establish that no direct named Skill1 handler or named regression fixture is currently evidenced by those files. The current APK foundation provides generic combat events, validated zone transfer, and data-only status records; the status record implementation explicitly leaves ticking, stacking, action locks, and status effects unresolved.

**Disposition:** A22 remains source-evidence-only and non-executable. No A22 rule is promoted, and no handler is added based on name matching alone.

## Safe next implementation sequence

1. Recover the missing A21 source row from the immutable DB29 source archive or an independently accessible original card page. Until then, retain an explicit missing-evidence record.
2. Build a card-specific trigger/operation matrix for A21–A22, preserving exact source excerpts and card IDs.
3. Map only verified operations onto existing primitives (event boundary, field transfer, status record, stat markers, hand/graveyard/soul state); distinguish primitive availability from rule completion.
4. Add independent positive, negative, boundary, and interaction tests per source-backed card before any execution gate is opened.
5. Keep custom Skill1 effects separate from the 27-rule Manual Skill1 catalogue and the eight source-gated Skill2 rules.

## Non-actions

- No DB29 data was edited.
- No DB30 was created or published.
- No PR was merged.
- No inferred Skill1 handler was activated.
- No status duration or stacking policy was guessed.
