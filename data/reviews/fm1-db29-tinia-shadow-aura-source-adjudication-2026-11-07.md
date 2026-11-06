# DB29 source adjudication — Tinia / Shadow Aura (card 11011925566)

Date: 2026-11-07  
Immutable source baseline: DB29 / `fm1-carddb-29`  
Review branch: `feat/carddb-effect-semantic-pass`  
Disposition: source text corroborated; effect remains pending implementation and boundary adjudication. No DB29 mutation, no DB30, no executable mapping promotion.

## Card identity and archived sources

- Card: 티니아 (`11011925566`), Chapter 4 exclusive Shadow Aura according to the historical card page.
- DB29 source URL: https://fmlunatic.com/card/11011925566
- Secondary archived reference: https://readonly.wiki/w/티니아
- Alternate mirror: https://seore.org/raw/티니아
- The archived references reproduce the same Shadow Aura text, including activation cost and the parenthetical no-effect condition. These are community/archive references, not a currently accessible official game manual. Preserve that evidence grade.

## Captured effect clause

The references state:

- Activation cost: 3 colored souls; each consecutive use requires +1 colored soul.
- Effect: one allied unit in hand with the same name as the source receives AP/HP −3; then the Shadow Aura holder receives AP/HP +3.
- No effect if there is no same-name unit in hand, or if the referenced unit's AP or HP would be 0 or less after activation.

Source citations:
- Read-only wiki card entry (card details and effect): https://readonly.wiki/w/티니아
- Seore raw archive (card page): https://seore.org/raw/티니아
- Search result from the archived page included the exact text for the Chapter 4 Tinia special ability. Treat it as a source capture to be revalidated against the local source snapshot before implementing.

## Semantic questions not closed

1. “same name” matching: display-name equality is the likely reading, but need determine whether it means localized name, a specific card identity, or a same-name family.
2. “that unit” in the AP/HP threshold: whether the condition checks the hand unit being reduced, the Shadow Aura holder receiving the increase, or both is not explicit enough to safely implement.
3. AP/HP threshold and ordering: validate pre-cost, after cost, after applying −3, or after both changes? The exact “발동 후” timing needs a boundary.
4. Does an invalid threshold cancel both changes atomically? The phrase “아무 효과 없음” suggests no effect, but engine must not partially apply the transfer.
5. Consecutive-use surcharge: determine whether the colored soul is the same attribute as initial cost and when the counter resets.
6. HP reduction and maximum HP: need clarify current HP versus max HP and how damage/heal semantics interact.
7. This ability is an activated Shadow Aura, not Skill1. It must not be implemented through the Skill1 attack dispatcher.

## Proposed test contract after source questions are resolved

- Exact card-ID/name eligibility: Tinia source with matching ally in hand, no matching ally, and a different-name ally.
- AP and HP after-activation boundary at 1, 0, and negative result; assert atomic no-op versus transfer.
- Colored-soul payment for first activation and consecutive-use surcharge, including insufficient soul.
- Source holder and hand target remain distinct entities; verify only intended stats change.
- Repeated activation counter reset at the documented timing.
- Test all relevant stat markers (AP/HP increase/decrease blockers) separately.
- Action always reaches terminal state; failed/invalid activation must not spend soul or partially mutate either unit.

## Cross-reference to broader same-name clause review

The DB29 audit #663 candidate batch contains the same parenthetical clause for five distinct units (Tinia, Natural Master, Arch Wizard, Resberk, Gold Dragon). This Tinia page supplies additional card-specific context and confirms that its “same-name” condition belongs to Shadow Aura activation, but it does not prove that the other four cards share identical complete effects or activation timing. Keep those IDs individually pending until their full source pages are reconciled.

## Outcome

This pass advances one exact card's source evidence and separates the activated ability from the already tested Beast Tamer Skill1. It does **not** authorize a runtime rule yet. Next: inspect the archived source snapshot fields and the Android ability-action UX, then implement only once atomicity, threshold subject, and consecutive-use reset are settled.