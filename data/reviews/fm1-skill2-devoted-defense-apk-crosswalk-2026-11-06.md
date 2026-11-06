# Skill2 헌신방어 66행 원문·APK 경계 교차감사 — 2026-11-06

## 1. 기준 및 보호 경계

- CardDB 저장소: `dragonslayers-k/T`
- 기준 브랜치: `feat/carddb-effect-semantic-pass`
- 변경 전 HEAD: `77b7a2ac81d37d987ede5466278fa2a1bc3b2f9c`
- 불변 데이터 기준: `fm1-carddb-29`
- 원문 검토 산출물: T Actions #573 / run `41970905894`
- 원문 검토 artifact: `13388874560`, `gap-reports/skill2-execution-review.jsonl`
- artifact에 기록된 분석 checkout SHA: `049a6623ae5caeacc1cf3fe7f3761d587abe801e`
- APK 비교 브랜치 HEAD: `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e` (PR #28, open/draft)
- 본 작업은 보고서만 추가한다. DB29/Release 29, 카드 원본, 매핑 상태, APK 실행 규칙은 변경하지 않는다.

## 2. 66행 전수 재집계

`skill2-execution-review.jsonl`에서 `source_name=헌신방어`인 66행을 다시 집계했다.

| 분류 | 행 수 | 판정 |
|---|---:|---|
| 실제 `additional_text` 효과 원문 보유 | 63 | 카드별 발췌 보존 |
| 카드별 효과 원문 미확보 | 3 | 별도 미해결 유지 |
| 합계 | 66 | Skill2 후보 행 |
| 고유 `additional_text` 효과 문구 | 6 | 공백/마침표 차이도 원문 그대로 보존 |
| `source_card_verified` 승격 | 0 | 변경 금지 |
| `executable` 승격 | 0 | 변경 금지 |

### 2.1 여섯 개 실제 효과 원문 변형

| 행 수 | 원문 |
|---:|---|
| 45 | `자신 파괴시 아군 필드 다음 유닛 공방체 +1` |
| 12 | `자신 파괴시 아군 필드 다음 유닛 공방체 +1.` |
| 3 | `자신 파괴시 아군 필드 다음 유닛 공방체+1` |
| 1 | `자신 파괴시 아군필드 다음 유닛 공방체 +1` |
| 1 | `자신 파괴시, 아군 필드 다음 유닛의 AP/DP/HP를 1 증가시킨다.` |
| 1 | `자신 파괴시 아군 다음 유닛 공방체 +1` |
| **63** | **합계** |

원문 변형을 하나의 canonical 문장으로 덮어쓰지 않는다. 특히 마지막 변형은 `필드`라는 단어가 빠져 있으므로 다른 다섯 변형과 동일한 위치 범위를 자동 확정하지 않는다.

### 2.2 효과 증거에서 제외한 보조 문구

다음 두 카드에는 Skill2 라벨과 연결된 `card_text` 서술이 추가로 존재하지만, 이는 실제 발동 효과 문구가 아니다. 두 카드 모두 별도의 `additional_text` 효과 원문도 있으므로 후보 행 자체를 제외하지 않고, 해당 보조 문구만 효과 증거에서 제외한다.

- `11050441261` 기사영예훈장 — 기술부여 설명은 훈장/기사의 서사 문구
- `11110241311` 발키리실드 — 기술부여 설명은 방패/발키리의 서사 문구

`card_text` 설명을 헌신방어의 동작·대상·수치·지속시간을 입증하는 자료로 사용하지 않는다.

## 3. 원문 발췌가 없는 3개 카드

| 카드 ID | 카드명 | DB29 필드 관찰 | 현재 처분 |
|---|---|---|---|
| `14031227302` | 순수한레비 | `TextBase`는 원본 빈 값. `TextExtra`는 원본 필드가 존재하지만 Skill2 효과 발췌는 미확보 | pending |
| `16110228578` | 설원고양이 | `TextBase`, `TextExtra` 모두 원본 빈 값 | pending |
| `16112328609` | 어둠기사 | `TextBase`는 원본 빈 값. `TextExtra`는 원본 필드가 존재하지만 Skill2 효과 발췌는 미확보 | pending |

카드 상세 URL:

- https://fmlunatic.com/card/14031227302
- https://fmlunatic.com/card/16110228578
- https://fmlunatic.com/card/16112328609

이번 조사에서 원본 상세 페이지는 웹 조회 도구로 열리지 않았다. 따라서 새 excerpt를 만들어 넣거나 이웃 카드의 문구를 복사하지 않았다. 다음 복구 시도는 보존된 원본 payload/이전 수집 스냅샷 및 원본 페이지 재조회로 한정한다. 원문이 끝내 없으면 `card_source_excerpt_missing` 상태를 유지한다.

## 4. APK 엔진·테스트 교차검토

비교 대상 APK:

- 저장소: `dragonslayers-k/FM-OFFLINE`
- 브랜치: `feat/combat-event-foundation`
- HEAD: `a8b7eeacc39f8be29cd54f1a42d4e44dbfa7153e`
- PR #28: open/draft/unmerged
- 구현: `app/src/main/assets/game/rules.js`
- 테스트: `tests/rules.test.cjs`

### 4.1 현재 handler 동작

- `skill2_devoted_defense`는 `unit_destroyed` 이벤트를 받는다.
- 파괴된 카드의 `fieldIndex` 뒤에 있는 생존 아군 중 물리 슬롯 번호가 가장 작은 유닛을 선택한다.
- 대상이 없으면 `next_friendly_unit_missing`으로 효과를 적용하지 않는다.
- 대상의 AP/DP/HP에 각각 +1을 임시 스탯으로 더한다.
- Skill2 handler는 `source_card_verified` + `card_source` + `source-card-rule-implemented`의 정확한 메타데이터 조합에서만 실행되도록 등록돼 있다.

### 4.2 관련 회귀 테스트

현재 APK 테스트 파일에서 헌신방어 관련 테스트명 13개를 확인했다. 주요 검증 범위는 다음과 같다.

- 공격자/방어자 전투 중 파괴 이벤트 뒤 다음 공격 전에 효과 처리
- 배열 삽입 순서와 실제 슬롯 순서가 달라도 물리적 다음 슬롯 선택
- 마지막 물리 슬롯에서 앞쪽 생존 유닛으로 wrap하지 않음
- 다음 준비 단계에서 임시 AP/DP/HP 보너스 만료
- 마법 피해로 파괴된 경우에도 이벤트 큐를 통해 처리
- 파괴된 슬롯 바로 다음 위치 및 다음 유닛 부재 경계
- source-authorized 메타데이터만 dispatcher에서 허용

이는 APK 내부 handler/fixture 테스트의 존재와 범위를 확인한 것이다. 테스트 helper가 `source_card_verified` 메타데이터를 직접 구성하므로 DB29의 실제 66개 카드 매핑이 검증되거나 실행 가능하다는 뜻은 아니다.

## 5. 아직 닫히지 않은 의미 경계

원문 6개 변형과 현재 APK 테스트를 대조해도 다음은 원문만으로 확정되지 않는다.

1. “다음”이 항상 파괴된 물리 슬롯보다 큰 슬롯 번호 중 가장 가까운 유닛을 뜻하는지, 빈 슬롯/필드 압축 시점이 어떻게 적용되는지
2. `필드` 표현이 빠진 1행도 같은 물리 슬롯 기준인지
3. AP/DP/HP +1의 지속시간이 전투 종료까지인지, 다음 준비 단계까지인지
4. HP +1이 현재 HP와 최대 HP에 각각 어떻게 반영되는지, 임시 HP가 피해를 받은 경우 만료 시 현재 HP가 어떻게 조정되는지
5. 파괴 이벤트가 연쇄적으로 발생할 때 각 이벤트가 원래 슬롯 스냅샷을 사용하는지

현재 테스트는 일부 경계를 구현 관점에서 고정하고 있지만, 효과 원문은 지속시간/HP 만료 규칙을 직접 말하지 않는다. 그러므로 이 부분은 source adjudication이 완료되기 전까지 후보 규칙으로 남긴다.

## 6. 판정 및 다음 단계

- 66행 중 63행은 카드별 `additional_text` 발췌가 존재한다.
- 3행은 카드별 효과 발췌가 없다.
- 효과 원문 변형은 6개이며 원문을 그대로 보존한다.
- 현재 APK에는 헌신방어 handler와 13개 관련 테스트가 있으나, 실제 DB29 66개 카드의 매핑은 모두 inferred 상태다.
- 본 교차감사로 `source_card_verified` 또는 `executable`로 승격한 카드는 0장이다.
- DB29 불변, DB30 미발행, T PR #9/#12 및 APK PR #28/#26/#25/#9 미병합.

### 다음 정확한 작업

1. 누락 3개 카드의 원본 payload/이전 snapshot에서 카드별 설명을 재확인한다. 원문이 없으면 미확보 상태를 유지한다.
2. APK 헌신방어 테스트에서 물리 슬롯 중간 공백, 일부 유닛의 `slotIndex` 누락/혼재, 임시 HP 만료 경계를 별도 테스트로 검토한다.
3. 원문에 없는 지속시간/HP 처리 가정은 원작 근거를 찾기 전까지 카드별 mapping 승인에 사용하지 않는다.
4. 다음 Skill2 그룹으로 넘어갈 때도 66행과 같은 방식으로 원문·테스트·미확정 범위를 분리한다.
