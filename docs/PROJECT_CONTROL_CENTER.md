> **최신 정책 우선 공지 — OPS-003 / 2026-11-06**  
> 이 문서는 v4.9 이전에 작성된 일부 상태·표현을 포함한다. 아래 **OPS-003 최신 기준점**이 과거의 충돌하는 문구를 명시적으로 대체한다. 최신 통합 마스터는 Library의 `FM-OFFLINE_통합_마스터_총괄본_2026-11-06_v4.9.md`이며, 특히 부록 29의 게임 플레이 우선 정책을 적용한다.  
> 중요: `pending_source_review`, `semantic_pending`, `non_executable`은 출처/검토 상태일 뿐 카드 전체 사용을 차단하지 않는다. 합리적 추정 runtime handler를 우선 적용하고, 추정 불가한 효과 clause만 deterministic fallback/no-op으로 종료한다. 비용·기본 행동·턴 진행은 반드시 완료되어야 한다.  
> DB29는 운영상 보존 대상이며 API의 `immutable=false`가 확인된 적이 있으므로 기술적으로 잠금되었다고 표현하지 않는다. DB30 발행 및 지정 PR 병합은 별도 명시 승인 전 금지한다.

# FM-OFFLINE / CardDB 프로젝트 통합 운영 기준점

- 기준일: 2026-11-06 (KST)
- 문서 역할: 대화가 바뀌어도 작업 상태·승인 경계·검증 이력을 반복 확인하지 않도록 하는 **단일 운영 기준점**
- 대상 저장소:
  - 카드DB: https://github.com/dragonslayers-k/T
  - Android 앱: https://github.com/dragonslayers-k/FM-OFFLINE
- 상위 기술·규칙 문서: 각 저장소의 기존 상세 문서와 `FM-OFFLINE 통합 마스터 총괄본 v4.9`. 이 문서는 상세 설계를 복제하지 않고, 현재 작업 포인터와 운영 규칙을 관리한다.

> 이 문서의 GitHub 기본 브랜치 최신본이 대화 기억보다 우선한다. 단, 실시간 상태는 매 작업 시작 시 GitHub API에서 SHA/PR/Actions를 다시 확인한다. 문서의 스냅샷은 갱신 시점 이후 자동으로 최신이라고 간주하지 않는다.

---

## 1. 변경 불가 승인 경계

| 항목 | 현재 결정 |
|---|---|
| DB29 | 기존 `fm1-carddb-29` 기준선 보존. 내용·태그 덮어쓰기 금지 |
| DB30 | 사용자 명시 승인 전 발행 금지 |
| T PR #9 | 병합 금지. 사용자 승인 전 Open 유지 |
| T PR #12 | 병합 금지. PR #9 종속 Draft로 유지 |
| APK PR #28 | 병합 금지. 사용자 승인 전 Open 유지 |
| APK PR #26 / #25 / #9 | 병합 금지. 각각 독립 검토 전까지 Open 유지 |
| 기능 작업 | DB 완성 우선 원칙 유지. DB 검증에 필요한 APK 소비자 측 변경만 예외 |
| 데이터 해석 | 원본값은 보존하고 source pending을 유지하되, runtime에는 근거 기반 추정 또는 deterministic fallback을 반드시 적용. pending/non_executable만으로 카드 사용을 차단하지 않음 |

DB29 Release API의 `immutable` 속성은 2026-11-06 조회 시 `false`였다. 따라서 DB29 불변성은 현재 **운영 정책**으로 지키고 있으며 GitHub Release 설정 차원의 기술적 잠금이 확인된 상태는 아니다. 태그/릴리스 덮어쓰기 금지는 계속 적용한다.

## 2. 현재 저장소 스냅샷

### 2.1 카드DB 저장소 — T

| 구분 | 기준 |
|---|---|
| main | `af2d8af5e6a0126a9b7d8c7973561916e718e9d9` |
| PR #9 | Open / `feat/carddb-effect-semantic-pass` / HEAD `abc39b0a9fd47abb4ddc6206894bdf4c60e05d53` |
| PR #9 최근 CI | Actions #660 성공, run ID `42169246867`, 위 HEAD SHA와 일치 |
| PR #12 | Open · Draft / `docs/external-reference-source-guide-2026-11-05` / HEAD `2845872c8f4cfd29cb5fa4bfc520510d09b7f5c0` |
| PR #12 종속성 | base가 PR #9 작업 브랜치 `feat/carddb-effect-semantic-pass`의 과거 SHA `f2ba6161859c3e21c27e340438933927cedf6b51`를 가리킴. PR #9 최신 HEAD와 차이가 있으므로 독립 병합 가능한 PR로 취급하지 말 것 |
| DB Release | `fm1-carddb-29`, tag target `7e2736ac49133409e7f8051ce90e21bcdeb0472e` |
| 최근 전체 감사 참고 | Actions #446은 2026-11-04의 과거 감사 결과. 이후 PR #9에서 추가 변경이 있었으므로 #446 수치를 현재 최종치로 재사용하지 말 것 |

PR #9의 본 작업 범위는 15,350장, 원본 55개 필드, 효과 절, 30,700개 이미지, 비용·기술·효과 의미 검증이다. PR 설명에 적힌 특정 감사 번호/잔여 수치는 해당 감사 SHA의 결과로만 인용한다. 최신 전체 감사가 다시 실행되기 전에는 이전 집계값을 최신 결과처럼 보고하지 않는다.

### 2.2 Android 앱 저장소 — FM-OFFLINE

| 구분 | 기준 |
|---|---|
| main | `8d28ac39ecc493cef40167c2c30dafa43db43f0e` |
| PR #28 | Open / Draft / `feat/combat-event-foundation` / HEAD `1bf65ab2dc80035a6329b10dd8c3b80dffd78114` |
| PR #28 최근 CI | Actions #260 성공, run ID `42166629234`, 위 HEAD SHA와 일치 |
| PR #26 | Open / `docs/fm1-external-references-2026-11-05` / HEAD `9882d0823712a4e461a69d9f17597a91d7d2bdc9` |
| PR #25 | Open / `fix/review-required-soul-cost-gating` / HEAD `44f7c477d2cb09d1a0724afa6d9faa3b84a655f9` |
| PR #9 | Open / `fix/skill2-ref-raw-metadata` / HEAD `c84a56ec6ae4e7e86d447b127a1c5a84d4cf93b2` |

APK PR #28의 #260 성공은 해당 HEAD에서 수행한 CI 범위의 성공이다. 이를 전체 카드 효과 구현, 모든 규칙 검증 또는 실기기 대전 완성으로 확대 해석하지 않는다. DB29 데이터팩/SQLite/에뮬레이터 검증의 기존 통과 사실도 그 실행 SHA와 범위를 붙여서만 인용한다.

### 2.3 저장소 보호 상태

2026-11-06 조회에서 두 저장소의 `main` 브랜치 모두 GitHub branch protection이 비활성(`protected=false`)이었다. PR 병합 금지와 DB29 보존은 자동 강제되는 기술 설정이 아니라 이 운영 기준서에 따른 승인 규칙이다. 이를 이유로 승인 없는 병합·태그 변경을 해서는 안 된다.

