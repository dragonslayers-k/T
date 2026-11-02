# 카드 데이터베이스 계약 v2

## 저장 원칙
- Firestore 문서의 전체 원본 필드는 `cards.raw_payload_json` 및 `data/raw/cards.jsonl`에 보존한다.
- 정규화 값은 `card_fields.normalized_value`에 별도로 저장한다.
- 원본 코드/텍스트/HTML을 정규화 값으로 덮어쓰지 않는다.
- ID는 Firestore 문서 ID를 사용하며 `KIND`는 이미지 번호로만 사용한다.
- 상세 URL은 사이트 라우트에서 확인한 `/card/{documentId}` 패턴을 저장한다.

## SQLite 테이블
| 테이블 | 내용 |
|---|---|
| cards | 카드 ID, 이름, 분류, 속성, 개별 URL, 원본 JSON, 해시 |
| card_fields | 55개 원본 필드와 정규화 표시값 |
| card_texts | TextBase/TextExtra 원문 및 검색용 plain text |
| card_costs | LP 값, RequireSoul 원문, 파싱 결과, 확정 여부 |
| card_soul_cost_tokens | RequireSoul 4자리 토큰별 코드·수량·아이콘·해석 상태 |
| card_images | 소형/대형 이미지 URL, 로컬 경로, 크기, SHA-256, 다운로드 상태 |
| card_effects | 기본 효과 텍스트와 발동/지속 관련 데이터 |
| source_pages | 카드 목록 및 개별 상세 페이지 URL |
| taxonomy | Firestore enumtable의 원본 분류값과 표시 이름 |
| verification | 카드/필드 단위 검증 근거 및 상태 |

## 값 표현
- 미상/누락은 NULL, 명시적 숫자 0은 0.
- LP 0은 유효한 값이다.
- RequireSoul 원본 문자열과 토큰별 해석을 함께 보존한다.
- 색상/무속성/무비용 코드가 확인된 경우에만 해당 색상으로 합산한다.
- 혼합 속성/NCS/BONUS 등 매뉴얼 의미가 불확실한 토큰은 원본 코드와 아이콘을 보존하고 manual_review로 표시한다.
- 모든 enum 값은 원본 튜플/객체와 표시 이름을 함께 보존한다.

## 검증 상태
`extracted_unverified`, `enum_mapped`, `manual_semantics_verified`, `image_verified`, `manual_review`, `manual_uncovered`.
원본 데이터 수집 성공은 카드 효과 구현 완료나 이미지 수동 검증 완료를 의미하지 않는다.

## 완료 기준
1. 고유 카드 15,350장.
2. 카드명/ID/목록 URL/개별 URL 완전성.
3. 55개 원본 필드와 enum 사전 보존.
4. 소형·대형 이미지 각 15,350개 다운로드 및 해시 확인.
5. SQLite의 카드·필드·텍스트·비용·토큰·이미지·taxonomy 참조 무결성.
6. 미확정 비용/매뉴얼 공백은 별도 수량으로 공개.
