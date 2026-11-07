# Skill2 얼라이디펜스 44행 원문·APK 경계 교차감사 — 2026-11-06

## 1. 기준

- 저장소/브랜치: `dragonslayers-k/T` / `feat/carddb-effect-semantic-pass`
- 변경 전 HEAD: `c704e1169dddc0119e3142c318a232c53d40adc1`
- 불변 기준: `fm1-carddb-29`
- 원문 분석: T Actions #573 / run `41970905894`, artifact `13388874560`
- APK 비교: `dragonslayers-k/FM-OFFLINE`, `feat/combat-event-foundation`, HEAD `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e`
- 본 문서는 evidence/test crosswalk만 추가한다. DB29, 원본 데이터, 카드별 매핑 및 APK 코드는 변경하지 않는다.

## 2. DB29 원문 후보 집계

`skill2-execution-review.jsonl`에서 `source_name=얼라이디펜스`인 행:

| 항목 | 수량 |
|---|---:|
| 후보 카드 행 / 고유 카드 ID | 44 / 44 |
| Skill2 enum | 100 |
| 실제 `additional_text` 발췌 | 44 |
| 실제 효과 원문 변형 | 3 |
| 카드별 발췌 누락 | 0 |
| `source_card_verified` | 0 |
| `executable` | 0 |

### 원문 변형

| 행 수 | 원문 |
|---:|---|
| 40 | `방어시, 자신을 제외한 자신과 동일한 소속의 필드 유닛 수 만큼 받는 데미지 감소.` |
| 2 | `방어시, 자신을 제외한 자신과 동일한 소속의 필드 유닛 수 만큼 받는 데 미지 감소.` |
| 2 | `방어시, 자신을 제외한 아군 필드 유닛 중 자신과 동일한 소속을 가진 유닛 수 만큼 자신이 받는 데미지를 감소시킨다.` |
| **44** | **합계** |

두 번째 변형의 `데 미지`는 원문 오탈자/띄어쓰기 변형으로 보존한다. 자동으로 원문을 고치지 않는다. 세 문구 모두 자기 자신 제외, 같은 소속, 필드 유닛 수에 따른 방어 피해 감소를 말한다.

## 3. APK 구현·테스트 crosswalk

### 구현

- 파일: `app/src/main/assets/game/rules.js`
- Rule ID: `skill2_alliance_defense`
- 방어 유닛의 `affiliation` 값이 비어 있으면 감소량 0.
- 방어 유닛 자신(`instanceId` 동일)을 제외하고, 같은 소유자의 `owner.units` 중 소속 문자열이 정확히 일치하는 유닛 수를 계산한다.
- 계산된 수만큼 피해 감소량을 반환한다.
- dispatcher는 `source_card_verified` + `card_source` + `source-card-rule-implemented` 조합만 허용한다.

### 관련 테스트 4개

1. `source Skill2 Alliance Defense reduces damage by each other field unit with the same affiliation`
2. `production Alliance Defense counts only other matching friendly field units and ignores missing or enemy affiliations`
3. `production Alliance Defense gives no reduction when the defender has no affiliation`
4. `production defensive handlers ignore inferred Alliance Defense mappings`

확인되는 테스트 범위:
- 자기 자신 제외 및 동일 소속 아군 수만 계산
- 다른 소속은 제외
- 소속 미기재 방어자는 감소 효과 없음
- 적군의 같은 소속 유닛은 방어자 측 감소량에 포함되지 않음
- inferred 메타데이터는 dispatcher에서 fail-closed

테스트 helper는 source-verified metadata를 직접 주입하므로, DB29 실제 44개 카드가 verified/runtime-ready라는 증거가 아니다.

## 4. 남은 검증 경계

- 44개 후보 행은 모두 실제 카드별 효과 발췌를 갖지만, 모두 `inferred` 상태다. excerpt 존재만으로 매핑을 승격하지 않는다.
- 원문은 “동일한 소속”을 말하지만 소속 값의 표준화/별칭 비교가 필요한지, 원본 필드의 빈 값·다중 소속 표현을 어떻게 처리할지는 별도 검토가 필요하다.
- 현재 구현은 정확한 문자열 일치(`String(ally.affiliation || '')===value`)를 사용한다. 이 값이 실제 DB29 normalized card에서 어떤 형태로 들어오는지 production-pack 경로 검증이 필요하다.
- 이 그룹 전용 테스트에는 감소량이 공격으로 계산된 피해보다 커질 때 결과가 0 아래로 내려가지 않는 경계가 명시적으로 확인되지 않았다. 공통 피해 계산 경로의 clamp와 결합 테스트를 추가 확인해야 한다.
- “방어시” 발동 시점 및 방어 유닛의 실제 필드 상태를 읽는 시점은 카드 원문만으로 세부 타이밍까지 설명되지 않는다.

## 5. 판정 및 다음 순서

- 44/44 행에 카드별 `additional_text` 원문이 연결돼 있다.
- 원문 변형 3개를 보존했다.
- APK handler 및 관련 테스트 4개가 확인됐다.
- source-verified 승격 0, executable 승격 0.
- DB29 불변, DB30 미발행, PR 병합 없음.

### 다음 Skill2 그룹

다음 검토 대상은 `레이셜디펜스` 35행이다. 얼라이디펜스와 동일한 구조를 갖더라도 종족 필드/값을 사용하므로 소속과 동일 규칙으로 합치지 않고 독립 검토한다.