---

## 3. 문서 우선순위 및 정보 충돌 해결

1. **실제 GitHub 현재 상태**: 기본 브랜치 SHA, PR head/base SHA, Actions run 결과, Release/tag 메타데이터.
2. **이 문서의 최신 갱신 항목**: 현재 작업 포인터, 승인 경계, 마지막 완료/차단 작업.
3. **상세 기술 문서**: T의 DB 계약·효과 파이프라인·완료 계획·Release 정책 및 APK의 PROJECT_STATUS/CARD_SCHEMA/RULES_SOURCES.
4. **통합 마스터 총괄본 v4.9 및 과거 대화**: 기술 배경과 결정 이력. 부록 29가 게임 플레이 우선 정책의 최상위 기준이다. GitHub보다 오래된 SHA·상태는 현재값으로 사용하지 않는다.

충돌 시 원본 기록을 삭제하거나 조용히 덮지 않는다. 어떤 문서의 어느 항목이 오래되었는지 이력에 남기고, 최신 상태를 이 문서에 갱신한다.

## 4. 반복 방지 운영 규칙

### 4.1 매 작업 시작 시 수행할 최소 확인

매 대화/작업 재개 시 아래 항목만 확인하고, 이미 확인된 내용을 다시 전수 조사하지 않는다.

1. 이 문서의 최신본과 마지막 작업 로그를 읽는다.
2. 두 저장소의 main SHA, 대상 PR의 head/base SHA, PR 상태를 확인한다.
3. 대상 HEAD SHA의 최신 Actions 결과가 있는지 확인한다.
4. 마지막 성공 SHA와 현재 SHA가 같으면 해당 성공 검증을 재실행하지 않는다.
5. SHA가 바뀌었거나 검증이 실패/누락된 경우에만 변경 영향 범위에 맞는 검증을 선택한다.

### 4.2 Actions 실행 절감

- 동일한 코드 SHA에서 동일 workflow가 성공했으면 같은 검증을 다시 실행하지 않는다.
- 실패 시 재실행 버튼부터 누르지 않는다. 실패 job/step/log에서 최초 실패 원인과 영향을 받은 파일을 확인한다.
- 코드 원인 수정은 한 번의 응집된 변경 묶음으로 처리하고, 수정 후 해당 SHA에서 필요한 workflow를 한 번 실행한다.
- 환경 일시 장애가 확인된 경우에만 동일 SHA 재실행을 허용하며, 재실행 사유를 로그에 남긴다.
- 전체 DB 감사/이미지 전수 검사/Release 검증은 파서·스키마·원본 데이터에 의미 있는 변경이 누적된 뒤 의도적으로 한 번 실행한다. 문서 수정이나 단일 단위 테스트 수정만으로 전체 감사를 실행하지 않는다.
- 경량 테스트, focused review, full audit, APK pack build, emulator smoke는 서로 다른 검증 단계다. 하나의 성공을 다른 단계의 성공으로 간주하지 않는다.

### 4.3 커밋·작업 묶음 관리

- 독립적인 작은 변경을 지나치게 잘게 나누어 연속 커밋/Actions를 발생시키지 않는다.
- 하나의 작업 ID에 목적, 대상 파일/데이터, 완료 기준, 필요한 테스트를 먼저 고정한다.
- 서로 다른 원인·승인 경계·릴리스 영향이 있는 변경은 한 묶음으로 합치지 않는다.
- 커밋 메시지에는 작업 ID 또는 명확한 변경 목적을 넣는다.
- 작업 완료는 “코드 수정”이 아니라 **수정 SHA + 통과한 검증 + 미해결 항목 변화**로 판정한다.

### 4.4 중복 작업 차단

새 작업을 시작하기 전에 작업 로그에서 같은 목적/파일/카드 ID/테스트가 이미 완료되었는지 확인한다. 완료 항목은 다시 구현하지 않고, 현재 SHA에서 유효한지만 확인한다. 재검증이 필요하면 그 이유(기준 SHA 변경, 회귀, 데이터 변경)를 명시한다.

### 4.5 데이터 완성도 판정

- 15,350장·55개 필드·효과 절·이미지 수는 모집단/구조 완전성 지표이지, 의미 해석 완료 지표가 아니다.
- 추출 성공, 후보 생성, 저신뢰 행 0, SQLite 무결성 통과를 의미 검토/엔진 실행 완료로 표현하지 않는다.
- 비용, Skill1, Skill2, 효과, 매뉴얼 충돌, 엔진 검증은 각각 별도 미해결 큐와 완료 게이트로 관리한다.
- 카드 ID·필드·원문·출처·검토 상태·검증 테스트를 연결한다. 값이 불명확하면 빈칸을 완료로 계산하지 말고 pending 상태와 조사 근거를 남긴다.
- APK에서 카드가 표시되는 것과 해당 카드의 비용/기술/효과가 원작대로 실행되는 것은 별도 완료 기준이다.

---

## 5. PR·Release 처리 게이트

### PR 병합 전

1. PR의 최신 head SHA와 base SHA를 기록한다.
2. 전체 변경 파일/삭제 파일/데이터 산출물/워크플로 변경을 확인한다.
3. 종속 PR 여부와 base가 최신 선행 PR HEAD를 가리키는지 확인한다.
4. 해당 SHA의 필수 CI가 성공했는지 확인한다.
5. DB29 불변·미확정 비용/효과 비실행·원본 provenance 보존을 확인한다.
6. 사용자 명시 승인 후에만 병합한다.

### DB30 발행 전

1. DB29를 입력 기준으로 사용하고 DB29 태그/산출물을 수정하지 않는다.
2. 15,350장, 55개 필드, URL, 이미지, 비용, Skill1/Skill2, 효과 원문·절, SQLite integrity/FK를 같은 감사 스냅샷에서 검증한다.
3. 각 미해결 큐가 0이거나, 0이 아닌 항목이 명시적 승인된 보류/비실행 상태로 설명되어야 한다. 단순히 카운트가 줄었다는 이유로 발행하지 않는다.
4. T 전체 감사 성공과 APK 데이터팩 소비자 검증을 별도로 확인한다.
5. 감사 SHA, 결과 요약, 체크섬, 산출물, 승인 기록을 확인한다.
6. 사용자의 DB30 발행 명시 승인을 받은 뒤에만 새 태그를 발행한다.

현재는 위 게이트를 완료한 것으로 간주하지 않는다. 이 문서 생성은 PR 병합이나 DB30 발행 승인이 아니다.

---

## 6. 작업 이력 — Append only

아래에는 작업이 실제로 완료되거나 기준점이 변경된 사실만 추가한다. 과거 항목을 삭제·재작성하지 않는다. 수치가 정정되면 새 항목에서 정정 사유와 근거를 연결한다.

### OPS-001 — 2026-11-06 — 통합 기준점 및 반복 방지 규칙 수립

