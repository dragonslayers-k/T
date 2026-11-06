# 전수 수집 방법

## 1. 이전 방식과의 차이
이전 크롤링 산출물은 참고 자료로만 취급한다. 현재 수집기는 사이트를 Chromium으로 실행해 Firestore와 Storage 사용 구조를 확인한 뒤, 원본 Firestore 문서를 직접 수집한다. 카드목록 DOM에 렌더링된 30장만 반복해서 긁는 구조가 아니다.

## 2. 실제 확인된 엔드포인트와 데이터
- Firestore project: `fmdb-bcb70`
- 카드 컬렉션: `livecardlist`
- 분류/이미지 경로 사전: `liveappsetting/enumtable`
- count aggregation: 15,350
- 정렬: `NumID DESC`, 문서명 보조 정렬
- query page size: 50
- expected pages: 307
- 카드별 원본 URL: `https://fmlunatic.com/card/{documentId}`

## 3. 수집 절차
1. Firestore aggregation으로 원본 문서 수를 확인한다. 15,350이 아니면 중지한다.
2. `liveappsetting/enumtable` 전체를 수집하고 원본 배열/맵 구조를 보존한다.
3. `livecardlist`를 50개씩 커서 조회한다.
4. 문서 ID 중복, 카드명 누락, 페이지별 첫/마지막 ID를 감사한다.
5. 각 문서의 모든 필드를 JSONL 원본에 기록한다.
6. Category enum의 ImageSmall/ImageLarge/ImagePrefix와 KIND로 소형·대형 WebP URL을 구성한다.
7. 카드별 소형·대형 이미지를 다운로드하고 HTTP 상태, 크기, SHA-256을 기록한다.
8. SQLite에 원본·정규화 필드·텍스트·비용 토큰·이미지·taxonomy를 구축한다.
9. 15,350장 및 30,700개 이미지 완전성을 감사한다.

## 4. 실패 복구
Firestore 조회는 재시도/지수 백오프를 적용한다. 이미지 다운로드는 카드 ID와 크기별로 실패를 기록한다. 실패한 이미지는 성공으로 계산하지 않는다. 원본 JSONL과 페이지 감사 자료를 기준으로 다시 실행할 수 있다.

## 5. 완료 판정
카드 수 15,350, 중복 ID 0, 이름 누락 0, 개별 URL 누락 0, 소형/대형 이미지 각 15,350개 다운로드 성공, SQLite 참조 무결성 통과가 필요하다. 소울 비용의 미확정 831장은 숨기지 않고 검토 대상으로 남기며, 이것은 카드 원본 수집 누락과 구분한다.
