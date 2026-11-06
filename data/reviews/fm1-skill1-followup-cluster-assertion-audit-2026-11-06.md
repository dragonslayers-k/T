# FM1 Manual Skill1 — 후속 규칙군 assertion 감사 (2026-11-06)

## 범위와 증거 수준
대상은 `vampiric_attack`, `aging_attack`, `beast_tamer`, `spell_suppression`, `weapon_suppression`, `ability_seal`이다. APK 저장소 `dragonslayers-k/FM-OFFLINE`의 `feat/combat-event-foundation` 테스트 및 엔진을 기준으로 한 감사 문서이며, APK 런타임/새 CI 성공이나 Manual 원문 전수 대조를 의미하지 않는다.

- tests/rules.test.cjs blob: `212a8d2c098116349b58cc47871207d3af064346`
- app/src/main/assets/game/rules.js blob: `d56da5c2a4f3eaff04c44384f947dc0cb4a3fa0e`

## 결과표

| Rule ID | 카드/테스트 근거 | 확인된 assertion | 제한 |
|---|---|---|---|
| `vampiric_attack` | 다크카운티스 `10010624542`, Skill1 흡혈공격 | 실제 HP 피해를 이용한 흡혈, 절반 계산 반올림, HP marker 처리 테스트가 존재 | Manual 원문 및 marker별 경계의 독립 대조는 별도 |
| `aging_attack` | 타락자 `13020626691`, Skill1 노화공격 | AP 1 공격으로 AP 4 대상 AP가 -1이 되는 결과와 피해 1 확인 | 해당 사례에서 AP 0 floor를 적용하지 않음. 이를 전 카드에 일반화하지 않음 |
| `beast_tamer` | aggregate test: 야수능력 보유자 및 야수 대상 표식 | 대상 AP 0 결과를 aggregate test가 검사 | 이 감사에서 DB29 대표 카드 ID 및 Manual 조항을 독립 연결하지 못함 |
| `spell_suppression` | aggregate test: 마법능력 / 마법 표식 | 대상 AP 0 결과 확인 | 정확한 DB29 Skill1 source row와 대표 카드 ID 연결 미완료 |
| `weapon_suppression` | aggregate test: 장비능력 / 장비 표식 | 대상 AP 0 결과 확인 | 정확한 DB29 Skill1 source row와 대표 카드 ID 연결 미완료 |
| `ability_seal` | 엔진 표준명은 `봉쇄공격`; alias `기술봉쇄` → `봉쇄공격` 존재 | alias만으로 카드 원문 및 Skill1/Skill2 구분은 입증되지 않음 | 환상낚시꾼 `10020324644`는 여기서 Skill1 확정 증거로 취급하지 않음 |

## 주의사항
1. `SPECIAL_SKILL_RULE_KEYWORDS`의 Rule ID/표준명 연결과 `SPECIAL_SKILL_NAME_ALIASES`의 호환 표기는 카드별 Manual 검증과 서로 다르다.
2. aggregate 테스트에서 태그를 이용한 효과 검증은 엔진 경로 증거일 뿐, DB29 카드-local Skill1 근거로 승격하지 않는다.
3. 흡혈공격은 표시 피해량과 실제 HP 피해를 구분한다. 반올림 및 marker 조건은 Manual 대조를 계속한다.
4. 노화공격의 음수 AP 사례는 그대로 기록하되, 임의의 상한/하한을 덧붙이지 않는다.
5. 봉쇄공격, 마법봉쇄공격, 무기뺏기공격은 서로 다른 Rule ID다. Skill1/Skill2 및 원문 라벨을 추정으로 합치지 않는다.

## 다음 단계
- CardDB source row에서 6개 Rule ID의 Skill1 label, 카드 ID, 원문 증거를 직접 연결한다.
- beast-tamer / spell-suppression / weapon-suppression aggregate 테스트를 정확한 DB29 카드 근거로 재현할 수 있는지 조사한다.
- ability-seal은 봉쇄공격의 Skill1 원문 카드 및 Manual 조항이 확인된 후에만 카드별 assertion 보강을 고려한다.
- vampiric / aging은 기존 테스트를 중복 작성하지 않고, Manual 대조 및 미검증 경계만 이어간다.

## 변경 및 릴리스 제약
- 이번 단계는 문서 감사만 수행하며 APK source/test는 변경하지 않았다.
- DB29 원본 보존, DB30 발행 금지, PR #9/#28 병합 금지.
- 어떤 Skill1도 이 문서만으로 실행 가능/검증 완료 상태로 승격하지 않는다.