- 상태: 기준 문서 생성
- T main: `af2d8af5e6a0126a9b7d8c7973561916e718e9d9`
- T PR #9 HEAD: `abc39b0a9fd47abb4ddc6206894bdf4c60e05d53`; Actions #660 성공
- T PR #12 HEAD: `2845872c8f4cfd29cb5fa4bfc520510d09b7f5c0`; PR #9의 과거 branch SHA를 base로 하는 종속 Draft
- APK main: `8d28ac39ecc493cef40167c2c30dafa43db43f0e`
- APK PR #28 HEAD: `1bf65ab2dc80035a6329b10dd8c3b80dffd78114`; Actions #260 성공
- APK PR #26/#25/#9: 모두 Open, 병합 승인 없음
- DB29: tag `fm1-carddb-29` 보존; DB30 미발행
- 수행하지 않은 작업: PR 병합, DB30 발행, 전체 감사 재실행, APK 빌드 재실행
- 다음 작업 원칙: 이 문서의 상태를 재확인한 뒤 미완료 작업 중 가장 영향이 큰 단일 묶음만 진행한다. 완료된 SHA의 검증을 반복하지 않는다.

---

## 7. 다음 작업 선택 기준

운영 기준점이 정착된 다음에는 카드DB 완성 작업으로 복귀한다. 우선순위는 다음과 같다.

1. PR #9 최신 HEAD의 실제 변경/테스트 범위를 확인하고, 이전 감사 결과와 최신 작업분을 혼동하지 않도록 최신 잔여 큐 산출 기준을 확정한다.
2. 전체 감사를 무작정 재실행하지 않고, 최근 변경으로 영향받는 효과/비용/기술 검토 큐를 focused 검증한다.
3. 카드 ID별로 확인 가능한 의미 항목을 실제 출처와 대조하고, 해결된 항목만 상태를 갱신한다.
4. APK는 DB 소비자 검증과 실제 구현 범위를 분리해 필요한 최소 변경만 진행한다.
5. PR 병합 및 DB30 발행은 별도 승인 게이트로 유지한다.

이 문서는 작업을 대신 완료했다고 주장하지 않는다. 다음 대화에서 이 파일을 읽으면 같은 배경 설명부터 다시 시작하지 않고, 최신 SHA 확인과 마지막 미완료 작업부터 이어간다.


## 8. 최신 재개 기준 — 2026-11-06 15:35 KST (OPS-002 적용)

> 이 부록은 OPS-001의 당시 스냅샷을 보존한다. 아래 조회 결과를 기준으로 재개하며, 이후 SHA는 작업 시작 때 다시 확인한다.

### 8.1 확인된 최신 GitHub 포인터

- T main: `75584d92ac4b4812f94d99fbc34f1360ea68eaf7` (통합 운영 기준점 문서 추가 커밋)
- T PR #9: Open, non-draft, HEAD `abc39b0a9fd47abb4ddc6206894bdf4c60e05d53`, base main `af2d8af5e6a0126a9b7d8c7973561916e718e9d9`; Actions #660 / run `42169246867` success on that exact SHA.
- T PR #12: Open, Draft, HEAD `2845872c8f4cfd29cb5fa4bfc520510d09b7f5c0`, base PR #9 historical SHA `f2ba6161859c3e21c27c340438933927cedf6b51`; stacked dependency remains stale; do not merge.
- T main audit #663: run `42173417874`, success on main SHA `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`, source tag `fm1-carddb-29`, publish false. This is **not** a PR #9 HEAD validation.
- APK main: `8d28ac39ecc493cef40167c2c30dafa43db43f0e`.
- APK PR #28: Open, Draft, HEAD `1bf65ab2dc80035a6329b10dd8c3b80dffd78114`, base main above; Actions #260 / run `42166629234` success on exact SHA.
- APK PR #26/#25/#9 remain Open and unmerged; their heads: `9882d0823712a4e461a69d9f17597a91d7d2bdc9`, `44f7c477d2cb09d1a0724afa6d9faa3b84a655f9`, `c84a56ec6ae4e7e86d447b127a1c5a84d4cf93b2` respectively.
- DB29 Release tag target remains `7e2736ac49133409e7f8051ce90e21bcdeb0472e`; GitHub reports `immutable=false`, so immutability remains a strict operational rule. No DB30 publication.

### 8.2 OPS-002 — artifact analysis runtime failure (D-type)

- Incident: run #663 semantic-review ZIP downloaded successfully through the GitHub connector and was materialized as `/mnt/data/files/semantic-review-663.zip` (2,203,104 bytes), but Python/container runtime calls returned `ClientError`. The error is in the analysis runtime access layer; it is not evidence that the artifact is corrupt or that the user must upload it.
- Workaround already used: recover aggregate values from Actions logs/job steps. Counts: 15,350 cards and unique IDs; 613,435 fields / 55 types; 17,407 effect texts; 48,281 effect pattern splits; 0 missing effect interpretations; 1,249 low-confidence interpretations; 0 unmapped skill rows; 30,700/30,700 images checked; 52 hybrid-cost mapping review items; 779 special-semantics review items; 0 FK errors.
- Limits: these aggregate counts do not identify card-level rows and do not prove semantic correctness or game-engine execution. Queues may overlap; do not sum as disjoint.
- Required next permanent improvement: have the workflow emit a compact card-ID JSON/CSV + a concise step-summary/log record, so review can continue without opening the large ZIP in a local runtime. Keep the full artifact as supporting evidence.
- User-request rule: do not ask for the artifact upload or a manual workflow run while connector/API/log/compact-output routes remain available. Request a user action only when a specific permission/input is genuinely missing and every available route is exhausted.

### 8.3 OPS-002 implementation state and next task

- OPS-002 document exists on branch `docs/ops-artifact-access-guard-2026-11-06`; it must be linked from this control center and submitted as a documentation PR. No merge is authorized.
- Next CardDB work: implement compact card-level semantic-review output for the existing review workflow and test it at PR #9's branch SHA. Do not rerun full audit #663, which was main-only.
- Preserve DB29; do not publish DB30; do not merge T PR #9/#12 or APK PR #28/#26/#25/#9.


## 8. OPS-002 incident and live restart checkpoint (2026-11-06 15:35 KST)

This append-only checkpoint supersedes stale state pointers above. Recheck live GitHub SHA at every subsequent resume.

### Live state (GitHub API)
- T main: `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`.
- T PR #9: Open, non-draft, `feat/carddb-effect-semantic-pass` HEAD `abc39b0a9fd47abb4ddc6206894bdf4c60e05d53`, base `af2d8af5e6a0126a9b7d8c7973561916e718e9d9`; latest exact-HEAD CI #660 success (run `42169246867`).
- T PR #12: Open Draft, HEAD `2845872c8f4cfd29cb5fa4bfc520510d09b7f5c0`; base points to historic PR #9 SHA `f2ba6161859c3e21c27c340438933927cedf6b51`, dependency remains unresolved.
- T main audit #663 success (run `42173417874`) was on main SHA `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`, DB29 source, publish false. It is not PR #9 validation. #662 was cancelled.
- APK main: `8d28ac39ecc493cef40167c2c30dafa43db43f0e`. PR #28 Open Draft HEAD `1bf65ab2dc80035a6329b10dd8c3b80dffd78114`, #260 success (run `42166629234`). PR #26/#25/#9 remain Open at `9882d0823712a4e461a69d9f17597a91d7d2bdc9`, `44f7c477d2cb09d1a0724afa6d9faa3b84a655f9`, and `c84a56ec6ae4e7e86d447b1271a5c84d4cf93b2`.
- DB29 tag `fm1-carddb-29` targets `7e2736ac49133409e7f8051ce90e21bcdeb0472e`; API says immutable=false, so preserve by operating policy. No DB30.

