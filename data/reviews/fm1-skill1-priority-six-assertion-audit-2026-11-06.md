# FM1 Manual Skill1 — 우선 규칙 6종 assertion-level 대조 (2026-11-06)

## 범위와 판단 규칙

이번 단계는 최초 27규칙 커버리지 표에서 우선 확인 대상으로 잡은 `shield_break`, `defense_convert`, `weaken_attack`, `petrify_attack`, `piercing_attack`, 일반 공격 경로를 APK 기준 브랜치 `feat/combat-event-foundation`의 실제 테스트 assertion 및 구현과 대조했다.

- APK 테스트 파일: `tests/rules.test.cjs` (branch ref `feat/combat-event-foundation`, blob SHA `212a8d2c098116349b58cc47871207d3af064346`)
- 구현 파일: `app/src/main/assets/game/rules.js` (branch ref `feat/combat-event-foundation`, blob SHA `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`)
- 구현 확인 범위: `resolveUnitAttack`
- 카드 식별은 테스트 코드 안의 DB29 카드 ID와 명시된 Manual Skill1 mapping을 증거로 사용했다.
- 이 결과는 테스트 assertion의 존재/범위 확인이다. 실제 APK 런타임/계측 결과, 원본 Manual의 문구 자체를 새로 확인한 결과, 규칙 승격을 의미하지 않는다.

## 결과 요약

| Rule ID | DB29 카드/테스트 근거 | assertion 확인 | 판단 |
|---|---|---|---|
| `shield_break` | 해적전투원 / `10010624551` | DP 양수 3에서 공격 피해 0 및 방패파괴 후 DP 0; DP -2에서는 음수 DP 유지 | 주요 경계값 테스트 있음 |
| `defense_convert` | 리듬포이 / `10010624563` | 방어 DP 4가 공격 피해를 막은 뒤 DP가 -4로 변환 | 양수 DP 사례 assertion 있음; DP 0/음수 경계는 이 전용 테스트에서 미확인 |
| `weaken_attack` | DB29 Manual piercing/weaken 묶음 테스트 | AP 1 vs DP 2에서 피해 전 AP/DP 각각 -1, 결과 AP 3/DP 1 확인 | 주요 효과 assertion 있음 |
| `petrify_attack` | FM1 petrification test | 대상 AP 4→0, DP 2→3 | 효과 assertion 있음 |
| `piercing_attack` | DB29 Manual piercing/weaken 묶음 테스트 | AP 4 vs DP 3에서 DP 0 및 남은 피해 1 확인 | 방어 상쇄/잔여 피해 assertion 있음 |
| 일반 공격(default) | FM1 attack-skills aggregate test helper | 기본 피해 계산 경로는 명시적 기술 분기 외 `attackPower - defenseRoll`로 확인; 일반전용 독립 테스트 여부는 이번 범위에서 미확정 | 구현 확인, 별도 증거는 더 필요 |

## 확인된 구현 동작

### 방패파괴

`resolveUnitAttack`에서 공격 가능한 대상에 대해 방패파괴가 적용되고, 대상의 DP roll이 0 이상일 때 DP를 0으로 설정한다. 테스트는 정확한 DB29 카드 `10010624551`로 다음 두 가지를 확인한다.

- DP 3: 기본 AP 1 공격은 처음 DP에 막혀 피해 0, 효과 처리 뒤 DP 0
- DP -2: 효과가 음수 DP를 변경하지 않음

따라서 이 테스트는 단순히 “DP를 0으로 만든다” 뿐 아니라 음수 DP 보존 경계도 assertion으로 고정한다.

### 방어전환

테스트는 DB29 카드 `10010624563` 리듬포이의 Manual mapping `defense_convert`을 직접 세팅한다. 대상 DP 4는 공격 피해를 막은 뒤 -4로 전환된다. 테스트 주석은 적용 순서가 “positive DP blocks attack before DP sign conversion”임을 명시한다.

