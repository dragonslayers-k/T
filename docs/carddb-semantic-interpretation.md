# FM1 Card DB semantic interpretation model

## Source preservation

- `cards.raw_payload_json`, `card_fields.source_value_json`, `card_texts.source_text`, and each card's source URL remain the authoritative source snapshot.
- Parsed fields and semantic candidates are additive. They must not replace, normalize away, or discard raw source values.
- Effect interpretation records retain the full `rawText`. When a trailing square-bracket quotation is recognized as lore, it is additionally copied to `flavorText`; the rule-only substring is stored as `mechanicText`.

## Effect interpretation

Each `card_effect_clauses` row must have exactly one `card_effect_interpretations` row. Interpretations include:

- `triggers`: event timing such as attack, defense, damage received, turn start/end, discard, or field exit.
- `actors` and `targets`: friendly/enemy/self and affected card zones or entities.
- `conditions`: level, turn, count, parity, range, comparison, and other textual gates.
- `operations`: structured candidates for stat changes, stat assignment formulas, stat division/multiplication, status application, skill modification, movement, destruction, coin changes, terrain transformation, and other text-defined actions.
- `numbers`, `rawText`, `flavorText`, and `mechanicText`: source evidence, not executable game code.

All inferred operations remain `executable=false` until independently verified against reliable game rules or reproducible game behavior. A medium-confidence pattern match is a typed candidate, not official confirmation. A low-confidence clause remains visible in the review queue with its card-specific source URL.

## Skill mapping provenance

- `manual_verified`: directly entered and checked against source documentation or an explicit card definition.
- `community_documented_candidate`: supported by community material, but not upgraded to official/manual verification. These rules are not playable by default.
- `inferred`: mapped from card-local definitions or explicit lexical candidates. `confidence` distinguishes text-evidence extraction from name-only guesses.
- `no_special_skill`: source field explicitly has no special skill.
- `unmapped`: should be zero for a semantic-complete build; any exception must fail the gate.

A definition extracted from a card description records the card ID, card name, card-specific URL, text type, matched label, and verbatim effect text.

## Card field coverage

The 15,350 × 55 coverage matrix is evaluated against each card's immutable raw payload:
- `source_snapshot_verified`: a non-empty value exists in both the raw payload and normalized field row, and the values match.
- `source_absent_confirmed`: the source payload omits the key or explicitly stores null/empty.
- `missing_on_card`: the raw payload contains a key but the normalized table does not. This is a genuine ingestion gap.

Absence in one card must never be inferred from whether another card type uses the field.

## RequireSoul cost review

Token decoding and semantic interpretation are separate. Parsed source tokens remain available even when hybrid-color mapping or special NCS/BONUS meaning is marked for review. A review flag must never be treated as a missing or corrupt source value, and it must not be silently converted to an assumed neutral cost. Review counts and source token evidence remain attached to the card.

## Release gates

A release requires source snapshot integrity, exact category/card/image counts, zero raw-payload mismatches, complete card-field coverage, complete effect-clause interpretation coverage, zero unmapped Skill1/Skill2 rows, complete cost token parsing, SQLite integrity, foreign-key integrity, and search checks. Semantic inference thresholds do not make low-confidence candidates authoritative; those remain explicitly marked in the database and review artifacts.
