# DB29 RequireSoul 공식 코드 의미 사전 — 7차 정정 및 기준 고정

## 기준 출처
DB29 Release의 `enumtable.json` 내 `Enum+RequireSoul`를 직접 읽어 공식 `KIND`, 영문 식별자, 아이콘 파일명을 추출했다. 이 문서는 이미지 모양으로 추측한 명칭보다 우선하는 원본 enum 기준이다.

## 공식 코드 매핑

| 코드 | 공식 enum 식별자 | 아이콘 파일 |
|---:|---|---|
| 01 | NONE | `/none.webp` |
| 11 | DARK | `/dark.webp` |
| 12 | DARK_EARTH | `/dark_earth.webp` |
| 13 | DARK_FIRE | `/dark_fire.webp` |
| 14 | DARK_LIGHT | `/dark_light.webp` |
| 15 | DARK_WATER | `/dark_water.webp` |
| 21 | FIRE | `/fire.webp` |
| 22 | FIRE_FOREST | `/fire_forest.webp` |
| 23 | FIRE_IRON | `/fire_iron.webp` |
| 24 | FIRE_WATER | `/fire_water.webp` |
| 31 | WATER | `/water.webp` |
| 32 | WATER_EARTH | `/water_earth.webp` |
| 33 | WATER_FOREST | `/water_forest.webp` |
| 41 | FOREST | `/forest.webp` |
| 42 | FOREST_IRON | `/forest_iron.webp` |
| 43 | FOREST_LIGHT | `/forest_light.webp` |
| 51 | IRON | `/iron.webp` |
| 52 | IRON_EARTH | `/iron_earth.webp` |
| 53 | IRON_LIGHT | `/iron_light.webp` |
| 61 | EARTH | `/earth.webp` |
| 62 | EARTH_LIGHT | `/earth_light.webp` |
| 71 | LIGHT | `/light.webp` |
| 81 | **MU** | `/mu.webp` |
| 82 | **NCS** | `/ncs.webp` |
| 83 | **BONUS** | `/bonus.webp` |

## 정정 사항

이전 시각 감사 문서와 임시 CSV에서 코드 81의 속이 빈 원형 표식을 외형상 설명하기 위해 `NEUTRAL` 또는 “중립”이라고 적은 부분은 공식 enum 명칭이 아니다. DB29 공식 이름은 **MU**다.

- 코드 81의 공식 명칭은 MU로 고정한다.
- 코드 82는 NCS, 코드 83은 BONUS로 고정한다.
- “속이 빈 원형 표식”은 아이콘의 외형 설명에만 사용하고 공식 의미 이름으로 사용하지 않는다.
- 이전 검수 스크립트의 `expected_neutral`/`detected_neutral` 필드는 `expected_mu`/`detected_mu`로 교체한다.
- 기존 778장 + 52장 시각 판독 수량은 코드 81의 명칭만 정정한 것이므로, 검출 수량과 판정 결과는 바뀌지 않아야 한다. 재실행으로 이를 확인한다.

## 해석 경계
이 enum은 코드 이름과 아이콘 리소스 경로를 정의한다. MU/NCS/BONUS가 게임 규칙상 어떤 자원 소비 방식·예외 조건을 갖는지, RequireSoul에서 다른 토큰과 어떻게 합산되는지는 별도 규칙 근거가 필요하다. enum 이름만으로 런타임 비용 의미를 단정하지 않는다.

## 실행 경로
- 원본 enum 파일: DB29 Release `fm1-carddb-29/enumtable.json`
- 공식 enum 검증: `scripts/audit_require_soul_source_join.py`와 이미지 프로브가 같은 Release에서 읽음
- 재실행 workflow: `.github/workflows/require-soul-rail-audit.yml`
