# Skill2 강한헌신방어 28행 원문·APK 경계 교차감사 — 2026-11-06

## 1. 기준 및 범위

- 저장소/브랜치: `dragonslayers-k/T` / `feat/carddb-effect-semantic-pass`
- 변경 전 HEAD: `b3a0677c7b26ee6c360b247e23dc9f2e15575107`
- DB 기준: 불변 `fm1-carddb-29`
- 원문 evidence source: T Actions #573 / run `41970905894`, artifact `13388874560`
- 분석 artifact checkout SHA: `049a6623ae5caeacc1cf3fe7f3761d587abe801e`
- APK 비교 HEAD: `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e` (PR #28, open/draft)
- 본 문서는 검토 산출물만 추가하며 DB29/카드 원본/매핑/런타임을 변경하지 않는다.

## 2. DB29 원문 후보 28행 재집계

`skill2-execution-review.jsonl`에서 `source_name=강한헌신방어`를 필터링한 결과:

| 항목 | 수량 |
|---|---:|
| 후보 카드 행 | 28 |
| 고유 카드 ID | 28 |
| Skill2 원본 enum | 3 |
| 카드별 `additional_text` 효과 발췌 | 28 |
| 실제 효과 원문 변형 | 2 |
| `source_card_verified` | 0 |
| `executable` | 0 |

### 원문 변형

| 행 수 | 원문 |
|---:|---|
| 21 | `자신 파괴시, 아군 필드 유닛 전체의 공방체가 1증가한다.` |
| 7 | `자신 파괴시, 아군 필드 유닛 전체의 공방체를 1씩 증가시킨다.` |
| **28** | **합계** |

두 문구 모두 파괴 시점, 아군 필드 유닛 전체, 공·방·체 각각 +1을 표현한다. 조사 산출물의 28행은 모두 실제 `additional_text` 근거가 연결되어 있다. 문장 차이는 원문 그대로 보존한다.

모든 카드 매핑은 `inferred`이며 `card_source_excerpt_available_pending_semantic_review` 상태다. 원문이 있다는 사실만으로 카드별 source-verified 승격이나 실행 승격을 하지 않는다.

## 3. APK handler와 테스트 교차검토

### 3.1 구현 위치와 동작

- 구현: `app/src/main/assets/game/rules.js`
- 테스트: `tests/rules.test.cjs`
- Rule ID: `skill2_strong_devoted_defense`
- 이벤트: `unit_destroyed`
- handler는 파괴된 유닛이 제거된 뒤 남은 `owner.units` 전체를 순회하며 AP/DP/HP에 각각 +1 임시 스탯을 적용한다.
- 남은 아군 유닛이 없으면 `no_remaining_friendly_units`로 효과를 적용하지 않는다.
- dispatcher 등록 메타데이터는 `source_card_verified` + `card_source` + `source-card-rule-implemented`이며, inferred 카드에는 fail-closed로 실행되지 않는다.

### 3.2 현재 확인된 관련 테스트 3개

1. `source Skill2 Strong Devoted Defense buffs every surviving friendly field unit when destroyed`
   - 파괴 후 생존한 두 아군 유닛의 AP/DP/HP 증가를 검사한다.
2. `production dispatcher applies Strong Devoted Defense to all survivors`
   - 실제 전투 경로와 event queue에서 생존 유닛 전체에 임시 보너스가 적용되는지 검사한다.
3. `production Strong Devoted Defense buffs only surviving friendly field units and excludes enemy units`
   - 생존 아군은 증가하고 적군은 변하지 않는지 검사한다.

이 테스트들은 synthetic helper가 source-verified 메타데이터를 직접 주입한다. DB29의 실제 28개 카드 행이 importer/normalized runtime까지 source-verified로 이어진다는 증거는 아니다.

## 4. 아직 원문만으로 확정되지 않은 사항

- 효과가 전투 중 임시인지, 다음 준비 단계까지인지, 혹은 더 오래 지속되는지 원문 두 문구에는 지속시간이 없다.
- HP +1이 현재 HP/최대 HP에 어떤 방식으로 적용되고 만료 시 어떻게 정리되는지 원문은 말하지 않는다.
- 파괴 이벤트 직후 필드에서 제거된 본인 카드가 대상에서 제외된다는 해석은 현재 엔진의 이벤트 순서와 테스트에 기반한 구현 결정이다. 원문만으로 세부 이벤트 순서를 설명하지 않는다.
- 생존 아군이 0명인 경우의 무효과 처리 및 연쇄 파괴 이벤트는 별도 source adjudication이 필요하다.

따라서 현재 handler/테스트는 구현 후보의 동작을 고정하지만, 지속시간/HP 처리에 관한 카드별 원문 승인을 대체하지 않는다.

## 5. 판정 및 다음 작업

- 28/28 카드에 실제 효과 원문이 존재한다.
- 2개 원문 변형은 서로 다른 문장으로 보존한다.
- APK에는 handler와 관련 테스트 3개가 있다.
- source-verified 승격 0, executable 승격 0.
- DB29 불변, DB30 미발행, T PR #9/#12 및 APK PR #28/#26/#25/#9 미병합.

### 다음 순서

1. 다음 Skill2 그룹 `얼라이디펜스` 44행의 원문 변형/테스트 경계를 같은 방식으로 교차검토한다.
2. 8개 Skill2 각 그룹의 실제 source rows와 APK 테스트 fixture가 분리돼 있음을 유지한다.
3. 지속시간/임시 HP 의미는 원작 자료가 추가 확보될 때까지 미확정으로 둔다.
