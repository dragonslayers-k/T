# Skill2 격노 20행 원문·APK 경계 교차감사 — 2026-11-06

## 1. 기준
- T `feat/carddb-effect-semantic-pass`, 변경 전 HEAD `72c29b4a3807e1ee9dc974abb0280f6f33c34a66`
- DB 기준: 불변 `fm1-carddb-29`
- Source: T Actions #573 / run `41970905894`, artifact `13388874560`
- APK 비교 HEAD: `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e`, PR #28 open/draft
- 검토 문서만 추가. DB29/원본/매핑/APK 코드 변경 없음.

## 2. DB29 후보와 원문 변형

| 항목 | 수량 |
|---|---:|
| 후보 행 / 고유 카드 ID | 20 / 20 |
| Skill2 enum | 5 |
| `additional_text` 효과 발췌 | 20 |
| 효과 원문 변형 | 2 |
| excerpt 누락 | 0 |
| source-verified / executable | 0 / 0 |

| 행 수 | 원문 |
|---:|---|
| 19 | `방어시 적군 유닛에게 자신이 공격을 받으면 자신의 HP가 깎인 수치만큼 AP 상승.` |
| 1 | `방어시 적군 유닛의 공격을 받으면 HP가 깎인 수치만큼 AP 상승.` |
| **20** | **합계** |

두 표현 모두 방어 중 HP가 실제 감소한 수치만큼 AP가 증가한다는 내용을 포함한다. 주어 생략/문장 차이를 보존한다.

## 3. APK handler 및 테스트

- 구현: `app/src/main/assets/game/rules.js`
- Rule ID: `skill2_frenzy_defense`
- 이벤트: `unit_hp_damage_applied`
- handler는 실제 HP 피해량을 `actualDamage`로 받아 0보다 큰 경우에만 AP를 증가시킨다.
- 대상 유닛이 생존하지 않았거나 실제 피해가 0이면 AP 증가를 적용하지 않는다.
- dispatcher는 source-verified + card-source + implemented 상태에서만 실행한다.

관련 테스트 4개:
1. `source Skill2 Wrath converts actual HP lost while defending into immediate AP`
2. `source Skill2 Wrath gains AP only for HP actually lost when the defender survives`
3. `source Skill2 Wrath does not gain AP from zero damage or lethal HP loss`
4. `production dispatcher applies Wrath from actual HP lost before retaliation`

테스트는 실제 HP 손실과 생존 조건, 0 피해/치명 피해의 제외, 반격 전 AP 적용 순서를 검증한다. 단, helper가 source-verified tuple을 주입하므로 DB29 20개 카드의 매핑을 승인하는 근거는 아니다.

## 4. 미해결 의미 경계

- 원문은 “HP가 깎인 수치”라고 하지만 HP 감소가 전투 중 다른 효과(흡수/반사/지속 피해)로 발생한 경우까지 포함하는지 명시하지 않는다. 현재 구현의 `unit_hp_damage_applied` 이벤트 범위를 검토해야 한다.
- HP가 감소한 뒤 회복되거나, 같은 전투에서 추가 HP 피해를 받는 연쇄 상황의 AP 증가 누적/시점은 별도 경계 확인이 필요하다.
- 생존 조건과 반격 전 AP 반영은 현재 엔진 테스트로 고정되어 있으나, 원문이 모든 전투 단계의 순서를 자세히 설명하는 것은 아니다.
- “HP 손실”을 원시 피해량/방어 후 최종 피해/현재 HP 차이 중 무엇으로 측정하는지 실제 전투 계산 경로와 일치해야 한다. 현재 테스트는 실제 적용된 HP 피해를 사용한다.

## 5. 판정
- 20/20 후보에 카드별 효과 발췌 존재.
- 두 원문 변형 보존.
- APK handler 및 관련 테스트 4개 확인.
- source-verified 승격 0, executable 승격 0.
- DB29 불변, DB30 미발행, PR 미병합.

## 다음
다음 그룹은 `홀리오오라` 2행이다. 방어 DP+현재 HP의 절반 내림, 공격 AP의 포함 경계, 실제 전투 계산에 사용되는 DP/HP 시점을 원문과 테스트에서 대조한다.
