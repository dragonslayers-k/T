# 데이터베이스 계약 v1

## 1. 정체성 및 완전성
- 대상: FM Lunatic 카드 목록 `https://fmlunatic.com/cardlist`
- 목표: 정확히 15,350개의 고유 카드 레코드.
- 기본 키: 원본의 안정적인 카드 ID. ID가 없으면 원본 상세 URL에서 유도한 임시 키를 쓰되 `id_quality=derived`로 표시한다.
- 이름만 같은 카드는 합치지 않는다. ID가 다르면 별도 카드다.

## 2. 원본 보존
카드마다 `raw_payload_json`, `source_list_url`, `source_card_url`, `source_image_url`, `source_thumbnail_url`, `source_large_image_url`, `source_collected_at`, `source_http_status`, `source_content_hash`를 보존한다.
원본 페이지가 없는 경우에도 목록 URL은 저장하고, 상세 URL 상태를 `not_found` 등으로 명시한다. 주소를 만들어내지 않는다.

## 3. 정규화 테이블
- cards: ID, 이름, 카드 종류, 속성, 에피소드, 상세 URL 상태, 원본 JSON
- card_fields: 사이트/매뉴얼에서 발견한 모든 분류·속성의 key, 원본 값, 정규화 값, 원본 표기, 출처
- card_texts: 설명, 카드 텍스트, 플레버 텍스트 등 텍스트 원문
- card_costs: LP 및 속성별 소울 비용. 미상과 명시적 0을 구분
- card_images: 원본 이미지 주소, 로컬 경로, MIME, 바이트, SHA-256, 이미지 종류
- card_effects: 효과 원문 및 추후 구조화할 발동 시점/대상/조건/지속시간
- source_pages: 카드별 원본 페이지와 페이지 수집 기록
- taxonomy: 실제 발견된 필드명·값 및 매뉴얼 대응 상태
- verification: 카드/필드 단위 검증 상태, 근거, 검증자, 시각

## 4. 값 표현
- 원본 값은 문자열/숫자/배열/객체 형태를 그대로 JSON으로 보존한다.
- 숫자 0은 0, 누락/미상은 NULL.
- 비용 판독 실패는 0으로 대체하지 않는다.
- 정규화는 별도 열에 저장하고 원본 값을 덮어쓰지 않는다.
- 분류 코드가 확정되지 않은 경우 `unmapped` 상태로 남긴다.

## 5. 검증 상태
`discovered`, `extracted_unverified`, `source_verified`, `image_verified`, `manual_verified`, `missing`, `parse_failed`.
검증 상태는 카드 전체와 필드 각각에 부여한다.

## 6. 완료 기준
1. 고유 카드 수 15,350.
2. 중복 ID 0, 카드명 누락 0.
3. 모든 카드에 확인된 원본 목록 URL, 개별 상세 URL 또는 명시적인 상세 URL 부재 사유.
4. 이미지 URL/로컬 이미지 여부를 카드별로 명시.
5. 상세 페이지에서 관찰된 필드가 하나도 버려지지 않고 원본/정규화 필드에 보존.
6. SQLite FK/유일성 검사 통과.
7. 감사 보고서에서 누락·실패·미검증 수량을 공개.
8. 단순 수집 성공과 매뉴얼 대조 검증 완료를 별도 집계.
