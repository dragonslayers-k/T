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


---

## Correction OPS-RUNTIME-001 — DB29 SQLite source-cost evidence recovered from Actions logs

The earlier cost section is limited to the Library `cards.json` snapshot only. It must **not** be generalized to the authoritative DB29 SQLite. The DB29 release SQLite was downloaded, checksum-verified, decompressed, and queried successfully by T main Actions run `42173417874` on 2026-11-06. The same DB29 source was downloaded and validated again by APK PR #28 Actions #261.

Verified DB29 SQLite facts from T main run `42173417874`:

| Metric | Observed |
|---|---:|
| Cards | 15,350 |
| `card_costs` rows | 15,350 |
| `RequireSoul` source field present | 15,350 |
| `RequireLP` source field present | 289 |
| `RequireLP` absent | 15,061 |
| `card_costs.soul_known=1` | 15,350 |
| Hybrid mapping review | 52 |
| Special semantics review | 779 |
| Soul token rows | 24,166 |
| SQLite integrity | `ok` |
| Effect candidate rows | 17,407 |
| Effect clause rows | 48,281 |
| Image rows / archive-verified images | 30,700 / 30,700 |
| Foreign-key errors | 0 |

DB29 source hashes recorded by the same run:
- Uncompressed SQLite SHA-256: `089fb67494a1a0bf853764fb443e1d015e1d0bc0aefaa528686b000fd953e3bf`
- Compressed SQLite SHA-256: `789539898d9742beb701ee632535ce439fc764ddbe07e3e182d53ed088f458a8`

The 15,061 missing `RequireLP` fields are not automatically missing costs; the source summary reports 289 land cards, matching the 289 present `RequireLP` records. Confirm by card type in the focused inventory before assigning applicability.

Cost interpretation:
- Do not infer costs from the Library `cards.json` snapshot; its `cost` objects are empty.
- Use DB29 SQLite `card_costs`, raw `RequireSoul`, and source `RequireLP` as the primary baseline.
- The 52 hybrid mapping-review and 779 special-semantics-review rows are parsed source tokens with unresolved interpretation details, not absent source costs. They need card-level/source/manual adjudication and a playable runtime interpretation; do not silently convert them to free or block the card.
- For values genuinely absent after the authoritative SQLite/source checks, infer from same-family cards with known source values, then use a tagged conservative payable fallback only where no defensible peer exists.

### Targeted inventory implementation

- Added `scripts/runtime_source_inventory.py` to inspect DB29 SQLite read-only and emit compact per-type source-cost, stat-field, effect, skill, and soul-vector inventories.
- Added a marker-gated step to `.github/workflows/carddb.yml`. A PR run only downloads `fm1_cards.sqlite.gz` and `sqlite-build-summary.json` when its latest commit message contains `[runtime-inventory]`. It verifies the release checksum and uploads only the compact JSON report. It does not download images, rebuild DB29, publish DB30, or run the six-hour full audit.
- This correction is being used to trigger exactly one focused DB29 inventory run. The result is pending until that Actions run completes.
- The 406 MB APK data-pack artifact inspection failure remains a local container-access issue. It does not prevent this new runner-side SQLite inspection path and is not evidence of a corrupt artifact.
