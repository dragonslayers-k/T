# Skill1 source evidence manifest — Batch A19

## Scope
DB29 semantic review artifact from Actions #430, strict `source_field == "Skill1"` filter. Next ten groups after A18 in frequency/name order. Skill2 excluded. Ancillary item text is not treated as Skill1 mechanics.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 아이언클래드 | 3 | 4 | 2 |
| 야수강타 | 3 | 3 | 1 |
| 에코카피 | 3 | 3 | 1 |
| 자연의경고 | 3 | 3 | 1 |
| 천상의벼락 | 3 | 1 | 1 |
| 초음파 | 3 | 2 | 2 |
| 칠색음 | 3 | 3 | 2 |
| 켄드드레인 | 3 | 1 | 1 |
| 코인적중 | 3 | 3 | 2 |
| 클리브 | 3 | 3 | 1 |
| **Total** | **30** | **26** | **14** |

## Evidence and unresolved semantics

### 아이언클래드 — 3 rows / 4 excerpts / 2 variants
- 3: "AP2 이상 공격시, 자신 AP-2 아군 핸드카드수 절반(내림) 만큼 DP/HP증가."
- 1 ancillary item text: equipment with 기선제압 grant converts all maintenance cost to colored soul permanently; not this Skill1.
Sample [친위대장](https://fmlunatic.com/card/11060125743), ID `11060125743`.
- Confirm AP cost is exactly -2 (not capped by current AP) and DP/HP gain equals floor(friendly hand card count / 2).
- Define whether the count includes non-unit cards and whether stat changes are temporary or permanent. Exclude item text.

### 야수강타 — 3 rows
3 × "AP1 이상 공격시, 상대 유닛이 야수면 아군 핸드 카드 수 만큼 추가 데미지."
Sample [암흑길드전사](https://fmlunatic.com/card/10102025294), ID `10102025294`.
- Confirm "야수" checks target's native unit ability/race tag, not a displayed name substring.
- Define hand-card count snapshot and whether extra damage is applied before or after DP.

### 에코카피 — 3 rows
3 × "자신 파괴시, 자신lv 이하 상대방 핸드 유닛 1을 아군 필드 다음 위치에 복사."
Sample [북해의지배자](https://fmlunatic.com/card/11112425408), ID `11112425408`.
- Define target selection among enemy hand units with level <= destroyed unit's level and exact copy semantics.
- Confirm whether copied unit retains original owner identity, items, skills, cost, and current damage; define full-field/no-eligible-target behavior.

### 자연의경고 — 3 rows
3 × "적 1파괴시, 야수가 아닌 적군 행동 가능 다음 유닛1은 마법개구리 카드로 교체."
Sample [생존왕](https://fmlunatic.com/card/11112425395), ID `11112425395`.
- Eligibility explicitly excludes beast units and requires an actionable next enemy unit. Define "next" ordering and behavior if the next unit is a beast (skip to next eligible or no effect).
- Need exact 마법개구리 card ID and whether replacement preserves slot/status/equipment.

### 천상의벼락 — 3 rows / 1 excerpt
1: "[●● 히어로]: 아군 필드에 있는 '케를랑' 1을 상위랭크로 변경하고 아군 필드에 '케를랑'이 없으면 아군 소각장에 위치한 '케를랑' 1을 삭제하고, 아군 핸드 빈공간에 '케를랑N'을 소환."
Sample [케를랑](https://fmlunatic.com/card/13011626659), ID `13011626659`.
- Only one source excerpt exists for three candidate rows; leave two unresolved.
- This appears to be a hero/quest conditional with a named-unit upgrade/recovery chain, not a generic Skill1 combat handler. Need full ●● hero context, exact rank progression, and all 케를랑N card IDs before implementation.

### 초음파 — 3 rows / 2 excerpts / 2 variants
- 1: "AP 1 이상 공격시, 적 행동가능 다음 유닛은 AP, DP-3."
- 1: "공격" only; no mechanic detail.
Sample [라이락스](https://fmlunatic.com/card/13061926900), ID `13061926900`; sparse [듀드티](https://fmlunatic.com/card/8070223547), ID `8070223547`.
- One candidate row has only a generic "공격" excerpt; keep it unresolved.
- Define next actionable enemy target, whether AP and DP each decrease by 3, duration/persistence, and no-target behavior.

### 칠색음 — 3 rows / 2 variants
- 2: "AP 1 이상 공격시, 자신의 속성을 랜덤으로 변경한 후 변경된 속성과 동일한 속성을 가진 적 핸드 카드 1을 파괴한다."
- 1: "AP1 이상 공격시, 자신의 속성을 랜덤하게 영구히 변경하고 변경된 속성과 동일한 적군 핸드 카드 1 파괴."
Samples [몽실아가씨](https://fmlunatic.com/card/14123127775), ID `14123127775`; [뮤즈에라토](https://fmlunatic.com/card/7102423226), ID `7102423226`.
- Wording differs on permanence. Preserve temporary-vs-permanent as separate unresolved source variants.
- Define RNG pool/seed, whether current attribute can be rolled again, enemy hand target selection, and no matching card behavior.

### 켄드드레인 — 3 rows / 1 excerpt
1: "AP1이상 공격시, 아군 적군 핸드 지형 수만큼 AP/HP를 증가 시킨 후 공격."
Sample [마이너가디스](https://fmlunatic.com/card/15112528177), ID `15112528177`.
- Only one of three candidate rows has source text. Keep the other two unresolved.
- Define whether "지형 수" is combined hand terrain count for both players, whether AP and HP both increase by that count, and modifier duration. Preserve "before attack" ordering.

### 코인적중 — 3 rows / 2 variants
- 2: "AP1이상으로 공격시, 각자의 코인 뜬 수가 같으면 방어유닛 행동불능으로 아군 필드 맨뒤 이동."
- 1: "AP 1 이상 공격시, 상대와 자신의 코인 앞면 수가 같으면 상대를 아군필드 맨뒤에 행동불능으로 이동시킨다."
Samples [피그대학생](https://fmlunatic.com/card/13103027106), ID `13103027106`; [태양의기사](https://fmlunatic.com/card/15020427811), ID `15020427811`.
- Define which coin profile is compared (shared tosses or stat-specific heads) and whether both players must have equal toss counts or equal heads.
- Movement to own field implies control/ownership transfer; define slot availability, unit owner, action-disabled duration, and item/status inheritance.

### 클리브 — 3 rows
3 rows; 3 non-empty excerpts; one exact wording variant in the source artifact.
- Candidate name is present in Skill1 mapping but the corresponding effect text is not surfaced in this batch extraction.
- Keep as unresolved until the exact source card URL and complete effectText are recovered; do not fill from skill-name inference.

## Cumulative Skill1 inventory
- A19: 30 candidate rows / 26 non-empty excerpts / 14 exact variants.
- A1–A18: 1,945 rows / 1,957 excerpts / 308 variants.
- A1–A19: **1,975 rows / 1,983 excerpts / 322 variants**.
- Inventory metrics are not executable-rule counts; missing excerpts remain explicitly unresolved.

## Promotion gate
Require full source for sparse entries, hero/quest branches, and card replacement/copy operations. Keep random attribute permanence variants separate. Add tests for ownership transfer, target eligibility, RNG determinism, empty lanes, and state inheritance before any implementation.
