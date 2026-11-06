# Skill1 source evidence manifest — Batch A9

## Scope
DB29 semantic review artifact from Actions #430; strict filter `source_field == "Skill1"`; group by exact `source_name`. Candidate rows count inferred-skill report records. Excerpts count non-empty evidence text, including ancillary text. Skill2 excluded. This is evidence indexing, not rule promotion.

| Skill1 | Candidate rows | Non-empty excerpts | Exact variants |
|---|---:|---:|---:|
| 포인트블랭크 | 14 | 15 | 4 |
| 환상훔치기 | 14 | 14 | 2 |
| 희생공격 | 13 | 12 | 2 |
| 기술파괴 | 12 | 10 | 3 |
| 순화공격 | 12 | 12 | 1 |
| 하급중독공격 | 12 | 14 | 3 |
| 키스멧어택 | 11 | 11 | 2 |
| 환상제거 | 11 | 9 | 4 |
| 카르마어택 | 10 | 17 | 10 |
| 시체먹기 | 9 | 10 | 4 |
| **Total** | **118** | **124** | **35** |

## Exact source evidence and unresolved semantics

### 포인트블랭크 — 14 rows / 4 variants
- 10: AP2 이상 공격시, 공격 이후 자신의 AP만큼 상대의 DP를 감소시키고 반격받지 않는다.
- 2: AP2 이상 공격시, 공격 이후 자신의 AP만큼 상대의 DP를 감소시키고 반격받지 않는다. (DP가 0이하까지 감소될 수 있고, 공격시 상대 DP에 막히면 반격받게 됩니다.)
- 2: AP 2 이상 공격시, 자신의 AP만큼 상대의 DP를 감소시키고 반격받지 않는다.
- 1 ancillary excerpt: 기선제압기술부여 장착시 장착 유닛의 유지비를 모두 유소울로 영구 변경한다.
- Sample: [협곡의주인](https://fmlunatic.com/card/11060125750), ID `11060125750`.
- Resolve apparent contradiction between "no counterattack" and the explanatory exception where the attack is blocked by DP. The ancillary equipment text is not part of this Skill1 effect.

### 환상훔치기 — 14 rows / 2 variants
- 7: AP1 이상 공격시, 적 유닛의 상태1을 제거 후 상태1을 자신에게 아군 전투턴 남은 무소울 만큼의 유지턴으로 부여(일부 상태는 효과가 정상적으로 적용되지 않을 수 있습니다)
- 7: AP1 이상 공격시, 공격당한 유닛의 상태1을 영구히 제거하고 제거한 상태1을 자신에게 아군 전투턴 남은 무소울 만큼의 유지턴으로 부여한다.
- Sample: [스켈톤](https://fmlunatic.com/card/9100724363), ID `9100724363`.
- Clarify source-state duration vs copied-state duration, which state is selected when multiple exist, and the "some states may not work" exception list.

### 희생공격 — 13 rows / 2 variants
- 11: AP1 이상으로 공격시 자신의 HP=1, 감소한만큼 다음 아군의 AP,HP에 더한다.
- 1: spacing variant.
- Sample: [카디널](https://fmlunatic.com/card/10091525211), ID `10091525211`.
- Define whether HP loss is measured from current HP or max HP, next friendly occupied slot selection, and AP/HP gain timing and persistence.

### 기술파괴 — 12 rows / 3 variants
- 7: AP 1 이상 공격시, 상대 특수기술을 일반공격으로 변경후 상대 보유했던 특수기술 수만큼 추가데미지
- 2: AP1 이상 공격시 상대 특수기술을 일반공격기술로 변경후 상대가 보유했던 특수 공격/방어기술 수만큼 추가데미지 (해당 기술은 균형의수호자를 제외한 모든 방어기술보다 먼저 발동합니다).
- 1: same mechanic with explicit exception for 균형의수호자 and a wording variation.
- Sample: [아우에디케](https://fmlunatic.com/card/13012326670), ID `13012326670`.
- Preserve the priority clause: this effect precedes all defense skills except 균형의수호자. Define count snapshot before skill replacement and clarify whether both Skill1 and Skill2 are counted/replaced.

### 순화공격 — 12 rows / 1 variant
- 12: AP1 이상으로 공격시 상대 AP가 5 이상이면 공격 후 상대 AP/DP=0.
- Sample: [순수함의천사](https://fmlunatic.com/card/13022726707), ID `13022726707`.
- Threshold is inclusive (AP>=5) by wording; test exactly 4/5/6 and confirm whether target AP is sampled before or after damage.

### 하급중독공격 — 12 rows / 3 variants
- 12: AP1 이상 공격시, 상대 보유상태 없으면 하급중독 2턴부여, 있으면 공방체 1씩 감소(DP에 막힐시 공방1씩감소)
- 2 ancillary excerpts are item ability/flavour descriptions, not separate attack mechanics.
- Sample: [스파이더솔져](https://fmlunatic.com/card/11092125894), ID `11092125894`.
- Define "has no status" across all status slots, whether the debuff branch reduces AP/DP/HP or AP/DP only when blocked, and how duration refresh works.

### 키스멧어택 — 11 rows / 2 variants
- 7: 상대 파괴시 자신에게 키스멧상태 2턴 추가 부여.
- 4: 적필드 유닛 1파괴시 자신에게 키스멧상태 2턴 추가 부여
- Sample: [잊혀진자](https://fmlunatic.com/card/13070326958), ID `13070326958`.
- Confirm trigger requires this unit to cause destruction, and whether the 2-turn state stacks or refreshes.

### 환상제거 — 11 rows / 4 variants
- 6: AP 1이상으로 공격시, 적 유닛이 상태보유 유닛이면 해당상태를 영구히 제거
- 1: spacing variant of the above.
- 1: 능력 : AP 1이상으로 공격시, 적 유닛이 상태보유 유닛이면 해당 상태를 영구히 제거
- 1: AP 1 이상 공격시, 상대가 보유한 상태를 영구히 제거한다.
- Sample: [방황하는영웅](https://fmlunatic.com/card/13090427043), ID `13090427043`.
- Define whether one state or all states are removed, and how state-owned passive abilities are affected.

### 카르마어택 — 10 rows / 10 variants
- 6: 적 필드 유닛 1 파괴시 기술 보유 유닛에게 카르마 상태 1턴 추가 부여
- 3: 적 필드 유닛 1파괴시 자신에게 카르마 상태 1턴 추가 부여한다.
- Remaining excerpts include item build-up penalty/description text and must not be merged into the Skill1 mechanic.
- Sample: [마왕의지팡이](https://fmlunatic.com/card/13070341465), ID `13070341465`.
- Distinguish Skill1 owner from equipped-item owner and confirm exact trigger attribution. Item penalty text is a separate field/effect.

### 시체먹기 — 9 rows / 4 variants
- 6: 적 1파괴시, 자신 HP +2
- 2: same with terminal punctuation.
- 1: 적 1 파괴시, 자신의 HP를 2 증가시킨다.
- 1 ancillary grant description is not a separate heal effect.
- Sample: [미궁의주인](https://fmlunatic.com/card/11100525923), ID `11100525923`.
- Confirm destruction attribution, HP cap, and whether this triggers on a destroyed enemy unit in any zone or only the opposing field.

## Cumulative Skill1 inventory
- A9: 118 candidate rows / 124 non-empty excerpts / 35 exact variants.
- A1–A8: 1,267 rows / 1,271 excerpts / 137 variants.
- A1–A9: **1,385 rows / 1,395 excerpts / 172 variants**.
- Inventory counts are not executable-rule counts. Ancillary text is counted in excerpts but separately labelled above.

## Promotion gate
Match exact DB29 card IDs, complete source text and URLs. Separate effect text from item descriptions and priority clauses. Add positive, negative, boundary and interaction tests only after trigger attribution, target eligibility, timing, state scope, persistence and ordering are explicit. Do not promote by frequency.
