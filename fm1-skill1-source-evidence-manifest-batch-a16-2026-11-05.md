# Skill1 source evidence manifest — Batch A16

## Scope
DB29 semantic review artifact from Actions #430, strict `source_field == "Skill1"`. Groups are the next ten after A15 in descending candidate-row frequency and name order. Skill2 excluded. Candidate rows and excerpts are inventory counts only.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 프레시어스 | 7 | 7 | 1 |
| 핫섬머 | 7 | 7 | 2 |
| 핫윈드 | 7 | 7 | 1 |
| 무지개솔생성 | 6 | 6 | 1 |
| 소울테이밍 | 6 | 5 | 2 |
| 켄드포스다운 | 6 | 6 | 1 |
| 코인예측 | 6 | 3 | 2 |
| 강한재생 | 5 | 6 | 2 |
| 기술방어 | 5 | 9 | 3 |
| 블러드어택 | 5 | 4 | 1 |
| **Total** | **60** | **57** | **16** |

## Evidence and unresolved semantics

### 프레시어스 — 7 rows
7 × "AP 1 이상 공격시, 아군 핸드 슬롯1에 특정 아이템 생성.(아군핸드 1이 비어있지 않으면 미발동)".
Sample [니헤르베](https://fmlunatic.com/card/13022726708), ID `13022726708`.
- The exact generated item is not named in this excerpt. Recover the card-specific item mapping.
- Slot 1 is explicit; test occupied slot, empty slot, and whether other empty hand slots are intentionally ignored.

### 핫섬머 — 7 rows / 2 variants
- 5 excerpts contain only "(방어기술)".
- 2: "(방어기술) - 자신 파괴시 적 남은 소울만큼의 유지턴을 지니는 열사상태를 적 핸드유닛 전체에게 부여".
Samples [여름의메그](https://fmlunatic.com/card/9062424115), ID `9062424115`; [여름의오덴](https://fmlunatic.com/card/9062424127), ID `9062424127`.
- Five rows lack mechanic text in the extracted evidence; do not infer their behavior from the skill name.
- For the two detailed rows, define whose remaining soul count is measured, whether zero duration is possible, enemy hand-unit eligibility, and status duration tick.

### 핫윈드 — 7 rows
7 × "(방어기술) : 자신 파괴시, 적 핸드 마법 또는 인첸트 카드 1의 소환 유소울이 2증가한다."
Sample [여름의마왕](https://fmlunatic.com/card/9081224259), ID `9081224259`.
- Define target selection among enemy hand spells/enchantments and whether cost mutation persists after the card leaves hand.
- Confirm this changes colored soul cost only (wording says 유소울) and whether two units are increased independently or one selected card only.

### 무지개솔생성 — 6 rows
6 × "AP 1 이상 공격시, 아군 다음 턴 모든 속성 유소울 1개와 무소울 1개를 다음 턴에 추가생성."
Sample [봉인된자](https://fmlunatic.com/card/12080126381), ID `12080126381`.
- "모든 속성" must map to the canonical seven colored-soul keys, not a guessed subset.
- Define whether production is one-time next-turn bonus or recurring, and exact timing relative to normal soul generation.

### 소울테이밍 — 6 rows / 5 excerpts / 2 variants
- 4: "적 1파괴시, 아군 핸드 유닛 1의 무소울에 따라 해당 핸드 유닛에게 강화 특수능력 영구 부여(기존 능력이 제거되고 강화 능력이 부여됩니다.)"
- 1: "(공격기술): 적 1파괴시, 아군 핸드 유닛 1의 무소울에 따라 해당 핸드 유닛에게 강화능력 영구 부여(기존 능력이 제거되고 강화 능력이 부여됩니다.)"
Sample [소울테이머](https://fmlunatic.com/card/10081925238), ID `10081925238`.
- One candidate row has no excerpt; leave it unresolved.
- Need the neutral-soul-count-to-upgraded-skill lookup table, eligible target selection, and exact replacement scope. Existing skill removal is explicit; don't preserve old skill by default.

### 켄드포스다운 — 6 rows
6 × "공격 후 자신의 AP를 영구히 1 감소시키고, 상대 유닛의 AP를 2 감소 시킨다.(자신의 AP만 영구 감소. 적유닛은 이번턴만 감소입니다.)"
Sample [암염귀](https://fmlunatic.com/card/16072828446), ID `16072828446`.
- Preserve distinct persistence: attacker AP -1 permanent; target AP -2 for this turn only.
- Define whether the self-penalty applies after successful attack only or every attack attempt, and marker/floor interactions.

### 코인예측 — 6 rows / 3 excerpts / 2 variants
- 2: "AP 1 이상 공격시, 자신의 코인이 모두 뒷면일 경우 적 AP=0".
- 1: "기술 : AP 1 이상 공격시, 자신의 코인이 모두 뒷면일 경우 적 AP=0."
Sample [후계자](https://fmlunatic.com/card/13030626735), ID `13030626735`; [블랙잭](https://fmlunatic.com/card/14121027747), ID `14121027747`.
- Three evidence excerpts only for six candidate rows; leave other rows without source text unresolved.
- Define "all coins" scope (shared profile vs AP/DP/HP rolls), behavior with zero coin tosses, and whether AP=0 is set before damage or after.

### 강한재생 — 5 rows / 6 excerpts / 2 variants
- 5: "공격시 자신의 체력코인 수만큼(최대3) HP증가."
- 1 ancillary item text: "기선제압기술부여 장착시 장착 유닛의 유지비를 모두 유소울로 영구 변경한다." This item-grant text is not the Skill1 healing mechanic.
Sample [숲의전사](https://fmlunatic.com/card/11060125736), ID `11060125736`; ancillary [맹약의증표](https://fmlunatic.com/card/12062041361), ID `12062041361`.
- Confirm whether HP gain counts heads or number of HP coins; phrase says "체력코인 수" and caps at 3, so do not substitute coin heads.
- Define max-HP interaction and when the coin count is snapshotted.

### 기술방어 — 5 rows / 9 excerpts / 3 variants
- 4: "자신 방어시, 상대의 특수기술을 일반공격 기술로 변환."
- 4: "보다 먼저 발동하는 기술 목록" (priority-list metadata, not a complete effect sentence).
- 1: same defense conversion with trailing "=" marker.
Sample [북해의지배자](https://fmlunatic.com/card/11112425394), ID `11112425394`; [레비아탄](https://fmlunatic.com/card/12091926426), ID `12091926426`.
- Preserve defense trigger. Define whether only Skill1 is replaced, whether Skill2 remains, and whether conversion is permanent or battle-local.
- Priority-list excerpts must be joined to their actual list before implementing ordering; do not treat the phrase itself as a standalone effect.

### 블러드어택 — 5 rows / 4 excerpts
4 × "AP1 이상 공격시, 아군 핸드 유닛1의 AP+3".
Sample [이블사이더](https://fmlunatic.com/card/10060124898), ID `10060124898`.
- One candidate row has no excerpt; keep it unresolved.
- Define hand target selection, AP modifier duration, and behavior if the hand has no unit. Do not assume the attacker itself receives the bonus.

## Cumulative Skill1 inventory
- A16: 60 candidate rows / 57 non-empty excerpts / 16 exact variants.
- A1–A15: 1,815 rows / 1,824 excerpts / 245 variants.
- A1–A16: **1,875 rows / 1,881 excerpts / 261 variants**.
- Inventory counts are not executable-rule counts. Missing excerpts remain missing; ancillary text is explicitly separated.

## Promotion gate
Recover missing rows and exact lookup tables before implementation. Preserve distinct durations, source field, hand-slot constraints, soul-roll semantics, and defense priority. Add tests for no-target, empty-hand, zero-coin, cap, persistence, and battle-order boundaries.