### OPS-002 artifact/runtime incident
- Run #663 artifact download succeeded, but the 2.2 MB semantic review ZIP could not be accessed by Python/container (ClientError). Classification: type D, runtime access failure; not evidence of archive corruption.
- Run #663 log-derived counts: 15,350 cards and unique IDs; 613,435 fields / 55 types; 17,407 effect texts; 48,281 effect splits; 0 missing interpretations; 1,249 low-confidence interpretations; 0 unmapped skill rows; 30,700/30,700 images checked; 52 hybrid-cost mapping reviews; 779 special-semantics reviews; 0 FK errors. Review queues may overlap. Counts are structural/log results, not semantic or engine completeness.
- On recurrence, inspect job logs and GitHub API/text first. If row-level output is missing, modify the workflow to emit a compact deterministic JSON/CSV/manifest and print core values in logs. Do not ask the user to upload the same artifact or manually run Actions before exhausting these alternatives.

### Next work pointer
1. Integrate OPS-002 into the control center via this documentation PR (do not merge without user authorization).
2. Continue focused CardDB review on PR #9 HEAD; do not repeat the 492 MiB full audit solely to extract rows.
3. Continue DB29 → card pack → APK importer → normalized runtime lineage checks as a separate unverified task.
4. Keep DB29 preserved, DB30 unpublished, and PR #9/#12/#28/#26/#25/#9 unmerged.



## 9. Correction — APK PR #28 Actions #260 proved DB29 pack lineage (2026-11-06)

The previous checkpoint's next-work pointer said DB29 → pack → APK lineage remained unverified. That statement is superseded by direct inspection of Actions #260 logs (run `42166629234`, APK PR #28 HEAD `1bf65ab2dc80035a6329b10dd8c3b80dffd78114`). This CI actually ran the lineage scripts; do not repeat the same verification unchanged.

Verified by #260:
- Source release: `fm1-carddb-29`; source SQLite summary was checked against the release SHA/checksum and SQLite integrity; 15,350 cards.
- Converter generated `FM1-CardData-v1.3.0.zip`.
- Representative Skill1 pack lineage: `verify-db29-skill1-pack-lineage.py` PASS for 6 source-linked examples.
- All-source Skill1/Skill2 mapping lineage: `verify-db29-skill-mapping-pack-lineage.py` PASS across 15,350 cards; SQLite has 10,381 Skill1 and 10,381 Skill2 rows; 20,762 pack mapping rows matched with enum/source, mapping status, confidence, evidence, authority and rule fields preserved.
- Runtime normalization: `verify-db29-skill1-runtime-normalization.cjs` PASS; 15,350 cards normalized in pages of 250 and six representative records checked for source URL, source Skill1/Skill2, rule metadata, and execution-status isolation.
- Emulator smoke: imported data pack and loaded WebView for 15,350 cards, PASS.

Boundaries:
- This is a valid DB29 source SQLite → Android pack → runtime-normalizer lineage pass at the above CI SHA.
- It does not certify every Skill1/Skill2 semantic behavior or 27-rule source-card-specific engine assertion, nor every battle scenario. Those remain the CardDB/APK semantic coverage workstream.
- APK PR #28 remains open and unmerged; the CI pass does not authorize merging it or issuing DB30.


### 8.4 D형 복구 성공 — #663 artifact 직접 경로

- Artifact ID `13481939094` 재다운로드 시 connector가 `/mnt/data/semantic-review-663-retry.zip`을 생성했고, container `ls` / `unzip -l` / extraction이 성공했다. 앞선 materialize 경로 `/mnt/data/files/semantic-review-663.zip`의 ClientError는 ZIP 손상을 뜻하지 않았다.
- ZIP size 2.2 MiB; expanded size 45,551,502 bytes. `effect-gap-report.jsonl` 1,020,911 bytes, 1,249 rows / 716 normalized patterns.
- First-pass queue labels: FAQ/help 26; named card/item 108; named state/status 16; condition/formula 417; metadata/flavor candidate 19; unclassified semantic candidate 663. These labels are heuristics only; all records remain pending and non-executable.
- Library now has v4.6 master and the detailed JSON triage index `fm1-db29-low-confidence-effect-cluster-triage-663.json`. Continue from these exact records rather than asking the user for the same artifact.
- Next CardDB work: source-grounded adjudication clusters. Do not run full audit #663 again; #663 already passed on main and the current review is card-level data triage, not a rebuild.


---

## OPS-003 — 2026-11-06 — v4.9 게임플레이 우선 정책 및 최신 실행 상태 동기화

### 1) 기준 문서와 최신 대화 반영
- 최신 통합 기준: Library `FM-OFFLINE_통합_마스터_총괄본_2026-11-06_v4.9.md`.
- 사용자가 2026-11-06 재확인한 절대 목표: DB 15,350장 전부 조회·덱 구성·실제 플레이 가능. 원본 자료를 최대한 조사하고도 부족한 필수값은 카드군/유사 카드/규칙/밸런스 기반으로 합리적으로 추정한다.
- 원본값과 추정값은 별도 보존한다: source_value, normalized_value, inferred_value, runtime_value, fallback_value, provenance/evidence/confidence/test IDs.
- 출처 검증 커버리지와 런타임 플레이 가능 커버리지는 별도 지표다. 출처 pending만으로 카드 전체를 선택/덱 구성/사용 불가 처리하지 않는다.
- 필수 런타임 값은 null/blank로 남기지 않는다. 비용을 무조건 0으로 만들지 않고 보수적이며 지불 가능한 카드별 값으로 추정한다.
- 효과는 clause별 implemented_verified / implemented_inferred / fallback_noop / not_applicable 중 하나로 종결한다. 추정이 위험하거나 근거가 부족한 clause만 deterministic no-op 처리하고, 그 외 카드 행동/비용/턴은 정상 종료한다. 즉사·무한루프·무한자원·확정승리 등 과도한 효과를 추정하지 않는다.
- E663-0014 [용의위압] 7개 카드는 상태 메커니즘 근거가 부족하므로 해당 clause만 pending + fallback_noop이며, 카드 자체는 플레이 가능해야 한다.
- 이 정책은 기존 DATABASE_CONTRACT.md의 “근거 확인 전까지 자동 실행하지 않는다” 및 과거 OPS 로그의 “pending/non-executable” 문구와 충돌할 경우 우선한다. 원본 보존/근거 추적 원칙은 계속 유효하다.

### 2) 2026-11-06 실제 GitHub 상태 스냅샷
조회 시점: 2026-11-06 (KST, 실행 시각 기준). 다음 SHA는 점검 당시 확인값이며 이후 실행에서 재조회한다.

