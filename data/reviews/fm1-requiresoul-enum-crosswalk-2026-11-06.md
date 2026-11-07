# Firestore enumtable RequireSoul / SoulType crosswalk — 2026-11-06

## 1. Source snapshot

- Dropbox file: `/판마/새 텍스트 문서.txt`
- Dropbox file ID: `id:FpfZw9ICIsQAAAAAAABjcg`
- server_modified: `2026-11-02T13:22:08Z`
- Extracted content length: 1,293,722 characters
- Relevant source object: `liveappsetting/enumtable` export containing `Enum+RequireSoul`, `Enum+SoulType`, and `Enum+UserDeckSoulType`.
- This source is an enum table snapshot, not a complete per-card record dump. Searching it for the 11 NCS+BONUS overlap card IDs returned no records.

## 2. Enum+RequireSoul — 25 entries

The source enum table explicitly maps enum integer values to names and icon paths:

| Enum integer | Name | Icon path | source flag |
|---:|---|---|---:|
| 1 | NONE | `/none.webp` | 0 |
| 11 | DARK | `/dark.webp` | 1 |
| 12 | DARK_EARTH | `/dark_earth.webp` | 1 |
| 13 | DARK_FIRE | `/dark_fire.webp` | 1 |
| 14 | DARK_LIGHT | `/dark_light.webp` | 1 |
| 15 | DARK_WATER | `/dark_water.webp` | 1 |
| 21 | FIRE | `/fire.webp` | 1 |
| 22 | FIRE_FOREST | `/fire_forest.webp` | 1 |
| 23 | FIRE_IRON | `/fire_iron.webp` | 1 |
| 24 | FIRE_WATER | `/fire_water.webp` | 1 |
| 31 | WATER | `/water.webp` | 1 |
| 32 | WATER_EARTH | `/water_earth.webp` | 1 |
| 33 | WATER_FOREST | `/water_forest.webp` | 1 |
| 41 | FOREST | `/forest.webp` | 1 |
| 42 | FOREST_IRON | `/forest_iron.webp` | 1 |
| 43 | FOREST_LIGHT | `/forest_light.webp` | 1 |
| 51 | IRON | `/iron.webp` | 1 |
| 52 | IRON_EARTH | `/iron_earth.webp` | 1 |
| 53 | IRON_LIGHT | `/iron_light.webp` | 1 |
| 61 | EARTH | `/earth.webp` | 1 |
| 62 | EARTH_LIGHT | `/earth_light.webp` | 1 |
| 71 | LIGHT | `/light.webp` | 1 |
| 81 | MU | `/mu.webp` | 1 |
| 82 | NCS | `/ncs.webp` | 1 |
| 83 | BONUS | `/bonus.webp` | 1 |

This establishes source enum identity and icon path only. The fourth integer in the enum array is preserved as a source field; its meaning is not inferred here.

## 3. Enum+SoulType and Enum+UserDeckSoulType are separate maps

### Enum+SoulType

Contains only the seven colored attributes:

- DARK 1 / 암흑
- FIRE 2 / 불
- WATER 3 / 물
- FOREST 4 / 숲
- IRON 5 / 금속
- EARTH 6 / 대지
- LIGHT 7 / 빛

No MU, NCS, BONUS, or hybrid combination is present in this map.

### Enum+UserDeckSoulType

Contains the seven colored types plus:

- DUAL 8 / 듀얼

It does not contain MU, NCS, BONUS, or the 14 RequireSoul hybrid enums.

### Consequence

- `MU(81)`, `NCS(82)`, and `BONUS(83)` are three distinct `Enum+RequireSoul` entries.
- Manual's blank/colorless bead and recurring upkeep rule should be investigated against `MU`, not silently aliased to NCS or BONUS. The name correspondence is strong, but the image pixels were not inspected in this pass.
- The 14 pair-name RequireSoul entries are not the same enum as `UserDeckSoulType.DUAL(8)`. Their visual naming and pair labels do not establish whether their payment semantics are “both colors”, “either color”, or another rule.
- NCS and BONUS are not normal `SoulType` or `UserDeckSoulType` categories. Their card-cost semantics remain unresolved.

## 4. Reconciliation with the 831-card queue

The existing queue counts remain unchanged:

- 14 RequireSoul pair-combination groups: 52 unique cards.
- NCS: 351 card occurrences.
- BONUS: 439 card occurrences.
- NCS+BONUS overlap: 11 cards.
- NCS∪BONUS: 779 unique cards.
- Total: 831 unique pending cards / 842 token occurrences.

The enum table validates the token names, integer identities, and icon paths behind these groups; it does not validate the 831 cards' payment rules.

## 5. Remaining evidence gaps

1. Visual comparison of `/mu.webp`, `/ncs.webp`, `/bonus.webp` and Manual `images/color.jpg`/`images/soulcost.jpg` is not completed. Dropbox currently exposes metadata/preview links and text extraction; raw image bytes were not available through the current fetch path.
2. The enum table does not define the gameplay semantics of NCS/BONUS.
3. The enum table does not define payment semantics for the 14 pair combinations.
4. The enum table does not explain how NCS/BONUS co-occurrence on 11 cards is paid or consumed.
5. No per-card records for the 11 overlap IDs were found in this enumtable text snapshot.

## 6. Decision

- Preserve MU/NCS/BONUS as distinct RequireSoul enum tokens 81/82/83.
- Do not map NCS or BONUS to MU.
- Do not map the 14 pair enums to UserDeckSoulType DUAL.
- Do not implement any payment rule from enum names or icon filenames alone.
- All 831 unique cards remain pending/non-executable until card-level source and gameplay semantics are verified.
- DB29 remains immutable; DB30 is not issued; PRs remain unmerged.
