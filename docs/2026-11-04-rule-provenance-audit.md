# Rule provenance and execution audit — 2026-11-04

## Purpose

Re-run the complete database audit against the immutable `fm1-carddb-29` source release before connecting any card effect to executable game logic.

## Required interpretation

- Original card records, card detail URLs, source text, taxonomy, and image references remain source data; do not overwrite them with inferred interpretations.
- Pixel-derived soul-cost readings remain candidates until manually checked against the original card image. Unknown cost must not be treated as zero or free.
- Manually verified skill catalogue entries may be represented as authoritative rule records only with their source/version and card mapping retained.
- Community-documented rules remain candidate evidence; they are not playable/executable by default.
- Effect-pattern inventories and parsed clauses are analysis artifacts, not proof that a game effect is fully understood or safe to execute.
- Unverified or partially parsed effects should preserve the original text and stay non-executable.

## Audit acceptance checks

The full workflow should verify, against the immutable release:

1. 15,350 source card records, expected category counts, unique IDs, exact source card URLs, and field/taxonomy quality.
2. 30,700 original image assets and archive integrity, linked to card IDs without missing references.
3. SQLite integrity, foreign-key integrity, normalized table counts, and search behavior.
4. Soul-cost provenance and confidence/status counts; no candidate is silently promoted to verified cost.
5. Manual and community rule catalogues, card mappings, mapping status, and community `playable_by_default=0` invariant.
6. Effect candidate spans/clauses and status inventory; do not equate extraction with implementation.

## Result policy

A successful audit certifies the source snapshot, normalized DB, and stated integrity checks only. It does not certify complete battle simulation or all card effects as executable. Publish a new immutable release only if every audit passes and the release contents are explicitly reviewed.
