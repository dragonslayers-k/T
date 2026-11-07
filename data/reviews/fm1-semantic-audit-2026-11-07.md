# CardDB source namespace audit — 2026-11-07

This audit separates same-looking labels that belong to different source namespaces.

| Namespace | Source | Meaning / status |
|---|---|---|
| User N/C/S(82) shorthand | User-confirmed notation | N Normal attack, C Critical attack, S Defense; attack dice 0–8, defense dice 0–2. Exact Firestore field mapping remains unproven. |
| RequireSoul NCS(82) | Firestore Enum+RequireSoul | Separate cost token; semantic_review; no upkeep. |
| RankType N/C/B/A/S | Firestore Enum+RankType | Rank metadata; not N/C/S combat stat shorthand. |
| Coin C | Manual coin.htm | Coin toss notation. One shared toss set is applied to AP/DP/HP. |
| StatType CONST/UP/DOWN | Firestore Enum+StatType + Manual cardability.htm | Raw codes 11/12/13 map to ★/▲/▼ restrictions; code 1 is NONE. |
| StatType FRONT/BACK/HAND/TURN/PLUS/MINUS/EQUAL | Firestore Enum+StatType | Source values preserved; no Manual runtime semantics found. |
| 치명공격기술 | Manual special ability catalogue | A named special skill; not equated to the N/C/S Critical category without evidence. |

The source app converter previously omitted ATKStatType/DEFStatType/HPStatType from the card pack. The current app PR now preserves those fields as sourceStatTech and maps only Manual-defined markers. Original raw source fields are retained.


## Enumtable raw-code convention correction

Firestore enumtable outer map keys are indexes; raw card fields use the first integer in each enum row. StatType raw codes: 1 NONE, 11 CONST, 12 UP, 13 DOWN, 21 FRONT, 22 BACK, 23 HAND, 24 TURN, 31 PLUS, 32 MINUS, 33 EQUAL. CoinType raw codes: 1 NONE, 2 PLUS, 3 MINUS, 4 X, 5 EQUAL. The app parser and tests were updated to use these raw values, not outer indexes.


### EarnSoul / RequireSoul code-82 namespace split

The Firestore enumtable defines `EarnSoul` raw code 82 as `MU02` (two neutral souls produced per token), while `RequireSoul` raw code 82 is the separate `NCS` token. The user-confirmed `NCS(82)` notation is a third, unrelated unit-stat shorthand (N/C/S with attack dice 0–8 and defense dice 0–2). A fourth literal, `NCS소울`, appears in some `TextExtra` effects and remains a separate source-text resource question. These meanings must never be joined by the shared number/string alone. The app's `parse_earn_soul_list` already decodes `EarnSoul` 8201 as two neutral output; converter self-tests cover it separately from `RequireSoul` 8201 review handling.


## 2026-11-07 — Runtime cost fail-closed correction

The earlier app/overlay code used a tagged generic neutral payment fallback for RequireSoul NCS(82), BONUS(83), hybrid pairs, and unknown/missing costs. Although those tokens were labelled unverified, the overlay marked cards playable and the app accepted the generic payment. This contradicted the source review status. The runtime overlay and app converter now block these cards until the payment semantics are supported by authoritative evidence. The source token and candidate interpretation remain preserved; no fallback payment is emitted.

Hybrid RequireSoul tokens are now stored as one candidate token with component names, not added to the normalized color totals as if both component colors were independently required. This prevents the SQLite representation from silently encoding a false both-colors cost.


## Runtime overlay revalidation request

The fail-closed RequireSoul correction is ready for a DB29-only runtime inventory pass. Reuse the immutable `fm1-carddb-29` SQLite Release as input; do not rebuild or publish a database Release. The audit must report the exact counts of source-decoded payable costs, inferred MU(81) costs, and intentionally blocked NCS/BONUS/hybrid/unknown costs, and preserve each blocked card's source token. This validation is diagnostic only and does not authorize DB29 mutation.


## 2026-11-07 — Firestore code 82 namespace proof

Firestore source card 16112710291 (구름도시) stores RequireSoul="71018101", EarnSoulList="8201", and MuSoul=2. RequireSoul uses Enum+RequireSoul: code 71 LIGHT ×1 and code 81 MU ×1. EarnSoulList uses Enum+EarnSoul: code 82 is MU02, one token produces two neutral/MU souls, and MuSoul=2 cross-checks the output. TextExtra independently says the land installation consumes 1 MU soul and 1 colored soul.

This is source-backed evidence that EarnSoul code 82 (MU02 production) is not RequireSoul code 82 (NCS cost token). They remain separate namespaces and neither is the user-defined N/C/S(82) stat shorthand.
