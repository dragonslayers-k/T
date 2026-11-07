# Skill2 홀리오오라·프레셔 원문 및 APK 경계 교차감사 — 2026-11-06

## 1. 기준
- T `feat/carddb-effect-semantic-pass`, 변경 전 HEAD `940b0d72a8a35afcf12ac9ef3803a1fd0fbbe738`
- 불변 DB Release: `fm1-carddb-29`
- source: T Actions #573 / run `41970905894`, artifact `13388874560`
- APK 비교: `feat/combat-event-foundation` HEAD `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e`, PR #28 open/draft
- 본 문서는 evidence/test review만 추가한다. DB29/원본/매핑/APK 코드 변경 없음.

## 2. 홀리오오라 — DB29 2행

| 항목 | 수량 |
|---|---:|
| 후보 행 / 고유 카드 ID | 2 / 2 |
| Skill2 enum | 181 |
| 실제 `additional_text` 발췌 | 2 |
| 원문 변형 | 2 |
| excerpt 누락 | 0 |
| source-verified / executable | 0 / 0 |

원문:
- 1행: `방어시 적군 유닛의 AP가 자신 방/체 합 1/2 이하일경우에는 데미지를 입지 않는다.`
- 1행: `방어시 적군 유닛의 AP가 자신 방/체 합 1/2 이하(내림)일경우에는 데미지를 입지 않는다.`

두 번째 문구는 내림을 명시하고 첫 번째 문구는 내림을 괄호로 명시하지 않는다. 원문 변형을 동일한 확정 표현으로 덮어쓰지 않는다.

### APK 구현·테스트

- 구현: `rules.js`, Rule ID `skill2_holy_aura`
- 계산: `floor((defender rolled DP + defender current HP) / 2)`
- 공격자의 공격 AP가 계산 임계값 이하이면 해당 공격 피해를 막는다.
- 관련 테스트:
  1. `source Skill2 Holy Aura prevents damage when attacker AP is at or below half of defender DP plus HP`
  2. `production dispatcher applies Holy Aura using floor of rolled DP plus current HP`
  3. `production Tactical Initiative and Holy Aura do not activate from inferred mappings`

현재 테스트는 DP 2 + HP 5의 절반 내림 임계값 3에서 공격 AP 3은 피해 0, AP 4는 피해 2가 되는 경계를 확인한다. 또한 inferred mapping은 실행하지 않는다. 다만 helper가 source-verified tuple을 직접 주입하므로 DB29 실제 두 카드의 매핑 검증은 아니다.

### 남은 경계

- 첫 번째 원문은 내림을 직접 쓰지 않고 두 번째만 `(내림)`을 명시한다. 두 행 모두 같은 계산식으로 묶을지 카드별 근거를 더 확인해야 한다.
- 원문은 “자신 방/체 합”이라고 하지만 계산 시점의 DP가 굴림값인지, 현재 DP인지, 장비/버프 적용 후 값인지 문장만으로 모두 설명하지 않는다. 현재 구현은 rolled DP + current HP를 사용한다.
- 피해 차단은 테스트된 공격 상황 외에 반사/관통/직접 피해 등 다른 피해 경로에도 적용되는지 별도 확인이 필요하다.

## 3. 프레셔 — DB29 1행

| 항목 | 수량 |
|---|---:|
| 후보 행 / 고유 카드 ID | 1 / 1 |
| Skill2 enum | 166 |
| 실제 `additional_text` 발췌 | 1 |
| 원문 변형 | 1 |
| excerpt 누락 | 0 |
| source-verified / executable | 0 / 0 |

원문: `방어시, 아군 필드 빈공간수 절반(내림) 만큼 받은 데미지를 감소시킨다`

### APK 구현·테스트

- 구현: `rules.js`, Rule ID `skill2_pressure_defense`
- 계산: `floor(max(0, 5 - owner.units.length) / 2)`
- 관련 테스트:
  1. `production dispatcher applies Pressure Defense from empty friendly slots`
  2. `production Pressure Defense respects the five-slot floor boundary`
  3. `production Pressure Defense applies floor(4/2) at the four-empty-slot boundary`

테스트는 빈 슬롯 0~4개 경계와 내림을 확인한다. 다만 5칸 필드의 점유 상태가 `owner.units.length`만으로 정확히 대표되는지, 유닛 수와 실제 빈 슬롯 수가 다른 상태가 생길 수 있는지 확인이 필요하다. 원문은 실제 빈 공간 수를 기준으로 하므로, 슬롯 인덱스/비어 있는 칸을 직접 세는 구현인지가 중요한 계약이다.

### 남은 경계

- 현재 구현이 배열 길이 기반 빈 슬롯 수를 사용하므로, 슬롯 중간 공백·slotIndex 불연속·일시적 미배치 상태에서 실제 빈 공간 수와 일치하는지 확인해야 한다.
- 감소량이 실제 피해보다 클 때 피해가 0보다 작아지지 않는 공통 계산 경계와 결합 테스트가 필요하다.
- source excerpt는 방어 시점의 빈 슬롯을 말하지만 스냅샷 시점(공격 전/방어 굴림 후/피해 계산 직전)은 상세히 특정하지 않는다.

## 4. 공통 판정

- 두 그룹 모두 카드별 효과 원문 발췌 누락은 0.
- 홀리오오라 2행 / 프레셔 1행 모두 `inferred` 상태.
- APK handler 및 테스트가 존재하지만 DB29 실제 카드의 source verification/executable 증거가 아니다.
- source-verified 승격 0, executable 승격 0.
- DB29 불변, DB30 미발행, PR 미병합.

## 5. 다음 단계

1. 8개 Skill2 그룹 중 남은 `기선제압` 175행의 원문 변형/경계 테스트를 현재 APK HEAD와 다시 교차검토한다. 이전 #617의 evidence adjudication을 현재 HEAD와 비교해 stale 여부를 확인한다.
2. 그 다음 8개 그룹의 crosswalk 결과를 통합해 원문 증거/테스트 커버리지/미해결 경계를 한 표로 집계한다.
3. 모든 카드 매핑은 실제 source row/DB29 데이터 경로가 검증되기 전까지 inferred로 유지한다.


## 6. 후속 APK 보완 — Pressure Defense 슬롯 계수

- APK 저장소: `dragonslayers-k/FM-OFFLINE`
- APK 브랜치: `feat/combat-event-foundation`
- 변경 커밋: `4cfbed7a9583eb6e2f03df3bc14f2105235bfc22`
- 변경 파일: `app/src/main/assets/game/rules.js`, `tests/rules.test.cjs`

기존 구현은 `5 - owner.units.length`로 빈 슬롯을 계산했다. 후속 수정에서는 화면의 5개 물리 슬롯 렌더링 규칙과 동일하게 슬롯 인덱스(미지정 시 배열 위치 fallback)를 적용하고, 1~5 범위의 고유 점유 슬롯 수를 기준으로 빈 슬롯을 계산한다.

추가한 생산 경로 회귀 테스트:
1. `production Pressure Defense counts unique visible slots when fallback and explicit slot indices collide`
2. `production Pressure Defense ignores units outside the five rendered field slots`

이 수정은 슬롯 점유 계산을 보완한 것이며, DB29의 프레셔 카드 매핑을 `source_card_verified` 또는 `executable`로 승격하지 않는다. CI 검증은 APK Actions #255에서 진행 중이며, 결과가 확정되기 전까지 성공으로 간주하지 않는다.

DB29 불변, DB30 미발행, T PR #9 미병합 원칙은 유지한다.
