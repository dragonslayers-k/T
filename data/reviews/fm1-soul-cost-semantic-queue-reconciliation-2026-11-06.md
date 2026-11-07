# DB29 비용·소울 semantic queue 분모 재조정 — 2026-11-06

## 1. 기준과 출처

- 저장소/브랜치: `dragonslayers-k/T` / `feat/carddb-effect-semantic-pass`
- 변경 전 HEAD: `9acf21268a52d20833ec9c063a76972ec0bb8d45`
- 기준 Release: 불변 `fm1-carddb-29`
- source: T Actions #573 / run `41970905894`, artifact `13388874560`
- 파일: `gap-reports/soul-semantic-review-queue.json`, `gap-reports/cost-code-inventory.json`
- 본 문서는 queue 분모/중복/원문 토큰을 재정리한 보고서다. 카드 비용 원본, 매핑, 런타임 실행 정책은 변경하지 않는다.

## 2. 831 카드와 842 token row의 차이

| 집계 단위 | 수량 | 의미 |
|---|---:|---|
| pending unique card rows | 831 | 소울 의미 검토 대상 고유 카드 |
| token rows / occurrences | 842 | 카드의 RequireSoul 안에 존재하는 개별 특수/하이브리드 토큰 occurrence |
| 하이브리드 카드 ID | 52 | 14개 hybrid 조합의 고유 카드 |
| NCS 카드 ID | 351 | NCS 토큰이 포함된 카드 |
| BONUS 카드 ID | 439 | BONUS 토큰이 포함된 카드 |
| NCS∩BONUS 중복 카드 | 11 | 같은 카드에 두 특수 토큰이 함께 존재 |
| NCS∪BONUS 고유 카드 | 779 | 351 + 439 - 11 |
| 고유 pending 카드 합계 | 831 | hybrid 52 + special union 779 |

따라서 `52 + 351 + 439 = 842`는 token occurrence 분모이고, `52 + 779 = 831`은 고유 카드 분모다. 두 수치를 서로 다른 조사량으로 구분한다. 이전 문서의 `hybrid 52 + NCS/BONUS 779 = 831`은 고유 카드 수를 뜻한다.

## 3. 16개 semantic groups

| 코드 | 원본 enum | 보존된 후보 해석 | 고유 카드/occurrence |
|---:|---|---|---:|
| 12 | DARK_EARTH | dark + earth | 3 |
| 13 | DARK_FIRE | dark + fire | 4 |
| 14 | DARK_LIGHT | dark + light | 4 |
| 15 | DARK_WATER | dark + water | 3 |
| 22 | FIRE_FOREST | fire + forest | 4 |
| 23 | FIRE_IRON | fire + iron | 3 |
| 24 | FIRE_WATER | fire + water | 5 |
| 32 | WATER_EARTH | earth + water | 3 |
| 33 | WATER_FOREST | forest + water | 4 |
| 42 | FOREST_IRON | forest + iron | 4 |
| 43 | FOREST_LIGHT | forest + light | 3 |
| 52 | IRON_EARTH | earth + iron | 4 |
| 53 | IRON_LIGHT | iron + light | 3 |
| 62 | EARTH_LIGHT | earth + light | 5 |
| 82 | NCS | NCS identity preserved | 351 |
| 83 | BONUS | BONUS identity preserved | 439 |

- 14 hybrid group 합계: 52개 고유 카드 / 52 occurrences.
- NCS: 351개 카드 / 351 occurrences.
- BONUS: 439개 카드 / 439 occurrences.
- 모든 그룹은 `executable=false`이며, hybrid/special payment semantics 검증 대기 상태다.

## 4. NCS·BONUS 원본 토큰 분포

### NCS (enum 82)

| 원본 토큰 | 수량 값 | occurrence |
|---|---:|---:|
| `8201` | 1 | 146 |
| `8202` | 2 | 125 |
| `8203` | 3 | 66 |
| `8204` | 4 | 11 |
| `8205` | 5 | 3 |
| **합계** |  | **351** |

### BONUS (enum 83)

| 원본 토큰 | 수량 값 | occurrence |
|---|---:|---:|
| `8301` | 1 | 438 |
| `8303` | 3 | 1 |
| **합계** |  | **439** |

원본 토큰 identity 및 amount는 파서의 수치값만으로 payment rule을 확정하지 않는다. 특히 BONUS `8303` 1건은 예외 사례로 따로 보존한다.

## 5. NCS와 BONUS가 함께 나타나는 11개 카드

| 카드 ID | 카드명 | 원본 RequireSoul | NCS | BONUS |
|---|---|---|---:|---:|
| `10021024687` | 발렌타인걸 | `820181018301` | 1 | 1 |
| `11020925600` | 초콜릿보이 | `82028301` | 2 | 1 |
| `12110726481` | 울프대학생 | `820281028301` | 2 | 1 |
| `13041726794` | 라리슈어 | `820481018303` | 4 | 3 |
| `13103027104` | 알파 | `820281028301` | 2 | 1 |
| `13103027106` | 피그대학생 | `820281028301` | 2 | 1 |
| `14102927674` | 햄스터대학생 | `82028301` | 2 | 1 |
| `15042927906` | 엘로히웨아 | `820381038301` | 3 | 1 |
| `15042927907` | 에리바웨아 | `820381038301` | 3 | 1 |
| `7111423264` | 리자드대학생 | `82018301` | 1 | 1 |
| `9111124468` | 양대학생 | `82028301` | 2 | 1 |

이 11행은 NCS와 BONUS를 두 개의 서로 다른 카드로 세지 않는다. 카드 고유 수는 11, token occurrence는 22다. 라리슈어는 BONUS amount 3인 유일한 예외이므로 별도 payment review 대상으로 둔다.

## 6. 현재 판정과 금지

- 831개 카드와 842개 토큰 occurrence 모두 semantic review 대상이다.
- 14개 hybrid group은 후보 색상 조합을 표시할 뿐 실제 결제 허용 조합을 확정하지 않는다.
- NCS와 BONUS는 원본 token identity를 보존하고 별도 지불 규칙 검증 전까지 사용 가능으로 처리하지 않는다.
- NCS/BONUS가 함께 있는 11개 카드의 결제 순서/대체 가능성/누적 지불 규칙을 추정하지 않는다.
- 원본 `RequireSoul`을 덮어쓰지 않는다. DB29 불변, DB30 미발행, PR 미병합.

## 7. 다음 정확한 작업

1. 11개 NCS+BONUS 중복 카드의 원본 카드 상세/이미지/과거 매뉴얼 자료를 먼저 조사해 두 토큰의 관계를 검토한다.
2. NCS 351과 BONUS 439의 단일 토큰 카드에서 원본 비용 구슬/설명과 token 수량이 일치하는지 별도 샘플/전수 기준을 정한다.
3. 14개 hybrid 52카드는 색상 조합과 실제 결제 규칙을 분리해 검토한다.
4. 지불 순서·대체·부족 시 거부·특수 소울 소비 시점의 테스트가 source evidence와 일치하기 전까지 모두 non-executable로 유지한다.
