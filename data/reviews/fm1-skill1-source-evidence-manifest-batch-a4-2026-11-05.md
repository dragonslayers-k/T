# Skill1 source evidence index — Batch A4 (DB29)

**Artifact verified:** CardDB Actions #430, artifact `fm1-carddb-semantic-review-fm1-carddb-29-430`, file `gap-reports/inferred-skill-report.jsonl`.  
**Scope:** 기술감지 (`Skill1`, source enum 79, inferred rule `inferred_skill1_79`).  
**Candidate group:** 42 card rows. All remain inferred; this index does not approve authority promotion or runtime implementation.

## Exact source-text variants

| Rows | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 36 | AP 1이상으로 공격시, 적 유닛이 일반공격 유닛이 아닐 경우 +1추가 데미지. | 10010624567 포춘텔러; 10022424697 시서펜트; 10022424705 이카리오스 |
| 2 | AP 1이상으로 공격시, 적 유닛이 일반공격 유닛이 아닐 경우 +1 추가 데미지. | 12070426306 헤네르나; 9020423827 실프 |
| 4 | AP 1 이상 공격시, 상대가 특수기술을 가지고 있다면 추가 1 데미지를 준다. | 14102227663 라이트유니콘; 15030427861 플레티넘엔젤; 15050627926 발탄랜서; 16100528542 유사하의요괴 |

The artifact also includes 3 non-mechanic card-text entries in the 42-row group:
- 10030341131 드래곤헬름 — 技術부여 flavor text
- 10040741141 투명한유리잔 — 능력부여 flavor text
- 11050441259 외눈안경 — 技術부여 flavor text

These are not effect definitions and must not be counted as a fourth mechanic variant. Exact card-local source URLs are `https://fmlunatic.com/card/{card_id}`.

## Interpretation boundary

The two “일반공격 유닛이 아닐 경우” phrasings differ only by spacing in the captured excerpts and can be treated as a text-format variant for review, but not as proof of engine semantics.

The four-row “상대가 특수기술을 가지고 있다면” wording is materially different:
- Does “특수기술” mean a non-normal-attack Skill1, any Skill1/Skill2, or any granted/attached ability?
- Is it equivalent to “일반공격 유닛이 아님”? The artifact does not establish equivalence.
- Are equipment-granted abilities included?
- Does the +1 modify AP before DP, or apply as a separate damage event?
- Does the AP 1 threshold apply identically to both wordings?

Do not merge the four-row wording with the 38-row non-normal-attack wording until the rule definition is established.

## Manual cross-check status

The captured Manual.zip `specialability.htm` section contains 27 named special-ability entries and does not list 기술감지. Its general rule that additional attack damage is added to AP can guide later test design, but it does not define “일반공격 유닛이 아님” or “특수기술 보유”.

Therefore:
- Authority remains inferred/card-source evidence only.
- Runtime remains disabled / not approved.
- No DB29 modification, DB30, or main merge.

## Required next verification

1. Resolve the target classification from version-specific authoritative rules or card engine evidence.
2. Compare the 4 “특수기술 보유” cards with the 38 “일반공격 유닛 아님” cards and their actual Skill1/Skill2/equipment fields.
3. Confirm whether equipment-granted abilities count.
4. Define positive, negative, and boundary cases for AP 0/1 and both target classes.
5. Only then author executable engine assertions tied to exact card IDs, exact excerpts, and source URLs.