| Repository | Ref | SHA / 상태 |
|---|---|---|
| T | main | `75584d92ac4b4812f94d99fbc34f1360ea68eaf7` |
| T | PR #9 | Open; `feat/carddb-effect-semantic-pass`; HEAD `3a4dd713f55e4761f9bc3704eb13e97e47e95fc6`; base main `af2d8af5e6a0126a9b7d8c7973561916e718e9d9` |
| T | PR #13 | Open; `docs/ops-artifact-access-guard-2026-11-06`; HEAD `58e7956ea18a098c985856f903ec5ba87155feae`; base main `75584d92ac4b4812f94d99fbc34f1360ea68eaf7` |
| T | PR #12 | Open / Draft; HEAD `2845872c8f4cfd29cb5fa4bfc520510d09b7f5c0`; base is an older PR #9 branch SHA; treat as dependent, not independently mergeable |
| FM-OFFLINE | main | `8d28ac39ecc493cef40167c2c30dafa43db43f0e` |
| FM-OFFLINE | PR #28 | Open / Draft; `feat/combat-event-foundation`; HEAD `671b73736e4fbbce5f2cd9e2df0ca2dfffb46a75`; base main `8d28ac39ecc493cef40167c2c30dafa43db43f0e` |
| FM-OFFLINE | PR #26/#25/#9 | Open; no merge authorization |

### 3) 최신 검증 결과
- T PR #9 HEAD `3a4dd713...`: Actions #682 / run `42182837792` succeeded. Scope: lightweight regression tests only; not a full DB audit or all-card semantic verification.
- T PR #13 HEAD `58e7956e...`: Actions #675 / run `42179071984` succeeded. Scope: lightweight regression tests only.
- FM-OFFLINE PR #28 HEAD `671b7373...`: Actions #261 / run `42183008394` completed successfully. Confirmed job steps include JavaScript rule tests, Firestore-to-Android converter checks, DB29 SQLite download and Android data ZIP build, Debug APK/optional signed Release APK build, package/signature/ZIP integrity checks, Android emulator install and launch, and artifact uploads.
- #261 artifacts reported: `FantasyMastersOffline-build-output` (670,974 bytes) and `FM1-CardData-v1.3.0-IMPORT-DB29` (406,080,839 bytes). Do not download the 406 MB archive again solely to repeat already completed lineage validation.
- #261 success is tied to PR #28 HEAD above. It does not establish all-card semantic effect completion, fixed-seed match coverage, or real-device acceptance.
- PR #28's earlier audit note inspected code at `1bf65ab2...`; it identified runtime hard gates but did not implement fixes. The audit is a backlog, not a code completion claim.

### 4) DB29 / DB30 / approvals
- DB29 tag `fm1-carddb-29` target observed: `7e2736ac49133409e7f8051ce90e21bcdeb0472e`. Preserve as-is.
- Release API previously reported `immutable=false`; treat protection as operational policy, not a platform-enforced lock.
- DB30 tag and release were both absent (404) at this check.
- No PR merge, DB30 publication, tag mutation, or workflow manual dispatch is authorized by this checkpoint.

### 5) Immediate next implementation work
1. T PR #9: create a versioned per-card runtime overlay contract and builder/validator over the DB29 SQLite source. The overlay must keep source values immutable and materialize card-specific inferred/fallback runtime values for every required field; do not fill all costs with zero or all effects with arbitrary no-ops.
2. Produce separate counts for source-confirmed, inferred, fallback, and still-unresolved runtime fields/effect clauses. Every card must have a terminal playability profile; unresolved provenance may remain.
3. Then update APK adapter/engine to consume the overlay, remove source-review-only play gates, guarantee finite upkeep, and resolve every unsupported effect clause to a terminal no-op without blocking cost/action/turn.
4. Start with focused tests and small representative cohorts; do not repeat successful #261 at the same SHA. Run pack/emulator validation only after a new overlay/data pack exists.
5. Keep DB29 preserved, DB30 unpublished, and all named PRs unmerged pending explicit user approval.

### 6) History and scope note
This append-only correction supersedes outdated status snapshots and conflicting interpretation in earlier sections; it does not delete prior history. The exact numbered conversation range was not exhaustively available as one transcript during this update. The policy is grounded in the latest v4.9 master, accessible recent conversation summary, and the GitHub commits/PR/Actions above; future checkpoints must report missing numbered conversation records rather than claiming full transcript coverage.


---

## OPS-004 — 2026-11-06 — DB29 runtime cost overlay generation completed

### Latest CardDB PR #9 state
- PR #9 remains Open / unmerged on `feat/carddb-effect-semantic-pass`.
- Latest HEAD at this append: `df80ff2448942c3eedb923f27251b0fed8e730fd`.
- Added read-only source inventory and runtime overlay tooling:
  - `scripts/runtime_source_inventory.py`
  - `scripts/build_runtime_cost_overlay.py`
  - `data/reviews/fm1-runtime-profile-source-snapshot-inventory-2026-11-06.md`
- The workflow downloads only the DB29 SQLite source and summary when the commit message contains `runtime-inventory`; it verifies the release checksum and does not run full audit or image downloads.
- Successful final focused run: Actions #703 / run `42186841634`, tested workflow HEAD `bd7dffd2b5db82fe18c59805722a009b04e6978f`. Artifact `fm1-db29-runtime-source-inventory-703`, ID `13488350675`, 601,956 bytes.
- Generated profile summary: 15,350/15,350 card profiles; 14,859 `implemented_verified`; 491 `implemented_inferred`; zero cost-profile fallback rows. This is profile generation only, not APK gameplay completion.
- Intermediate focused-workflow issues were corrected: PR merge SHA versus head SHA marker lookup, card_fields/card_type join, decoder import path, and zero-valued color slots. #701 was a self-test failure; #702 was canceled by the superseding run; #703 passed. No full audit was run and no same-SHA successful run was repeated.

### Source and inference findings
- DB29 `card_costs`: 15,350 rows; RequireSoul present and parsed for 15,350; RequireLP present for all 289 lands.
- Current decoder status: 14,859 cards without review; 439 BONUS semantic-review cards; 52 hybrid mapping-review cards. The old DB29 stored semantic-review count of 779 included 351 NCS tokens that the current parser now classifies as Manual-semantics-verified.
- Runtime overlay: 52 hybrid cards infer both component colors; 439 BONUS cards retain a separate bonus field and use a tagged generic one-time payment inference with no NCS-style recurring upkeep. Source review flags remain preserved.
- **Enum namespaces are distinct:** RequireSoul code 82=NCS, code 83=BONUS; EarnSoul code 82=MU02, code 83=MU03, code 02=SPELL/MagicLand. The land `소원의보름달` with EarnSoulList 8301 is MU03, not BONUS production.
- All 289 lands have RequireLP/RequireSoul/EarnSoulList/MuSoul source fields. 50 MagicLand cards use EarnSoulList 0201 and MuSoul 0; their special effect/playability gate remains unresolved and must not block card installation.
- Unit AP/DP/HP source fields exist for all 8,633 units; item stat fields also exist for 1,748 items. This does not by itself prove their effects are implemented.

