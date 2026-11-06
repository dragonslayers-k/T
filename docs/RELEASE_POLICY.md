# FM1 카드DB 불변 Release 정책

## 기준 구조

- 원본 수집 및 정규화 SQLite의 유일한 기준 저장소는 `dragonslayers-k/T`다.
- Android 앱 저장소는 T Release를 소비하며 별도의 카드DB 크롤러나 비용 해석기를 운영하지 않는다.
- 현재 검증된 원본 스냅샷은 `fm1-carddb-27`이다. 이 Release는 수정하지 않는다.
- 정규화 DB v2, 카드별 효과 후보/절 구간, 이미지/URL 검증 결과를 포함한 새 배포본은 `fm1-carddb-28`로 한 번 발행한다.

## Release 발행 조건

Release는 일반 코드 push, 테스트, 수동 DB 감사만으로 생성하지 않는다.

하나의 의도적인 통합 커밋에 아래 두 표식을 모두 포함할 때만 기존 `carddb.yml`이 전체 감사를 실행하고 새 Release를 발행한다.

- `[full-db-audit]`: 기존 불변 Release를 입력으로 15,350장, 55개 필드, URL, 30,700개 WebP, 비용/효과 후보, SQLite 무결성을 다시 검사한다.
- `[publish-db-release]`: 전체 감사가 성공한 경우에만 `fm1-carddb-28`을 새 태그로 생성한다.

워크플로우는 추가하지 않는다. `carddb.yml` 하나가 테스트, 수동 전체 감사, 수동 수집, 조건부 Release 발행을 담당한다. Release 태그가 이미 존재하면 발행을 중단한다.

## Release 28 산출물

- `fm1_cards.sqlite.gz`: 정규화 SQLite DB v2
- `sqlite-build-summary.json`: DB 통계, 검증 결과, 원본/압축 SQLite 및 기타 자산 SHA-256
- `cards.jsonl.gz`, `enumtable.json`, `appsettings.json`
- `images.tar.gz.part-aa` (필요 시 추가 파트)
- 카드 분류/필드 감사, 이미지 감사, 원본 비용 검토 상태, 효과 후보 요약

APK 저장소는 Release 28에서 SQLite/enum/image archive와 summary를 받아 SHA-256 및 SQLite 무결성을 재검사한다. 카드 상세 URL, 원본 이미지 URL/해시, 비용 검토 상태, 효과 후보 원문 위치를 변환 결과에도 보존한다.

## 검증 경계

혼합 비용 `mapping_review`, NCS/BONUS `semantic_review`, 자동 효과 텍스트 `pattern_candidate`는 미확정 상태 그대로 보존한다. 이를 무료 비용 또는 실행 가능한 카드 효과로 승격하지 않는다.
