# Skill1 source evidence manifest — Batch A17

## Scope
DB29 semantic review artifact from Actions #430, strict `source_field == "Skill1"` filter. These are the next ten candidate groups after A16 in descending row-count/name order. Skill2 excluded. Excerpts include ancillary card-text entries where identified; they are not automatically part of the Skill1 effect.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 길티컨션스 | 4 | 4 | 2 |
| 나락의화염 | 4 | 4 | 1 |
| 더블디펜스 | 4 | 4 | 2 |
| 동아리모집 | 4 | 4 | 3 |
| 소울증오 | 4 | 5 | 2 |
| 시간차공격 | 4 | 5 | 2 |
| 시체폭발 | 4 | 4 | 3 |
| 심판 | 4 | 4 | 2 |
| 어둠의부름 | 4 | 3 | 2 |
| 용의권능 | 4 | 3 | 3 |
| **Total** | **40** | **40** | **22** |

## Evidence and unresolved semantics

### 길티컨션스 — 4 rows / 2 variants
- 3: "AP1 이상 공격시, 상대 유닛 킬수가 홀수면 킬수+1만큼 아군 필드 유닛 전체 공체 증가 짝수면 핸드 유닛 전체 공체 증가."
- 1: "AP 1 이상 공격시, 상대 킬수 홀수면 킬수+1만큼 아군 필드유닛 전체 공체 증가, 짝수면 핸드유닛 전체 공체 증가."
Sample [두랄의기사](https://fmlunatic.com/card/11112425433), ID `11112425433`; [발락사스](https://fmlunatic.com/card/14061827428), ID `14061827428`.
- Clarify which opponent unit's kill count is read and whether the value is sampled before or after this attack's destruction.
- Define "공체" as AP and HP, exact target zones, and whether gains are permanent. Test odd/even boundary and zero kills.

### 나락의화염 — 4 rows
4 × "자신 레벨 이하 적 유닛 1 파괴시, 파이어볼, 레벨 넘는 유닛 파괴시 파이어링 아군 필드 맨 뒤에 행불로 소환."
Sample [비슐로소서러](https://fmlunatic.com/card/11112425393), ID `11112425393`.
- Preserve branch threshold: destroyed enemy level <= own level selects 파이어볼; greater selects 파이어링.
- Need exact generated card IDs, summon zone/slot, and whether 행동불능 applies to the summoned spell/unit. Confirm equality at own level.

### 더블디펜스 — 4 rows / 2 variants
- 3: "공격한 유닛 AP의 절반으로(올림) 데미지를 입고, 남은 데미지를 아군 다음 유닛에게 전달."
- 1: "방어시, 상대 AP의 절반(올림)만큼 데미지를 받고, 남은 데미지를 아군 필드 다음 유닛에게 전달한다."
Samples [프라이빗아이](https://fmlunatic.com/card/7050222951), ID `7050222951`; [기술의벽](https://fmlunatic.com/card/14111241589), ID `14111241589`.
- Wording may define damage split differently. Resolve whether defender takes ceil(AP/2) and ally takes remainder, or only the defender's reduced damage is capped.
- Define next ally target, no-next-ally behavior, damage floors, and whether transferred damage bypasses DP/defense skills.

### 동아리모집 — 4 rows / 3 variants
- 2: "AP 1 이상 공격시, 아군 핸드 유닛1의 소속을 스튜던트로 영구히 변경한 후 AP를 1 증가시킨다."
- 1: "AP1 이상 공격시, 아군 핸드 유닛1의 소속을 영구히 스튜던트로 변경 후 AP+1"
- 1: punctuation/spacing variant.
Samples [카우대학생](https://fmlunatic.com/card/15111828175), ID `15111828175`; [울프수험생](https://fmlunatic.com/card/12110726480), ID `12110726480`.
- Target is specifically hand unit slot 1; confirm whether AP+1 applies to that same target.
- Test empty slot, non-unit card in slot 1, already-Student affiliation, and permanence.

### 소울증오 — 4 rows / 5 excerpts / 2 variants
- 4: "AP1 이상 공격시, 상대 유닛 유소울이 없거나 무소울이 없는 유닛일 경우 파괴."
- 1 ancillary item description: "능력부여 [집중력과 감성을 높여주어, 금전 이 들어온다고 전해지는 수정입니다. 착용자가 강력한 마법을 시전 할 수 있도록 도와줍니다만 정신력의 소모가 커서 평소보다 강하게 피로를 느낄 수 있습니다.]"
Sample [콰츠](https://fmlunatic.com/card/10062341161), ID `10062341161`.
- Condition is an OR: target lacking colored soul OR lacking neutral soul. Verify whether "없다" means zero current pool, zero printed summon cost, or no soul type on the unit.
- Ancillary item flavour/equipment text is not a separate Skill1 rule.

### 시간차공격 — 4 rows / 5 excerpts / 2 variants
- 4: "AP1이상으로 공격시, Turn의 1의자리수 만큼 추가 데미지".
- 1 ancillary item-grant description about a crown; not part of the attack effect.
Sample [설원경비대장](https://fmlunatic.com/card/10060124904), ID `10060124904`.
- Define turn number source and modulo-10 handling, including turn 10, 11, 20, and turn 0 if relevant.
- Confirm bonus damage is applied before or after DP and whether the current turn is sampled before battle phase advancement. Separate item description from Skill1.

### 시체폭발 — 4 rows / 3 variants
- 2: "적군 소멸시 소멸한 적군 체력치로 적군 전체 HP에 단계별 데미지를 준다."
- 1: "적군 파괴시 파괴된 적군 체력치로 적군 전체 HP에 단계별 데미지를 준다."
- 1: "적군 파괴시 파괴한 적군 체력치로 적군 전체 HP에 단계별 데미지를 준다."
Samples [스파이더퀸](https://fmlunatic.com/card/13110627109), ID `13110627109`; [천하명궁](https://fmlunatic.com/card/12071126322), ID `12071126322`.
- "소멸" and "파괴" may be distinct event types; do not merge until engine event taxonomy confirms.
- Need exact stepwise damage formula and order across all enemy units, including whether damage is based on pre-destruction HP.

### 심판 — 4 rows / 4 excerpts / 2 variants
- 3: "AP1 이상 공격시, 공격받은 적 유닛의 킬 수 만큼 행동가능한 다음 위치 유닛의 공방체 각각 감소."
- 1 ancillary item-grant flavour text for 지르콘, not a second effect.
Sample [주시자](https://fmlunatic.com/card/10040724819), ID `10040724819`.
- Define whether "next position" is next occupied enemy slot and what happens if no actionable next unit exists.
- Define reduction amount and stat-marker/floor interactions; exclude item flavour text.

### 어둠의부름 — 4 rows / 3 excerpts / 2 variants
- 2: "적 1파괴시, 아군 소각장 카드 4장 소각 후 아군 필드 다음 위치에 마왕의홀을 착용한 암흑광신도(홀수레벨 파괴시) 또는 다크템플러(짝수레벨 파괴시) 1을 소환."
- 1: "적군 1 파괴시, 아군 소각장 카드 4장 소각 후 아군 다음 위치 에 마왕의홀을 착용한 암흑광신도 또는 다크템플러 카드 1을 소환."
Samples [아이바](https://fmlunatic.com/card/7020722837), ID `7020722837`; [심연의안내자](https://fmlunatic.com/card/11112425399), ID `11112425399`.
- Preserve graveyard cost of four cards, odd/even level branch, generated unit and attached item. Confirm exact IDs and item payload.
- Define whether fewer than four graveyard cards suppresses the entire effect or burns the available cards, and whether parity is based on destroyed unit's level before removal.

### 용의권능 — 4 rows / 3 variants
- 1: "적 1파괴시, 적 필드 행동 가능한 다음 유닛 1을 행동불능시킨다."
- 1: "적군 1 파괴시, 적 필드 행동가능 다음 유닛 1은 행동불능."
- 1: punctuation variant.
Samples [용술사의보옥](https://fmlunatic.com/card/15093041648), ID `15093041648`; [용의주술사](https://fmlunatic.com/card/7062723058), ID `7062723058`.
- Define next actionable enemy unit selection and duration/reset point for 행동불능.
- Confirm trigger attribution (this Skill1 owner caused destruction) and no-target behavior.

## Cumulative Skill1 inventory
- A17: 40 candidate rows / 40 non-empty excerpts / 22 exact variants.
- A1–A16: 1,875 rows / 1,881 excerpts / 261 variants.
- A1–A17: **1,915 rows / 1,921 excerpts / 283 variants**.
- Inventory counts are not implementation totals. Ancillary text remains explicitly excluded from effect interpretation.

## Promotion gate
Resolve event taxonomy (파괴 vs 소멸), branch formulas, generated-card IDs, graveyard costs, and damage split before coding. Add tests for event attribution, parity/turn boundaries, insufficient resources, empty target lanes, and chained effects.
