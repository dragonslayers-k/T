# Skill2 기선제압 181행 원문·APK 경계 교차감사 — 2026-11-06

## 1. 기준
- T `feat/carddb-effect-semantic-pass`, 변경 전 HEAD `8a67a2c36617654b940d14c417ca933ecb8d669d`
- 불변 DB: `fm1-carddb-29`
- Source artifact: Actions #573 / run `41970905894`, artifact `13388874560`
- APK 비교 HEAD: `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e`, PR #28 open/draft
- 이 문서는 원문/test crosswalk다. DB29/원본/매핑/APK 코드 변경 없음.

## 2. 후보·증거 수량의 분모 구분

기선제압은 후보 행 181개다. 이 중 카드별 `additional_text` 실제 효과 원문 175행, `card_text` 보조 문구만 있는 1행, 카드별 발췌 미확보 5행이다.

| 분류 | 행 수 | 처분 |
|---|---:|---|
| 실제 `additional_text` 효과 원문 | 175 | 문구별 독립 검토 |
| `card_text` 보조 문구만 존재 | 1 | Skill2 효과 증거에서 제외 |
| 카드별 원문 발췌 미확보 | 5 | pending |
| 합계 후보 | 181 |  |
| source-verified / executable | 0 / 0 | 승격 없음 |

### 실제 효과 원문 6개 변형

| 행 수 | 원문 |
|---:|---|
| 133 | `적군이 아군보다 이하 레벨일 경우 데미지를 1 덜 받는다.` |
| 18 | `방어시, 상대의 레벨 수치가 자신 레벨 수치 이하이면 자신이 받는 데미지를 1 감소시킨다.` |
| 16 | `적군이 아군보다 이하 레벨인 경우 상대 AP로 인한 데미지를 1 덜 받는다.` |
| 6 | `방어시, 상대의 레벨이 자신보다 이하면 받는 데미지를 1 감소시킨다.` |
| 1 | `방어시, 상대의 레벨이 자신보다 낮은 경우 받는 데미지를 1 감소시킨다.` |
| 1 | `적군LV이 아군 이하일 경우 데미지를 1 덜 받는다` |
| **175** | **합계** |

### 보조 문구와 누락

- `6082340724` 패황의전투마는 `card_text` 서술만 존재하며 실제 효과 원문 증거로 제외한다.
- 카드별 excerpt 누락 5개:
  - `12111426500` 신비의바다
  - `16102628565` 마왕
  - `16110928590` 불의정령여왕
  - `6121340763` 고대나무뿌리
  - `8080640943` 용기의정령
- 누락은 Skill2 부재를 증명하지 않는다. 인접 카드의 원문을 복사하지 않는다.

## 3. APK 구현·테스트

- 구현: `app/src/main/assets/game/rules.js`
- Rule ID: `skill2_tactical_initiative`
- 현재 handler는 공격 유닛 레벨 `<=` 방어 유닛 레벨이면 피해 1 감소를 반환한다.
- dispatcher는 source-verified/card-source/implemented metadata tuple만 허용한다.

확인된 테스트:
1. `source Skill2 Tactical Initiative reduces incoming damage by one at equal or lower attacker level`
2. `source Skill2 Tactical Initiative does not reduce damage when attacker level is higher`
3. `production dispatcher applies Tactical Initiative through a verified pre-damage event`
4. `production Tactical Initiative and Holy Aura do not activate from inferred mappings`

이 테스트들은 equality/inclusive 조건과 higher-level negative case, production event 경로, inferred fail-closed를 검사한다. 테스트 fixture는 source-verified metadata를 직접 주입하므로 DB29 175개 카드의 매핑 승인을 입증하지 않는다.

## 4. 원문과 현재 handler 사이의 미해결 충돌

1. **strict vs inclusive:** 174개 변형은 이하/이하면 표현이지만 1개는 `자신보다 낮은 경우`라고 적혀 있다. 해당 1행까지 `<= ` handler로 처리할 근거는 아직 부족하다. 별도 strict 후보로 유지한다.
2. **전체 피해 vs 상대 AP 피해:** 16행은 `상대 AP로 인한 데미지`라고 한정한다. 현재 handler는 damage source를 확인하지 않고 방어 피해 전반에 1 감소를 반환한다. 이 16행을 전체 피해 감소와 동일 규칙으로 자동 통합하지 않는다.
3. **레벨 비교 주체:** `적군이 아군보다 이하`와 `상대 레벨 수치가 자신 레벨 수치 이하`는 전투에서 공격자/방어자 레벨 매핑이 정확히 어느 방향인지 검증해야 한다.
4. **피해 하한:** 감소 전 피해가 0 또는 1일 때 음수 피해가 발생하지 않는지 공통 계산 경로와 결합해 확인해야 한다.

따라서 기존 테스트는 후보 handler의 일부 해석을 고정하지만, 모든 175행을 동일한 실행 규칙으로 승인할 수 없다.

## 5. 판정

- 후보 181행 중 실제 효과 원문 175, 보조 card_text 1, excerpt 미확보 5.
- 실제 효과 원문 변형 6개.
- APK handler 및 관련 테스트 4개 확인.
- source-verified 승격 0, executable 승격 0.
- DB29 불변, DB30 미발행, PR 미병합.

## 6. Skill2 전체 crosswalk checkpoint

| Skill2 그룹 | 후보 행 | additional_text 효과 행 | 변형 수 | excerpt 누락 | APK 테스트 crosswalk |
|---|---:|---:|---:|---:|---|
| 기선제압 | 181 | 175 | 6 | 5 | 완료 |
| 헌신방어 | 66 | 63 | 6 | 3 | 완료 |
| 강한헌신방어 | 28 | 28 | 2 | 0 | 완료 |
| 얼라이디펜스 | 44 | 44 | 3 | 0 | 완료 |
| 레이셜디펜스 | 35 | 35 | 2 | 0 | 완료 |
| 격노 | 20 | 20 | 2 | 0 | 완료 |
| 홀리오오라 | 2 | 2 | 2 | 0 | 완료 |
| 프레셔 | 1 | 1 | 1 | 0 | 완료 |
| **합계** | **377** | **368** | **24** | **8** | **8개 그룹 crosswalk** |

주의: 377 후보 행 중 1행은 card_text만 있고 8행은 카드별 excerpt가 없으므로 실제 additional_text는 368행이다. 각 그룹의 모든 매핑은 아직 inferred이며 source-verified/executable 0이다. 이 표는 원문/테스트 교차조사 완료를 의미할 뿐 Skill2 실행 규칙 승인이나 DB 완성을 의미하지 않는다.

## 다음 단계
1. 8개 그룹 crosswalk를 바탕으로 APK의 Skill2 handler 중 원문과 충돌하는 해석(특히 기선제압 16 AP 피해 한정 행, strict 비교 1행)을 카드별로 fail-closed 유지한다.
2. 8개 그룹의 DB29 실제 source row → converter → pack → importer lineage 검증 범위를 정한다.
3. 다음으로 비용 831건(hybrid 52 + NCS/BONUS 779)의 동일 분모 재계측으로 이동한다.
