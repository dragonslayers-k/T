# Skill2 레이셜디펜스 35행 원문·APK 경계 교차감사 — 2026-11-06

## 기준
- T `feat/carddb-effect-semantic-pass`, 변경 전 HEAD `c60fd8aed19933aea08431959f8cb7be9f9915c9`
- 불변 DB `fm1-carddb-29`
- 원문 source: Actions #573 / run `41970905894`, artifact `13388874560`
- APK: `feat/combat-event-foundation` HEAD `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e`, PR #28 open/draft
- 보고서만 추가. DB29/원본/매핑/APK 코드 변경 없음.

## DB29 원문 집계

| 항목 | 수량 |
|---|---:|
| 후보 행 / 고유 카드 ID | 35 / 35 |
| Skill2 enum | 44 |
| 실제 `additional_text` 발췌 | 35 |
| 원문 변형 | 2 |
| excerpt 누락 | 0 |
| source-verified / executable | 0 / 0 |

| 행 수 | 원문 |
|---:|---|
| 30 | `방어시, 자신을 제외한 자신과 동일한 종족의 필드 유닛 수 만큼 받는 데미지 감소.` |
| 5 | `방어시, 자신을 제외한 아군 필드 유닛 중 자신과 동일한 종족을 가진 유닛 수 만큼 자신이 받는 데미지를 감소시킨다.` |
| **35** | **합계** |

두 문구는 자기 자신 제외, 같은 종족, 아군 필드 유닛 수에 따른 방어 피해 감소를 설명한다. 원문은 카드별로 보존하고 문구를 합쳐 덮어쓰지 않는다.

## APK crosswalk

구현은 `rules.js`의 `skill2_racial_defense`이며, 방어 유닛의 `race`를 기준으로 같은 소유자의 다른 유닛 중 정확히 같은 종족 문자열을 가진 수를 계산한다. 자기 자신과 적군은 제외하며 방어자의 종족이 비어 있으면 0을 반환한다. 실행은 source-verified/card-source/implemented의 정확한 metadata tuple에서만 허용된다.

확인된 관련 테스트:
1. `source Skill2 Racial Defense reduces damage by each other field unit with the same race`
2. `production Racial Defense counts only other matching friendly field units and ignores missing or enemy races`
3. `production Racial Defense gives no reduction when the defender has no race`
4. `production defensive handlers ignore inferred Racial Defense mappings`

테스트 helper가 source-verified tuple을 직접 주입하므로 DB29 35개 카드의 source verification을 입증하지 않는다.

## 미해결 경계

- 모든 35행은 `inferred` 상태다. 원문 excerpt가 있어도 매핑 승격 근거로 충분하지 않다.
- 현재 구현은 `race` 문자열의 정확 일치를 사용한다. 실제 DB29 normalized card에서 종족이 별칭/복수값/공백 포함 값으로 나타나는지 확인이 필요하다.
- 피해 감소량이 계산된 피해보다 클 때 음수 피해를 방지하는 그룹 전용 경계 테스트가 명시적으로 확인되지 않았다. 공통 피해 clamp와 연결한 검증이 필요하다.
- 방어 시점의 종족/필드 상태 스냅샷 타이밍은 원문에 상세히 정의되어 있지 않다.
- 종족과 소속은 별도 필드다. 얼라이디펜스와 같은 규칙으로 통합하지 않는다.

## 판정
- 35/35 카드에 카드별 효과 원문 발췌 존재.
- 변형 2개 보존.
- APK handler 및 관련 테스트 4개 확인.
- source-verified 0, executable 0.
- DB29 불변, DB30 미발행, PR 미병합.

## 다음
다음 그룹은 `격노` 20행이다. 실제 HP 손실, 생존 조건, AP 갱신 시점의 원문·엔진 테스트 정합성을 독립 확인한다.
