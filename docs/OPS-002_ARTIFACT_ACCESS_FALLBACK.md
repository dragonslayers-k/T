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


## 원천 원인 진단·복구 프로토콜 — D형 실행 런타임 ClientError (2026-11-06 보강)

### 현재 사례와 판정 범위
- 이번 반복 장애: `container.exec`의 단순 `pwd`/`echo`/`ls`와 Python 최소 실행이 모두 `ClientError`로 실패했다. Files API와 GitHub connector는 별도 응답했다.
- 이 양상은 JSON 파서·특정 ZIP·프로젝트 코드보다는 **대화의 로컬 실행 컨테이너/도구 연결 계층** 문제 가능성을 높인다. 내부 서비스 로그가 노출되지 않으므로 backend provisioning, 세션, 스토리지, 라우팅 중 무엇인지는 미확정이다.
- 이전 run #663에는 materialization 경로 차이로 성공한 시도도 기록되어 있다. 그러므로 모든 장애를 무조건 컨테이너 전역 장애로 판정하지 않고 아래 순서로 분리한다.
- Assistant는 실행 컨테이너를 재시작하거나 backend를 수정할 권한이 없다. 확인할 수 없는 내부 로그를 추측하지 말고, 재현 가능한 증거를 기록한다.

### 진단 단계 — 순서대로 1회씩, 반복 호출 금지
1. **도구 상태 분리:** Files/GitHub connector 응답 여부와 로컬 실행 도구 상태를 별도로 기록한다.
2. **최소 probe:** `container.exec`에서 `pwd` 또는 `echo` 1회, Python에서 `print(1)` 1회. 둘 다 `ClientError`면 프로젝트 파일·코드 검사를 중단한다.
3. **경로·mount 분리:** 재다운로드 전에 materialize 응답의 실제 path·size·file ref를 기록한다. 기존 성공 경로와 다른 경로가 근거상 존재할 때만 1회 경로 확인을 한다. 경로를 추측하지 않는다.
4. **작은 입력 probe:** 최소 probe가 정상일 때만 작은 텍스트 파일/간단한 파일 목록을 검사한다. 큰 artifact를 장애 진단용으로 쓰지 않는다.
5. **계층 분류:**
   - connector 성공 + 최소 런타임 probe 전부 실패 → runtime/tool-session 후보
   - 최소 probe 성공 + 특정 path 실패 → mount/path/permission 후보
   - 작은 파일 성공 + 큰 파일 실패 → size/transfer/resource/format 후보
   - ZIP 목록 성공 + extraction/parser 실패 → 압축·데이터·메모리·코드 후보
   - workflow/job 자체 실패 → Actions 계층 후보
6. **증거 기록:** KST 시각, 도구·명령·정확한 오류, file ref·실제 반환 path·size, 성공한 connector, 이전 성공 경로와 사용자 요청 여부. 토큰·비밀값은 기록하지 않는다.

### 원천 복구와 지속 가능한 우회
A. **Assistant가 가능한 원천 진단:** 동일 세션에서 반복 호출을 멈춘다. 가능하면 새 대화/새 실행 세션에서 최소 probe를 수행해 세션 한정 여부를 비교한다. 새 세션에서도 재현되면 프로젝트 작업을 무한 재시도하지 말고 ChatGPT/OpenAI 지원에 재현 기록을 제출한다. 새 세션 시도는 복구 확인이지, 해결 완료 주장이 아니다.
B. **경로 재시도:** connector가 반환한 정확한 materialized path만 사용한다. 임의의 `/mnt/data` 경로를 가정하지 않는다. 이전 성공 경로가 명확할 때만 path variation을 1회 시험한다.
C. **컨테이너 우회:** Files search/read로 텍스트를 분할 조회하고, GitHub Contents API로 저장소의 텍스트 소스를 읽는다. Actions logs에는 핵심 집계와 상태를 출력한다.
D. **Artifact 구조 개선:** 단일 대형 ZIP에만 의존하지 않는다. 압축 없이 작은 `summary.json`(집계·버전·SHA·검증범위), `manifest.json`(파일명·크기·SHA-256·schema), 카드 단위 `review.csv/jsonl`(ID·원문·source URL·검토상태)를 별도 제공한다. 상세 산출물은 chunk/partition으로 나눠 필요한 부분만 접근 가능하게 한다.
E. **생성 단계 검증:** row count, schema/version, file size, SHA-256, JSONL parse count를 로그와 manifest에 남긴다. 다운로드/도구 호출 실패와 데이터 파싱 실패를 서로 다른 상태로 기록한다.
F. **사용자 요청 최소화:** 동일 파일 재업로드나 같은 Actions 수동 실행을 요청하지 않는다. 권한/입력이 실제로 없고 대체 경로가 모두 막혔을 때만 구체적인 단일 요청을 한다.

### 재발 기록 양식
- Incident ID / KST timestamp:
- Repository / run ID / commit SHA / immutable DB release:
- Layer: workflow / artifact generation / connector / materialize path / container runtime / parser / permission:
- Minimal probe + exact error:
- File ref / exact path / size / checksum:
- Known-good path/session and result:
- Root-cause confidence: confirmed / probable / undetermined; evidence:
- Immediate recovery / durable fix:
- User action (none unless unavoidable):
- Next occurrence: first three exact steps:

### 이번 사건 판정
- Classification: D형. **실행 컨테이너/도구 연결 계층 장애 가능성 높음; 내부 원인 미확정.**
- Confirmed: container.exec 및 Python 최소 probe가 ClientError; Files/GitHub connector 응답.
- Not confirmed: artifact 손상, 프로젝트 소스 결함, 내부 backend의 구체적 root cause.
- Immediate action: 컨테이너 반복 호출 중지; Files/GitHub connector 및 compact outputs로 진행.
- Durable action: 향후 OPS-002 장애 분류에 이 증상 시그니처를 포함하고, 새 세션에서도 재현될 경우 지원팀 보고 대상으로 분류한다. 프로젝트 문서 수정만으로 플랫폼 런타임이 고쳐졌다고 표현하지 않는다.
