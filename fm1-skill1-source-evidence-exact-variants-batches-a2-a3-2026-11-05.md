# Skill1 Batch A2–A3 exact source-variant expansion (DB29)

**Verified against:** Actions #430 artifact `fm1-carddb-semantic-review-fm1-carddb-29-430/gap-reports/inferred-skill-report.jsonl`.  
The excerpts below are exact `additional_text` values in that artifact. Counts are source references, not counts of unique engine implementations. All rules remain inferred and non-executable.

## A2 — 환상제어 (68 candidate rows; 67 mechanic excerpts; 6 exact variants)

| Count | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 60 | AP 1이상으로 공격시, 적유닛이 상태보유 유닛이면 AP/DP=0, HP=1 | 10050424833 다크프리스트; 10050424839 헬블레이드; 10050424846 갑판원 |
| 2 | AP 1이상으로 공격시, 적유닛이 상태보유 유닛이면 AP/DP=0, HP=1. | 10100625267 정글안내자; 12012526118 아키하 |
| 2 | AP 1이상으로 공격시, 적 유닛이 상태보유 유닛이면 AP/DP=0 HP=1 | 9021823862 카드워리어; 9021823863 카드매지션 |
| 1 | AP 1 이상으로 공격시, 적이 상태보유 유닛이면 AP/DP=0 HP=1. | 13061926904 드로아 |
| 1 | AP 1 이상 공격시, 상대가 상태를 보유했다면 AP/DP를 0으로, HP를 1로 변경시킨다. | 16051128347 실버락 |
| 1 | AP 1 이상으로 공격시, 적 유닛이 상태보유 유닛이면 AP/DP=0 HP=1. | 9060324085 세이져 |

**Still unresolved:** status marker definition; whether HP is set before/after AP/DP; attack cancellation; target protection; already-dead target; HP=1 replacement vs reduction.

## A2 — 약탈공격 (61 candidate rows; 60 mechanic excerpts; 3 exact variants)

| Count | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 45 | AP 1이상으로 공격시, 자신과 상대의 코인 수 차이만큼 추가데미지. | 10020324682 낭만기사; 10030324707 다크조커; 10070724973 수병 |
| 13 | AP 1 이상 공격시, 자신과 상대의 코인 수 차이만큼 추가데미지를 준다. | 14121727764 키마스터; 15030427855 하피레인져; 15040127889 서커스단장 |
| 2 | AP 1 이상으로 공격시, 자신과 상대의 코인 수 차이만큼 추가데미지. | 13010226612 섀도우울프; 15060327962 리자드정찰대 |

**Still unresolved:** coin field/source, subtraction direction, negative result handling, timing relative to DP, and whether coin values can change during attack.

## A2 — 컨슘 (50 candidate rows; 49 mechanic excerpts; 2 exact variants)

| Count | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 48 | Lv2 이하의 적 파괴시, 상대 유닛 HP 흡수. | 10020324655 루프플랜트; 10021724693 샌드웜; 10030324726 오션웜 |
| 1 | 적 1 파괴시, 파괴시킨 상대의 레벨 수치가 2 이하이면 공격 전 상대 유닛의 HP 만큼 자신의 HP를 증가시킨다. | 15050627918 리자드제너럴 |

**Still unresolved:** which unit receives HP; current/base HP amount; whether this unit must cause destruction; whether the pre-attack variant is distinct; HP cap and simultaneous-destruction handling.

## Separate Skill2 item — 환상폭발 (48 candidate rows; 47 mechanic excerpts; 2 exact variants)

| Count | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 40 | 자신 파괴시, 상대가 상태보유 유닛이면 파괴. | 10110325335 그레이브가드; 10110325342 낙인죄수; 10110325349 블루워리어 |
| 7 | 자신 파괴시, 파괴시킨 상대가 상태를 보유했다면 상대를 파괴한다. | 15021127814 죽음의연주자; 15021127815 볼케닉골렘; 15021127816 산호섬거북이 |

**Still unresolved:** destroyed event definition, target selection, state check timing, prevention/replacement effects, and simultaneous destruction.

## A3 — 음파공격 (46 candidate rows; 45 mechanic excerpts; 4 exact variants)

| Count | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 30 | AP 1이상으로 공격시, 적군 필드 다음 유닛 AP/DP -2. | 10010624554 시비숍; 10030324722 윈드메이커; 10050424848 갑판원 |
| 9 | AP 1 이상 공격시, 적 필드 다음 유닛 1의 AP/DP를 2 감소시킨다. | 15010727792 스트라냐; 15050627925 리틀터틀리아; 15052727948 오케아니스 |
| 5 | AP 1 이상으로 공격시, 적군 필드 다음 유닛 AP/DP -2. | 13010226588 디미온; 14031927315 해룡; 14121027749 타이푼비스트 |
| 1 | 1이상으로 공격시, 적군 필드 다음 유닛 AP/DP -2. | 13092527060 레이디 |

**Still unresolved:** “next” field position, empty slot/end-of-field, AP/DP lower bounds, protection, duration/stacking, and attack failure.

## A3 — 마법숙련 (43 candidate rows; 43 mechanic excerpts; 3 exact variants)

| Count | Exact source excerpt | Sample card IDs / names |
|---:|---|---|
| 36 | AP1 이상 공격시, 공격 당한 유닛이 마법이면 +2추가 데미지를 준다. | 10010624561 울프라이더; 10012024610 포레스매터; 10020324641 데빌하피 |
| 4 | AP 1 이상 공격시, 상대의 능력이 마법능력이면 추가 2 데미지를 준다. | 15010727777 이즈호드; 15010727779 자이언트베어; 15010727781 힐골렘 |
| 3 | AP 1 이상 공격시, 공격 당한 유닛이 마법이면 +2추가 데미지를 준다. | 14052827394 심연의귀족; 14052827397 로얄독; 9020423833 루나틱스켈톤 |

**Still unresolved:** “magic” card/type/ability classification, bonus application relative to DP, and temporary/copied classifications.

**Field-separation correction:** 환상폭발 is recorded under `Skill2` in Actions #430 and is not part of Skill1 Batch A3. Its section above is retained as a separate Skill2 item and must not be counted in Skill1 coverage.\n\n## Source and implementation boundary

- This file is a source-index expansion only; it does not claim that the summarized semantics are fully resolved.
- A1–A4 source candidate groups must remain distinct from the 27 Manual-authority rules.
- Do not mark any candidate `manual_verified`, `source_card_verified`, or playable based on this file alone.
- Require authoritative/version-specific semantic evidence and executable runtime tests before implementation.
- DB29 remains immutable; no DB30, release update, or main merge.
