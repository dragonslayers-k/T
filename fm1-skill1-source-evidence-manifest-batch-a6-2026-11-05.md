# Skill1 source evidence manifest — Batch A6

## Scope and counting rule

- Source: DB29 Release semantic review artifact from successful Actions run #430.
- Filter applied strictly: `source_field == "Skill1"`. Skill2 rows are excluded.
- This is source-evidence indexing only. It does not promote any inferred skill to executable status.
- Batch A6 continues the top-count Skill1 list after A1–A5; all names below are Skill1 only.

## Batch A6 coverage

| Skill1 name | Candidate card rows | Mechanic excerpts | Exact wording variants |
|---|---:|---:|---:|
| 결계해제 | 36 | 58 | 6 |
| 뫼비우스 | 35 | 35 | 3 |
| 장비숙련 | 35 | 35 | 3 |
| 코인버스트 | 35 | 35 | 1 |
| 플래툰어택 | 35 | 35 | 3 |
| 실드어택 | 34 | 37 | 6 |
| 야수숙련 | 33 | 33 | 3 |
| 공격이용 | 28 | 28 | 3 |
| 예측공격 | 24 | 24 | 7 |
| 연합방어 | 23 | 23 | 2 |
| **Total** | **318** | **350** | **37** |

## Exact mechanic text variants

### 결계해제 — 36 rows / 58 excerpts / 6 variants

- 21: 상태 : 인첸트카드 발동 페이즈시, 상태 보유 유닛의 슬롯 맨 위 인첸트카드 1을 파괴시킨다.
- 19: 적 1파괴시, 결계해제상태가 없는 적 핸드 유닛 1에게 결계해제상태를 3턴간 부여.
- 14: 기술 : 적 1파괴시, 결계해제상태가 없는 적 핸드 유닛 1에게 결계해제상태를 3턴간 부여.
- 2: 적 1파괴시, 결계해제상태가 없는 적 핸드 유닛 1에게 결계해제상태를 3턴간 부여
- 1: 적 1 파괴시, 결계해제 상태가 없는 적 핸드 유닛 1에게
- 1: 상태를 3턴간 부여한다.

