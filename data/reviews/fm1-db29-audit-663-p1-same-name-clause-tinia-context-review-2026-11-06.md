# DB29 audit #663 — same-name hand prerequisite: TINIA contextual source review

- Review date: 2026-11-06
- Baseline: immutable DB29 / audit #663 / source SHA `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`
- Review branch: `feat/carddb-effect-semantic-pass`
- Candidate: `11011925566` / 티니아 / unit / repeated clause in audit #663
- Snapshot crosswalk: `U05566S` (crosswalk based on archived asset-code suffix; not an independently validated live-page identity)
- Evidence source: fan-maintained card reference article, not an official game manual or live game capture:
  - https://www.namu.moe/w/티니아
  - https://readonly.wiki/w/티니아
  - archived raw article mirror: https://seore.org/raw/문서:티니아

## Surrounding card-specific text captured

The card article identifies this specific Chapter 4 TINIA version as possessing Shadow Aura and states:

- Cost: 3 attribute souls; an additional 1 attribute soul is required on repeated use.
- Effect: one allied hand unit with the same name as TINIA has AP/HP reduced by 3, then the Shadow Aura holder's AP/HP is increased by 3.
- No effect if no same-name allied hand unit exists, or if that affected hand unit's AP or HP becomes 0 or less after activation.

The article explicitly qualifies the ability as Chapter 4 TINIA only. This matters because the name TINIA has earlier printings/versions and should not be treated as a universal card-name rule.

## Narrow interpretation supported for this card only

For this TINIA entry, the parenthetical condition is tied to the same-name allied hand unit selected by the effect: the no-effect condition concerns the AP/HP state of that affected hand unit after the activation-related change. The surrounding description identifies the transfer as `-3 AP/HP` on the hand unit followed by `+3 AP/HP` on the Shadow Aura holder.

This source resolves some ambiguity in the raw clause for TINIA; it does **not** establish that the five audit examples have identical surrounding effect bodies, identical costs, or identical sequencing. No behavior should be generalized from the shared parenthetical alone.

## Still open for this candidate

- Whether the source article's "after activation" means after cost payment, after applying the -3 to the hand unit, or another engine-defined timing boundary.
- Exact treatment of AP/HP values and edge cases if either stat is already below the threshold.
- The card-specific text is secondary-source evidence; obtain manual/client evidence or corroborating source capture before final rule adjudication.
- No executable handler or engine test is authorized by this review note.

## Disposition

- Source context: partially recovered for TINIA from a secondary card-reference article.
- Clause semantics: partially clarified for TINIA only; exact timing still pending.
- Other four cards in the audit cluster: remain independently pending.
- DB29: unchanged.
- DB30: not published.
- Queue status: retain `pending_source_review` / `non_executable`; do not increment executable/completed counts.

## Verification boundary

The referenced articles were discoverable through web search during this review. The official FMLunatic detail page and official game manual were not independently captured in this pass. This document is a source-review note, not an authoritative official ruling.
