# FM1 Manual Skill1 우선 6개 규칙 — assertion 본문 감사 (2026-11-06)

## 범위와 보호선

- CardDB 기준 브랜치: `feat/carddb-effect-semantic-pass`
- 기준 HEAD: `a5f9b1a2c4f8397864c487f71a60ef1acfa99e71`
- APK 기준 브랜치: `feat/combat-event-foundation`
- APK 기준 HEAD: `4033c1ab84c054c070ad187106a577600585503a`
- APK 테스트 파일: `tests/rules.test.cjs` (blob `212a8d2c098116349b58cc47871207d3af064346`)
- APK 전투 처리: `app/src/main/assets/game/rules.js` (blob `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`)
- DB29 불변, DB30 미발행. PR #9/#28 병합 금지.
- 이 문서는 기존 테스트의 실제 assertion 본문을 확인한 정적 감사다. CI/Node 테스트/Android 빌드/에뮬레이터는 이번 단계에서 실행하지 않았다.

## 실제 테스트 본문에서 확인한 것

| Rule ID | DB29 대표 카드 | 기존 assertion에서 확인한 결과 | 남은 검증 공백 |
|---|---|---|---|
| `normal_attack` | 은룡의검 `10020341112` | AP 3 - DP 1 = 피해 2, 방어자 DP 불변. AP=DP 경계와 AP=0에서 피해 0 | DB29 실물 pack/import 경로에서 카드 metadata가 그대로 전달되는지 미검증 |
| `piercing_attack` | 블랙유니콘 `10091525214` | AP 4가 DP 2를 소모하고 잔여 피해 2 적용, DP 0 | DP가 AP보다 큰 경우, 음수 DP, DP=0의 독립 경계 assertion 확인 필요 |
| `weaken_attack` | 이블크로우 `10091525190` | 초기 DP가 피해를 막아도 공격 조건이 성립하면 AP -1 및 DP -1. AP ▲는 AP 감소를 막고 DP ▼는 DP 감소 허용 | HP 피해가 실제 발생하는 양성 사례, AP/DP marker 각각의 반대 방향 분리 assertion 부족 |
| `petrify_attack` | 파프니르 `10010624589` | AP 1 공격 조건에서 대상 AP 0, DP +1. AP ▲ 및 DP ▼ marker는 각 변경을 막음 | 공격 AP=0일 때 효과 미발동, AP/DP 각 독립 marker 방향 및 이미 AP 0인 경계 확인 필요 |
| `shield_break` | 해적전투원 `10010624551` | 방어 굴림 DP 3에서 공격 피해 0 후 대상 DP 0. 음수 DP -2는 유지. DP ▲는 감소 차단 | DP=0, 양수 DP marker 반대 방향, 실제 pack 기반 metadata 확인 필요 |
| `defense_convert` | 리듬포이 `10010624563` | 양수 DP 4를 -4로 변환. DP 0 및 -2는 그대로 유지. DP ▲는 변환 차단 | DP marker 방향별 독립 경계 및 attack AP=0 미발동 여부 확인 필요 |

## 소스 코드와 assertion의 연결

APK `resolveUnitAttack` 본문에서 다음 실행 조건을 확인했다.

- 일반 공격은 별도 특수 분기 없이 AP - DP 기본 피해 경로를 사용한다.
- 관통공격은 양수 방어 DP 중 공격 AP 이하의 값을 DP에서 소모하고 잔여 AP를 피해로 계산한다.
- 약화공격/석화공격은 `canAffectDefender` 조건에서만 실행되며, 코드상 `canAffectDefender = attackRoll.value >= 1`이다.
- 방패파괴는 공격 조건 성립 및 방어 굴림 DP가 0 이상일 때 DP를 0으로 설정한다.
- 방어전환은 공격 조건 성립 및 방어 굴림 DP가 양수일 때 DP를 음수 절댓값으로 설정한다.

이것은 현재 코드의 동작을 기술한 것이며 Manual 원문이 그 의미를 완전히 뒷받침하는지에 대한 독립 검증과는 구분한다.

## 중요한 한계 — source fixture와 실물 DB29 pack은 다르다

현재 테스트들은 DB29 카드 ID/이름/Skill1 라벨을 주석과 fixture에 직접 넣고, 테스트 객체에 `specialSkillRuleId`, `specialSkillMappingStatus='manual_verified'`, `specialSkillRuleAuthority='manual'`를 직접 주입한다. 따라서 이 테스트들은 카드별 규칙 handler assertion으로는 유효하지만 다음을 증명하지 않는다.

1. 불변 DB29 SQLite의 실제 행이 그 카드 ID/이름/Skill1 및 Manual 매핑 상태를 갖는지
2. DB29 release converter가 그 값을 카드 pack JSON에 정확히 기록하는지
3. Android importer 및 WebView normalizer가 그 값을 실제 설치 데이터에서 보존하는지

이 구간은 기존 lineage audit에서 요구한 release-bound integration gate로 남긴다. fixture 테스트 결과를 end-to-end 통과로 격상하지 않는다.

## 다음 구현 순서

1. 먼저 immutable `fm1-carddb-29` release asset을 CI 안에서 다운로드/검증하고, 위 6개 카드의 실제 SQLite source row를 읽는 read-only integration test를 연결한다.
2. converter 산출물과 importer/normalizer 출력에서 카드 ID, Skill1 원문 라벨, Skill2 분리, Manual authority, canonical rule ID가 동일하게 유지되는지 assertion한다.
3. 그 다음에만 이번 표의 부족 경계 assertion을 추가한다. 특히 Manual 조항/원문에서 기대 결과를 확인할 수 없는 경계는 추측으로 작성하지 않는다.
4. 테스트는 DB29 asset/tag/commit/checksum 불일치 시 fail-closed 한다. DB29 데이터 자체는 수정하지 않는다.

## 이번 단계 결론

- 6개 우선 규칙 모두 기존 APK 소스 또는 테스트에서 확인할 수 있는 구체적 assertion이 있다.
- 현재 가장 큰 결함은 단순히 테스트 개수가 아니라 **실물 DB29 → converter → Android import → runtime normalization을 연결하는 검증이 빠져 있다는 점**이다.
- 이 감사에서는 APK 소스/테스트를 변경하지 않았고, DB29/DB30/PR 상태도 변경하지 않았다.
