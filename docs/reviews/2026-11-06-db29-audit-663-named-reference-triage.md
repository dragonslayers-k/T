# DB29 audit #663 — named card/item reference candidate triage (batch 2)

- Immutable source: `fm1-carddb-29`
- Audit: #663 / run `42173417874`
- Source commit: `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`
- Scope: 108 rows / 48 patterns from the heuristic category `named_card_or_item_reference`.
- The category was heuristic. This pass separates literal-form groups; it does not establish effect meaning.
- All rows remain `pending_source_review` and `non_executable`. No game mechanic is affirmed.

## Group counts

| Conservative literal class | Patterns |
|---|---:|
| literal_named_equipment_or_affiliation_label | 15 |
| mechanic_or_named_reference_mixed_candidate | 11 |
| stat_formula_or_field_definition_candidate | 6 |
| metadata_flavor_or_announcement_candidate | 7 |
| literal_named_unit_or_card_list | 9 |

## What was determined

The first five element/equipment name forms and similar labels can be isolated as literal named labels, but a text label alone does not prove whether it is a requirement, a bonus, a roster descriptor, or a game mechanic. Numbered named unit rows are roster-like text; the exact DB29 card IDs and duplicate-name distinctions still need to be resolved. Formula clauses and mechanics descriptions were separated from simple names. Flavor, announcement, and author-note strings are preserved but not modeled as executable effects.

## Next evidence pass

1. Resolve literal item/equipment labels to exact DB29 card IDs and inspect the corresponding source clauses.
2. Resolve numbered roster/name lists against the DB29 inventory without alias auto-merging.
3. Cross-check formula candidates against FM1 manual and engine tests.
4. Keep every unconfirmed clause pending/non-executable, with original card ID, clause index, raw text, and detail URL.
5. Do not change DB29, publish DB30, or merge PRs.

Detailed per-pattern and card-level rows are preserved in the companion Library JSON triage artifact.