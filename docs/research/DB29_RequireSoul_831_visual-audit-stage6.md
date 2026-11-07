# DB29 RequireSoul — 최종 이미지 원본 복구 결과 (6차)

## 피어스그렘린 10091525191 원본 이미지 확인

미확정 카드의 DB29 원본 레코드에서 원본 이미지 URL을 추출하고 GitHub Actions 러너에서 직접 다운로드했다.

| 항목 | 결과 |
|---|---|
| 카드 ID / 이름 | `10091525191` / 피어스그렘린 |
| DB29 RequireSoul | `21028301` |
| 원본 large URL | `https://storage.googleapis.com/fmdb-bcb70.appspot.com/cardlist/unit/large/05/U05191L.webp` |
| 원본 small URL | `https://storage.googleapis.com/fmdb-bcb70.appspot.com/cardlist/unit/small/05/U05191S.webp` |
| large / small 크기 | 둘 다 100×142 |
| 바이트 크기 | 둘 다 4,192 |
| SHA-256 | `fcffedfde8335f1a4a84901248efe62c2d4ca9479193a3ad67b7461f379af1cc` |
| 이미지 내용 | 구형 축소 카드 이미지. Modern/Legacy 레일 템플릿에 해당하는 좌측 RequireSoul 표식 레일이 없음 |

원본 사이트 페이지는 React SPA shell만 반환했으나, 페이지 JavaScript 번들에서 Firebase Storage 경로 규칙을 확인했고, DB29 원본 레코드에 보존된 `source_image_urls`에서 실제 large/small 주소를 확보했다. 두 주소를 직접 다운로드한 결과 기존 이미지 아카이브의 100×142 파일과 바이트 크기 및 SHA-256이 동일했다. 따라서 더 큰 원본 이미지가 누락된 것이 아니라, 원본 사이트가 제공하는 이미지 자체가 100×142 축소본임을 확인했다.

## 최종 831장 검증 상태

| 범위 | 카드 수 | 판정 |
|---|---:|---|
| BONUS/NCS/중립 | 779 | 778장 표식 수량 정확 일치, 피어스그렘린 1장 원본 이미지에 레일 없음 |
| 하이브리드 | 52 | 51장 자동 일치 + 1장 수동 시각 확인, 전체 시퀀스 일치 |
| DB29 원본 조인 | 831 | 카드 ID·RequireSoul 문자열·토큰 순서·수량 831장 전부 일치 |

따라서 DB29 원본 데이터 정합성은 831/831 확인됐다. 이미지에서 표식 개수까지 확인된 것은 830장이다. 나머지 한 장은 원본 이미지에 레일이 없으므로 시각 계수 불가이며, 데이터 불일치로 보지 않는다.

## 최종 판정과 후속 처리

- `10091525191`은 원본 RequireSoul 데이터 오류가 아니다.
- 별도 이미지 프레임/축소 템플릿으로 기록하고, 레일 기반 표식 계수에서는 시각 증거 미적용으로 유지한다.
- 이 카드의 토큰 의미를 임의로 수정하거나 이미지에 없는 표식을 상상해 채우지 않는다.
- 시각 감사와 독립 원본 조인이 완료됐으므로 다음 별도 작업은 14개 하이브리드 코드 및 NCS/BONUS/중립 코드의 의미 매핑 후보를 정리하는 단계다. 의미 매핑은 이번 검증과 별개이며, 승인 전 DB29나 런타임에 반영하지 않는다.

## 실행 기록
- 최종 원본 이미지 조사 run: https://github.com/dragonslayers-k/T/actions/runs/42366550043
- 최종 원본 조인 run: https://github.com/dragonslayers-k/T/actions/runs/42366008132
- 연구 브랜치: `research/require-soul-visual-audit-831-stage1`
- DB29 태그/Release, 앱 저장소, PR #9: 변경·병합·리베이스 없음.
