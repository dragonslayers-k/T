# DB29 RequireSoul 831장 독립 원본 조인 및 통합 검증 — 5차 결과

## 검증 경로
GitHub Actions run `42366008132`에서 다음 자료를 서로 독립적으로 대조했다.

1. 원본 DB29 Release `fm1-carddb-29/cards.jsonl.gz` — 15,350개 카드 원본
2. run `42357466809`의 831장 이미지 증거 artifact
3. modern/legacy 레일 판독 CSV와 하이브리드 전체 시퀀스 판독 CSV

원본 Release JSONL에서 카드 ID와 `RequireSoul` 문자열을 다시 읽어 831개 대상 카드와 조인하고, 4자리 토큰 분할·순서·수량을 비교했다.

## 결과

| 검증 항목 | 결과 |
|---|---:|
| 원본 DB29 카드 레코드 | 15,350 |
| 대상 카드 | 831 |
| 원본 ID 중복 | 0 |
| 원본 RequireSoul 문자열 일치 | 831/831 |
| 토큰 순서·코드·수량 일치 | 831/831 |
| 시각 검증까지 완료 | 830/831 |
| 시각 증거 미확정 | 1 |

원본 DB29 조인은 `source_join_complete=true`로 통과했다. 831장 전부 원본 ID, 원문 RequireSoul, 토큰 배열이 정확히 일치했다.

### 시각 검증 세부
- BONUS/NCS/중립 779장: modern 593 + legacy 185 = 778장 표식 수량 정확 일치.
- 하이브리드 52장: 51장 자동 템플릿 일치 + 1장 수동 이미지 확인. 후속 속성/중립 표식 수량은 52장 모두 일치.
- 전체 830장 시각 확인, 1장 시각 확인 보류. 전체 확인률 99.88%.

## 유일한 보류 카드

- `10091525191` 피어스그렘린
- 원본 DB29 RequireSoul: `21028301`
- 이미지 증거: large/small 모두 100×142, 좌측 RequireSoul 레일이 없는 축소 이미지
- 독립 원본 조인: ID 일치, RequireSoul 문자열 일치, 토큰 배열 일치
- 판정: 원본 데이터는 정상 확인. 시각 증거만 부족하므로 시각 확인 보류.

이 카드를 원본 데이터 오류로 처리하거나 임의로 수량을 보정하지 않는다.

## 산출물
- `DB29_RequireSoul_831_integrated_visual_source_audit.csv`: 831장 통합 결과. 원본 조인과 시각 판정이 한 행에 결합됨.
- `require-soul-source-join-audit.csv`: DB29 원본 15,350행과 831장 대상의 독립 조인 상세
- `require-soul-source-join-summary.json`: 원본 조인 집계
- 시각 검수 상세: `require-soul-rail-card-audit.csv`, `require-soul-hybrid-orb-audit.csv`

## 다음 단계
1. `10091525191`의 원본 사이트 고해상도 이미지 URL 또는 별도 원본 이미지 아카이브를 복구한다.
2. 해당 이미지에 레일이 실제로 존재하지 않는 카드 템플릿인지 확인한다. 원본 디자인에 표식이 없다면 그 템플릿을 별도 판독 규칙으로 기록한다.
3. 831장 통합 검증표와 원본 DB29 조인 결과를 최종 기준 자료로 보존한다.
4. 그 이후에만 RequireSoul 코드의 의미 매핑/런타임 적용안을 별도 검토한다.

## 보호 경계
DB29 원본 Release/tag, Android 앱 저장소, 기존 PR #9는 수정·병합·리베이스하지 않았다. 연구 브랜치에 검수 코드·workflow·보고서만 추가했다.
