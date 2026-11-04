# Skill1 source evidence manifest — Batch A13

## Scope
DB29 semantic review artifact from Actions #430. Strict filter: `source_field == "Skill1"`; sorted by candidate-row frequency, then exact skill name. Skill2 excluded. All 10 groups below have 7 candidate rows and 7 non-empty excerpts each. Inventory frequency does not establish executable semantics.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 방어자세 | 7 | 7 | 1 |
| 베리어블어택 | 7 | 7 | 1 |
| 병사모집 | 7 | 7 | 1 |
| 복수의의지 | 7 | 7 | 1 |
| 비전이터 | 7 | 7 | 1 |
| 빛과그림자 | 7 | 7 | 1 |
| 사형선고 | 7 | 7 | 1 |
| 소녀의장난감 | 7 | 7 | 1 |
| 소울스탬프 | 7 | 7 | 1 |
| 소울퓨리 | 7 | 7 | 1 |
| **Total** | **70** | **70** | **10** |

## Exact evidence and engine questions

### 방어자세 — 7 rows
7 × "방어시, 상대의 덱포인트가 60 이상이면 상대에게 스턴상태 2턴부여".
Sample [본골렘](https://fmlunatic.com/card/13091727051), ID `13091727051`.
- Confirm whether the threshold uses printed deck points or current effective deck points; test 59/60/61.
- Define which opposing unit is the target and whether the stun is applied before or after damage resolution.

### 베리어블어택 — 7 rows
7 × "공격시 자신의 공격력을 아군 필드의 자신과 다른 등급 카드 수 만큼 증가시킨 후 공격한다."
Sample [흑영수](https://fmlunatic.com/card/16060128380), ID `16060128380`.
- Clarify whether "different rank" means every friendly field card whose rank differs from the attacker, or distinct rank values.
- Test no other ranks, one different-rank card, multiple cards sharing a rank, and rank changes caused by effects.

### 병사모집 — 7 rows
7 × "AP1 이상 공격시, 아군 핸드 유닛1의 소속을 영구히 자신과 동일하게 변경한다."
Sample [하북의영웅](https://fmlunatic.com/card/11081025840), ID `11081025840`.
- Target selection is unspecified: user choice, deterministic first eligible slot, or random.
- Define whether "same affiliation" snapshots the attacker's affiliation at trigger time and whether the change is persistent outside battle.

### 복수의의지 — 7 rows
7 × "자신 파괴시 아군 필드 맨 뒤에 적장목베기 마법 1을 행동불능으로 소환한다."
Sample [콥스아라크네](https://fmlunatic.com/card/15072928039), ID `15072928039`.
- Define full-field behavior, whether the summon fails or uses another slot, and the duration/meaning of 행동불능.
- Confirm that the generated spell is a field unit/entity in the runtime model rather than a hand/deck card.

### 비전이터 — 7 rows
7 × "AP1 이상 공격 시, 상대 유닛의 상태 보유 수에 따라 효과 발동".
Sample [뱀파이어](https://fmlunatic.com/card/10020324632), ID `10020324632`.
- Evidence text is only a summary, not a complete effect definition. Do not implement from this sentence.
- Retrieve full card text and determine the state-count thresholds, resulting effects, status eligibility, and whether the count is sampled before or after attack-side status changes.

### 빛과그림자 — 7 rows
7 × "적 1 파괴시, 파괴된 유닛의 레벨과 레벨 홀짝에 따라 지정된 효과가 발생한다."
Sample [칠흑묘킷](https://fmlunatic.com/card/13121827163), ID `13121827163`.
- This is a branch-summary only. Need exact level-to-effect lookup table and exact handling for odd/even levels.
- Define whether level is printed/current level at destruction and how unsupported levels behave. Do not invent the missing table.

### 사형선고 — 7 rows
7 × "AP 1 이상 공격시, 상대의 HP를 1로 변경하고 상대 유닛의 기술을 일반공격으로 변경한다."
Sample [노스에구엘](https://fmlunatic.com/card/13112727132), ID `13112727132`.
- Clarify whether HP is set to 1 before or after attack damage; if the target is already at 1 HP, normal attack damage may otherwise destroy it.
- Define "기술" scope: Skill1 only, Skill2 only, both, or all special abilities. Keep this distinct from manual-backed skill replacement rules.

### 소녀의장난감 — 7 rows
7 × "자신 파괴시 아군 필드 다음 유닛에게 능력치가 변경된 탈렌티움(+1 / 0 / +2)을 장착."
Sample [리틀아이리](https://fmlunatic.com/card/15050627909), ID `15050627909`.
- Define next-unit selection, item-slot occupied behavior, and whether the modified item is a distinct generated definition or a mutation of the base Talantium item.
- Confirm AP/DP/HP modifiers and item stacking/replacement behavior.

### 소울스탬프 — 7 rows
7 × "AP 4 이상 공격시 상대 유닛에게 '영혼각인' 상태를 1턴간 부여한다."
Sample [네카인](https://fmlunatic.com/card/16041228299), ID `16041228299`.
- Test AP 3/4/5; establish whether AP is checked before temporary modifiers and before attack damage.
- Retrieve the authoritative 영혼각인 status definition, duration tick order, and whether reapplication refreshes or stacks.

### 소울퓨리 — 7 rows
7 × "AP1 이상 공격시, 적 유닛과의 레벨 차이만큼 공체 증가."
Sample [미궁의악령](https://fmlunatic.com/card/10090125143), ID `10090125143`.
- Clarify whether level difference is attacker minus defender, absolute difference, or a signed value; source wording alone does not resolve it.
- Define whether both AP and HP increase, whether increase is temporary/permanent, and whether values are snapshotted before damage. Test equal, higher, and lower defender levels.

## Cumulative Skill1 inventory
- A13: 70 candidate rows / 70 non-empty excerpts / 10 exact variants.
- A1–A12: 1,605 rows / 1,614 excerpts / 214 variants.
- A1–A13: **1,675 rows / 1,684 excerpts / 224 variants**.
- These are source-evidence inventory counts, not counts of implemented or executable effects.

## Promotion gate
Resolve full card source for summary-only or branch-table mechanics before coding. Record exact target, stat basis, trigger timing, state mutation, persistence, and fallback behavior. Add positive, negative, boundary, and interaction tests. No inference-only promotion.