### APK state and next task
- APK PR #28 remains Open / Draft at HEAD `671b73736e4fbbce5f2cd9e2df0ca2dfffb46a75`. Actions #261 succeeded at that SHA, including data pack build, Debug APK, emulator install/launch, and artifact upload. It did not consume the newly generated runtime overlay.
- Next implementation: update APK PR #28's pack adapter and rules engine to consume source-separated `runtimeCost`; support BONUS as inferred generic one-time payment without recurring NCS upkeep; keep source review flags for provenance; allow MagicLand installation with only its unresolved effect clause receiving deterministic fallback/no-op. Add focused payment/turn-resolution tests, then one APK pack/emulator run on the new SHA.
- No PR merged, no DB29 mutation, no DB30 tag/release, no APK code changes by this OPS-004 append.


---

## OPS-005 — 2026-11-06 — APK runtime-cost consumer integration in progress

- APK PR #28 remains Open / Draft / unmerged. Current branch HEAD: `2358f2ce75e3178d9c3a960d4ffaa84005f2c98e`.
- Commit `6403e72fe32818d6bfea39cdd268b6c630a3326c` changed:
  - `app/src/main/assets/game/rules.js`: prefer `runtimeCost` when `runtimeCostKnown=true`; accept `bonus` as a cost key; pay BONUS as a generic one-time requirement from the generated colored/neutral pool; keep recurring upkeep limited to `neutral`.
  - `app/src/main/assets/game/card-schema.js`: normalize and retain separate runtime-cost fields.
  - `scripts/fm1-offline/build-firestore-card-pack.py`: preserve source cost review and emit separate runtime cost fields from the DB29 normalized cost row; inferred hybrid/BONUS status remains explicit.
  - `tests/rules.test.cjs`: add a regression proving a source-pending BONUS card can pay its inferred runtime cost without treating it as free.
- Follow-up commit `2358f2c` updates the validation reason string so the pre-existing fail-closed test continues to match its expected Korean diagnostic.
- Actions #262 failed only on that old diagnostic-string assertion. The new runtime BONUS payment test passed; other listed game-rule tests passed. The reason string was corrected.
- Actions #263 / run `42187559110` is still in progress at this append. JavaScript tests and Firestore-to-Android converter passed; DB29 SQLite-to-Android data ZIP generation was still running. Do not claim APK pack or emulator success until this run completes.
- Not yet changed: UI cost label does not yet display the inferred runtime-cost status; 50 MagicLand cards still hit the old special-effect installation gate; enchant candidate-only and other effect gates remain.
- Next focused steps after #263: inspect generated pack manifest/runtime-cost coverage; update the UI to show inferred runtime costs without erasing source-review status; make MagicLand installation playable with its unresolved effect clause receiving deterministic fallback/no-op; then run one final pack/emulator validation.
- No PR merged, no DB29 mutation, no DB30 publication.


---

## OPS-006 — 2026-11-06 — APK runtime-cost validation checkpoint correction

- Correct the OPS-005 in-progress snapshot: APK PR #28 is now at HEAD `988c45282f0c5ae87851c0e2d74a3eb285e69f0f`.
- Actions #263 completed failure because its run used the preceding merge snapshot and still observed the old Korean diagnostic text. The follow-up commit updated that message while retaining fail-closed behavior when neither source cost nor runtime cost exists.
- Actions #264 / run `42187725403` is the current validation run. JavaScript rule tests and Firestore-to-Android converter passed; DB29 SQLite-to-Android data ZIP generation is still in progress at this checkpoint. No APK build/emulator result is available yet.
- Do not rerun #264 or start another workflow while it is active. After completion, inspect the first failing step if any; only continue to APK build/emulator if data-pack generation succeeds.
- The runtimeCost implementation is not merged. Source cost review remains preserved. The UI inferred-cost label and MagicLand fallback are still pending.


---

## OPS-007 — 2026-11-06 — APK runtime-cost pack validator remains the blocker

- APK PR #28 HEAD: `988c45282f0c5ae87851c0e2d74a3eb285e69f0f`.
- Actions #264 / run `42187725403` completed failure. JavaScript tests and Firestore converter passed, including the new BONUS runtime-payment regression. DB29 SQLite was downloaded and the 15,350-card Android pack was generated, but pack validation failed; Android/Gradle/emulator stages were skipped.
- Pack source summary: 15,350 cards; non-land cost review 817; mapping review non-land 38; semantic review non-land 779; land install cost review 0; hybrid mapping review for land installation 14.
- The validator reports 802 cards as `unresolved or review-required soul cost incorrectly accepted`. Root cause is the legacy pack validator still interpreting source review flags as runtime playability blockers, even though the pack now preserves those flags and emits separate `runtimeCost` fields.
- Next change must update the exact validator to check two independent conditions: source review flags and `costKnown` remain honest; `runtimeCostKnown/runtimeCost` are present, valid, and non-free for every profile. Do not delete or suppress source review flags. Then run one focused pack validation and only proceed to Android build/emulator if it passes.
- #264 is not to be rerun. No APK build/emulator success, no PR merge, no DB29 mutation, and no DB30 publication.

---

## OPS-008 — 2026-11-06 — v4.9 runtime profile / playability synchronization

### Governing policy
- The latest Library master is `FM-OFFLINE_통합_마스터_총괄본_2026-11-06_v4.9.md`, Appendix 29. It supersedes older v4.4/v4.8 language in this control center and historical review notes.
- Source verification and runtime playability are separate axes. `pending_source_review`, `semantic_pending`, `non_executable`, mapping review, or semantic review must not by themselves block deck selection, card use, cost payment, basic action completion, or turn progression.
- T's `docs/RUNTIME_PROFILE_CONTRACT_2026-11-06.md` is the field-level data contract. It is present on PR #9's branch; it is not on main until that PR is merged.

### Current CardDB T PR #9 implementation
- PR #9 remains Open / non-draft / unmerged, base main, branch `feat/carddb-effect-semantic-pass`, current HEAD `751af024e9e9880b72a209494be41f7ef1c47720`.
- Commit `fd217a39cabb9d3962f5b77fbf3c6fc576d424f7` fixes the runtime-cost overlay: BONUS is represented as a one-time generic neutral payment while its source identity stays in candidate provenance; NCS is the only special token that contributes unit recurring upkeep.
- Commit `4432162f87c5ada12ba66d558caec3a666ae8ed7` adds self-tests for mixed NCS/BONUS and upkeep separation.
- Commit `8fb9ec7db25674b0e2af0335da5e49142088f448` adds the field-level runtime profile contract.
- Commit `751af024e9e9880b72a209494be41f7ef1c47720` links that contract from the gameplay completion policy.
- No PR #9 Actions run is confirmed for this exact latest SHA in the current check; do not claim its new builder tests passed until a matching run is inspected.

