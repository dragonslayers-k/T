# Skill1 source evidence manifest — Batch A7

## Scope
DB29 semantic review artifact from Actions #430. Strictly filtered to `source_field == "Skill1"`, grouped by exact `source_name`. Candidate rows count inferred-skill records. Excerpt counts include all non-empty evidence `effectText` entries, including descriptive item text where present. Exact variants retain punctuation and spacing. Skill2 excluded. This inventory does not promote any rule.

## Coverage

| Skill1 | Candidate rows | Non-empty excerpts | Exact variants |
|---|---:|---:|---:|
| 밴딩어택 | 22 | 22 | 1 |
| 탈피공격 | 22 | 22 | 12 |
| 방어강탈 | 18 | 17 | 3 |
| 소울이용 | 18 | 19 | 5 |
| 솔버스트 | 17 | 17 | 2 |
| 물구나무 | 16 | 16 | 2 |
| 연환공격 | 16 | 16 | 3 |
| 포인트배리어 | 16 | 16 | 2 |
| 랜덤어택 | 15 | 15 | 3 |
| 치료능력 | 15 | 17 | 4 |
| **Total** | **175** | **178** | **37** |

## Exact text and unresolved semantics

### 밴딩어택 — 22 rows / 1 variant
- 22: AP 1이상 공격시 자신과 종족이 같은 아군 핸드, 필드 유닛 전체는 AP/HP +1(자신제외)
- Sample: [스컬윙서전트](https://fmlunatic.com/card/11101225968), ID `11101225968`.
- Verify native race, hand-unit stat persistence, stacking, and self-exclusion.

### 탈피공격 — 22 rows / 12 variants
Frequent variants:
- 5: AP 1이상 공격시, DP+1만큼 HP 증가. DP=0 (DP가 0일 경우 발동하지 않습니다.)
- 3: AP 1이상 공격시, 자신의 DP=0이 되고, 감소된 DP수치+1만큼 HP가 증가한다.(DP가 0일 경우 발동하지 않습니다.)
- 2: AP 1이상 공격시, DP+1만큼 HP 증가, DP=0 (DP가 0일 경우 발동하지 않습니다).
- 2: AP 1 이상 공격시, 자신의 DP=0이 되고, 감소된 DP수치+1만큼 HP가 증가한다.
- 2: AP 1 이상 공격시, 자신의 DP를 0으로 감소시키고 감소된 DP수치 +1만큼 자신의 HP를 증가시킨다.
- Sample: [포레스트웜](https://fmlunatic.com/card/10021724691), ID `10021724691`.
- The dominant phrases are not semantically identical on their face. Keep "DP+1" and "set DP to zero, add lost DP+1 to HP" as separate candidates until reconciled. Check stat markers and HP caps.

### 방어강탈 — 18 rows / 3 variants
- 8: AP1 이상 공격시, 상대 유닛이 방어기술이 있는 경우 영구히 제거하고 자신에게 해당 방어기술을 영구히 추가한다.
- 8: AP 1 이상 공격시, 상대에게 방어기술이 있는 경우, 상대의 방어기술을 영구히 제거하고 자신에게 제거한 방어기술을 영구히 추가부여한다.
- 1: punctuation/spacing variant.
- Sample: [미궁의주인](https://fmlunatic.com/card/11100525925), ID `11100525925`.
- Define eligible defense skills, multiple skills, transfer/copy behavior, and Skill1/Skill2 boundaries.

### 소울이용 — 18 rows / 5 variants
- 7: AP 1 이상 공격시, 자신의 무소울 수 만큼 추가데미지를 준 후 상대가 파괴되면 자신의 무소울 1을 자신 속성의 유소울 1로 교체한다.
- 7: AP 1 이상 공격시, 자신의 무소울 수 만큼 AP에 더해서 공격한 후 상대가 파괴되면 자신의 무소울 1을 자신과 동일한 속성의 유소울로 영구히 교체한다.
- 3: AP1 이상 공격시, 자신 무소울 수 만큼 AP에 더해서 공격 후 적 유닛이 파괴되면 무소울 하나를 자신 속성의 유소울로 영구교체.
- 1: punctuation variant; 1 additional item description.
- Sample: [펄](https://fmlunatic.com/card/10062341162), ID `10062341162`.
- AP bonus and post-combat bonus-damage branches differ. Keep separate; define soul pool, timing, and conversion condition.

### 솔버스트 — 17 rows / 2 variants
- 16: 준비턴에 남은 무소울만큼 자신의 AP에 더하여 공격한다.
- 1: 공격시, 아군 준비턴에 남은 무소울만큼 AP를 증가시키고 아군 남은 무소울 전체를 소각한다.
- Sample: [스쿨핸디맨](https://fmlunatic.com/card/10080425093), ID `10080425093`.
- Resolve snapshot timing and whether the remaining neutral souls are consumed.

### 물구나무 — 16 rows / 2 variants
- 15: AP1 이상으로 공격시 자신의 AP와 HP를 바꾼다.
- 1: AP 1 이상 공격시, 자신의 AP와 HP를 바꾼다
- Sample: [라티노반솔져](https://fmlunatic.com/card/16030228272), ID `16030228272`.
- Define swap timing relative to attack damage, HP loss, caps, and stat markers.

### 연환공격 — 16 rows / 3 variants
- 10: AP 1이상으로 공격시, 아군 필드 다음 유닛 AP +1.
- 5: AP 1 이상 공격시, 아군 필드 다음 유닛 AP를 1 증가시킨다.
- 1: punctuation variant.
- Sample: [가르젠티탄](https://fmlunatic.com/card/12110726454), ID `12110726454`.
- Define next occupied slot vs next position, no-target behavior, and duration.

### 포인트배리어 — 16 rows / 2 variants
- 15: AP0 이하 공격시 상대 유닛의 특수기술을 일반공격기술로 영구히 변경하고, AP/HP 영구히 3감소.
- 1: AP 0 이하 공격시, 상대의 특수기술을 일반공격기술로 영구히 변경시키고, 상대의 AP/HP도 영구히 3감소시킨다.
- Sample: [빅볼조커](https://fmlunatic.com/card/12051626266), ID `12051626266`.
- AP<=0 is an explicit trigger exception to the common AP>=1 gate. Verify Skill1/Skill2 replacement scope and stat-marker interaction.

### 랜덤어택 — 15 rows / 3 variants
- 7: 공격시 자신의 능력을 장비/마법/야수 중 하나로 랜덤하게 변경하고, 공격 당한 적 유닛이 변경된 능력과 동일한능력이면 적 유닛에게 스턴상태를 2턴간 부여.
- 7: spacing variant.
- 1: same mechanic with added stun description (AP -2 / DP -1 / HP -2 and 혼란공격기술 부여).
- Sample: [암흑도우미](https://fmlunatic.com/card/15031127863), ID `15031127863`.
- Define deterministic RNG/replay seed, change timing, native vs modified ability comparison, and whether the added stun rider is card-specific.

### 치료능력 — 15 rows / 4 variants
- 14: AP1 이상으로 공격시 다른 아군 전체의 능력치가 원래대로 회복.
- 3 additional excerpts are ability/item flavour text, not independent healing mechanics.
- Sample: [기억장치](https://fmlunatic.com/card/14061841552), ID `14061841552`.
- Define original-stat snapshot, hand inclusion, and whether reset affects numeric modifiers only or status/stat markers too.

## Cumulative totals
- A7: 175 rows / 178 non-empty excerpts / 37 exact variants.
- A1–A6: 951 rows / 958 excerpts / 83 variants.
- A1–A7: **1,126 rows / 1,136 excerpts / 120 variants**.
- These are evidence-inventory counts, not executable-rule counts.

## Promotion gate
Reconcile exact DB29 card source text and URL for each candidate. Keep different semantic branches separate. Add positive, negative, boundary, and interaction tests only after trigger timing, target eligibility, state mutation, persistence, and ordering are explicit. Do not promote from frequency alone.
