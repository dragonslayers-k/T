# FM-OFFLINE / CardDB 프로젝트 통합 운영 기준점

- 기준일: 2026-11-06 (KST)
- 문서 역할: 대화가 바뀌어도 작업 상태·승인 경계·검증 이력을 반복 확인하지 않도록 하는 **단일 운영 기준점**
- 대상 저장소:
  - 카드DB: https://github.com/dragonslayers-k/T
  - Android 앱: https://github.com/dragonslayers-k/FM-OFFLINE
- 상위 기술·규칙 문서: 각 저장소의 기존 상세 문서와 `FM-OFFLINE 통합 마스터 총괄본 v4.4`. 이 문서는 상세 설계를 복제하지 않고, 현재 작업 포인터와 운영 규칙을 관리한다.

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
| 데이터 해석 | 출처·근거 없는 추정으로 원본값을 덮지 않음. 미확정 값은 pending / non-executable 유지 |

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
4. **통합 마스터 총괄본 v4.4 및 과거 대화**: 기술 배경과 결정 이력. GitHub보다 오래된 SHA·상태는 현재값으로 사용하지 않는다.

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
