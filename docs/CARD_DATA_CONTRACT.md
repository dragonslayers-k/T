# 카드 데이터 계약 (초기)

## 원본 필드 보존
각 카드 레코드의 `id`, `name`, `type`, `faction`, `category`, `text`, `description`, `artImage`, `thumbnail`, `largeImage`, `tabs`는 출처 데이터의 의미를 보존한다. 정규화 결과가 원본 값을 덮어쓰지 않도록 한다.

## 미상과 명시적 0
- `cost: {}` 및 `costKnown: false`는 비용 미상이다. 무료 카드로 간주하지 않는다.
- 명시적 숫자 0은 유효한 값이며 미상과 구분한다.
- 지형 `requiredLP`도 명시적 0, 값 누락, 파싱 실패를 구별한다.
- 빈 문자열/빈 객체를 자동으로 0으로 치환하지 않는다.

## 추적성
추출/검증 데이터는 카드 ID로 연결하고, 각 필드에 가능한 한 다음을 둔다.
- `source`, `sourceTab`, `sourceText`
- `verificationStatus`, `verifiedBy`, `verifiedAt`
- `evidence` 또는 원본 이미지 참조

## 유형
현재 데이터팩에서 확인되는 유형: `land`, `unit`, `item`, `spell`, `enchant`.
새 유형은 원본에 근거가 있을 때만 추가한다. 실제 제공 JSON의 지형 유형값은 `land`다.
