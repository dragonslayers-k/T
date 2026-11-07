# RequireSoul NCS / MU / BONUS — Manual crosswalk adjudication — 2026-11-06

## 판정 요약

현재 CardDB 작업 브랜치에서는 RequireSoul NCS(82)를 Manual의 '무속성' 지불 규칙에 연결한다. MU(81)는 별도 enum으로 유지하고, BONUS(83)는 여전히 의미 검토 대상으로 둔다. 따라서 NCS와 MU를 같은 enum으로 취급하지 않는다.

## 원문과 enum의 구분

- Manual.zip의 soulcost.htm은 '무속성' 비용의 동작을 설명한다: 어떤 속성으로든 지불 가능하며, 해당 규칙은 무속성 유닛의 소울 비용에 적용된다. 유닛의 소환/유지 비용 적용 범위도 구분한다.
- Manual의 추출 텍스트 자체에는 영문 enum 문자열 NCS, MU, BONUS가 직접 등장하지 않는다.
- Firestore liveappsetting/enumtable의 Enum+RequireSoul은 MU=81 (/mu.webp), NCS=82 (/ncs.webp), BONUS=83 (/bonus.webp)를 별도 값으로 정의한다.
- 따라서 Manual의 의미 설명과 Firestore enum을 연결하는 작업은 원문에 적힌 문자열의 단순 동일성 주장이 아니라, 프로젝트의 enum-to-manual crosswalk다.

## 현재 프로젝트 crosswalk

| RequireSoul | 현재 처리 | 근거/상태 |
|---|---|---|
| MU=81 | neutral enum으로 별도 보존 | NCS와 동일 enum으로 합치지 않음 |
| NCS=82 | Manual의 '무속성' 규칙에 매핑 | soul_costs.py의 manual_semantics_verified; 앱 후보 지불은 neutral로 변환하되 원본 special token은 보존 |
| BONUS=83 | semantic_review 유지 | Manual의 무속성 규칙으로 자동 매핑하지 않음 |
| 14개 pair enum | mapping_review 유지 | 양쪽 색 후보는 보존하되 지불 규칙은 미확정 |

이 판정은 Manual의 '무속성' 동작을 NCS 토큰에 연결한 현재 프로젝트 결정이다. Manual 텍스트가 NCS라는 약어를 직접 정의한다고 과장하지 않는다. NCS/MU의 icon-level 대응 근거는 enumtable의 icon path와 Manual 이미지 crosswalk를 함께 보존해야 하며, MU와 NCS의 raw identity는 계속 분리한다.

## 전수 audit 반영

- T Actions #647 / run 42165013581: success.
- 현재 branch rebuild의 semantic_review=439, hybrid_mapping_review=52, cost_review_provenance_rows=491.
- NCS를 Manual 무속성 규칙에 매핑한 결과, NCS 351건은 review queue에서 빠지고 BONUS 439건과 hybrid 52건이 남는다.
- unresolved_cost_rows=0은 모든 카드에 비용 provenance row가 존재한다는 뜻이며, 남은 491건의 의미가 해결됐다는 뜻이 아니다.
- 이 결과는 현재 T 브랜치의 후보 SQLite 재생성 결과다. DB29 fm1-carddb-29 release를 변경하지 않았고, DB30을 발행하지 않았다.
- APK PR #28은 불변 DB29 release를 사용하므로, APK #258에서 보이는 831개 비용 review provenance는 이전 release 상태다. T branch의 491개는 새 후보 재생성 결과이며 서로 다른 버전의 수치다.

## APK 경계

APK PR #28의 현재 DB29 import는 불변 DB29 release를 사용한다. APK helper의 fail-closed gate는 기존 DB29의 mapping/semantic review를 실행 비용으로 승격하지 않는다. 새 T branch crosswalk를 APK로 가져오려면 별도 새 release 승인 절차가 필요하다. 현재는 DB29를 덮어쓰거나 DB30을 발행하지 않는다.


## SUPERSEDED — 2026-11-07

The earlier adjudication that mapped RequireSoul NCS(82) to the Manual's colorless bead and recurring upkeep is withdrawn. The Manual text does not name NCS; the enumtable distinguishes MU(81), NCS(82), and BONUS(83). The updated decision is in `docs/MANUAL_MAPPING.md`. NCS(82) now remains semantic_review and is not assigned upkeep. MU(81) is the inferred Manual-neutral crosswalk candidate pending icon-level verification.