Sample cards: [어보미네이션](https://fmlunatic.com/card/10040724771), [레드이몰리스](https://fmlunatic.com/card/10040724783).
Review issue: one Skill1 label contains two distinct mechanics (grant a 3-turn hand-unit status on enemy destruction; destroy the top enchant on the status-holder's slot during enchant activation). They must not be collapsed into one handler without source/manual clarification.

### 뫼비우스 — 35 rows / 35 excerpts / 3 variants

- 27: AP1 이상 공격시, 자신의 유지비 만큼 적 필드 특수능력 유닛 전체 공방체 각각 감소.
- 7: AP 1 이상 공격시, 적 필드 특수능력 유닛 전체의 AP/DP/HP를 자신의 유지비 만큼 각각 감소시킨다.
- 1: AP1 이상 공격시, 자신의 유지비 만큼 적 필드 특수능력 유닛 전체 공방체 각각 감소

Sample: [페르섀도우](https://fmlunatic.com/card/10072125020).
Review issue: define "특수능력 유닛" eligibility and whether upkeep is snapshotted before any target changes.

### 장비숙련 — 35 rows / 35 excerpts / 3 variants

- 30: AP1 이상 공격시, 공격 당한 유닛이 장비면 +2추가 데미지를 준다.
- 3: AP 1 이상 공격시, 공격 당한 유닛이 장비면 +2추가 데미지를 준다.
- 2: AP 1 이상 공격시, 상대의 능력이 장비능력이면 추가 2 데미지를 준다.

Sample: [포춘텔러](https://fmlunatic.com/card/10010624569).
Review issue: use target's native unit ability, not an item/equipment currently attached to it.

### 코인버스트 — 35 rows / 35 excerpts / 1 variant

- 35: AP1 이상 공격시, 자신의 코인이 전부 앞면이면 상대 유닛 파괴.

Sample: [치카포노펜](https://fmlunatic.com/card/10062324942).
Review issue: confirm which shared coin profile is tested and whether "all heads" with zero coin tosses is false or vacuously true.

### 플래툰어택 — 35 rows / 35 excerpts / 3 variants

- 32: AP 1이상 공격시 자신과 소속이 같은 아군 핸드, 필드 유닛 전체는 AP/HP +1(자신제외)
- 2: AP 1 이상 공격시 자신과 소속이 같은 아군 핸드, 필드 유닛 전체는 AP/HP +1(자신제외).
- 1: AP 1 이상 공격시 자신과 소속이 같은 아군 핸드, 필드 유닛 전체는 AP/HP +1(자신제외)

Sample: [하북의영웅](https://fmlunatic.com/card/11081025841).
Review issue: hand and field recipients differ in what stats can be modified; define timing, self-exclusion, and whether hand bonuses persist while in hand.

### 실드어택 — 34 rows / 37 excerpts / 6 variants

- 32: AP 1이상 공격시, 적 유닛과 자신의 DP수치 차이만큼 추가데미지를 준다.
- 1: 기술부여 [분명히 나뭇잎일 텐데, 살짝만 건드려도 산산이 찢겨야 할 물건이 강력한 공격을 막아내는 방패로 변해있었다. 이것은 무슨 조화란 말인가. 더욱이 잎사귀의 날카로움이 공격력을 더하고 있다.]
- 1: 기술부여 [정의를 수호하는 성스러운 빛의 기사가 착용하는 방패, 겉면에는 항마법의 처리가 되어 있으며 겉은 단단하고 만족은 부드러워 충 격을 쉽게 이겨낼 수 있는 구조로 만들어져 있다.
- 1: AP 1 이상 공격시, 적 유닛과 자신의 DP수치 차이만큼 추가데미지를 준다.
- 1: AP 1이상 공격시, 자신과 상대의 DP수치 차이로 추가데미지를 준다.
- 1: 기술부여 ※ 아이템빌드업(응축부여) [두려움을 버려라. 누구도 그대의 몸을 감히 해할 수 없을 것이다. 믿음을 가지고 느껴라. 고대의 힘이 가진 권능을. 그리하면 승리가 그대와 함께할 것이다.]

Sample: [실드파이터](https://fmlunatic.com/card/10030324736).
Review issue: source rows include descriptive/technology-grant prose as well as mechanic text. Only the explicit DP-difference mechanic is executable evidence; confirm signed difference, floor at zero, and whether attacker DP is evaluated before or after other modifiers.

### 야수숙련 — 33 rows / 33 excerpts / 3 variants

- 30: AP1 이상 공격시, 공격 당한 유닛이 야수면 +2추가 데미지를 준다.
- 2: AP 1 이상 공격시, 공격 당한 유닛이 야수면 +2 추가 데미지를 준다.
- 1: AP 1 이상 공격시, 상대의 능력이 야수능력이면 추가 2 데미지를 준다.

Sample: [떠돌이용병](https://fmlunatic.com/card/10020324656).
Review issue: use target's native ability tag (야수), not merely race or equipped-item state.

### 공격이용 — 28 rows / 28 excerpts / 3 variants

- 22: 공격시 자신의 AP수치 반만큼(올림) 적 AP를 감소시키고, 감소된 수치만큼 자신의 AP에 더한다.
- 5: 공격시 자신의 AP수치 반만큼(올림) 적 AP를 감소시키고, 감소된 수치만큼 추가 공격 데미지.
- 1: 자신의 AP수치 반만큼(올림) 적 AP 감소 후 AP 증가

Sample: [아돌프](https://fmlunatic.com/card/10070725009).
Review issue: two different recipient effects appear (attacker AP increase versus extra attack damage). Keep variant branches distinct until card-by-card mapping resolves them.

### 예측공격 — 24 rows / 24 excerpts / 7 variants

- 11: AP 1이상 공격시, 자신의 AP와 적 AP의 홀짝이 같으면 해당 적 유닛 AP=0
- 5: AP 1 이상 공격시, 자신과 상대의 AP의 홀짝이 동일하면 상대의 AP를 0으로 변경시킨다.
- 4: AP 1 이상 공격시, 자신의 AP와 적 AP의 홀짝이 같으면 해당 적 유닛 AP=0.
- 1: AP 1이상 공격시, 자신의 AP와 적 AP의 홀짝이 같으면 해당 적 유닛 AP=0.
- 1: AP 1이상 공격시, 자신의 AP와 적 AP의 홀짝이 같으면 해당
- 1: AP 1이상 공격시, 자신의 AP와 적 AP의 홀짝이 같으면 적 유닛 AP=0.
- 1: AP 1이상 공격시, 자신과 적 AP 홀짝 같으면 적 AP=0

Sample: [람히르](https://fmlunatic.com/card/10022424701).
Review issue: parity should use rolled AP or base/modified AP? Define whether zeroing occurs before damage and whether AP=0 target remains eligible for later retaliation.

### 연합방어 — 23 rows / 23 excerpts / 2 variants

- 16: AP 1이상으로 공격시, 아군 필드내 자신과 동일한 능력의 유닛수만큼 HP증가. (자신제외)
- 7: AP 1이상으로 공격 시, 아군 필드 내 자신과 동일한 능력의 유닛수만큼 HP가 증가 (자신제외)

Sample: [인큐버스](https://fmlunatic.com/card/10040724774).
Review issue: the source says "same ability" rather than same affiliation/race; count only other friendly field units with the same native ability.

## Batch A6 totals

- 318 Skill1 candidate card rows
- 350 mechanic excerpts
- 37 exact wording variants

These totals are A6 only and must not be added to Skill2 counts. The existing A1–A5 Skill1 total remains 633 rows / 608 excerpts / 46 variants; combined A1–A6 coverage is 951 rows / 958 excerpts / 83 variants.

## Promotion gate

Do not mark any of these inferred rules executable based only on repeated source text. For each rule, obtain exact card ID/source text, determine whether variants are distinct mechanics, specify target eligibility and timing, then add independent engine assertions for positive, negative, boundary, and interaction cases. Manual authority and source-card mapping remain separate requirements.
