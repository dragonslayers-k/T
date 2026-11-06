# Skill1 source evidence manifest — Batch A14

## Scope
DB29 semantic review artifact from Actions #430; strict `source_field == "Skill1"` filter, ordered by candidate-row frequency then skill name. Skill2 excluded. Each group below has 7 candidate rows and 7 non-empty excerpts. These are source-evidence candidates, not executable rules.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 아이템전수 | 7 | 7 | 1 |
| 아티팩트 | 7 | 7 | 1 |
| 야생의해방 | 7 | 7 | 1 |
| 야수압도 | 7 | 7 | 2 |
| 에피소드링크 | 7 | 7 | 1 |
| 영혼의사슬 | 7 | 7 | 1 |
| 오블리비언 | 7 | 7 | 1 |
| 운명개척 | 7 | 7 | 1 |
| 윈터파티 | 7 | 7 | 1 |
| 적성자 | 7 | 7 | 1 |
| **Total** | **70** | **70** | **11** |

## Evidence and implementation questions

### 아이템전수 — 7 rows
7 × "자신 파괴시, 아군 핸드 유닛 카드 1에 정해진 아이템을 장착한다."
Sample [소울컨슈머](https://fmlunatic.com/card/11040625644), ID `11040625644`.
- "정해진 아이템" is unresolved in this excerpt. Recover per-card item mapping from complete card text; define eligible hand target and behavior when it already has an item.
- Do not use a generic item or infer mapping from skill name.

### 아티팩트 — 7 rows
7 × "적 1 파괴시, 유닛별 자신에게 지정된 아이템 장착."
Sample [사로드](https://fmlunatic.com/card/13123127187), ID `13123127187`.
- This is a per-unit mapping family. Need exact card-to-item pairs and item stat/skill payloads.
- Define item slot replacement, whether the item attaches to the destroying unit, and whether no mapping means no effect.

### 야생의해방 — 7 rows
7 × "AP 1 이상 공격시, 적 필드 맨 뒤 유닛 1에게 와일드니스 상태를 무한턴 부여한다."
Sample [헤어리](https://fmlunatic.com/card/14111227711), ID `14111227711`.
- Confirm "맨 뒤" means the final occupied enemy slot or fixed last lane; define no-enemy behavior.
- Verify authoritative 와일드니스 status semantics and whether 무한턴 is represented as permanent/no-expiry.

### 야수압도 — 7 rows / 2 variants
- 6 × "방어시, 상대 유닛이 야수면 받는 데미지 2점 감소."
- 1 × "방어시, 상대의 능력이 야수능력이면 자신이 받는 데미지를 2 감소시킨다."
Samples [물의길드전사](https://fmlunatic.com/card/10102025301), ID `10102025301`; [제아르](https://fmlunatic.com/card/14121727760), ID `14121727760`.
- The wording differs between race/type "야수" and ability "야수능력". Keep the two eligibility interpretations separate until source model proves equivalence.
- Test damage floor and whether reduction is applied before other defense modifiers.

### 에피소드링크 — 7 rows
7 × "자신 파괴시, 아군 핸드 에피소드1~15 카드 1의 레벨을 2 감소시킨다. (카드레벨 최소 1까지 감소하며, 유지비부터 감소)."
Sample [페이탈뮤턴트](https://fmlunatic.com/card/14030527294), ID `14030527294`.
- Preserve episode 1–15 inclusion, hand-only target, level floor 1, and maintenance-cost-first reduction.
- Define target selection and whether a card with maintenance cost 0 can reduce another level component.

### 영혼의사슬 — 7 rows
7 × "자신 파괴시, 아군 소각장 맨 위에 위치한 유닛을 최대 2개의 유닛을 아군 핸드 빈공간으로 이동시킨다."
Sample [악령지배자](https://fmlunatic.com/card/15100728141), ID `15100728141`.
- Wording is grammatically ambiguous: determine whether it moves up to two topmost units or one unit with a maximum-two constraint.
- Define order (top-first), number of available hand spaces, and behavior when the graveyard top card is not a unit.

### 오블리비언 — 7 rows
7 × "AP 1 이상 공격시, 상대에게 중급망각상태 2턴간 부여".
Sample [흑염의기사](https://fmlunatic.com/card/13100827081), ID `13100827081`.
- Retrieve the canonical middle-tier oblivion status definition, its blocked actions/effects, and exact turn-expiry tick.
- Test existing status replacement/refresh and target status capacity.

### 운명개척 — 7 rows
7 × "공격시 자신을 포함한 아군 핸드, 필드 유닛 전체 AP1 증가 후 공격(증가한 후 데미지를 줍니다.)"
Sample [심연의이단자](https://fmlunatic.com/card/15032527877), ID `15032527877`.
- Explicit ordering says the AP increase occurs before damage. Preserve this in combat-order tests.
- Define whether AP increases are permanent or temporary and whether every hand/field unit receives a distinct +1 modifier; ensure the attacker is counted once.

### 윈터파티 — 7 rows
7 × "적 1파괴시, 아군 필드 유닛 전체 레벨1 영구 증가. (속성 유소울 증가)".
Sample [파티의은룡](https://fmlunatic.com/card/10012724615), ID `10012724615`.
- Define how level increase affects attribute soul generation, maintenance cost, and other derived values.
- Test all friendly field units including the destroying unit, level caps, and persistence after battle.

### 적성자 — 7 rows
7 × "공격시, 자신의 장착 아이템이 탈렌티움이면 AP/HP+4, 탈렌티움이 아니면 아이템 이름수 절반(올림)만큼 AP/HP 증가."
Sample [앤즈이니엠](https://fmlunatic.com/card/13062626929), ID `13062626929`.
- Define whether "아이템 이름수" counts distinct item names, equipped item names, or all item-name occurrences.
- Confirm Talantium comparison uses canonical item ID rather than display string; determine buff duration and AP/HP snapshot timing.

## Cumulative Skill1 inventory
- A14: 70 candidate rows / 70 non-empty excerpts / 11 exact variants.
- A1–A13: 1,675 rows / 1,684 excerpts / 224 variants.
- A1–A14: **1,745 rows / 1,754 excerpts / 235 variants**.
- Inventory counts do not imply runtime implementation or verified mechanics.

## Promotion gate
Recover complete card source and mapping data for generic labels such as "정해진 아이템". Separate race-based from ability-based eligibility. Preserve explicit ordering statements. Add positive, negative, boundary, full-zone, and interaction tests before implementation; do not infer missing mappings.
