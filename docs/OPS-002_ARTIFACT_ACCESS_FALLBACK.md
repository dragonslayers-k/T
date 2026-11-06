# OPS-002 — 도구·아티팩트 접근 장애 대응 규칙
기준일: 2026-11-06
대상: FM-OFFLINE / CardDB T 저장소 작업 재개 및 지속 개발

## 목적
사용자에게 파일 업로드나 Actions 수동 실행을 반복 요청하지 않도록, 장애 계층을 구분하고 우회·영구 개선을 우선 적용한다.

## 장애 구분
A. workflow 미실행/실패
B. artifact 생성/업로드 실패
C. GitHub connector 다운로드 실패
D. artifact 다운로드는 성공했으나 Python/container 분석 런타임 접근 실패
E. 권한/사용자 입력 자체가 없음

D형은 파일 손상 또는 사용자 측 문제라고 단정하지 않는다. connector file reference, materialized path, runtime 접근은 별도 계층이다.

## 필수 우회 절차
1. 기준서, workflow, PR 상태를 GitHub API/connector에서 먼저 확인한다.
2. 성공한 Actions의 job logs에서 요약, 카운트, 경로, 체크섬, 검증 범위를 회수한다.
3. 로그에 필요한 값이 없거나 큰 artifact를 런타임에서 읽을 수 없으면, workflow에 작은 독립 JSON/CSV/manifest/compact review set을 생성하고 업로드하도록 보완한다. 핵심 수치는 로그에도 출력한다.
4. 저장소에 이미 있는 텍스트 산출물은 개별 파일을 GitHub contents API로 조회한다. 이진/대형 파일을 텍스트 fetch로 처리한다고 가정하지 않는다.
5. 장애 메시지와 최초 실패 단계부터 확인한다. 환경 장애는 대체경로, 코드 장애는 응집된 수정과 영향 범위에 맞는 focused test로 처리한다.
6. 같은 장애가 재발하면 이 절차를 먼저 적용한다. 조사 없이 사용자에게 재차 업로드/수동 실행을 요청하지 않는다.
7. 사용자 요청은 API/권한상 필요한 입력이 실제로 없고 모든 대체경로가 막혔을 때만 한다. 요청은 구체적이고 한 번에 끝나도록 하며, 시도한 경로와 막힌 이유를 밝힌다.
8. 연결 도구가 workflow_dispatch를 지원하지 않는 경우만 수동 실행을 예외 요청한다. workflow, ref, inputs, 목적을 정확히 지정하며 push-triggered 대안과 기존 로그 조회를 먼저 검토한다.

## 장애 기록
장애 ID, 날짜, run ID/SHA, A–E 분류, 정확한 오류/단계, 사용자 요청 없이 시도한 우회, 결과, 영구 개선(워크플로 출력·compact report·스크립트·테스트·문서), 다음 재발 시 우선 절차를 남긴다.

## 금지
- 런타임 ClientError만으로 artifact 손상을 주장하지 않는다.
- 다운로드 성공을 로컬 분석 성공으로 보고하지 않는다.
- 로그 집계만으로 카드별 원문 검토를 주장하지 않는다.
- 이미 지시받은 우회를 무시하고 같은 사용자 요청을 반복하지 않는다.

## 적용할 프로젝트 승인 경계
DB29 보존, DB30 발행 금지, T PR #9/#12 및 APK PR #28/#26/#25/#9 병합 금지는 기존 PROJECT_CONTROL_CENTER 규칙을 그대로 따른다. 본 규칙은 발행·병합 승인이 아니다.


## 실제 적용 기록 — 2026-11-06 / D형 / Actions #663

- 대상: T run #663 (42173417874), SHA 75584d92ac4b4812f94d99fbc34f1360ea68eaf7, DB29 source, publish=false.
- 정확한 장애: GitHub connector artifact download 성공 및 materialization 경로 생성 후 Python/container가 ClientError로 접근 실패. 아티팩트 ZIP 손상 여부를 판정하지 않는다.
- 사용자에게 요청하지 않고 사용한 우회: Actions run/job metadata 및 logs에서 완료 단계와 집계값을 확인.
- 복구된 집계: 15,350 cards / unique IDs; 613,435 fields (55 types); 17,407 effect texts; 48,281 pattern splits; 0 missing interpretation; 1,249 low-confidence interpretations; 0 unmapped skill rows; 30,700/30,700 images checked; 52 hybrid cost mapping review; 779 special semantics review; 0 FK errors.
- 남은 제약: aggregate logs alone cannot reconstruct the card-level review records; queue overlap is unknown; no claim of semantic/engine completion.
- 영구 개선 작업: workflow should print concise summary and upload a compact JSON/CSV containing card IDs, original text, source URL, review reason/status, and evidence pointers. Ensure this can be fetched as text or parsed from job logs; do not require full ZIP local extraction.
- 다음 재발 시 우선: logs and GitHub API -> compact artifact/text file -> targeted workflow output changes -> only then consider asking user for a concrete missing permission/input. Never ask the user to upload the same artifact or manually dispatch the same workflow just because the runtime failed.


## D형 재시도 경로 성공 — 2026-11-06 / run #663

- 동일 artifact ID 13481939094를 connector로 다시 다운로드하자 `/mnt/data/semantic-review-663-retry.zip`에 직접 materialize 되었고, container `ls` 및 `unzip -l`로 ZIP 정상과 실제 entry를 확인했다.
- 이전 `/mnt/data/files/semantic-review-663.zip` 경로는 런타임에서 ClientError가 났지만, 이번 direct path는 접근 가능했다. 이는 path/materialization route 장애와 ZIP 손상을 구분해야 함을 보여준다.
- ZIP 2.2 MiB, expanded files 45,551,502 bytes. Effect queue JSONL 1,020,911 bytes / 1,249 card-level rows; 716 normalized patterns. Full inferred-skill file (42.7 MB) was not needed for this focused task.
- Card-level effect rows were parsed successfully; exact raw text, card ID/name/type, clause index, interpretation candidate, verification status, and source URL were preserved in a triage queue uploaded to the Library as `fm1-db29-low-confidence-effect-cluster-triage-663.json`.
- Deterministic first-pass labels only organize pending review: FAQ/external help 26 rows; named card/item reference 108; named state/status 16; condition/formula 417; metadata/flavor candidate 19; unclassified semantic candidate 663. All remain `pending_source_review` and `non_executable`; labels do not resolve meaning.
- Revised retry precedence: (1) connector re-download -> inspect exact direct path, (2) validate ZIP listing and extract the smallest needed file, (3) parse relevant JSONL, (4) use job logs/compact summary as secondary, (5) update workflow output for future runs. User upload or manual dispatch remains last resort only for a missing permission/input.
