# Skill1 source evidence manifest — Batch A15

## Scope
DB29 semantic review artifact from Actions #430; strict `source_field == "Skill1"` filter; candidate groups ranked by row frequency then exact skill name. Skill2 excluded. All groups below have 7 candidate rows and 7 non-empty evidence excerpts. These are evidence candidates, not executable rules.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 전주곡 | 7 | 7 | 1 |
| 진두지휘 | 7 | 7 | 1 |
| 켄드스케일 | 7 | 7 | 1 |
| 코스튬체인지 | 7 | 7 | 1 |
| 코스튬파티 | 7 | 7 | 1 |
| 쿨섬머 | 7 | 7 | 1 |
| 쿨윈드 | 7 | 7 | 1 |
| 크리티컬히트 | 7 | 7 | 1 |
| 파인드코어 | 7 | 7 | 1 |
| 폴리모프아더 | 7 | 7 | 1 |
| **Total** | **70** | **70** | **10** |

## Evidence and engine questions

### 전주곡 — 7 rows
7 × "자신 파괴시, 자신을 파괴시킨 상대 유닛에게 유지비가 없으면 함께 파괴한다."
Sample [듀라한제너럴](https://fmlunatic.com/card/14090327584), ID `14090327584`.
- Trigger is self-destruction and target is the unit that caused it. Define attribution when destruction is caused by a status, spell, or chain effect rather than direct combat.
- "유지비가 없으면" must be checked against current maintenance-cost state at resolution; test zero and nonzero cost. Prevent recursive destruction loops.

### 진두지휘 — 7 rows
7 × "AP 1이상 공격시, 자신을 제외한 아군 핸드와 필드 동일 소속 유닛 수 절반(올림)만큼 자신의 AP/HP를 증가시킨다."
Sample [장준예](https://fmlunatic.com/card/14080627528), ID `14080627528`.
- Count matching-affiliation units in both hand and field, excluding the attacker. Do not count non-unit cards.
- Apply ceiling division. Define whether AP/HP gains are temporary or permanent and whether hand/field changes during combat affect the snapshot.

### 켄드스케일 — 7 rows
7 × "AP1 이상 공격시 아군 적군 맨뒤 지형의 이름수 차이(절대값)만큼 추가 데미지."
Sample [섀도우리벤져](https://fmlunatic.com/card/16072728439), ID `16072728439`.
- Define "맨뒤 지형" as last occupied terrain or last lane and "이름수" as distinct names vs count of terrain cards.
- Absolute difference means no negative damage; test equal counts, attacker greater, and defender greater. Clarify whether both sides must have a terrain.

### 코스튬체인지 — 7 rows
7 × "(고유기술) : 적1 파괴시, 아이템 미장착한 아군 행동가능 다음유닛 1에게 지정아이템을 랜덤 장착 후, 자신의 일러스트를 교체하고 공격기술을 코스튬리턴으로 영구히 변경".
Sample [엘리트아이바](https://fmlunatic.com/card/14012227224), ID `14012227224`.
- Exact random item pool and eligibility are missing from the excerpt. Do not choose an arbitrary item.
- Preserve order: select eligible next ally, equip item, replace own illustration, then permanently change attack skill. Define behavior if no eligible ally exists and whether later steps still occur.

### 코스튬파티 — 7 rows
7 × "적 1파괴시, 아군 필드 유닛 전체 보유 무소울 1이 자신속성 유소울로 영구변경.(NCS 소울 보유 유닛의 경우 유지비가 먼저 변경된 후 NCS 소울이 변경됩니다.)"
Sample [파티의서큐](https://fmlunatic.com/card/10011324594), ID `10011324594`.
- Explicit ordering: for units with NCS soul, maintenance cost is changed before NCS is converted. Preserve this ordering in tests.
- Define whether exactly one neutral soul is converted per unit, what happens if none exists, and whether attribute soul is added to a unit-specific or player-level pool.

### 쿨섬머 — 7 rows
7 × "(공격기술)".
Sample [해변의메그](https://fmlunatic.com/card/9062424116), ID `9062424116`.
- No mechanic text is present. Keep as unresolved; do not invent an effect from the skill name or classify it as a verified executable attack.

### 쿨윈드 — 7 rows
7 × "(공격기술) : AP 1이상 공격시, 아군 핸드 마법 또는 인첸트 카드 1의 소환소울이 1 감소한다(무소울부터 감소 최대 2레벨)."
Sample [해변의마왕](https://fmlunatic.com/card/9081224266), ID `9081224266`.
- Define target selection among eligible hand spells/enchantments, and whether reduction applies to total level or summon soul only.
- Preserve neutral-soul-first reduction and max two-level cap; test cost with/without neutral souls and floor at zero/one.

### 크리티컬히트 — 7 rows
7 × "AP1 이상 공격시, 상대 유닛의 방체합이 자신의 방체합보다 높은 경우 자신의 유지비만큼 상대 유닛의 공체 감소."
Sample [타락천사](https://fmlunatic.com/card/11101225975), ID `11101225975`.
- Define 방체합 as DP+HP or another source-defined measure, and snapshot before/after attack.
- "자신의 유지비만큼" appears to reduce target AP and HP; confirm both stat deltas, marker restrictions, and minimum stat floors.

### 파인드코어 — 7 rows
7 × "적 1 파괴시, 자신을 동일한 이름의 S랭크 유닛으로 교체한다."
Sample [다브노자에](https://fmlunatic.com/card/13010226598), ID `13010226598`.
- Need exact same-name S-rank card ID lookup, card availability, and whether replacement inherits current HP, items, kills, slot, and status.
- Define behavior if no S-rank counterpart exists; do not silently create a generic unit.

### 폴리모프아더 — 7 rows
7 × "자신 파괴시 아군 필드 행동 가능한 다음 위치 유닛1을 지정된 유닛으로 교체."
Sample [어둠의지배자](https://fmlunatic.com/card/11060125714), ID `11060125714`.
- "지정된 유닛" mapping is absent from the excerpt. Recover card-specific replacement target and source ID.
- Define target selection, inheritance of slot/items/status, and whether replacement is suppressed when no next actionable ally exists.

## Cumulative Skill1 inventory
- A15: 70 candidate rows / 70 non-empty excerpts / 10 exact variants.
- A1–A14: 1,745 rows / 1,754 excerpts / 235 variants.
- A1–A15: **1,815 rows / 1,824 excerpts / 245 variants**.
- These are inventory counts only. They do not certify implementation.

## Promotion gate
Do not implement summary-only, random, or mapping-dependent effects without complete card-level source tables. Preserve explicit event attribution, effect ordering, and cost-conversion order. Add boundary, no-target, recursive-trigger, and state-inheritance tests before promotion.