### Current Android FM-OFFLINE PR #28 implementation
- PR #28 remains Open / Draft / unmerged, base main, branch `feat/combat-event-foundation`, current HEAD `8a4def7ad294a0790d44f48db90659b6dcbc3801`.
- Runtime cost resolver, DB29 SQLite converter, finite upkeep, item target fallback, MagicLand install fallback, and paid terminal spell/enchant no-op paths have been changed on this branch.
- The converter now adds a separate `runtimeDisposition=fallback_noop` to each source effect clause while preserving source clause text/spans. The pack validator now requires all 48,281 candidate clauses to have a terminal disposition.
- Pack validator now checks runtime payment profiles for all 15,350 cards separately from source cost review counts. It must not reject a runtime-usable card just because its source cost remains under review.
- Latest Actions #276 / run `42189332608` is running on HEAD `8a4def7...` with JavaScript rule tests and converter tests successful, DB29 pack intentionally skipped, and Debug APK build in progress. This is not the full DB29 pack or emulator gate.
- Earlier full pack run #270 failed with 40 item cards whose parsed condition text remained unmapped. The subsequent schema change assigns those items `fallback_any_unit`; a new full DB29 pack validation is still required. Do not rerun #270 unchanged.

### Verification and safety
- Runtime-cost/source-cost counts, 15,350-card readiness, 8,633 unit upkeep profiles, and 48,281 effect clause dispositions must be reported separately.
- DB29 tag/release/source database remain preserved by operating policy. DB30 is not published. T PR #9/#12/#13 and APK PR #28/#26/#25/#9 remain unmerged.
- Ordinary PR sync should run lightweight tests only. Full DB29 pack and emulator smoke are explicitly gated; perform them once on the final combined HEAD using workflow dispatch inputs or both explicit markers.
- The scheduled baseline-check automation remains read-only. This conversation's explicit development authorization does not grant future scheduled runs permission to edit repositories.

---

## OPS-009 — 2026-11-06 — runtime profile implementation / latest CI pointer

### Canonical policy and automation
- Library master v4.10 is now the latest project baseline. It preserves v4.9 Appendix 29 and adds Appendix 30 with the runtime profile contract, current implementation, verification limits, and next steps.
- The scheduled task prompt was updated after v4.10 publication. It remains daily 15:00 Asia/Seoul and read-only. Its new instructions distinguish the Library master from the saved prompt and do not grant future scheduled runs repository-write authority.

### Current T PR pointers
- PR #9 remains Open/non-draft/unmerged, branch `feat/carddb-effect-semantic-pass`, HEAD `3a2bcd036f5e7c11b1b1b3da2ded39331327614f`, base SHA `af2d8af5e6a0126a9b7d8c7973561916e718e9d9`.
- PR #9 now contains the runtime overlay BONUS/NCS correction, runtime profile contract, gameplay policy link, and overlay self-tests. No Actions success for this exact HEAD is confirmed in the latest connector check. Previous #682/#684 successes apply only to their original SHAs.
- PR #13 remains Open/non-draft/unmerged, branch `docs/ops-artifact-access-guard-2026-11-06`, current branch HEAD before this append `f55799904f46501f10b16433072058a938a1abf4`, base SHA `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`. This base is older than PR #9's base; keep the out-of-date status explicit and synchronize before merge. Main control center is still older; PR-only updates are not main synchronization.

### Current APK PR #28 pointers
- PR #28 remains Open/Draft/unmerged, branch `feat/combat-event-foundation`, latest HEAD before this append `6705c06225d7954ed1ae1a9aafba33b6a5fa3fff`, base main `8d28ac39ecc493cef40167c2c30dafa43db43f0e`.
- Actions #279 / run `42190057320` failed in JavaScript tests only because the newly added NCS test fixture omitted its card `instanceId`; it was a fixture identity issue, not a production resolver failure.
- Follow-up commit `6705c06225d7954ed1ae1a9aafba33b6a5fa3fff` adds the missing fixture ID. Actions #280 / run `42190525354` is in progress; JS rule tests and Python converter tests have passed, DB29 pack is intentionally skipped, and Android SDK/Gradle Debug build is still running at this checkpoint.
- Actions #276 / run `42189332608` succeeded on an earlier SHA for lightweight JS/Python checks and Debug APK/package/signature/ZIP verification. DB29 pack and emulator were skipped.
- Full DB29 pack run #270 failed before the later item schema fallback and clause-disposition changes. Do not repeat #270; one full pack validation is still required on the final combined SHA.

### Current implementation contract
- T and Android keep source values/review flags separate from runtime values.
- BONUS is a one-time generic neutral payment; NCS is generic payment and unit-only recurring upkeep.
- All runtime costs must use engine-supported color keys; no `bonus` key may reach the resolver.
- Unmapped item conditions receive deterministic fallback target; MagicLand installs without invented ordinary production; unsupported spell/enchant clauses consume cost and complete the action through terminal no-op.
- Each of 48,281 source effect clauses receives a terminal runtime disposition in the generated pack. This is not a claim that all original effects are semantically implemented.
- Final gates remain: runtime costs 15,350/15,350; finite unit upkeep 8,633/8,633; effect clause dispositions 48,281/48,281; zero card-wide blockers; same-SHA emulator install/launch.

DB29 remains preserved; DB30 remains unpublished; all designated PRs remain unmerged.

---

## OPS-010 — 2026-11-06 — safe simple-spell inference and final validation gate

### Additional runtime semantics
- APK PR #28 now permits a tested inferred handler only for an exact simple-text spell effect with supported attack/defend/battle-start timing and a supported target/effect type.
- Candidate/source status remains `pattern_candidate`; the separate runtime disposition may be `implemented_inferred` only when the converter and Android schema parser agree on the same simple handler.
- All enchants remain `fallback_noop` until a correct event/duration-bound slot engine exists. A decoded slot plus a simple text match is not sufficient to claim enchant execution.
- Unsupported spells and all enchants still pay runtime cost, leave the hand, reach a terminal zone, and complete the action through effect-only fallback.
- Android pack validator cross-checks clause-level dispositions, card-level dispositions, and manifest counts so converter/parser disagreement fails the pack rather than silently misclassifying effects.

### Updated pointers
- T PR #9 HEAD is now `2aad86adf76a823446296f6754181b1cdb4da294` after the runtime contract boundary update. Latest SHA Actions success remains unconfirmed.
- T PR #13 HEAD before this append is `161a9a97de1f0688fba0c61969fe49f7a4e264e6`; base SHA remains older than PR #9's base. The branch remains Open and unmerged; do not claim main control-center synchronization.
- APK PR #28 HEAD is `ceaed7ae0326215ec2b990805879362179b06a40`. Actions #301 / run `42191317316` is pending on this HEAD. It is a lightweight validation run; the explicit full DB29 pack/emulator gates are still not triggered.
- Actions #280 / run `42190525354` succeeded on the earlier HEAD `6705c06225d7954ed1ae1a9aafba33b6a5fa3fff`: JS rule tests, Python converter tests, Debug APK build, package/signature/ZIP integrity. DB29 pack, emulator, and data archive upload were skipped.
- The latest code change adds tests for simple inferred spell, complex spell fallback, enchant fallback, NCS upkeep, BONUS one-time payment, and runtime item fallback. Wait for #301 before declaring those latest tests passed.

