# DB29 audit #663 — E663-0013 seven-card turn-gate candidate review

- Review date: 2026-11-06
- Audit artifact: `fm1-db29-low-confidence-effect-cluster-triage-663.json`
- Audit run: `42173417874`
- Source commit: `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`
- Review branch: `feat/carddb-effect-semantic-pass`

## Candidate cluster

- Cluster: `E663-0013`
- Occurrences: 7
- Exact text: `6턴 이상 or 0턴 - 효과 없음.`
- Heuristic category: `condition_or_formula_candidate`
- Existing status: `pending_source_review` / `non_executable`

## Complete card cohort

| Detail ID | Card | Archived assetCode crosswalk | Detail URL |
|---|---|---|---|
| 9111124473 | 파블로 | U04473S | https://fmlunatic.com/card/9111124473 |
| 9111124476 | 탐정부장 | U04476S | https://fmlunatic.com/card/9111124476 |
| 9111224470 | 엔비 | U04470S | https://fmlunatic.com/card/9111224470 |
| 9111224474 | 노르니르 | U04474S | https://fmlunatic.com/card/9111224474 |
| 9111324472 | 하이웨이 | U04472S | https://fmlunatic.com/card/9111324472 |
| 9111424475 | 이마딘소드 | U04475S | https://fmlunatic.com/card/9111424475 |
| 9111524471 | 비슐로퀸 | U04471S | https://fmlunatic.com/card/9111524471 |

The crosswalk was made by exact card-name matching between the audit queue and the archived `cards.json` snapshot, then checked against the asset-code suffix. All seven archived records have `detailStatus=ok`. Their archived `text` and `description` fields contain unit stats and metadata (Chapter2, Secret rarity, faction/race/skill); they do **not** contain the effect clause or its surrounding effect body. Therefore this is identity/metadata corroboration only, not semantic evidence.

## Structural observations

- All seven are archived as Chapter2 Secret units, but have distinct factions, races, abilities and skills.
- The exact same temporal clause appears at clause index 10 in each audit row.
- The wording contains two alternatives joined by `or`: `6턴 이상` and `0턴`, followed by `효과 없음`.
- It is not safe to decide from this fragment whether these are turn-number conditions, a duration window, a cooldown, a card-specific exception, or a condition on some referenced state. The scope of `효과 없음` is also not established without the preceding clauses.

## Source acquisition result

Attempted to open all seven FMLunatic detail URLs during this review. The web reader returned an access/internal error for each URL. Searches did not surface an attributable complete card effect text for this cohort. No original client image or official manual excerpt was recovered in this pass.

This is an access limitation; it is not evidence that the pages/cards are absent. Do not substitute a generic Fantasy Masters rules article for these card-specific details.

## Required evidence and decision questions

For each of the seven cards, acquire a complete detail-page HTML/screenshot or original card image with source URL and capture time. Preserve exact line breaks and punctuation. Then determine:
1. What event/phase/turn counter is referred to by `6턴 이상`?
2. Does `0턴` mean the first turn, a duration value, or a separate state?
3. Does `or` express mutually alternative no-effect gates, and what is their subject?
4. Which preceding effect clauses are suppressed by `효과 없음`?
5. Are the seven surrounding effect bodies identical, or does this clause occur in otherwise different effects?

Do not implement a turn gate, infer inclusive/exclusive boundary behavior, or write engine assertions until the card-specific context is sourced.

## Disposition

- Cohort inventory: 7/7 reconciled to archived card identity/metadata.
- Full effect body: not recovered.
- Clause semantics: unresolved.
- Executable handler/test: none authorized.
- All seven remain `pending_source_review` / `non_executable`.
- No audit completion count increment.
- DB29 and Release/tag `fm1-carddb-29`: unchanged.
- DB30: not published.
- PR #9: remains open; no merge.
