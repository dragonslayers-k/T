# Runtime profile source snapshot inventory — 2026-11-06

## Purpose

This is a focused inventory of the currently available Library snapshot `cards.json` (15,350 records) before implementing the per-card runtime overlay. It is not a replacement for the DB29 SQLite source and does not certify original cost semantics.

## Snapshot population

| Card type | Count |
|---|---:|
| Unit | 8,633 |
| Spell | 3,857 |
| Item | 1,748 |
| Enchant | 823 |
| Land | 289 |
| **Total** | **15,350** |

All 15,350 records contain non-empty `text` and `description` strings in this snapshot.

## Cost-field availability

- Non-empty `cost` objects: **0 / 15,350**.
- `costKnown=false`: **15,061**.
- `costKnown=null/missing`: **289** (the land records).
- Therefore this snapshot contains **no usable per-card cost values**. It must not be treated as a cost reference set, and no cost inference should be trained from its empty cost field.
- Do not convert these missing values into zero/free costs. The runtime overlay must recover source costs from DB29 SQLite/raw RequireLP+RequireSoul or other actual source evidence first; only then may same-family distributions be used to infer unresolved costs. If no source or peer basis exists, use a clearly tagged conservative payable fallback rather than zero.

## Unit combat-stat availability

All 8,633 unit records have numeric `ap`, `dp`, and `hp` fields in this snapshot.

| Stat | Count present | Minimum | Median | Maximum |
|---|---:|---:|---:|---:|
| AP | 8,633 | 0 | 3 | 11 |
| DP | 8,633 | 0 | 0 | 5 |
| HP | 8,633 | 0 | 5 | 12 |

These are available normalized snapshot values, not independent confirmation that every stat matches original card source. Explicit zero is preserved as a value; do not replace it merely because it is zero. The other 6,717 non-unit cards do not have AP/DP/HP fields in this snapshot, which is expected for those types.

## Other fields

- Unit skill and unit-ability fields are present for all 8,633 units.
- Item skill metadata is present for all 1,748 items.
- This snapshot can support card identity/type/faction/race/rarity/affiliation/skill cohort analysis and text/effect-clause extraction.
- It cannot support original LP/soul cost recovery because all `cost` objects are empty.

## DB29 pack retrieval and access limitation

- APK PR #28 Actions #261 succeeded at HEAD `671b73736e4fbbce5f2cd9e2df0ca2dfffb46a75`.
- The run uploaded artifact `FM1-CardData-v1.3.0-IMPORT-DB29` (406,080,839 bytes), artifact ID `13485933239`.
- The artifact was downloaded once through the GitHub connector as `FM1-CardData-v1.3.0-IMPORT-DB29.zip`.
- Subsequent container `ls/unzip` and Python minimal file access returned `ClientError`. Per OPS-002, do not retry the same container calls in this session. Files can identify the ZIP but did not parse its binary contents.
- This is an artifact-inspection blocker, not evidence that the ZIP is corrupt. Do not request the user to upload it again and do not repeatedly download the 406 MB artifact.

## Next implementation gate

1. Recover access to the existing DB29 SQLite or the downloaded pack through an approved alternate path, without repeating the same failing container route.
2. Inspect the actual DB29 schema and source rows for RequireLP, RequireSoul, unit stat fields, land EarnSoul/production, and card effect source clauses.
3. Build a per-card runtime overlay with source/inferred/fallback values stored separately. Use actual same-family peers with known values for inference; never use the empty cost field in this snapshot as a reference.
4. Ensure every card receives a terminal playability profile. Keep source-review status separate from runtime playability; an unresolved effect clause may become deterministic `fallback_noop`, but must not block payment, base action, or turn completion.
5. Add focused fixture tests for each card type and coverage validation for all 15,350 IDs before generating a new data pack.

## Scope and non-claims

- No source DB, DB29 tag, release, card data, or APK code was changed by this inventory.
- No DB30 was created or published.
- This inventory does not claim that the runtime overlay has been implemented or that all cards are currently playable.
