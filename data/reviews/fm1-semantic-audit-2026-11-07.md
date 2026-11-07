# CardDB source namespace audit — 2026-11-07

This audit separates same-looking labels that belong to different source namespaces.

| Namespace | Source | Meaning / status |
|---|---|---|
| User N/C/S(82) shorthand | User-confirmed notation | N Normal attack, C Critical attack, S Defense; attack dice 0–8, defense dice 0–2. Exact Firestore field mapping remains unproven. |
| RequireSoul NCS(82) | Firestore Enum+RequireSoul | Separate cost token; semantic_review; no upkeep. |
| RankType N/C/B/A/S | Firestore Enum+RankType | Rank metadata; not N/C/S combat stat shorthand. |
| Coin C | Manual coin.htm | Coin toss notation. One shared toss set is applied to AP/DP/HP. |
| StatType CONST/UP/DOWN | Firestore Enum+StatType + Manual cardability.htm | Codes 1/2/3 map to ★/▲/▼ restrictions. |
| StatType FRONT/BACK/HAND/TURN/PLUS/MINUS/EQUAL | Firestore Enum+StatType | Source values preserved; no Manual runtime semantics found. |
| 치명공격기술 | Manual special ability catalogue | A named special skill; not equated to the N/C/S Critical category without evidence. |

The source app converter previously omitted ATKStatType/DEFStatType/HPStatType from the card pack. The current app PR now preserves those fields as sourceStatTech and maps only Manual-defined markers. Original raw source fields are retained.
