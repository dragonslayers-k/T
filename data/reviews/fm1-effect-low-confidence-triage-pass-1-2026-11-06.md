# DB29 low-confidence effect triage — pass 1 — 2026-11-06

## 범위와 수치

Source: T Actions #647 / run 42165013581, semantic-review artifact.

- 카드: 15,350장
- effect clause rows: 48,281
- interpretation rows: 48,281
- missing interpretation rows: 0
- low-confidence interpretation rows: 1,249
- normalized unique text patterns: 716
- low-confidence classes: 656 unparsed effect text, 593 conditional/reference candidates

주의: semantic_completeness_pass=true 및 missing=0은 모든 clause에 interpretation record가 존재한다는 coverage 검사다. 1,249건의 실제 의미가 확정되었거나 APK에서 실행 가능하다는 뜻이 아니다.

## 반복 패턴 1차 분류

### A. FAQ·설명·참조 메타데이터 — 실행 규칙으로 승격 금지
- FAQ의 아이템빌드업 참고 (9건; 예: 10102041206 차원의열쇠, 10102041207 차원의파편, 10110341208 악마의뿔피리)
- 해당 아이템은 1차 강화능력을 보유하고 있습니다. (6건)
- 자세한 사항은 FAQ를 참고하세요. (6건)
- 이 문구는 카드 텍스트와 출처를 보존하되 그 자체를 handler로 만들지 않는다.

### B. 상태 이름 참조 — status catalogue 대조 필요
- [영혼지배]상태 (9건)
- [용의위압] 상태 (7건)
- 하급에카마엘상태 (6건)
- 제물상태 관련 문구 (여러 건)
- 이름만으로 지속시간, 중첩, 제거 시점, 행동 제한을 추정하지 않는다. Manual 상태 정의와 기존 APK status primitive를 대조한 뒤 개별 assertion을 만든다.

### C. 조건부 실행 문장 — 우선순위 P1
- 핸드에 같은 이름의 유닛이 없거나, 발동 후 해당 유닛의 AP/HP가 0 이하가 되는 경우 효과 없음 (7건)
- 6턴 이상 또는 0턴이면 효과 없음 (7건)
- 필드 빈 공간 수에 따라 유닛/상태가 달라지는 분기 (6건 이상)
- 이들은 실제 조건식 후보지만, 조건 평가 시점, 대상 소유자, 현재/발동 후 AP·HP, 턴 경계의 포함 여부를 원문별로 확인해야 한다.

### D. 대상/스탯 범위 문구 — 우선순위 P1/P2
- 아이템:DP, 유닛/인챈트:HP, 지형/마법:AP 같은 타입별 스탯 참조
- 만능 : 중급 강화 상태(+2/+1/+2) 같은 stat bundle
- 카드 타입별 대상 선택과 스탯 변경을 분리해 구조화한다. 이름만 보고 모든 카드 타입에 같은 스탯을 적용하지 않는다.

### E. 이름 목록·아이템/유닛 roster — card ID crosswalk 필요
- 금-유리가면, 물-지혜의투구, 불-트리플스피어, 빛-영광의망토, 숲-플로라의반지, 암-속임수의반지, 대지-대지의건틀렛 (각 8~9건)
- 어린마왕/어린릭시아/어린조각가 등 색상별 유닛 목록, 로드 계열, 유대 목록
- 이는 대상 또는 참고 목록이지 독립적인 실행 효과가 아니다. DB29 card ID와 해당 아이템/유닛 원문을 연결한 뒤 대상 조건으로만 사용한다.

### F. 원문 손상/불완전 — source recovery 필요
- 말줄임표 단독/말줄임 구간 (8건)
- 원본 카드 이미지/HTML에서 누락된 앞뒤 문장을 복구하기 전까지 해석하지 않는다.

## 다음 조사 순서

1. P1: 상태 이름과 조건부 실행 문장을 카드 ID별 원문 전체 문맥으로 재대조.
2. P1: 타입별 스탯/빈 슬롯/턴 경계 조건을 Manual 문구와 연결.
3. P2: 이름 목록을 실제 카드 ID로 crosswalk.
4. P3: FAQ/설명 메타데이터와 flavor text를 effect handler 후보에서 분리하되 원문 필드는 보존.
5. P4: 말줄임/손상 원문은 이미지·HTML 재확보 후 재평가.

## 구현 승인 게이트

효과 handler를 추가하기 전에 카드 ID, 원문 URL, 전체 source excerpt, 대상 범위, trigger/timing, duration, stack/replace, cost interaction, confidence, executable status를 모두 기록한다. 하나라도 불명확하면 review-only로 남긴다. 이 pass에서는 APK 코드를 변경하지 않는다.
