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


## 10. 지형 설치 소울과 생산 소울의 정규화

SQLite는 지형의 `RequireLP` 및 `RequireSoul` 설치 조건과 `EarnSoulList` 생산 규칙을 분리한다. `card_costs`에는 LP와 설치 소울 비용이 저장되고, `card_land_production`에는 카드별 생산 결과·MagicLand 표시·MuSoul 대조 결과가 저장된다. 개별 생산 토큰은 `card_soul_production_tokens`에 원문 토큰, enum 코드·심볼·아이콘, 정규화 생산량과 판독 상태를 보존한다.

`EarnSoulList`의 2색 심볼은 각 색상 1개씩, `ALL`은 7개 속성 소울 각 1개씩, `MU01/MU02/MU03`은 무소울 1/2/3개씩 생산한다. `SPELL`은 MagicLand 효과 표시이며 일반 소울 생산량으로 계산하지 않는다. MagicLand는 50장 모두 별도 유형 효과 구현 대상으로 관리한다. 각 일반 지형의 정규화 무소울 생산량은 `MuSoul` 원본값과 대조한다.
