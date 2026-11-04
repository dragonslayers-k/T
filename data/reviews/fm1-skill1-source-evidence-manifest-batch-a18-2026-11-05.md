# Skill1 source evidence manifest — Batch A18

## Scope
DB29 semantic review artifact from Actions #430; strict `source_field == "Skill1"` filter. Next ten groups after A17 in frequency/name order. Skill2 excluded. Ancillary item text is counted in excerpts but not treated as the Skill1 effect.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 기술무력화 | 3 | 4 | 2 |
| 눈덩이제작 | 3 | 3 | 3 |
| 더블소울 | 3 | 4 | 3 |
| 데스브레스 | 3 | 3 | 2 |
| 디바이드어택 | 3 | 4 | 2 |
| 버닝퓨리 | 3 | 4 | 2 |
| 블레스 | 3 | 4 | 3 |
| 빙결공격 | 3 | 4 | 4 |
| 선물하기 | 3 | 3 | 3 |
| 솔카운터 | 3 | 3 | 1 |
| **Total** | **30** | **36** | **25** |

## Evidence and review notes

### 기술무력화 — 3 rows / 4 excerpts
- 3: "AP1 이상 공격시, 상대 유닛이 특수능력을 보유하고 있다면 일반공격으로 변경 후 AP/DP=0".
- 1 ancillary item text: third-stage enhancement penalty applies heat/death status for 3 turns; not this Skill1.
Sample [시체수집가](https://fmlunatic.com/card/10060124890), ID `10060124890`.
- Define "특수능력" scope (Skill1, Skill2, unit ability, or all); do not assume all channels are interchangeable.
- Confirm AP/DP set-to-zero timing relative to damage and whether permanent or battle-only. Exclude the unrelated item penalty.

### 눈덩이제작 — 3 rows / 3 variants
- 1: "자신 파괴시, 아군 필드 빈공간에 아군 핸드 빈공간만큼 마법눈덩이 카드를 소환한다."
- 1: "AP 1 이상 공격시, 아군 핸드 슬롯 1에 마법눈덩이 생성. (핸드 슬롯1이 빈공간 아니면 마법눈덩이 생성안함)"
- 1: "(공격기술)" only.
Samples [눈사람병사](https://fmlunatic.com/card/12040426237), ID `12040426237`; [프로즌레이디](https://fmlunatic.com/card/12121826564), ID `12121826564`.
- These are distinct trigger variants: self-destruction field summons vs AP-gated hand-slot creation. Do not merge them into one rule.
- Need exact 마법눈덩이 card ID, quantity cap, field/hand empty-slot semantics, and clarify whether the third candidate has any effect text at all.

### 더블소울 — 3 rows / 4 excerpts / 3 variants
- 2: "AP1 이상 공격시, 아군 다음턴 생성 소울 +2".
- 1: "AP1 이상 공격시, 아군 다음턴 생성 소울 +2 (자신의 속성에 맞는 기존 솔생성과 같이)".
- 1 ancillary item build-up penalty/flavour text, not the Skill1 mechanic.
Samples [황실예언가](https://fmlunatic.com/card/11112425418), ID `11112425418`; [광폭의전사](https://fmlunatic.com/card/10060124925), ID `10060124925`.
- Define whether +2 is neutral soul or colored soul matching the attacker; the second wording explicitly says it coexists with normal attribute production.
- Confirm one-time next-turn generation and whether it stacks across multiple activations. Exclude item penalty.

### 데스브레스 — 3 rows / 2 variants
- 2: "적1 파괴시, 아군 소각장에 파괴된 적 유닛의 레벨 만큼 죽음의대지를 생성."
- 1: "적1 파괴시, 아군 소각장에 파괴된 유닛의 레벨 만큼 죽음의대지 생성."
Samples [아너치세르](https://fmlunatic.com/card/10121525483), ID `10121525483`; [오도어](https://fmlunatic.com/card/10080125027), ID `10080125027`.
- Define generated card ID and whether "레벨 만큼" means create N copies in graveyard. Clarify ordering and behavior if graveyard is full or no longer accessible.
- Confirm level snapshot at destruction and trigger attribution.

### 디바이드어택 — 3 rows / 4 excerpts / 2 variants
- 3: "AP 2이상으로 공격시, 자신의 AP 절반만큼 감소(내림), 감소된 수치만큼 적 필드 다음 유닛에게 데미지를 준다."
- 1 ancillary item text about maintenance-cost conversion; not the attack mechanic.
Sample [블러디소드맨](https://fmlunatic.com/card/11022325602), ID `11022325602`.
- Define whether "자신의 AP" is rolled AP or base/effective AP; attacker AP is reduced by floor(AP/2), then same amount is direct damage to the next enemy unit.
- Clarify whether the secondary damage bypasses DP and what happens without a next enemy unit. Keep item penalty separate.

### 버닝퓨리 — 3 rows / 4 excerpts / 2 variants
- 3: "적 1파괴시, 자신의 AP만큼 아군 필드 행동가능 다음 유닛 1의 AP가 증가."
- 1 ancillary item flavour text, not the Skill1 mechanic.
Sample [화염의정령](https://fmlunatic.com/card/11031625631), ID `11031625631`.
- Define AP snapshot (rolled vs current effective), target next actionable ally, and whether gain is temporary/permanent.
- No-target behavior and stat-marker restrictions need tests.

### 블레스 — 3 rows / 4 excerpts / 3 variants
- 2: "AP1 이상 공격시, 아군핸드 유닛1 공방체+1".
- 1 ancillary item-grant flavour text.
- 1: same Skill1 effect with terminal punctuation.
Sample [신성한조력자](https://fmlunatic.com/card/11060125757), ID `11060125757`.
- Explicit hand slot 1 target. Define whether +1 applies to AP/DP/HP of that card and whether the buff persists after deployment.
- Exclude item flavour text and test occupied non-unit/empty slot.

### 빙결공격 — 3 rows / 4 excerpts / 4 variants
- 1 ancillary item description for 소달라이트; not the attack mechanic.
- 1: "AP1 이상 공격시, 상대 유닛에게 빙결상태 2턴간 부여. 이미 상대에게 빙결상태가 부여되어 있는 경우 상위 빙결상태를 2턴간 부여.(상급인 경우는 상급 2턴 부여)".
- 1 punctuation variant.
- 1 wording variant with same stated upgrade behavior.
Samples [소달라이트](https://fmlunatic.com/card/10062341158), ID `10062341158`; [라푸시누](https://fmlunatic.com/card/14010827212), ID `14010827212`; [궁전근위병](https://fmlunatic.com/card/9120224498), ID `9120224498`.
- Define status tier ordering and whether existing superior status is refreshed or retained. "상급인 경우는 상급 2턴" must not downgrade or reset incorrectly.
- Retrieve canonical ice status definitions and exact duration tick order.

### 선물하기 — 3 rows / 3 variants
- 1: "자신 파괴시, 자신 킬수만큼의 적군 핸드 카드를 성탄절선물 카드로 교체."
- 1: "자신 파괴 시 자신 보유 Kill수만큼 상대 핸드카드 1번부터 성탄절선물 카드로 교체 : 성탄절선물 : (0 / 0 / 0)."
- 1: same effect without final punctuation.
Samples [성탄절양말](https://fmlunatic.com/card/13121841508), ID `13121841508`; [꼬마산타](https://fmlunatic.com/card/15122328207), ID `15122328207`.
- Explicit slot order from hand slot 1; define whether it replaces all cards or only occupied eligible slots, and cap by available cards.
- Confirm generated gift card exact definition and whether current kill count is sampled before destruction.

### 솔카운터 — 3 rows
3 × "아군적군 준비턴에 남은 무소울의 합만큼 자신의 AP에 더하여 공격한다."
Sample [두랄의기사](https://fmlunatic.com/card/11112425398), ID `11112425398`.
- Define whether "아군적군 준비턴에 남은 무소울" is combined across both players and only unspent neutral souls, not colored souls.
- Snapshot before attack and test 0, 1, and multiple remaining neutral souls. Determine whether AP bonus is temporary and whether the bonus is capped.

## Cumulative Skill1 inventory
- A18: 30 candidate rows / 36 non-empty excerpts / 25 exact variants.
- A1–A17: 1,915 rows / 1,921 excerpts / 283 variants.
- A1–A18: **1,945 rows / 1,957 excerpts / 308 variants**.
- Ancillary item text is counted as source excerpts but explicitly excluded from Skill1 mechanics. Inventory totals are not implementation totals.

## Promotion gate
Separate distinct trigger variants and card-specific generated objects. Resolve stat snapshot, damage routing, slot targeting, status tier/expiry, and soul-pool semantics before coding. Add tests for empty slots, no-target, status upgrades, turn timing, and generated-card identity.
