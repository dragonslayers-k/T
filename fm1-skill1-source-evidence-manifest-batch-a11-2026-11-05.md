# Skill1 source evidence manifest — Batch A11

## Scope
DB29 semantic review artifact from Actions #430; strict `source_field == "Skill1"` filter and exact `source_name` grouping. Candidate rows count report records. Excerpts count non-empty evidence text. Skill2 excluded. No rule is promoted by this inventory.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 강한격노 | 7 | 7 | 1 |
| 계승된힘 | 7 | 7 | 1 |
| 고대의태동 | 7 | 7 | 1 |
| 공격흡수 | 7 | 7 | 1 |
| 과도한마력 | 7 | 7 | 1 |
| 기력보조 | 7 | 7 | 1 |
| 기호파괴 | 7 | 7 | 1 |
| 네임드어택 | 7 | 7 | 1 |
| 드래곤메모리 | 7 | 7 | 1 |
| 드래곤브레스 | 7 | 7 | 1 |
| **Total** | **70** | **70** | **10** |

## Source evidence and review questions

- **강한격노** (7): 방어시, 자신의 HP가 깎인 수치만큼 AP를 상승시킨 후 상대의 유소울 절반(내림)만큼 자신의 HP를 증가시킨다. Sample [굶주린자](https://fmlunatic.com/card/13112727139), ID 13112727139. Define HP loss snapshot, opposing 유소울 count timing, floor division, and HP cap.
- **계승된힘** (7): 자신 파괴시 아군 필드 유닛 전체 킬수 총합 만큼 자신을 제외한 아군 필드 유닛 전체의 공체를 영구 증가(최대5)시킨다. Sample [각성한지테사](https://fmlunatic.com/card/16121528664), ID 16121528664. Clarify whether the total kill count is capped at 5 before applying to both AP and HP, and define no-survivor behavior.
- **고대의태동** (7): AP1 이상 공격시 아군 핸드에 위치한 에피소드 1~3 카드의 레벨 1 감소(지형 제외, 무소울부터, 최소 1레벨). Sample [고양이사역마](https://fmlunatic.com/card/12021526163), ID 12021526163. Preserve exclusions: terrain excluded, neutral-soul cost first, minimum level 1. Define whether "card level" changes cost only or printed level metadata.
- **공격흡수** (7): 공격 전에 상대 유닛의 AP를 1 영구히 감소시키고(최소1) 상대 유닛이 자신 레벨 미만이면 자신의 AP를 영구히 1 증가시킨다. Sample [삼두룡](https://fmlunatic.com/card/13102327095), ID 13102327095. Trigger explicitly precedes attack; test AP floor at 1 and strict defender-level less-than condition.
- **과도한마력** (7): 자신 파괴시 적 핸드 디스펠 타입 마법 전체의 무소울을 2증가. Sample [스컬콘술](https://fmlunatic.com/card/16120828650), ID 16120828650. Define "dispel-type magic" eligibility, hand scope and whether soul cost increase is permanent.
- **기력보조** (7): 자신파괴시 아군 필드 유닛 중 공/체 수치가 5이하인 수치가 있는 유닛1의 공체를 2배로 변경한다. Sample [다키시프터](https://fmlunatic.com/card/16120828643), ID 16120828643. Define target selection, whether each stat is doubled independently only when <=5, and exact threshold inclusion.
- **기호파괴** (7): AP 1 이상 공격시, 상대의 AP/DP에 있는 ▲ 기호를 영구히 제거한다. Sample [섀도우데몬](https://fmlunatic.com/card/13030626722), ID 13030626722. Identify the ▲ marker representation and whether removing it changes displayed or calculated stats.
- **네임드어택** (7): AP 1 이상 공격시, 상대 이름 수 절반(내림)만큼 추가데미지를 준다. Sample [메로웰리](https://fmlunatic.com/card/14070227465), ID 14070227465. Define "opponent name count" (unit names on field/hand/deck?) and floor division.
- **드래곤메모리** (7): 적 1 파괴시, 아군 핸드 슬롯 1에 상대 파괴 후 자신이 보유한 킬 수에 따라 지정된 카드 1을 생성한다. Sample [세그와흐](https://fmlunatic.com/card/14073027521), ID 14073027521. Preserve post-destruction kill-count timing; define exact count-to-card lookup and slot-1 availability.
- **드래곤브레스** (7): 적 1 파괴시, 자신에게 기술봉쇄 / 디토네이트 기술이 부여된 용의숨결을 장착시키고, 파괴한 적의 레벨이 자신 레벨이상이면 장착시키는 기술봉쇄/디토네이트가 부여된 용의숨결 아이템의 AP/HP수치를 영구히 1 증가시킨다. Sample [세그와흐](https://fmlunatic.com/card/14073027514), ID 14073027514. Define item slot replacement, skill grants, level equality boundary and whether AP/HP permanent increments happen on the newly equipped item.

## Cumulative Skill1 inventory
- A11: 70 rows / 70 non-empty excerpts / 10 exact variants.
- A1–A10: 1,465 rows / 1,474 excerpts / 188 variants.
- A1–A11: **1,535 rows / 1,544 excerpts / 198 variants**.
- These are evidence inventory metrics, not executable-rule counts.

## Promotion gate
Reconcile full DB29 source text and exact card IDs/URLs. Define stat marker, target, timing, persistence and lookup-table semantics before adding engine handlers. Add positive, negative, boundary and interaction assertions. Never promote a rule by repetition count alone.
