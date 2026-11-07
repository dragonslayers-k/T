# FM-OFFLINE 게임 플레이 우선 데이터 완성 정책
- 기준일: 2026-11-06 (KST)
- 적용 저장소: `dragonslayers-k/T` (CardDB), `dragonslayers-k/FM-OFFLINE` (Android runtime)
- 상위 기준: 통합 마스터 총괄본 v4.9, 부록 29
- 적용 범위: DB29 15,350장 전체 및 모든 비용/Skill/effect/status runtime clause

## 1. 최상위 목표

원본 사이트, 원본 DB/Firestore, 카드 이미지, Manual.zip, 기존 보고서, 나무위키/namu.moe, 커뮤니티/공략, 외부 웹 검색을 교차 조사한다. 그래도 확인되지 않는 필드와 효과는 다른 카드·동일 계열·동일 기술/효과 템플릿·카드 유형/속성/레벨/등급/종족·DB 분포·규칙 제약을 분석해 가장 타당한 추정값을 반드시 보완한다.

**원본 근거가 부족하다는 이유만으로 카드 데이터를 삭제하거나 덱 편성을 막지 않는다. 다만 필수 소환/사용 비용의 의미가 불명확하면, 임의 결제로 카드를 내보내지 말고 해당 카드 사용을 차단한다.**

## 2. 엄격히 분리할 두 축

- 원작 의미 검증: `source_verified`, `pending_source_review`, `semantic_pending`, `non_executable` 등 provenance/review 메타데이터.
- 게임 진행 가능성: 카드의 필수 runtime profile 및 effect disposition이 존재하고 실제 엔진에서 action이 완료되는지.

Provenance가 pending/non_executable이라는 표지만으로 카드 선택이나 덱 편성을 막지 않는다. 단, 필수 RequireSoul 비용 자체가 NCS/BONUS/하이브리드/미상/누락/오류 상태라면 합법적인 지불 규칙이 확인될 때까지 해당 카드의 실제 사용은 차단한다. source-review gate와 payment-legality gate를 구분한다.

## 3. Runtime 값 선택

원본 테이블은 수정하지 않는다. 별도 overlay로 다음을 보존한다.

- `source_value`: 원본 그대로
- `normalized_value`: 원본 의미를 확인한 정규화 값
- `inferred_value`: 카드DB 분석으로 도출한 추정값
- `runtime_value`: 엔진에서 실제 사용하는 값
- `fallback_value`: 안전한 단일 추정이 불가능할 때의 결정적 대체값

우선순위: source-verified → 테스트를 통과한 high-confidence inference → 보수적으로 제한한 medium/low inference → deterministic fallback.

추정값마다 카드 ID/필드 또는 clause ID, inference method, 참조 카드 ID, evidence refs, confidence, 선택 이유/배제 대안, runtime policy/limit, diagnostic tag, ruleset version, test ID를 남긴다.

## 4. 필수 필드 및 효과 처리

- 필수 runtime field는 15,350장 모두 null/blank가 아니어야 한다. 원본 누락은 inferred/fallback layer로 채운다.
- 비용 미확정은 무료(0)나 임의의 중립 소울 결제로 처리하지 않는다. 원본 토큰과 후보 해석을 보존하고, 의미가 확인될 때까지 해당 카드 사용을 차단한다. 검증된 순수 속성 비용, 명시적 무비용, 추정 상태가 분명한 MU(81) 후보 대응만 런타임 지불 프로필을 받는다.
- 모든 효과 clause는 `implemented_verified`, `implemented_inferred`, `fallback_noop`, `not_applicable` 중 하나로 최종 disposition한다.
- 효과를 안전하게 추정할 수 있으면 보수적 handler를 적용한다. 해석 불가능하면 해당 clause만 `fallback_noop`으로 종료 처리한다.
- 효과 no-op은 비용이 별도로 확인된 카드에 한해 카드 기본 action을 정상 처리하고 effect resolution을 닫아 턴 진행을 계속한다. 필수 비용이 미확정인 카드는 no-op 효과를 이유로 지불 검증을 우회하지 않는다.
- 즉사, 무한 반복, 무제한 자원, 확정 승리 같은 강한 효과는 명시적 근거 없이 추정하지 않는다.

## 5. E663-0014 용의위압 7개 카드의 적용 판정

대상 detail IDs: `15093028105`–`15093028111` (네투라, 네하트라, 네파다하, 이미피브, 카디지크, 루와다하, 시메트라).

현재 원본 상태 정의/효과 본문을 확보하지 못했으므로 [용의위압]의 구체적인 수치·대상·지속·해제 효과를 창작하지 않는다. 해당 clause의 source review 상태는 pending으로 유지하되 runtime disposition은 `fallback_noop`이다. 이 상태 문구만을 이유로 카드 전체를 사용 불가로 처리해서는 안 된다. 다른 효과 clause는 독립적으로 판정한다.