다음 케이스는 이 전용 테스트에서 확인되지 않았다: DP 0, 음수 DP, DP roll과 카드의 실제 stat marker 간 차이. 이를 현재 구현이 잘못됐다고 단정하지 않으며, 후속 경계 테스트 후보로 남긴다.

### 약화 / 석화 / 관통

기존 aggregate assertion들은 실제 stat 결과를 검증한다. 약화는 대상 AP와 DP를 각각 1 낮추며, 석화는 AP를 0으로 만들고 DP를 1 올린다. 관통은 공격 AP와 대상 DP의 최소값만 DP에서 제거하고, 남은 공격량이 피해가 된다. 이 테스트들은 현재 핵심 수치 동작에 대한 독립 assertion을 갖고 있다.

## 미해결 사항 / 다음 순서

1. 일반 공격(default) 경로에 대해 DB29의 Manual `일반공격` 대표 카드 ID를 연결한 전용 assertion을 확인/추가한다. aggregate helper의 결과를 일반 공격 전용 카드 증거로 간주하지 않는다.
2. 방어전환의 DP 0 및 음수 DP 경계 동작을 Manual 원문과 정확한 DB29 대표 카드 근거에 맞춰 검증한다. 원문이 확인되지 않으면 예상 동작을 추가하지 않는다.
3. 다음 audit 대상은 `fatal`, `charge`, `bravery/fear`, `regeneration/frenzy`로 진행한다. 기존 assertion을 재작성하거나 중복 실행하지 않는다.

## 변경/승격 상태

- 이 문서는 검토 결과만 기록한다. APK 소스/테스트를 수정하지 않았다.
- DB29 원본 유지, DB30 발행 금지.
- PR #9 / #28 병합 금지.
- 어떤 Skill1도 이 문서만으로 실행 가능 규칙으로 승격하지 않는다.


## 2026-11-06 follow-up — defense_convert DP sign boundaries

- Primary Manual source was re-read from Dropbox `/판마/Manual.zip`, `specialability.htm`, section `27. 방어전환기술`: `공격당한 상대는 DP에 - 가 붙게 됩니다.` The exact sentence is retained as evidence, not paraphrased into a broader effect.
- APK test commit `56f26aa9b30756c99adc0aca4a395ea8eb1403d7` expands the DB29 source-card fixture `리듬포이 / 10010624563` to assert three independent outcomes: DP +4 blocks one damage then becomes -4; DP 0 allows 1 damage and remains 0; DP -2 allows 3 damage and remains -2.
- The implementation condition remains restricted to a successful attack against a defender and positive rolled DP; no speculative new effect was added.
- This is a focused source-backed boundary test addition. Do not promote the rule beyond the existing verified status until the new APK PR check for the exact test commit completes.


### Verified results — 2026-11-06 Actions #336 / #337

- The Manual-backed defense-convert three-way DP sign test passed on APK PR #28 commit `56f26aa9b30756c99adc0aca4a395ea8eb1403d7`, Actions #336 / run `42203965191`. The log records the exact test and `fail 0`.
- T PR #9 documentation follow-up commit `3f1707149b531562cea75b0fbda12d81393a23c4` passed Actions #724 / run `42204057551` (lightweight regression + compact DB29 runtime inventory; large crawl/full image/SQLite/Release stages skipped).
- Subsequent APK test commit `98f5678291aad551c865aae32339d5662b5723c7`, Actions #337 / run `42204718679`, passed `DB29 Manual source-backed Skill1 cards preserve petrify, aging and charge attack rules` and `DB29 Manual piercing and weakening attacks follow their exact AP and DP effects`, with `fail 0`.
- The expanded petrify assertions apply `cardability.htm` stat-marker rules independently: AP `▲` blocks the `=0` decrease while DP `▼` blocks the `+1` increase; the other stat effect still applies. The weakening positive-damage case confirms the AP/DP −1 effect also occurs when the attack deals 2 HP damage, alongside the existing zero-HP-damage case.
- These are focused rule tests, not DB29 full-pack or emulator revalidation. No source mapping is promoted solely by these fixtures.