### Remaining final gate
After #301 completes, update PR #28 with the explicit `[build-card-pack] [run-emulator]` markers once. Confirm the generated data pack has 15,350/15,350 valid runtime costs, 8,633/8,633 finite unit upkeep profiles, 48,281/48,281 terminal effect-clause dispositions, zero card-wide blockers, and a same-SHA emulator install/launch. Do not run a second full pack or emulator job on the same SHA.

---

## OPS-011 — 2026-11-06 — per-card action terminal-state gate / CI cost control

### Latest verified checks
- T PR #9 HEAD `2aad86adf76a823446296f6754181b1cdb4da294` passed Actions #716 / run `42191294766`. Scope: lightweight regression tests and runtime overlay self-test; not a full DB29 audit.
- APK PR #28 HEAD `ce1918` passed Actions #313 / run `42192048398`: JS rule tests, Python converter tests, Gradle Debug APK build, application ID/package/signature/ZIP checks. DB29 pack and emulator steps were skipped.
- APK PR #28 latest HEAD `cba3519cc1744b03b583461aece515a7f33a4ede` includes the runtime action audit, partial item fallback correction, safe simple-spell inference boundary, and explicit CI gate policy. Actions #319 / run `42192469551` is pending; this run is lightweight-only by design.

### Actual card-action readiness gate
- The full pack validator now simulates the actual `FM.playCard()` path for every one of the 15,350 cards with synthetic but legal resources/LP/targets. It checks success, hand removal, a type-appropriate terminal zone/queue, and `playedAnyCardThisPhase` completion.
- Required result: runtimeActionAudit 15,350 attempted / 15,350 completed / 0 blocked, with terminal states split by card type. This is separate from cost readiness and structural validation.
- Item fallback ignores only unsupported source clauses; known owner/race/affiliation/allowed-ability restrictions remain enforced in both rules engine and target-selection UI.
- Exact simple spell inference is limited to one simple clause plus supported attack/defend/battle-start timing and a valid effect target. All enchants remain effect-only fallback until event/duration slot execution exists.

### CI cost control
- Normal PR synchronize now runs JS/Python checks only; Gradle/Android SDK setup is skipped.
- PR title `[build-apk]` requests APK build; `[build-card-pack]` requests DB29 data pack plus APK; both `[build-card-pack]` and `[run-emulator]` request emulator install/launch.
- Main pushes still build APK automatically. Manual workflow_dispatch expensive inputs default false; emulator requires card-pack generation.

DB29 remains preserved; DB30 unpublished; designated PRs remain open and unmerged. PR #13 base SHA is still older than PR #9 base, and the main-branch control center is not yet synchronized; PR-branch documentation is not main synchronization.
---

## OPS-012 — 2026-11-06 — first full pack gate / manifest validator correction

- APK Actions #322 / run 42192589114 on HEAD cba3519cc1744b03b583461aece515a7f33a4ede successfully downloaded the protected DB29 release assets, verified the release metadata/hash/SQLite integrity and 15,350-card count, converted all 15,350 cards, and generated the Android data ZIP. It then failed in the pack validator with ReferenceError: manifest is not defined because the validator's new manifest cross-check referenced a manifest object that was not an input.
- This was a validator wiring defect, not a DB29 download/hash failure, converter failure, or card-level action blocker. No DB29/Release data was changed.
- Correction: validator now accepts the extracted manifest as its fifth input and verifies canonical fields cardsCount, sourceDatabase.releaseTag, and sourceDatabase.cardCount; workflow extracts manifest.json from the generated ZIP and passes it to the validator. The validator then cross-checks manifest/card/clause effect dispositions.
- Fix commits: validator manifest load 560c16a433bedaedf7da378dd42d2492707cb2c6; workflow manifest extraction 60681acc02974f6f6e8721def63b24f0823a6d6e.
- APK Actions #325 / run 42192845020 is queued on the corrected HEAD 60681acc02974f6f6e8721def63b24f0823a6d6e with the same full pack/APK/emulator markers. Inspect its first failure if any; do not rerun the unchanged #322 SHA.

DB29 remains preserved; DB30 remains unpublished; all designated PRs remain open/unmerged.

## OPS-013 — GitHub Actions 실행량·실패 비용 통제 (2026-11-06)

### 확인된 실행 이력
- T PR #9 Actions #716: 경량 회귀 테스트 및 compact source inventory 생성 성공. 전체 DB 감사/크롤링/Release 단계는 skip.
- T PR #13 Actions #719: 경량 회귀 테스트 성공. 전체 DB 감사/크롤링/Release 단계는 skip.
- FM-OFFLINE PR #28 Actions #322: JS/Python 검사와 DB29 다운로드·15,350장 변환·ZIP 생성까지 성공했으나 validate-app-card-pack.cjs 551행의 ReferenceError: manifest is not defined로 실패. 데이터 원본 실패가 아닌 validator 코드 결함.
- FM-OFFLINE PR #28 Actions #325: 수정 SHA 60681acc에서 DB29 pack, APK, APK 무결성, emulator install/launch까지 성공.
- FM-OFFLINE PR #28 CI gate 수정 커밋 0be807b9dd3b67e5555ea9140e9083d698301bf5의 Actions #327: 성공. JS/Python 검사는 수행했고 DB29 pack, JDK/SDK/Gradle, APK, emulator 단계는 모두 skip됨.

### 원인
기존 Android CI는 PR 제목에 [build-card-pack] / [run-emulator]가 들어 있으면 PR의 모든 synchronize에서도 DB29 대용량 다운로드·변환과 emulator를 실행했다. PR #28 제목에 두 marker가 상시 포함되어 있어 코드 수정마다 고비용 검증이 반복될 수 있었다. pull_request.edited와 cancel-in-progress: false도 제목 편집/구버전 실행 누적 위험을 높였다.

### 수정
FM-OFFLINE PR #28 .github/workflows/android-ci.yml에서 다음을 반영했다.
1. PR 이벤트 edited 제거; opened/synchronize/reopened만 유지.
2. PR에만 cancel-in-progress: true 적용; main push와 수동 workflow_dispatch는 취소하지 않음.
3. PR 제목 marker에 의한 DB29 pack 및 emulator 실행 경로 제거.
4. PR 제목 [build-apk]는 APK 전용 빌드 gate로 유지.
5. DB29 pack/emulator는 workflow_dispatch의 명시적 boolean 입력으로만 요청 가능. main의 승인된 push marker는 유지.
6. 동일 SHA 성공 검증은 재실행하지 않고, 실패 시 최초 실패 step/log 확인 후 새 SHA에서 필요한 최소 검증만 수행.

### 운영 기준
- PR마다 JS/Python 경량 회귀 테스트는 유지한다.
- 대형 DB29 pack + APK + emulator는 최종 통합 SHA에서 한 번 수행한다.
- 문서 전용 변경 및 단순 PR synchronize는 고비용 pack/emulator를 실행하지 않는다.
- 검증 축소가 목적이 아니라 불필요한 반복만 제거한다.
- DB29 보존, DB30 미발행, 지정 PR 병합 금지 경계는 유지한다.
