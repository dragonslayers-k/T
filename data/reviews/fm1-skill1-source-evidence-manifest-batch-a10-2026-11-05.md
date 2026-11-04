# Skill1 source evidence manifest — Batch A10

Source: DB29 semantic review artifact from Actions #430. Strict filter `source_field == "Skill1"`; grouped by exact `source_name`. Candidate rows count report records; excerpts count non-empty evidence text. Skill2 excluded. This is an inventory, not an executable-rule promotion.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 그림자감지 | 8 | 8 | 2 |
| 기호제거 | 8 | 8 | 2 |
| 난세의영웅 | 8 | 8 | 1 |
| 디토네이트 | 8 | 8 | 1 |
| 레거시 | 8 | 8 | 1 |
| 리더쉽어택 | 8 | 8 | 2 |
| 방어지원 | 8 | 8 | 2 |
| 솔감소 | 8 | 7 | 1 |
| 어드바이즈 | 8 | 8 | 2 |
| 탈렌티움소드 | 8 | 8 | 2 |
| **Total** | **80** | **79** | **16** |

## Evidence notes

- **그림자감지** (8): 7 × "공격시, 섀도우 능력 보유 유닛에게 2 추가데미지."; 1 × "공격시, 상대가 섀도우 능력 보유 유닛이면 추가 2 데미지." Sample [로르디스](https://fmlunatic.com/card/13010226565), ID 13010226565. Verify native ability tag and damage timing.
- **기호제거** (8): 7 × "AP 1 이상 공격시, 상대가 보유한 모든 기호를 영구히 제거한 후 공격한다."; 1 punctuation variant. Sample [블레이드댄서](https://fmlunatic.com/card/13091127049), ID 13091127049. Define "기호", target scope and order.
- **난세의영웅** (8): "적 1 파괴시, 적군 필드 덱포인트 40 이상인 유닛 1을 아군 핸드 슬롯 1에 위치한 덱 포인트가 40 미만인 유닛 1로 교체한다. (아군 핸드 슬롯 1에 유닛이 없으면 발동안함)." Sample [위무제조조](https://fmlunatic.com/card/14020527239), ID 14020527239. Verify >=40 and <40 boundaries, slot selection and zone transition.
- **디토네이트** (8): "자신 파괴시, 아군 핸드 슬롯1의 카드는 속성에 맞는 디스펠 카드로 변경." Sample [유령공녀](https://fmlunatic.com/card/13080727011), ID 13080727011. Define attribute-to-card mapping and empty-slot behavior.
- **레거시** (8): "자신 파괴시, 아이템이 아닌 아군적군 핸드카드 1을 파괴된 유닛의 속성에 따라 지정된 아이템으로 교체." Sample [데슬러](https://fmlunatic.com/card/9061724101), ID 9061724101. Define eligible cards, item exclusion, mapping and target choice.
- **리더쉽어택** (8): 5 × "AP1이상 공격시 아군 필드 자신을 제외한 같은 소속 유닛수만큼 추가 데미지"; 3 spacing variants. Sample [블랙사바스](https://fmlunatic.com/card/11010525549), ID 11010525549. Match affiliation, not race.
- **방어지원** (8): 7 × "AP 1이상으로 공격시, 자신을 제외한 아군 필드 유닛 수=DP가 된다."; 1 spacing variant. Sample [지니](https://fmlunatic.com/card/10010624575), ID 10010624575. Wording indicates DP assignment, not addition; test markers and timing.
- **솔감소** (8; only 7 excerpts): "AP1 이상 공격시, 아군 다음턴 생성 무소울1 감소." Sample [임모쿠](https://fmlunatic.com/card/13010226572), ID 13010226572. One row has no text; leave unresolved. Define generation timing and floor at zero.
- **어드바이즈** (8): 6 × "자신 파괴시, 속성/종족/소속에 따라 아군 핸드 빈공간 1에 특정 카드 생성."; 2 include explicit priority: attribute, then race, then affiliation; when race matches, affiliation is not checked. Sample [탈출한암살자](https://fmlunatic.com/card/13041026788), ID 13041026788. Preserve this lookup priority and define no-match behavior.
- **탈렌티움소드** (8): 7 × "적 1 파괴시, 자신에게 탈렌티움(+3/0/+3) 아이템을 장착시킨 후 자신의 공격기술을 영구히 일반공격으로 변경한다."; 1 omits item stats. Sample [아이리](https://fmlunatic.com/card/12121526543), ID 12121526543. Define item slot/stacking and whether the change applies to Skill1 only or all attack skills.

## Cumulative Skill1 inventory
A10: 80 rows / 79 excerpts / 16 variants.
A1–A9: 1,385 rows / 1,395 excerpts / 172 variants.
A1–A10: **1,465 rows / 1,474 excerpts / 188 variants**.
These are inventory metrics, not executable-rule counts. The missing 솔감소 excerpt remains unresolved.

## Promotion gate
Match exact DB29 card ID, full text and URL. Preserve target selection, mapping tables, trigger timing, ownership and state scope. Add positive, negative, boundary and interaction tests before promotion. Never fill missing text by inference.
