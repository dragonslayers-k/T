# DB29 semantic reference-list card-ID crosswalk — 2026-11-05

## Source and policy

- Baseline: immutable `fm1-carddb-29`.
- Source evidence: Actions #573 artifact `fm1-carddb-semantic-review-fm1-carddb-29-573`, file `gap-reports/card-field-card-summary.jsonl`.
- The source file contains the 15,350 DB29 card IDs, exact names and source card types.
- This crosswalk resolves exact name-to-ID references only. It does not verify random selection, target eligibility, equip/summon success/failure, or runtime behavior.
- Exact name match required. No suffix stripping, fuzzy match, or inferred alias promotion.

## Pattern `b8ddb2d0e1f2521e` — Costume-change item pool

The TextExtra list on the seven Elite Aiba-family cards contains seven exact item names. All seven resolve uniquely to DB29 item cards.

| Exact source name | DB29 card ID | Type | Match |
|---|---:|---|---|
| 블러드본랜스 | 3121240377 | 아이템 | exact |
| 루비소드 | 3121240378 | 아이템 | exact |
| 레드아이스링 | 3090840343 | 아이템 | exact |
| 네추럴링 | 3121240380 | 아이템 | exact |
| 생명의물약 | 3121240381 | 아이템 | exact |
| 번개의모래 | 3090840346 | 아이템 | exact |
| 그리핀석상 | 3041840292 | 아이템 | exact |

**Result:** 7/7 exact card IDs resolved. The runtime candidate must still preserve the source condition: an eligible next friendly unit with no item equipped receives one randomly selected item from this named pool. Do not infer uniform probability, replacement behavior, or fallback when no eligible unit exists.

## Pattern `5fe169892b95ee55` — Nature's Wrath summon pool

The source list contains seven exact names. Six resolve uniquely; one does not.

| Exact source name | DB29 card ID | Type | Match |
|---|---:|---|---|
| 롯트 | 4072121236 | 유닛 | exact |
| 장생수 | 11090725879 | 유닛 | exact |
| 맨이터롯트N | — | — | unresolved exact name |
| 이모탈트리 | 4021320945 | 유닛 | exact |
| 손드트리 | 2071120140 | 유닛 | exact |
| 뮤턴트엔트 | 10050424857 | 유닛 | exact |
| 에인션트엔트 | 3041120439 | 유닛 | exact |

A DB29 card named `맨이터롯트` exists at ID `8111923692`, type 유닛, but the source reference explicitly includes the suffix `N`. This is a candidate only, **not an exact match**. Keep the pool at 6/7 resolved until a version/variant source proves that `맨이터롯트N` maps to `맨이터롯트` or supplies a separate ID.

## Remaining semantic gates

- Pattern 1: item-name → card-ID lookup complete; random pool selection and eligible target behavior remain pending.
- Pattern 2: 6/7 summon-pool names resolved; exact `맨이터롯트N` identity pending.
- Both patterns remain `non_executable` until source-backed target, selection, failure and ordering tests pass.
- DB29 remains immutable; no DB30, main merge, or PR merge.
