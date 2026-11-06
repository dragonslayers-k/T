# FM1 Manual Skill1 — 다음 규칙군 assertion 감사 (2026-11-06)

## 범위

APK 저장소 `dragonslayers-k/FM-OFFLINE`, 브랜치 `feat/combat-event-foundation`의 현재 테스트 및 구현을 실제 코드 단위로 대조했다. 대상은 `fatal_attack`, `charge_attack`, `bravery_attack`, `fear_attack`, `regeneration`, `frenzy_attack`이며, 일반 공격의 대표 근거도 전 단계 문서에 보완 확인했다.

- 테스트 파일 blob: `tests/rules.test.cjs`, SHA `212a8d2c098116349b58cc47871207d3af064346`
- 엔진 파일 blob: `app/src/main/assets/game/rules.js`, SHA `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`
- 이 문서는 테스트 설계/구현 확인이며, 별도 Actions 실행이나 APK 계측 성공을 주장하지 않는다.

## 규칙별 결과

| Rule ID | 대표 카드 근거 | assertion | 결과 / 남은 점 |
|---|---|---|---|
| `normal_attack` | 은룡의검 / `10020341112` / Skill1 일반공격 | AP 3 - DP 1 = 피해 2, HP 8→6, 대상 DP 유지; 주석은 Manual `specialability.htm §1` baseline을 명시 | 독립 카드 assertion 확인 |
| `fatal_attack` | 선더골렘 / `10012024612` / 치명공격 | 이미 HP 0인 대상에게 피해 0, 부활 방지, 필드 이탈 및 묘지 유지 | 이미 파괴된 대상 안전성 assertion. 정상 HP 대상의 치명 효과 자체는 aggregate test와 구현 분기 확인; 별도 DB29 대표 테스트 보강은 추후 |
| `charge_attack` | 패스파인더 / `10010624588` / 돌진공격 | AP 2 + 공격자 DP 3 - 대상 DP 1 = 피해 4, HP 10→6 | 핵심 산식 assertion 확인 |
| `bravery_attack` | 타투파이터 / `10010624545` | 레벨 같음에서 AP 0이어도 피해 1; 낮은 레벨 대상에서는 피해 0 | 레벨 경계 assertion 확인 |
| `fear_attack` | 다크프리스트 / `10050424835` | 동등/낮은 대상 레벨에서 피해 1; 높은 레벨 대상은 피해 0 | 레벨 경계 assertion 확인 |
| `regeneration` | 울프라이더 / `10010624560` / 재생능력 | 대상 DP가 공격을 막아 피해 0이어도 공격자 HP 5→6, printed max HP를 넘음 | 테스트는 Manual의 무조건 HP +1 문구를 근거로 캡 미적용 확인. 카드 HP marker/실전 상한 정책은 별도 |
| `frenzy_attack` | 다크퍼밀리어 / `10010624538` | HP 4→1로 3 희생하고 공격 피해 +3; 시작 HP 1은 유지하며 추가 희생 없음 | HP 1 floor 및 피해 보너스 assertion 확인 |

## 근거 해석 / 구분

1. `normal_attack`는 이름만으로 일반 경로에 매핑하지 않았다. 테스트는 DB29 ID와 Skill1 mapping을 명시하고 Manual §1을 baseline으로 적었다.
2. `fatal_attack` 테스트는 “이미 HP 0인 타깃이 치명공격에 의해 revive 되지 않는다”는 회귀 조건이다. 이를 정상 HP 대상에 대한 전체 Fatal Attack 의미 검증으로 확대하지 않는다.
3. `charge_attack`, bravery/fear는 테스트에 DB29 카드 ID 및 Manual Skill1 label을 명시하고, 수치 결과를 assertion으로 고정했다.
4. `regeneration`의 현재 테스트는 HP printed maximum 초과도 허용한다는 구현 결정을 검증한다. 카드 HP marker나 전투 종료 후 처리의 완전성은 이 테스트로 입증되지 않는다.
5. `frenzy_attack`은 공격자 HP 1 floor를 분명히 검사하지만, source Manual의 문구/예외 전체를 독립적으로 재검증한 건 아니다.

## 다음 추가 검증 후보

- `fatal_attack`: 정확한 DB29 대표 카드의 정상 HP 대상에 대한 효과와 대상 HP 경계(HP 1/이미 0)를 하나의 Manual 근거에 따라 독립 assertion으로 묶을지 확인한다. 문구 미확인 시 신규 의미를 가정하지 않는다.
- `regeneration`: HP marker(`*`, `★`, `▲`, `△`)와 HP +1이 충돌하는 경우를 source 기준으로 검토한다.
- 27개 Skill1 전부의 승격 여부는 본 문서가 결정하지 않는다. Source row, Manual 조항, 카드-local 의미 패킷, engine assertion 및 검증 절차를 모두 충족해야 한다.

## 상태

- 이번 단계는 감사 문서만 추가한다. APK 코드/테스트를 수정하지 않는다.
- DB29 보존, DB30 발행 금지.
- PR #9 / #28 미병합.
- 자동화 실행은 필요 이상으로 새로 트리거하지 않는다.