## 6. 완료 게이트

1. 15,350장 전부 runtime profile 존재.
2. 필수 runtime field null/blank 0.
3. 모든 effect clause에 네 가지 disposition 중 하나가 배정됨.
4. provenance pending만으로 카드가 deck builder에서 제외되지 않음. 단, 미확정 필수 비용은 action legality에서 차단되고 별도 집계됨.
5. 추정 비용 지불, 소환, 장착, 마법/인챈트, unsupported effect no-op, 대상 없음, 수치 경계, 상태 만료, 턴 종료, 승패 판정의 고정 seed 테스트 통과.
6. unsupported effect가 action/match deadlock을 만들지 않음.
7. source-verified coverage와 inferred/fallback runtime coverage를 별도 보고.

## 7. 다음 실행 작업

- T와 APK에서 `pending`, `non_executable`, `mapping_review`, `semantic_review`가 카드 사용/덱 구성/턴 진행을 막는 모든 gate를 inventory한다.
- provenance와 playability를 분리하는 source-first runtime resolver 및 data-pack contract를 구현/검증한다.
- DB29 전체 필수 runtime field 및 미처리 effect clause를 카드 ID 단위로 산출한다.
- 기존 추정 adjudication은 재사용하고, 누락된 부분만 batch overlay로 보완한다.
- focused tests → APK data-pack contract → fixed-seed game scenario 순으로 검증한다.
- DB29/Release 29 보존, DB30 미발행, PR 병합 금지 승인 게이트는 그대로 유지한다.

## 8. 해석 우선순위

이 정책은 과거 review note의 `pending_source_review` / `non_executable` 표현을 원작 의미 검증 상태로 한정한다. 이를 카드 전체의 런타임 사용 차단으로 해석하는 문구와 충돌하면 본 정책과 통합 마스터 v4.9 부록 29를 우선 적용한다.

## 9. 구현 데이터 계약 및 Android 연결

상세 필드 계약은 같은 브랜치의 `docs/RUNTIME_PROFILE_CONTRACT_2026-11-06.md`를 따른다. 특히 다음 경계를 고정한다.

- `sourceRequireSoul` / `candidateCost`는 원본·후보 의미를 보존하고, `runtimeCost`는 엔진 허용 키(`dark/fire/water/forest/metal/earth/light/neutral`)만 사용한다.
- RequireSoul MU(81)만 Manual 무속성 구슬의 추정 대응으로 any-color 결제와 유닛 한정 반복 유지비를 받는다. NCS(82)와 BONUS(83)는 범용 결제가 아니며, 의미가 확인될 때까지 카드 사용을 차단한다.
- 하이브리드/미상/누락/오류 비용은 중립 fallback을 부여하지 않고 차단한다. 원본 비용 문자열과 후보 토큰은 보존한다.
- 모든 effect candidate clause는 별도 `runtimeDisposition`을 갖는다. 카드별 검증 handler가 없는 clause는 `fallback_noop`으로 종료하고, 원본 후보 텍스트/구간은 수정하지 않는다.
- APK pack validator는 15,350장의 runtime cost와 8,633 유닛의 유한 upkeep, 48,281 effect clause의 terminal disposition, 카드별 runtime action readiness를 검사한다. source-verified coverage는 별도로 집계한다.
- DB29/DB30/PR 병합 승인 경계는 기존과 동일하다.


## 2026-11-07 — RequireSoul 비용 차단 정책 정정

이 부록은 본 문서의 기존 '모든 카드가 지불 가능한 비용을 가져야 한다', '미확정 비용은 보수적 중립 fallback' 문구와 Section 9의 NCS/BONUS 범용 결제 문구를 대체한다.

- 데이터 보존/덱 편성과 실제 카드 사용 가능성은 구분한다. 모든 15,350장 원본 카드는 보존하지만, 비용 의미가 불명확한 카드는 플레이를 허용하지 않는다.
- RequireSoul 81(MU)은 Manual의 무속성 구슬에 대한 추정 crosswalk다. 지불은 어떤 생성 소울로도 가능하며 유닛에만 같은 수량의 매턴 유지비를 적용한다. 아이콘 시각 대조가 끝날 때까지 inferred로 표시한다.
- RequireSoul 82(NCS), 83(BONUS), 하이브리드 코드, unknown/missing/invalid는 비용을 만들어내지 않고 차단한다.
- EarnSoul 82(MU02)는 지형 생산 토큰으로 중립 소울 2개를 뜻하며 RequireSoul 82(NCS)와 다른 enum이다. 사용자가 설명한 N/C/S(82) 스탯 표기도 제3의 별도 표기다.
- 최신 DB29 runtime inventory: 원본 카드 15,350장, 지불 프로필 14,519장, 의미 검토 차단 831장. 차단 831장은 삭제/변환 실패가 아니라 의도적인 안전 차단이다.
