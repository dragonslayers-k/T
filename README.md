# Fantasy Masters 1 — Card Database Rebuild

**목표: fmlunatic.com의 카드 15,350장 전수 DB화**

이 저장소는 과거 크롤링 산출물이나 기존 앱 구현을 데이터 기준으로 사용하지 않고, 현재 사이트의 실제 데이터 구조를 조사해 새로 구축하는 FM1 카드DB 프로젝트다.

## 확인된 원본 구조
- 카드 목록: https://fmlunatic.com/cardlist
- 공개 Firestore 프로젝트: `fmdb-bcb70`
- 카드 컬렉션: `livecardlist`
- 분류 사전: `liveappsetting/enumtable`
- 원본 집계: 15,350개 문서
- 카드 문서 ID는 개별 카드 URL `https://fmlunatic.com/card/{documentId}`에 사용된다.
- 이미지 원본은 Firebase Storage / Google Cloud Storage의 소형·대형 WebP 파일이다.

## 새 수집 방법
브라우저에서 사이트를 직접 실행해 데이터 흐름과 UI를 조사한 뒤, 사이트가 실제 사용하는 Firestore 문서와 enum 분류표를 수집한다. 목록 UI의 30개씩 더 보기 동작에 의존하지 않고 Firestore의 안정적인 문서 정렬·커서 조회로 전체 15,350장을 페이지 단위로 수집한다.

## 주요 파일
- `docs/SITE_SCHEMA.md`: 사이트의 실제 데이터 구조, 필드 인벤토리, 이미지·개별 URL 규칙
- `docs/MANUAL_MAPPING.md`: Dropbox Manual.zip과 현재 사이트 분류표의 대응 및 미확정 사항
- `docs/DATABASE_CONTRACT.md`: SQLite 테이블과 원본 보존 원칙
- `scripts/probe.mjs`: 브라우저/Firestore/UI 구조 탐색
- `scripts/crawl.mjs`: Firestore 카드 문서 15,350장 수집
- `scripts/download_images.mjs`: 카드별 소형·대형 원본 이미지 다운로드
- `scripts/build_db.py`: SQLite 정규화, enum 매핑, 소울 비용 토큰 분석
- `scripts/audit_db.py`: 카드·URL·필드·이미지 완전성 검사
- `.github/workflows/carddb.yml`: GitHub Actions 자동 구축

## 데이터 원칙
1. 목표 카드 수 15,350장. 일부 수집으로 완료 판정하지 않는다.
2. 모든 원본 필드는 JSON 원문으로 보존하고, 정규화 값은 별도 필드로 저장한다.
3. 카드별 개별 원본 URL과 이미지 원본 URL을 저장한다.
4. 사이트 enum 값과 Manual.zip 의미를 연결하되, 매뉴얼에 없는 값은 추정하지 않는다.
5. 숫자 0과 미상/누락을 구분한다.
6. 소울 비용의 원본 코드·토큰·해석 상태를 모두 보존한다.
7. 이미지 누락과 판독 미확정 카드를 숨기지 않고 감사 보고서에 집계한다.

## 실행
GitHub Actions → **Card DB pipeline**에서 실행한다. `probe`는 사이트 구조 확인, `crawl`은 전체 카드·이미지·SQLite 구축이다.

완료 산출물은 SQLite, 원본 카드 JSONL, enum 사전, 이미지 파일팩, 감사 보고서로 구성한다. 감사에서 15,350장과 이미지 30,700개가 모두 확인되기 전에는 완성본으로 표시하지 않는다.
