# Skill1 source evidence manifest — Batch A8

Source: DB29 semantic review artifact from Actions #430. Filter strictly to `source_field == "Skill1"`; group by exact `source_name`. Excerpt counts include all non-empty evidence text, including ancillary text. Skill2 excluded. No executable promotion.

| Skill1 | Candidate rows | Non-empty excerpts | Exact variants |
|---|---:|---:|---:|
| 코인디펜스 | 15 | 15 | 1 |
| 거인제압 | 14 | 14 | 1 |
| 랭크제압 | 14 | 14 | 1 |
| 레이트섬머 | 14 | 14 | 1 |
| 리제너레이션 | 14 | 14 | 1 |
| 서브켄드파워 | 14 | 7 | 1 |
| 성장강화 | 14 | 14 | 1 |
| 소울링어택 | 14 | 14 | 2 |
| 전략선택 | 14 | 14 | 2 |
| 트라이브어택 | 14 | 15 | 6 |
| **Total** | **141** | **135** | **17** |

## Exact evidence and open questions

### 코인디펜스 — 15 rows
15: 방어시, 자신의 코인 앞면 수 만큼 받는 데미지 감소.
Sample: [디스트로이어](https://fmlunatic.com/card/10070724960), ID 10070724960.
Check shared coin-roll timing and minimum damage floor.

### 거인제압 — 14 rows
14: AP 1 이상 공격시, 상대의 방체합이 상대의 레벨 +5 이상이면 AP,DP=0, HP=1로 변경한다.
Sample: [듀크](https://fmlunatic.com/card/14012227231), ID 14012227231.
Define 방체합, equality threshold and pre/post-damage snapshot.

### 랭크제압 — 14 rows
14: AP1 이상 공격시, 상대 유닛이 C랭크 이상이면 적 유닛은 =0 / =0 / =1.
Sample: [흡혈귀백작](https://fmlunatic.com/card/11011225556), ID 11011225556.
Verify the abbreviated AP=0, DP=0, HP=1 assignment and rank ordering.

### 레이트섬머 — 14 rows
14: 적 1 파괴시, 적 필드 다음 위치 유닛 1에게 중급열사상태를 2턴간 부여한다. (상태는 바로 발동하지 않음).
Sample: [해변의트네인](https://fmlunatic.com/card/14082727566), ID 14082727566.
Define next occupied slot and delayed status activation.

### 리제너레이션 — 14 rows
14: 공격시, 자신의 AP가 자신 레벨 수치보다 낮다면 자신의 AP를 자신의 레벨 수치만큼 증가시키고 자신의 HP를 자신의 유지비만큼 증가시킨 후 증가된 수치만큼 추가데미지.
Sample: [데스제너럴](https://fmlunatic.com/card/14031927306), ID 14031927306.
Clarify whether extra damage is AP delta or combined AP/HP change; define ordering and HP cap.

### 서브켄드파워 — 14 rows / 7 excerpts
7: AP1이상 공격시, 아군 핸드 지형 수 만큼 자신의 AP/HP를 증가한 후 공격.
Sample: [키안](https://fmlunatic.com/card/16022428260), ID 16022428260.
Seven candidate rows have no non-empty excerpt. Leave missing rows unresolved. Define hand-terrain eligibility and buff duration.

### 성장강화 — 14 rows
14: 공격시 자신 제외 아군 필드 유닛 1의 DP 2 증가, 돌진공격 기술 추가부여.
Sample: [인형집사마리](https://fmlunatic.com/card/16101928547), ID 16101928547.
Define target selection, no-target behavior, persistence, and authority gate for the added skill.

### 소울링어택 — 14 rows / 2 variants
7: AP 1 이상 공격시, 자신의 유소울 수 절반(올림)만큼 상대 유닛에게 추가 데미지를 주고, 자신의 유지비 수만큼 적 필드 다음 유닛 1에게 HP 데미지.
7: AP 1 이상 공격시, 자신 유소울수 절반(올림)만큼 상대에게 추가 데미지, 자신 유지비수만큼 적 필드 다음유닛 1에게 HP 데미지.
Sample: [디아이비](https://fmlunatic.com/card/13052226851), ID 13052226851.
Check ceiling division, soul snapshot, second target and no-target behavior.

### 전략선택 — 14 rows / 2 variants
7: 공격시 아군 핸드 유닛 1의 기술을 일반공격/일반방어로 변경하고, 적 필드 유닛 전체 방어기술을 일반방어 기술로 변경.
7: 공격기술은 기술방어 기술보다 늦게 발동합니다.
Sample: [만월의당주](https://fmlunatic.com/card/16052528359), ID 16052528359.
Second excerpt is an ordering clause, not a separate effect. Define hand target and Skill1/Skill2 replacement scope.

### 트라이브어택 — 14 rows / 6 variants
6: AP1이상 공격시 아군 필드 자신을 제외한 같은 종족 유닛수만큼 추 가데미지
4: AP1이상 공격시 아군 필드 자신을 제외한 같은 종족 유닛수만큼 추가데미지.
2: AP1이상 공격시 아군 필드 자신을 제외한 같은 종족 유닛수만큼 추가 데미지.
1: spacing variant; 1 ancillary item build-up text, not the attack mechanic.
Sample: [차원의작은신](https://fmlunatic.com/card/10102025322), ID 10102025322.
Check native race matching, count snapshot, and damage order. Do not merge item penalty text into this rule.

## Cumulative Skill1 inventory
A8: 141 rows / 135 non-empty excerpts / 17 variants.
A1–A7: 1,126 rows / 1,136 excerpts / 120 variants.
A1–A8: **1,267 rows / 1,271 excerpts / 137 variants**.
Counts are inventory metrics, not executable-rule counts. Missing source excerpts remain unresolved; no inference-based promotion.
