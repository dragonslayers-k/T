# DB29 low-confidence effect triage — source-context expansion pass 2

**Sources:** Actions #430 `effect-gap-report.jsonl` and existing adjudication `fm1-carddb-29-effect-review-disposition-454.json` (source audit run 41835460152).  
This addendum supersedes any “recover adjacent text” note for the three cards below: their full DB29 TextBase/TextExtra context was already preserved in the #454 adjudication. All remain non-executable pending engine verification.

## 1. 라이트닝버그 — card 8111923702

- **Disposition:** `effect_condition_continuation_candidate`
- **TextBase:** empty
- **TextExtra (preserved):**

```text
중급중독공격

AP1이상으로 공격시, 상대 유닛이 장비/야수면 3턴간
중급 중독 부여.(중급중독상태 : HP-3)


만능능력

3차 강화 카드는 만능능력 유닛입니다.
따라서, 아이템 착용에 있어서 제한이 전혀 없는 특징을 갖고 있는 유닛입니다.
또한 3차 강화 카드는 자기 레벨 미만의 아이템을 장착할 때 소울을 지불하지 않습니다.
```

**Resolved source structure:** AP 1+ attack; target unit category 장비 or 야수; apply 중급 중독 for 3 turns; status definition is HP-3. The remaining 만능능력 paragraphs are separate equipment/upgrade metadata, not part of the poison effect.

**Pending engine tests:** AP 0 vs 1; eligible/ineligible target categories; duration decrement timing; whether HP-3 is immediate or periodic; interaction with status immunity/reapplication.

## 2. 녹음의습격 — card 13071033261

- **Disposition:** `conditional_name_diversity_branch_reference`
- **TextBase (preserved):**

```text
아군 핸드필드 플랜트 종족유닛의 이름종류수보다 레벨이 낮은 적 필드유닛 중 공방체합이 가장 높은 유닛 1 "가시풀" 장착하고 종족을 플랜트로 영구변경하여 아군 필드 맨뒤에 행동가능으로 이동시킨다.
※ 발동시 이름종류수에 따라 특 별 효과가 발동한다(특이사항)
```

- **TextExtra (preserved):**

```text
★ 가시풀 : ●●, 일반공격 +3 / 0 / +2 -5%
▶ 아군 필드 유닛 1이상 필요
※ 발동시 핸드 / 필드 플랜트 종족 유닛의 이름 수 종류가 5이상이면
장착 아이템인 가시풀의 일반공격 부여를 제거하고
6이상이면 추가로 가시풀의 AP/HP 증가 수치를 1 증가시킨다.
```

**Resolved source structure:** main effect selects an enemy field unit whose level is lower than the count of distinct-name Plant units in friendly hand+field; among eligible targets, choose highest combined AP/DP/HP; equip 가시풀, permanently change race to Plant, then move it to the rear of friendly field as actionable. Additional branches: distinct-name count >=5 removes the granted normal-attack ability from 가시풀; >=6 additionally increases its AP/HP modifiers by 1.

**Pending engine tests:** name uniqueness across hand+field; same-name multiple cards; eligible target level boundary; tie-breaking for highest AP+DP+HP; empty friendly field; 5/6 name-count thresholds; order of equipment, race change, and movement; whether “공방체합” includes modified or base stats.

## 3. 추억 — card 11050432579

- **Disposition:** `conditional_unit_profile_reference`
- **TextBase (preserved):**

```text
아군 필드 유닛이 모두 마법학교 소속 유닛이면, 조건부 이서리얼1을 아군 필드 다음 위치에 소환.
※ 발동시 아군 핸드/필드/소각장에 "메를린"이 존재하면 이서리얼 1에게 그로잉 상태 무한턴 부여 후 아군 소각장의 "메를린" 1을 아군 필드 맨뒤로 이동.
```

- **TextExtra (preserved):**

```text
▶ 아군 필드 마법학교 유닛 1 이상 필요
▶ 조건에 따른 이서리얼의 능력.
기술 : 기선제압.
유소울 : 아군 필드 마법학교 유닛 수.
무소울 : 아군 핸드 마법학교 유닛 수+2.
AP : 아군 필드 마법학교 유닛 수 + 아군 백필드 지형 절반(내림).
DP : 아군 핸드 마법학교 유닛 수.
HP : 아군 필드 마법학교 유닛 수 + 아군 백필드 지형 절반(내림).
공격코인 : 아군 필드 마법학교 유닛 수 / +C1~3.
방어코인 : 없음.
체력코인 : 아군 필드 마법학교 유닛 수 / +C1~3.
일러스트 : 아군 핸드 필드에 메를린이 없는 경우 이서리얼 일러스트로, 메를린이 있는 경우 이서리얼샷 일러스트로 변경.

해당 유닛은 소환시 그로잉 상태가 부여되지 않습니다.
```

**Resolved source structure:** summon requires at least one friendly field Magic School unit and all friendly field units must belong to that affiliation. The conditional Ecaemael profile derives skill, soul costs, AP/DP/HP, attack/HP coins, and illustration from counts of friendly field/hand Magic School units and half the number of friendly backfield terrains (rounded down). Merlin presence in hand/field/graveyard triggers a separate growing-state and movement branch. The summon itself does not grant Growing by default.

**Pending engine tests:** exact affiliation membership; field/hand count scope; terrain half-rounding; coin generation range; Merlin location check; ordering of Growing and Merlin movement; next-position vs rear placement; summon failure when any friendly field unit is outside Magic School.

## Disposition

The three source fragments are no longer “context missing”; they have card-local definitions in #454. Their semantic formulas and game-state interactions still require independent engine verification. Keep the original source text unchanged, keep inferred interpretations separate, and do not enable runtime behavior based on this addendum alone.
