# DB29 RequireSoul visual audit — Stage 2: full-population rail review index

## Purpose
Stage 1 confirmed the source population and some symbol interpretations. This stage prepares a card-by-card visual inspection atlas rather than pretending that all 779 BONUS/NCS cards have already been counted.

## Population
- Total target cards: 831.
- Hybrid group: 52.
- Non-hybrid BONUS/NCS group: 779.
- Evidence source: workflow run #809, complete large/small image set (831 each).

## Artifacts generated
- `DB29_RequireSoul_831_left_rail_review_atlas.pdf`: 831 card left-rail crops, indexed by card ID and source token codes; arranged in a paginated visual atlas (24 cards/page).
- `DB29_RequireSoul_831_stage2_rail_audit_index.csv`: one row per target card, with source RequireSoul, code/amount list, review group, image path, and explicit pending status.
- These are review aids. They do not certify visual counts.

## Work status
- [x] Produce an all-831-card rail atlas and per-card index.
- [x] Keep the 52 hybrid cards identified separately.
- [ ] Classify the 779 BONUS/NCS cards into card-frame/template families.
- [ ] Derive family-specific marker positions and marker classes.
- [ ] Compare detected marker counts with source token amounts for all 779 cards.
- [ ] Manually inspect only residual mismatches and low-confidence crops.

## Method constraints
1. Do not use one fixed set of image coordinates across all card generations.
2. Do not infer BONUS/NCS/neutral counts from the bottom-right large numeral.
3. Do not promote a token semantic or modify DB29 on the basis of the atlas alone.
4. Record a card as verified only after its marker count has been compared to the original encoded token amount.

## Baseline protection
DB29 tag `fm1-carddb-29`, its source data, and the open PR #9 are not changed, merged, or rebased by this stage.
