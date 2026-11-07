# RequireSoul MU(81) Manual rule adjudication — 2026-11-07

## Scope and result

This report resolves the previous conflation between (a) the source Manual's colorless-bead rule and (b) the visual identification of the RequireSoul MU=81 glyph. These are separate evidence questions.

**Rule result from the official Manual review:** for ordinary MU/colorless-bead cost, the Manual states that the initial summon cost can be paid using any attribute soul; unit Soul Cost/upkeep is recurring from the preparation turn; and when the soul cost cannot be paid, the number of unpaid souls is paid as deck-card destruction. The unpaid upkeep does not directly destroy the unit. This supersedes any PDF secondary proposal claiming immediate unit destruction.

**Mapping result:** the source enum independently identifies RequireSoul code 81 as MU. The semantic crosswalk of MU to the Manual's colorless bead is supported by the matching rule context, but the icon-level visual comparison of the actual /mu.webp and Manual illustration remains a distinct verification item. The PR's prior wording “provisionally crosswalked” should not be read as meaning that the MU rule itself is wholly unknown.

## Runtime boundary

- The verified Manual behavior applies to MU(81)/ordinary colorless-bead costs only.
- It does not establish payment semantics for RequireSoul NCS(82), BONUS(83), or any hybrid token.
- NCS, BONUS and hybrid remain semantic-review blocked and non-executable.
- Do not infer a payment pool, conversion, or payment priority from token ordering, filenames, card text references, or visual similarity alone.
- Keep original raw RequireSoul token strings, namespace, parsed token counts, candidate mapping and evidence state separate.
- Preserve source DB29 as immutable. No DB30, release/tag, PR merge, or runtime-cost promotion is authorized by this report.

## Evidence chain

1. Official Manual review (Library report FM_OFFLINE_secondary_priority_PDF_review_v2.md): soulcost.htm, ready.htm, cardtype.htm, gamerule.htm, and coin.htm were cross-checked. It records the MU/colorless soul rules and deck-card penalty for unpaid soul.
2. Firestore source enum review: RequireSoul and EarnSoul are separate namespaces; RequireSoul 81 is MU, RequireSoul 82 is NCS, RequireSoul 83 is BONUS; EarnSoul 82 is MU02.
3. DB29 NCS evidence review: 351 NCS rows remain semantic_review_blocked, runtimeCostKnown=false, playable=false; direct NCS effect text does not establish RequireSoul payment semantics.
4. The secondary-priority PDF claim matrix classifies the PDF's proposed color/universal soul budget as an unverified hypothesis and its unpaid-unit destruction as contradicted by the official Manual.

## Next narrow evidence gate

The remaining useful work is image identity inspection, not reopening established MU text rules:
- obtain actual source bytes for Manual soulcost.jpg and the source RequireSoul /mu.webp, /ncs.webp, and /bonus.webp glyphs;
- compare exact icon shapes and card image cost areas for the 17 direct-NCS text candidates and 11 NCS+BONUS overlaps;
- use visual evidence only to identify glyph identity; require original-client behavior or authoritative rule text to determine NCS/BONUS/hybrid payment.

## Verification status

This is a documentation-only adjudication based on the named Library reports and source enum/card inventories. It does not claim new pixel inspection, game-client testing, or a new Actions result.
