# Skill1 source evidence manifest — Batch A12

Source: DB29 semantic review artifact from Actions #430; strict `source_field == "Skill1"` filter, grouped by exact `source_name`. Skill2 excluded. Candidate rows and excerpts are inventory counts, not executable-rule counts.

| Skill1 | Candidate rows | Excerpts | Exact variants |
|---|---:|---:|---:|
| 드래곤피어 | 7 | 7 | 1 |
| 리버스어택 | 7 | 7 | 1 |
| 리사이클매직 | 7 | 7 | 7 |
| 마강격 | 7 | 7 | 1 |
| 마스터콜링 | 7 | 7 | 1 |
| 마인드컨트롤 | 7 | 7 | 1 |
| 마크체인지 | 7 | 7 | 1 |
| 망명 | 7 | 7 | 1 |
| 문명의발전 | 7 | 7 | 1 |
| 미스릴레이 | 7 | 7 | 1 |
| **Total** | **70** | **70** | **16** |

## Evidence notes and open semantics

- **드래곤피어** (7): 적 1파괴시, 필드 맨 뒤에 드래곤컨슘 상태를 무한턴 부여한 속성별 특정 유닛 1을 행동가능으로 소환. Sample [타무흐라트](https://fmlunatic.com/card/12032126201), ID 12032126201. Define attribute-to-unit table, field capacity, and whether the summoned unit's action-ready flag survives the current phase.
- **리버스어택** (7): AP1 이상 공격시, 상대 유닛이 ▲,* 기호가 있을 경우 해당 기호를 ▼로 영구히 교체하고, ▼기호가 있을 경우 해당 수치를 2 감소시킨 후 공격한다. Sample [고웨이마쿠](https://fmlunatic.com/card/12081426382), ID 12081426382. Define marker precedence when multiple symbols coexist and whether ▼ reduction occurs before attack damage.
- **리사이클매직** (7): seven exact variants each name a different card (e.g. "자신 파괴시, 아군 소각장에 위치한 특정 카드1(블러드피어)을 덱 맨 위로 이동."). Sample [어둠의백작](https://fmlunatic.com/card/11092825912), ID 11092825912. This is a card-specific lookup family, not one universal card name. Build an exact card-ID-to-return-card table; do not infer from the skill label.
- **마강격** (7): AP1이상 공격시, 자신의 AP를 상대 소각장 마법수 절반(올림)만큼 증가 시킨 후 공격한다. Sample [전략의라치오](https://fmlunatic.com/card/16081028470), ID 16081028470. Define spell card eligibility in graveyard and ceiling division snapshot timing.
- **마스터콜링** (7): 자신 파괴시 아군 핸드 1번이 빈 공간이면 해당 공간에 스페셜 등급의 마법, 아이템 카드 1을 랜덤하게 생성. 핸드 1번이 빈 공간이 아니면 아군 필드 다음 위치에 스페셜 등급의 유닛 1을 행동불능으로 소환. Sample [블랙윙](https://fmlunatic.com/card/7013122787), ID 7013122787. Preserve branch order, random pool, next-field-position selection and summoned unit's unable-to-act state.
- **마인드컨트롤** (7): 자신 파괴시 상대 유닛이 보유한 모든 상태 제거 후 속박 상태를 1턴간 부여한다. Sample [조커매지션](https://fmlunatic.com/card/15040127899), ID 15040127899. Define opposing target selection and whether all statuses are cleared before binding is applied.
- **마크체인지** (7): AP1 이상 공격시 적이 보유한 ★,▲,▼ 기호를 ▼기호로 영구히 변경시킨 후 공격한다(일시 부여된 기호도 포함). Sample [고성의주인](https://fmlunatic.com/card/16062228403), ID 16062228403. Explicitly includes temporary markers; define marker conversion and stat recalculation order.
- **망명** (7): 자신 파괴시, 아군 핸드 유닛 1의 소속을 영구히 자신과 같은 소속으로 변경. Sample [코넌드럼](https://fmlunatic.com/card/14073026557), ID 14073026557. Define hand target choice, original owner affiliation snapshot, and persistence.
- **문명의발전** (7): AP1 이상으로 공격시 아군 핸드에 위치한 에피소드 4~6 카드의 레벨 1감소(지형제외, 무소울부터, 최소 1레벨). Sample [알폰스남작](https://fmlunatic.com/card/12041826238), ID 12041826238. Preserve terrain exclusion, neutral-soul-first reduction and minimum level 1.
- **미스릴레이** (7): 공격시 아군 핸드 유닛1과 자신의 AP/HP를 2 증가시킨 후 공격. Sample [파브네헤트](https://fmlunatic.com/card/16012028230), ID 16012028230. Define target choice, whether both AP and HP increase for both units, duration and no-eligible-target behavior.

## Cumulative Skill1 inventory
A12: 70 rows / 70 excerpts / 16 variants.
A1–A11: 1,535 rows / 1,544 excerpts / 198 variants.
A1–A12: **1,605 rows / 1,614 excerpts / 214 variants**.
No rule is promoted by this inventory. Card-specific lookup families and marker transformations require exact source-backed tables and engine tests.
