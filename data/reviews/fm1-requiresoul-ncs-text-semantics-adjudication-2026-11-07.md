# DB29 RequireSoul NCS 텍스트 의미 대조 — 2026-11-07

## 판정

- NCS가 게임 효과 문장에 등장하는 용례는 카드별 원문에서 확인된다.
- NCS는 적어도 일부 효과에서 별도 soul/resource label로 다뤄지며, 일반 유소울·무소울과 문맥상 구분된다.
- 이 증거는 `RequireSoul=82 (NCS)`의 소환/유지비 지불 알고리즘을 정의하지 않는다.
- 따라서 NCS/BONUS/Hybrid RequireSoul의 runtime payment mapping은 `semantic_review_blocked` / non-executable로 유지한다.
- DB29 Release 불변. DB30 생성·발행 및 PR 병합 없음.

## Source basis

1. Immutable DB29 source records and source effect text, mapped by card ID.
2. `DB29_NCS_text_17_asset_crosswalk.csv` — 17 direct-NCS text candidates, original RequireSoul tokens, effect excerpts, and image identity crosswalk.
3. `fm1-requiresoul-image-glyph-adjudication-2026-11-07.md` — visual glyph review of the extracted DB29 image cohort.
4. Official Manual review — no literal NCS/BONUS/Hybrid payment semantics; colorless bead guidance must not be generalized to NCS/BONUS.
5. Community card-effect compilation at Inven (2017) — secondary evidence only, not official rules:
   https://www.inven.co.kr/board/hs/3509/1426815

## 17-card effect-text classification

| DB29 card ID | Card | Direct text evidence | Narrow interpretation |
|---|---|---|---|
| 7090523166 | 네이처보이 | Explicitly says a reduction of ordinary `유소울` does not reduce `NCS소울` or `무소울`; terrain-card soul is also excluded. | Strong local distinction among resource classes. |
| 11110926018 | 카드수집가 | Copies/replaces a hand card with a rarity-selected card marked `NCS소울`. | NCS labels the resulting card's soul classification. |
| 11110926019 | 피닉스대학생 | Converts its own `NCS소울 1` permanently into upkeep. | NCS can be converted into a maintenance-cost unit in this effect. |
| 12112826515 | 버드라이딩캣 | Replaces a hand card with an `NCS 소울` card named 첩보원의귀환. | NCS is used as a card-generation/replacement classification. |
| 13013026686 | 희망의기사 | When converting upkeep to the card's attribute soul, a colorless card is converted to NCS soul. | Specific colorless-to-NCS rule in this card effect only. |
| 13061226897 | 데스레이피어 | Generates an attribute-selected card in hand as `NCS소울`. | NCS is an explicit generated-card soul label. |
| 13103027108 | 루미너스 | Replaces an enemy hand card with a cat-statue card marked `NCS소울`. | NCS labels a transformed card. |
| 14032627336 | 전쟁의여신 | Converts its `무소울 1` to `NCS소울 1` permanently. | Direct evidence that this effect treats MU/무소울 and NCS as distinguishable values. |
| 14102227672 | 할로윈위치 | Replaces an enemy hand card with a card described as `NCS소울` and all-purpose. | NCS soul and all-purpose ability are stated as separate properties. |
| 14102927674 | 햄스터대학생 | Converts upkeep to attribute-specific `유소울`; colorless uses NCS soul. | Another card-local colorless-to-NCS conversion. |
| 14110550816 | 초원 (Enchant) | Changes a hand card's `유소울` to NCS. | Direct soul-class conversion, not a RequireSoul payment rule. |
| 14121027754 | 판타지마스터 | Uses the phrase `유소울(NCS)` in a state description. | A local expression that groups NCS with 유소울 for this effect; not a global equivalence. |
| 15070828030 | 켄드디오드로 | Moves an enemy graveyard item into hand as NCS soul. | NCS labels the resulting card classification. |
| 15082628089 | 항아 | Increases own `유소울`; the colorless case is NCS. | Card-local colorless-to-NCS convention. |
| 15082628090 | 어우동 | Converts upkeep to attribute soul; if colorless, uses NCS. | Card-local colorless-to-NCS conversion. |
| 16050428344 | 크루얼체리엇 | Replaces the enemy's highest-level hand card with a card marked NCS soul and all-purpose. | NCS and all-purpose are independently specified. |
| 16060128394 | 이계의복수자 | Converts the top enemy graveyard card with highest `유소울` into NCS soul and moves it to hand. | NCS is an explicit conversion destination. |

## Evidence tiers

### Verified directly from DB29 card text
- 17 candidate rows contain literal NCS text; 10 contain the exact phrase `NCS소울`.
- The effect text includes card creation/replacement, resource conversion, and explicit exclusion from ordinary `유소울` reduction.
- The original RequireSoul token values remain distinct in the source data.

### Supported only as a secondary-source observation
The Inven community compilation describes NCS soul used as a generated/replaced card classification in multiple effects and uses phrases such as `NCS소울`, `무소울`, and `유소울(NCS포함)`. This corroborates the lexical use in card effects but does not establish the RequireSoul payment algorithm. The source is old, user-maintained, and not a rule authority.

### Not established
- Whether a RequireSoul NCS cost is paid from a dedicated NCS pool, ordinary colored souls, MU/neutral souls, or some combination.
- Whether NCS is exchangeable for ordinary `유소울` at summon or upkeep.
- Whether any payment order/priority applies when a cost contains NCS + MU + BONUS or hybrid tokens.
- Whether BONUS is a resource pool, a bonus modifier, or another payment class in RequireSoul semantics.
- Whether the card-local phrase `유소울(NCS)` is a universal rule.

## Implementation boundary

Do not implement any of the following from this evidence alone:
- NCS -> MU / generic neutral / all-colors fallback;
- NCS -> ordinary colored-soul equivalence;
- BONUS or hybrid auto-payment;
- payment priority based on token order;
- playable/runtime-cost promotion.

Keep original enum namespace, raw token string, parsed token multiplicity, evidence state, and candidate interpretation separate. Next valid evidence gate is a card-local original-client/play record or authoritative source showing actual summon/upkeep payment and resulting pool deltas for NCS, BONUS, and hybrid costs.
