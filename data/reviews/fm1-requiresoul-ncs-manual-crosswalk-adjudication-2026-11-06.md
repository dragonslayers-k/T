# SUPERSEDED — RequireSoul NCS/MU/BONUS Manual crosswalk (2026-11-06)

**This document's original adjudication was wrong and is withdrawn. Do not use its former NCS(82) → Manual neutral-bead mapping or the associated 351-card promotion.** The correction was made on 2026-11-07 after re-reading the full Dropbox Manual.zip and Firestore enumtable.

## Current decision

- Manual `soulcost.htm` defines a colorless/neutral bead on Unit cards: it is payable at summon using any generated attribute soul, then recurs as unit upkeep from the next preparation phase; unpaid upkeep destroys the corresponding number of deck cards.
- Firestore `RequireSoul` has three separate enum entries: MU(81), NCS(82), BONUS(83).
- MU(81) is the inferred candidate for the Manual neutral bead. It remains `implemented_inferred` pending visual comparison of the MU icon with the Manual image.
- NCS(82) remains `semantic_review`; it is not neutral payment and is not recurring upkeep.
- BONUS(83) remains `semantic_review`.
- Fourteen hybrid RequireSoul pair codes remain `mapping_review`; neither both-color nor either-color payment is assumed.
- The user's N/C/S(82) combat-stat notation (N=Normal attack, C=Critical attack, S=Defense; attack dice 0–8, defense dice 0–2) is unrelated to Firestore RequireSoul NCS(82), Firestore EarnSoul code 82, and literal `NCS소울` text in card effects.

## Evidence and implementation boundary

Source evidence: Dropbox `/판마/Manual.zip`, `soulcost.htm`; Dropbox Firestore enum snapshot `/판마/새 텍스트 문서.txt`, `Enum+RequireSoul`; T PR #9 runtime source audit. The current CardDB and app converters preserve raw token values and block NCS/BONUS/hybrid payment until semantics are independently verified. DB29 is immutable; DB30 has not been issued; neither PR is merged.
