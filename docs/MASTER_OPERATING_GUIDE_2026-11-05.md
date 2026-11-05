# Fantasy Masters 1 외부 참고자료·카드 규칙 통합 운영 가이드

- 기준일: 2026-11-05 (KST)
- 기준 DB: 불변 Release `fm1-carddb-29`
- DB 작업 브랜치: `feat/carddb-effect-semantic-pass`
- PR: https://github.com/dragonslayers-k/T/pull/9
- 적용 저장소: 카드DB `dragonslayers-k/T`, Android 게임 `dragonslayers-k/FM-OFFLINE`
- 목적: 사용자가 제공한 나무위키 복사본(A.docx), 3.4~3.6 지식베이스, 개인 가이드 캡처, 공개 카드·기술 자료를 두 저장소의 데이터·엔진 작업에 일관되게 반영하기 위한 운영 기준

## 1. 변하지 않는 승인 경계

1. DB29의 Release/tag/assets는 불변이며 덮어쓰기·재발행하지 않는다.
2. DB30은 카드DB 품질 게이트를 모두 통과하고 사용자가 명시 승인하기 전까지 발행하지 않는다.
3. PR #9는 검증 완료 및 사용자 승인 전까지 main에 병합하지 않는다.
4. 외부 커뮤니티 자료만으로 카드 효과·비용·엔진 규칙의 `executable=true`를 설정하지 않는다.
5. 원본 카드 필드, `TextBase`, `TextExtra`, 원본 URL, 이미지와 ID는 변경하지 않는다. 외부 설명은 별도 `SourceDocument/SourceClaim` 또는 provenance 레코드로 연결한다.
6. 미확인 값은 0, 무료, 기본값, 빈 효과로 치환하지 않는다. 의미검토는 `pending`, 런타임은 `non_executable`을 유지한다.
7. 판타지 마스터즈 1(FM1)과 판타지 마스터즈 2(FM2), FAN-MADE MASTERS의 규칙을 혼합하지 않는다.

## 2. 저장소별 책임과 반영 범위

| 저장소 | 책임 | 외부 자료 반영 위치 |
|---|---|---|
| [T 카드DB](https://github.com/dragonslayers-k/T) | 원본 데이터, 카드 ID·필드·효과·비용·기술 provenance, 검토 큐, SQLite/Release | `data/reviews/`, `docs/`, source registry |
| [FM-OFFLINE APK](https://github.com/dragonslayers-k/FM-OFFLINE) | 카드 데이터팩 adapter, 카드 도감, 게임 엔진, 전투·비용·기술·효과 실행과 Android 검증 | `docs/RULES_SOURCES.md`, `docs/CARD_SCHEMA.md`, `docs/PROJECT_STATUS.md`, 별도 외부 참조 가이드 |
| [FM LUNATIC 카드 아카이브](https://fmlunatic.com/cardlist) | 원본 카드 목록·카드 ID·상세 텍스트·이미지와 현행 카드별 증거 | 두 저장소의 원본 데이터 검증 근거 |

T에서 확인한 사실이나 스키마가 APK 엔진의 구현 완료를 의미하지 않는다. T의 SQLite Release가 승인·발행되기 전에는 APK가 임의의 작업 브랜치 데이터를 소비하지 않는다.

## 3. 출처 권위·용도 분류

### 3.1 규칙과 카드별 사실의 우선순위

| 우선순위 | 출처 | 사용 목적과 제한 |
|---:|---|---|
| 1 | 사용자가 제공한 FM1 `Manual.zip` | 공통 게임 규칙과 매뉴얼에 수록된 27개 기본 특수 공격 기술. 단, 매뉴얼 내부 충돌은 충돌 항목으로 유지 |
| 2 | 불변 DB29의 원본 카드 payload 및 해당 카드 상세 URL | 카드 ID, 카드명, `TextBase`, `TextExtra`, 비용·속성·종족·소속 등 카드 단위 근거 |
| 3 | FM LUNATIC 카드 상세/목록 | 카드 원본 필드와 ID, 상세 설명을 확인하는 카드 아카이브. 별도 매뉴얼 규칙의 대체물이 아님 |
| 4 | NamuWiki/Namu-moe의 FM1 문서·개별 카드 항목 | 카드 분류, 명칭, 역사적 텍스트, 기술 사례, 속성·종족·소속의 보조 색인. 커뮤니티 편집 자료이므로 단독 실행 근거 불가 |
| 5 | Neginote 개인 가이드 | 카드 종류·등급·지형 LP/소울·유닛 필드·마법 턴 정보 등의 보조 개념 자료 |
| 6 | Inven 2017 기술 모음 및 기타 개인·커뮤니티 분석 | 기술 이름·목록·예시의 독립 교차참조. 작성 시기의 판본 차이 및 생략 조건을 카드 원문과 대조 |
| 7 | Gamechosun 2002 소개 등 과거 기사 | 초기 게임 구조·당시 속성 체계의 역사적 맥락만 참고. 후대 규칙의 증거로 사용하지 않음 |
| 별도 보류 | Naver jlplace 원작 가이드 | 본문 접근이 차단되었고 제공 캡처는 폭 65px로 글자를 신뢰성 있게 판독할 수 없음. 본문/규칙 추출 전까지 내용 미인용 |

나무위키 링크가 있다는 사실과 해당 링크가 게임 전용 문서라는 사실은 다르다. 종족·소속 링크가 일반 사전·동음이의어 문서로 이동하면 게임 설정으로 간주하지 않는다. 접근 오류·캐시 누락·404는 삭제 또는 내용 부재의 증거가 아니라 해당 접근 경로의 상태로만 기록한다.

### 3.2 확인된 추가 참조 URL

- NamuWiki 메인: https://www.namu.moe/w/판타지_마스터즈
- NamuWiki 속성: https://m.namu.moe/w/판타지%20마스터즈/속성
- NamuWiki 종족과 소속: https://www.namu.moe/w/판타지%20마스터즈/종족과%20소속
- NamuWiki 금속 카드 예시: https://www.namu.moe/w/스터두라엘
- NamuWiki 숲 카드 예시: https://www.namu.moe/w/번창하는숲
- NamuWiki 숲 스페셜 카드 예시: https://www.namu.moe/w/샤와타의그물
- NamuWiki 동음이의어/카드명 주의 예시: https://namu.moe/w/무
- Neginote 가이드: https://neginote.wixsite.com/fantasymasters/main-guide
- Neginote 지형: https://neginote.wixsite.com/fantasymasters/guide-rand
- Neginote 유닛: https://neginote.wixsite.com/fantasymasters/guide-units
- Neginote 마법: https://neginote.wixsite.com/fantasymasters/guide-magic
- Inven 2017 기술 모음: https://www.inven.co.kr/board/hs/3509/1426815
- Gamechosun 초기 소개: https://www.gamechosun.co.kr/webzine/article/view.php?from=articlelist&no=13712
- Naver jlplace 가이드: https://m.blog.naver.com/jlplace/220468684977

## 4. 데이터 모델 및 용어 기준

### 4.1 구분해야 할 분류

- `attribute` / 카드 속성: 암흑·불·물·숲·대지·금속·빛·무(중립) 8개. 3.4 하위 문서는 7개 속성을 상세 설명하지만, 메인 문서의 대격변 이후 설명은 무속성을 여덟 번째 속성으로 구분한다.
- `race` / 종족: 유닛의 종족 분류값.
- `affiliation` / 소속: 집단·직업·조직·세력의 소속값.
- `card_type` / 카드 종류: 지형·유니트·아이템·마법·인챈트 5종. APK UI/스키마에서는 마법을 `spell`로 표현한다.
- `ability` / 유닛 능력: 장비·마법·야수·만능. 아이템 장착 적격성을 종족과 혼동하지 않는다.

앱의 기존 데이터 계약에서 `faction`은 카드 속성(color)을 나타내고 `affiliation`은 소속을 나타낸다. 신규 문서·데이터 설계는 모호성을 피하기 위해 `attribute`, `race`, `affiliation`을 사용한다. 구형 `faction` 키는 호환성 유지 목적으로만 사용한다.

### 4.2 속성·종족·소속 엔터티

카드명·종족명·소속명이 같거나 비슷하다는 이유로 같은 엔터티로 합치지 않는다. 정규화 모델은 `Card`, `Race`, `Affiliation`, `CardRace`, `CardAffiliation`, `CardVersion`, `SourceDocument`, `SourceClaim`의 구분을 권장한다. 실제 카드와 연결할 때는 카드 ID, 원본 속성, 카드 종류, 종족·소속 필드, 카드 이미지, 카드 상세 URL을 함께 대조한다.

### 4.3 목록을 병합하지 않는 원칙

다음 목록은 출처와 시점이 다른 별도 inventory로 유지한다.

1. NamuWiki 본문 3.6에 나오는 개별 항목이 개설된 카드 목록
2. 속성별 분류 페이지에 현재 포함된 카드 목록
3. DB29의 전체 15,350개 카드 ID 목록
4. 사용자 제공 카드·스킬 개인 가이드의 역사적 사례

분류 페이지에 추가 카드가 있거나 3.6 목록에 빠진 카드가 있어도 전체 DB에 없는 카드라고 단정하지 않는다. 반대로 이름이 같다고 카드 ID를 합치지 않는다. 표기 차이·리콜·개명·동음이의어는 별도 alias 후보와 검토 근거를 남긴다.

## 5. 카드 원문에서 구조화할 효과 필드

효과 해석은 카드 원문을 보존한 별도 구조 데이터로 진행한다. 최소한 다음 요소를 분리한다.

- `trigger_timing`: 공격턴·방어턴·공격 시·방어 시·파괴 시·준비 단계 등 발동 시점
- `actor`: 효과를 발생시키는 카드·플레이어·유닛
- `target_selector`: 아군/적군, 유닛/지형/아이템/마법/핸드/소각장/서고, 슬롯 번호, 종족·소속·속성 필터
- `preconditions`: 레벨, 카드 이름 수, 필드·핸드·지형 수, 유닛 능력, 장비 상태 등의 발동 조건
- `cost`: 소울·LP·카드 소각 등 비용
- `operation`: 소환·파괴·장착·이동·복제·능력치 수정·상태 부여·카드 회수 등 실제 행위
- `formula`: AP/DP/HP·레벨·소각장 수·핸드 수 등 계산식과 반올림/상한 규칙
- `duration`: 유지 턴과 종료 시점
- `failure_effect`: 조건 실패 시 발생하는 불이익
- `stacking`: 중첩 및 반복 사용 처리
- `source_claims`, `verification_status`, `executable`: 주장 출처, 검증 상태, 실행 허용 여부

원문에 수량 단위·반올림·최댓값·적용 순서가 없으면 추정하지 않는다. `행동불능`, `데스`, `시엘`, `소각장`, `유소울`, `무소울` 같은 FM1 용어를 일반 TCG 용어로 임의 치환하지 말고 별도 용어 사전으로 관리한다.

## 6. 첨부된 카드별 설명의 검토 대상

아래 항목은 A.docx에 포함된 NamuWiki 3.6 본문 설명의 *커뮤니티 서술*이다. 현재 DB29 카드 원문·공식 매뉴얼·엔진 테스트를 확인한 사실로 승격하지 않는다.

- 슬픈재회: 레어/GP 900/SP 45,000, 납치 계열 마법과 자신의 최고 레벨 유닛에 2턴 데스 부여 설명. 원문 표현 `구매 룩`은 의미 불명으로 보존.
- 인어의애정: 핸드의 종족 수만큼 필드의 물 속성 유닛에게 시엘 장착한다는 설명.
- 도깨비씨름: 레벨 4 이상을 행동불능으로 만든다는 설명.
- 뿌리침투: 자신의 1번 지형과 상대 1번 지형을 동시에 제거한다는 설명.
- 숲의지도자: 공격하면 상대 필드 전체 야수 AP/DP를 0으로 만든다는 `야수지배` 설명.
- 짙은안개: 방어 마법/카운터 계열, 양측 전체 AP를 0으로 만든다는 설명.
- 폐허의흔적: 자신의 소각장 유닛 수에 따라 상대가 사용한 마법을 필드로 회수한다는 설명과 6개 중 4개를 3~6번째 순으로 가져오는 예시.
- 마력결계진: 1 금속 소울·방어턴 디스펠, 대상 카드 이름 수와 상대 유닛 이름 수가 같을 때 파괴, 실패 시 자신의 첫 유닛 행동불능이라는 설명.
- 석병팔진: 4 소울(금속 3/무 1), 양측 핸드 합 8장 및 자신의 지형 8장일 때 상대 필드 전체 유닛과 자신의 핸드 지형을 파괴한다는 설명.
- 소르다스의검: 2 금속 소울, 자신의 첫 유닛의 유소울 또는 유지비 이하 비용 장비를 장착하고 상대 유닛에 순차 피해·행동불능을 준다는 설명.

각 카드는 DB29의 `TextBase`/`TextExtra`를 먼저 확인하고 원본 상세 URL과 ID를 연결한다. 이름이 맞더라도 카드 버전·리콜·능력치·비용·타겟 조건이 다르면 서로 다른 주장으로 보존한다.

## 7. NamuWiki 개별 페이지에서 추가로 확인한 사례

- 속성 문서는 7개 속성(암흑·불·물·숲·대지·금속·빛)을 별도 절로 나눈다. 메인 문서의 중립/무속성은 별도 8번째 속성으로 다루므로 3.4 문서 목차와 전체 속성 수를 혼동하지 않는다.
- 종족·소속 문서는 명칭 색인 역할을 한다. 항목 링크가 일반 단어·리디렉션·동음이의어로 연결될 수 있으므로 게임별 카드의 실제 `race`/`affiliation` 값은 DB 원본에서 확인한다.
- 스터두라엘 문서에는 금속 유니트, 휴먼 종족, 머시너리 소속, 에픽, 에피소드/구매 정보, 고유 능력 설명이 함께 기재되어 있다. 카드 필드 전체가 현행 DB29와 일치한다고 단정하지 않고, 필드별 대조 예제로 사용한다.
- 번창하는숲 문서는 숲 레어 카드의 구매·에피소드 정보, 핸드 지형 소각과 그 수만큼 트리언트 소환이라는 효과 설명 및 과거 덱 전략을 포함한다. 효과 수량 계산과 특수 소울 처리를 원문·엔진으로 별도 검증해야 한다.
- 샤와타의그물 문서는 숲 스페셜 카드의 에피소드/앨범 보상·제한·구매·발매 정보와 세계관 설명을 포함한다. 역사적 메타 서술과 카드 원본 필드를 구분한다.
- '무' 문서는 동음이의어 페이지 내에 숲 속성 시크릿 유닛 사례를 포함한다. 카드 이름 `무`와 속성 `무속성`은 동일한 값이 아니다.
- 판타지 마스터즈 분류 페이지는 본문 3.6 목록에 포함되지 않은 개별 항목도 인덱싱한다. 예를 들어 독도·리틀마스터 등은 별도 카드 페이지 또는 분류 링크 존재 여부를 추가 확인한다.

## 8. 54행 pending 효과 검토 및 다음 작업 순서

#460의 54행/54개 카드 ID는 #454 저신뢰 19행과 동일한 측정치가 아니다. #460의 54행 전체는 `pending_manual_semantic_review` 및 `non_executable`로 보존한다. #462 실패와 #463 수정 성공의 기록도 지우지 않는다. #464는 외부 링크·과거 기술 목록을 교차 대조했으나 54행을 실행 가능으로 승격하지 않았다.

작업 순서:
1. 23 디스인첸트 참조: TextExtra의 공통 정의와 정확한 카드명/기술명/참조 ID를 연결한다. 기술 참조를 효과 연산으로 오인하지 않는다.
2. 에카마엘 소환 프로필 7건과 별도 모래의형상화 공식 1건: DB29 전체 카드 ID에서 후보 유닛 목록을 정확 매칭한다. 종족·속성·챕터·레벨·랭크·이벤트 제외·예외 규칙과 홀짝 보너스를 각각 검증한다. 모래의형상화는 턴 자릿수 소울과 존 카운트 능력치 공식으로 분리한다. Inven 자료는 에카마엘 지형 최대 5의 보조 교차참조일 뿐 소환 풀이나 엔진 하드캡을 확정하지 않는다.
3. 7 영역/지형 카운터: TextBase/TextExtra의 마레마/아레아 등 실제 명칭을 보존한다. #462/#463에서 확인한 대로 6 mismatch/1 match의 실제 값을 전제로 테스트한다. 명칭이 비슷하다는 이유로 alias 자동 통합 금지.
4. 8 카드 이름 목록: 각 이름을 DB29 전체에서 정확 매칭하고 중복명·리콜·랭크·카드 종류 및 장착 적격성을 분리한다. 코스튬체인지 지정 아이템 7개는 Inven 글과 대조하되 DB29 원문에 있는 '아이템 미장착' 조건을 제거하지 않는다.
5. 나머지 8행: 조건·분기·상태·주석·변형·실패 효과·불완전 원문을 카드 ID 별로 분리하고 불확실한 항목은 pending 유지.
6. 효과 구조화는 trigger/actor/target/precondition/cost/operation/formula/duration/failure/stacking까지 근거가 확인되는 항목만 수행한다.
7. 실제 변경 후 focused tests를 실행하고 결과를 검토한다. 같은 변경에 대해 Actions를 중복 실행하지 않는다.

이후 잔여 과제:
8. 이름 기반 Skill 26개 및 카드별 근거 누락 123행: 정확명·동명이인·OCR exact/fuzzy/name collision/not found 구분을 유지하고 출처 문구와 카드 상세 URL 연결.
9. 소울 의미 831건: hybrid 52 및 NCS/BONUS 779를 토큰 파싱과 분리해 카드별 지불 의미를 검증. 비용이 불확실하면 사용 차단.
10. 엔진 검증 대기 42건과 매뉴얼 규칙 충돌 1건: 규칙별 재현 시나리오와 회귀 테스트로 해결.
11. 실질 변경 배치 완료 후 필요할 때 DB29 full audit 1회만 실행. 숫자를 낮추기 위한 반복 전체 감사 금지.
12. 사용자 승인 전 DB30 발행 및 main 병합 금지.

26/52/779/42 및 123은 이전 전체 감사에서 기록된 기준 잔여량이며 #464에서 새로 전수 재산출된 수치로 보고하지 않는다.

## 9. APK 엔진 반영 게이트

- NamuWiki/개인 가이드는 카드 도감 표시, 검색, 태그/필드 색인, 검토 큐의 보조 근거로 활용할 수 있다.
- 엔진에서 실행되는 공통 규칙은 Manual.zip 또는 명확한 카드별 원본 텍스트와 테스트가 있어야 한다.
- 커뮤니티 페이지의 효과 설명만으로 `rules.js` 핸들러를 추가하거나 기존 핸들러를 바꾸지 않는다.
- 각 효과 핸들러는 카드 ID 또는 검증된 Rule ID, trigger timing, actor/target, condition, operation, duration, failure/stacking behavior를 명시한다.
- 엔진 테스트는 효과별 성공·실패·경계조건·슬롯 순서·지속시간·중첩·양측 상호작용을 포함한다.
- `pattern_candidate`, `pending`, 커뮤니티 출처만 있는 Skill1/Skill2는 미실행으로 유지한다.
- APK 카드 스키마의 `faction`은 카드 속성 키의 기존 호환 이름이고, `race`와 `affiliation`은 별도 필드다.

## 10. 출처 접근·갱신 규칙

- NamuWiki 본문과 Namu-moe/d.namu.moe/m.namu.moe 미러는 URL과 도메인을 별도로 기록한다. 검색 색인으로만 확인된 페이지는 `search_index_retrieved` 상태로 둔다.
- 링크가 일반 사전으로 연결되면 `generic_dictionary_link`; 캐시 누락이면 `cache_miss`; 접근 차단이면 `blocked`; 본문 확인이면 `body_retrieved`로 구분한다.
- 링크 색인 목록의 개수와 본문을 실제로 읽은 페이지 개수를 분리해 보고한다.
- 개인 블로그/포럼은 작성자·발행일·판본·카드 ID 제공 여부를 기록한다. 캡처 OCR/전사 결과는 원본 본문과 같은 근거 수준으로 올리지 않는다.
- 새 근거가 기존 주장과 다르면 삭제하지 말고 `SourceClaim` conflict로 기록하며, 엔진 실행 여부는 별도 검증한다.

## 11. 상태 스냅샷

2026-11-05 확인 시점:
- T 작업 브랜치 `feat/carddb-effect-semantic-pass`, PR #9 open/unmerged.
- #464 Actions 성공: https://github.com/dragonslayers-k/T/actions/runs/41848414940
- #460 semantic pending: 54행 / 54 카드 ID / 41개 고유 패턴, 모두 non-executable.
- #462 failed / #463 passed; 테스트 가정 오류를 바로잡았으며 해당 조치에서 데이터 원본을 임의 수정하지 않음.
- DB29 immutable, DB30 미발행, main 미병합.
- Naver 원작 가이드 본문은 접근 차단, 첨부 캡처는 원문 글자 전사 불가.
- NamuWiki의 일부 링크는 검색 색인으로 문서 사실을 확인했지만, 모든 링크의 전체 본문을 완독했다고 주장하지 않는다.

이 문서는 후속 확인에 따라 수정하되 DB 원본과 실행 가능 상태는 별도 승인·검증 절차를 따른다.


## #466 디스인첸트 23행 공통 정의 연결

- 23개 원문 근거 행의 `TextExtra`에 공통 디스인첸트 정의가 반복 수록된 것을 확인하여 `fm1_enchantment_disenchant_first_by_field_count`로 연결했다.
- 해당 23행은 23개 고유 카드 ID다. 원문에 열거된 종류는 7속성×3종=21개이며, 21개 명칭은 23개 근거 행 내에서 카드명과 ID를 정확히 연결했다. 이 매칭은 전체 DB 내 동명 중복까지 증명하는 전역 검색 결과로 과장하지 않는다.
- 나머지 2개 `칠색조의가호`, `시스카이`는 공통 설명을 포함하지만 해당 종류 목록에는 없어 별도 보조 근거로 남겼다.
- 서로 다른 `TextExtra` 본문 14종은 원문 그대로 보존했다. 카드별 재생성, 파괴 정의, 랭크결박, 저스티스, 홀리레인, LP, 방체 데미지, 시스카이 예외는 공통 규칙에 합치지 않았다.
- 공통 텍스트는 source-defined/transcribed 상태로 구조화했으나, 카운트 스냅샷, 빈 슬롯, 처리 순서, 양측 처리, 재생성/디스펠 상호작용은 미해결이다. 23행 모두 pending/non_executable 유지.
- 테스트: `tests/test_disenchant_shared_rule.py`에서 23행/23 IDs, 21개 이름 매핑, 원문 보존, runtime gate 검증.

## 2026-11-05 소환 프로필 분류 정정
기존 named_summon_unit_profile_reference 8행은 에카마엘 8종이 아니다. DB29 원문 재검토 결과 에카마엘 7장과 별도 모래의형상화 1장이다. 별도 추억→이서리얼 조건부 소환 프로필 1건도 독립 유지한다.
- 에카마엘 7장: 키뇨엘(10102025324), 라드비엘(10102025325), 쿠두루스엘(10102025326), 피드엘(10102025327), 올피리엘(10102025328), 산치엘(10102025329), 마이엘(10102025330).
- 공통 원문: 1~3챕터 유닛, 같은 레벨·같은 속성의 유닛을 무작위 구성, 랭크 카드 포함, 이벤트 등급 제외, 일부 제외 카드 존재. 지형 수 홀수 AP+1 / 짝수 HP+1.
- 제외 카드 ID, 후보 풀 전체, 0개 처리, 하드캡은 미확인. Inven의 최대 5장 언급은 보조자료다.
- 모래의형상화(9010731883)는 대지 지형 파괴 후 속박 2턴 소환, 유소울=턴 일의자리, 무소울=십의자리, AP=소각장 유닛 수, DP=핸드 유닛 수, HP=백필드 지형 수, 최대 레벨 10이라는 별도 공식이다.
모든 내용은 원문 구조화이며 엔진 검증 전까지 pending/non_executable이다.

---

## 2026-11-05 최신 운영 갱신 — 병렬 진행 / A30 / APK PR #28

### 현재 검증된 저장소 상태

- T 브랜치 `feat/carddb-effect-semantic-pass`: HEAD `00c0480d0bd3eec3b2685986cdc471f20ca6fffb`; PR #9 open/unmerged. Actions #532 성공: https://github.com/dragonslayers-k/T/actions/runs/41934778231
- DB29 `fm1-carddb-29`는 불변 기준선. DB30 발행과 PR #9 병합은 사용자 명시 승인 전 금지.
- Skill1 원문 조사 문서는 A30까지 존재한다. A1~A30 합계는 후보 행 2,198 / 원문 발췌 2,224 / 정확 문구 변형 477이다. 이 값은 근거 인벤토리이지 의미 검증·엔진 구현 완료량이 아니다. A31은 Skill1만 필터링한 후보 빈도 262~271위로 이어간다. Skill2와 혼합 금지.
- FM-OFFLINE PR #28: https://github.com/dragonslayers-k/FM-OFFLINE/pull/28 — HEAD `4f19702fc0fccc7a1651ddf5bd09257e24162402`, open/draft/unmerged. Actions #129 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41935871522. JS 규칙 테스트, Python 변환기 검사, Android Debug APK 빌드, APK 패키지/ZIP 검증과 산출물 업로드가 성공했다. 이 run은 선택형 DB29 카드팩·에뮬레이터 검증을 실행하지 않았으므로 실제 카드팩 설치·대전 검증 성공으로 간주하지 않는다.
- PR #28에는 불변 전투 이벤트 레코드·결정적 큐와 검증된 카드 영역 이동 primitive가 들어 있다. 이것은 효과 실행 기반이며 모든 카드 효과가 이벤트에 연결된 것은 아니다. 별도 PR #29 변경은 #28에 통합 후 중복 방지를 위해 닫았다.

### 기존 순차 계획을 병렬 진행으로 전환

DB 의미 조사가 끝날 때까지 엔진 개발을 대기시키지 않는다. 독립 작업은 동시에 진행한다.

1. **T 원본/필드 감사:** 카드 15,350장·55개 필드·이미지·URL의 원본 보존과 카드 ID별 누락/빈값/미적용/미확인 분류.
2. **T Skill1/Skill2:** A31 이후 Skill1 근거 배치, Skill2 미확보 8행 복구, 매뉴얼·카드 원문 교차 검증. 두 스킬 필드는 분리.
3. **T 효과/비용:** 저신뢰 효과, hybrid 52, NCS/BONUS 779, 수식·분기·소울/LP/유지비 의미를 병렬 검증. 기존 수치는 최신 재산출 전까지 기준 스냅샷으로만 사용.
4. **APK 공통 엔진:** 이벤트 dispatch, 대상 선택, 재진입/순환 방지, zone owner/capacity, 상태 snapshot, 영구·임시 능력치, 소환/복제/장착 primitive를 독립 테스트.
5. **APK 규칙 핸들러:** Manual authority 규칙 및 카드별 원문 근거가 확보된 항목부터 구현. 근거 없는 후보는 계속 non_executable.
6. **T↔APK 데이터팩 계약:** SQLite→converter→manifest→importer 간 카드 필드, enum, provenance, executable gate, 버전·해시 일치 테스트.
7. **통합 검증:** 변경 묶음의 focused tests 후 필요한 시점에 DB29 전체 감사, 데이터팩 import, emulator, 고정 시드 대전 검증을 묶어 수행.

### 속도·CI 운영 규칙

- 독립 트랙을 병렬 진행하고 동일 기능의 중복 PR을 만들지 않는다. 상호 의존 코드는 통합 PR에 묶는다.
- 관련 변경과 focused tests를 한 번에 묶고, 같은 SHA에서 통과한 Actions를 반복 실행하지 않는다.
- PR에서는 경량 회귀 테스트 우선. 전체 DB audit·크롤링·이미지 다운로드·에뮬레이터 검증은 실제 통합 시점에 필요한 만큼만 수행한다.
- 실패 시 로그의 최초 실패 step을 수정한 뒤 재실행한다. 취소는 실패로 집계하지 않으며 후속 성공이 동일 SHA/변경을 포함하는지 확인한다.
- 진척은 문서 수가 아니라 원문 근거 확보 / 의미 검증 / 실행 handler / 회귀 테스트 / 통합 검증으로 분리 보고한다.
- DB29·Release 29는 불변, DB30 미발행, PR #9와 PR #28 미병합 원칙을 유지한다.

다음 상태 보고는 T/APK 각각의 HEAD SHA, PR 상태, Actions run ID/conclusion, 후보 원문 누계, 의미 검증 수, 실행 handler 수, 통과 테스트 수, 미확인 backlog를 구분한다. Actions 성공은 실제 실행된 job 단계의 성공으로만 보고한다.


## 2026-11-05 추가 갱신 — Skill1 A31 / APK 전투 이벤트 연결

### Skill1 A31 완료

- 기준 산출물: CardDB Actions #430의 semantic-review artifact `13312586416` 안의 `gap-reports/inferred-skill-report.jsonl`. 원본에서 `source_field == Skill1`만 추출했고 Skill2는 제외했다.
- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a31-2026-11-05.md`
- 범위: 빈도순 262~271위 10개 Skill1 그룹. 퍼니쉬먼트, 페이탈더스트, 포레스트콜링, 플라워그로우, 피어스윕, 혼돈의꿈, 혼령매료, 황폐화, 흡혈확산, 히어로크라잉.
- A31: 20 후보 행 / 23 원문 발췌 / 14 정확 문구 변형.
- A1~A31: **2,218 후보 행 / 2,247 원문 발췌 / 491 정확 문구 변형**.
- 포레스트콜링은 공격 시 히어로 카운터와 히어로 능력 사용 효과를 분리한다. 혼령매료의 애머시스트 능력부여 설명은 전투 효과에서 제외한다. 나머지 후보도 조건·대상·순서·지속 검증 전까지 pending/non_executable이다.
- 이 누계는 원문 후보 인벤토리이며 의미 검증이나 APK 실행 구현 완료량이 아니다.

### APK PR #28 — 전투 이벤트 실흐름 연결

- PR #28의 기존 event queue/zone transfer 기반 위에 실제 게임 state의 `combatEventQueue`를 초기화하도록 연결했다.
- 유닛 파괴 성공 시 `unit_destroyed` 이벤트를 1회 기록한다. 소유자, 원인(effect/combat), 원본 공격자, 대상 인스턴스, 파괴 당시 필드 위치, 파괴 전 스탯 snapshot, 장착 아이템 요약을 보존한다.
- 직접 공격과 유닛 간 공격 종료 시 `unit_attack_resolved` 이벤트를 기록한다. 공격자/대상 snapshot, 피해량, 직접 공격 여부, 방어 유닛 생존 여부를 payload로 남긴다.
- 영역 이동 검증 실패 시 파괴 이벤트를 발행하지 않고 원본 유닛을 보존한다. 이벤트는 현재 관찰/기록 기반이며 카드 효과 구독·실행을 자동 활성화하지 않는다.
- Actions #131은 새 회귀 테스트의 lazy queue 가정 오류로 실패(118 pass / 1 fail)했다. 실패 원인은 게임 규칙 변경이 아니라, transfer 거부 경로에서 queue가 아직 생성되지 않았는데 테스트가 queue를 직접 참조한 것이다. 테스트를 optional queue 검사로 수정했고 Actions #132에서 재검증 중이다.
- #132 성공 전까지 이 변경은 테스트 완료로 보고하지 않는다. PR #28은 open/draft/unmerged 유지.

### 즉시 다음 작업

1. Actions #132의 JS 테스트, converter, Android 빌드 및 package 검증 결과 확인. 실패 시 최초 실패 테스트/step만 수정.
2. 통과 후 공격 이벤트의 경계 케이스(직접 공격, 무효 비용, 방어 유닛 파괴, 대상 없음) 회귀 테스트를 보강한다.
3. 이벤트 subscriber/handler를 분리하고, source-card verified 상태의 카드 규칙만 등록하는 fail-closed gate를 추가한다.
4. Skill1 A32는 원본 artifact에서 Skill1 전용 빈도순 272~281위로 이어간다. A31의 2,218/2,247/491 누계를 기준으로 갱신한다.


## 상태 정정 및 누적 갱신 — A32 / APK #132 (2026-11-05)

이 항목은 위 A31 시점의 “#132 재검증 중” 문구를 최신 결과로 대체한다.

- A32 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a32-2026-11-05.md`. Skill1 빈도순 272~281위 10개 단일 후보 그룹을 카드 ID별 원문으로 기록했다.
- A32: 10 후보 행 / 10 원문 발췌 / 10 정확 문구 변형.
- A1~A32 최신 누계: **2,228 후보 행 / 2,257 원문 발췌 / 501 정확 문구 변형**.
- APK Actions #132 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41937261537. JS 규칙 테스트, Python converter 검사, Android Debug APK build, APK application ID/signature/ZIP 검증, artifact upload 전 단계 성공.
- #131 실패(118 pass / 1 fail)는 queue lazy-init 상태를 가정한 테스트 assertion 오류였으며, assertion 수정 후 #132에서 성공했다. 취소된 #130은 실패로 집계하지 않는다.
- APK PR #28 최신 확인 SHA `81ef0d872917ad8aa1122e9609020e006cdd68d6`, open/draft/unmerged. #132는 emulator/실제 대전/DB29 카드팩 통합 테스트를 실행하지 않았으므로 이 세 항목은 미검증이다.
- 다음 Skill1 배치는 A33, 원본 빈도순 282~291위. Skill1/Skill2 분리 및 카드별 근거/비실행 게이트 유지.


## Skill1 A33 누적 반영 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a33-2026-11-05.md`.
- 범위: Skill1 빈도순 282~291위 10개 후보 그룹. 개화하는소질, 거대화, 거짓된풍요, 검은저울, 검의주인, 게놈뮤테이션, 겨울의노래, 경국지색, 경험전달, 계승의식.
- A33: **10 후보 행 / 12 원문 발췌 / 12 정확 문구 변형**. 개화하는소질은 evidenceCount 0이므로 효과 원문 미확보로 명시하고 해석하지 않는다.
- A1~A33 누계: **2,238 후보 행 / 2,269 원문 발췌 / 513 정확 문구 변형**.
- 거대화/거짓된풍요의 히어로 카운터와 능력 발동, 경국지색의 미확인 `xC1`, 개화하는소질 원문 누락은 각각 별도 미해결 항목이다. 근거 없는 자동 승격 금지.
- APK PR #28 검증 기준은 Actions #132 성공 및 SHA `81ef0d872917ad8aa1122e9609020e006cdd68d6`다. 다음 단계는 이벤트 경계 회귀 테스트와 source-verified 구독자 gate이며, 실제 에뮬레이터/DB29 통합은 별도 미검증 상태다.


## A34 및 APK Actions #133 통과 갱신 (2026-11-05)

- A34 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a34-2026-11-05.md` — Skill1 빈도순 292~301위 10개 그룹.
- A34: 10 후보 행 / 14 원문 발췌 / 14 정확 문구 변형.
- A1~A34 최신 누계: **2,248 후보 행 / 2,283 원문 발췌 / 527 정확 문구 변형**. 근거 인벤토리 수치이며 의미 검증/실행 구현 완료량이 아니다.
- APK Actions #133 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41937577446. JS 122개 규칙 테스트(기존 119 + attack event 경계 3), converter, Android Debug APK 빌드, application ID/signature/ZIP 검증, APK artifact 업로드 성공.
- #133에서 확인된 이벤트 순서: 방어 유닛이 파괴되는 공격은 `unit_destroyed`가 먼저, `unit_attack_resolved`가 뒤에 큐에 기록된다. 직접 공격은 유닛 대상 없이 attack-resolved 이벤트를 기록한다.
- PR #28은 최신 검증 SHA `52dcca2167b5fadc977c0eef30ccd2994ca481de`에서 Actions #133 성공, open/draft/unmerged. 선택형 DB29 data pack build와 emulator는 이 run에서 skipped였으므로 실제 카드팩/에뮬레이터 통합은 별도 검증 대상으로 남는다.
- 다음 엔진 단계는 이벤트 subscriber/dispatcher의 fail-closed 등록 계약과 중복 등록/순서/격리 테스트다. 카드 효과 실행은 해당 카드의 승인된 mapping/authority/execution tuple을 만족할 때만 연결한다.


## Skill1 A35 누적 반영 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a35-2026-11-05.md`.
- 범위: Skill1 빈도순 302~311위 10개 후보 그룹. 괴팍한수집욕, 구원자의인정, 군주의위엄, 궁극의무기, 궁극의방어구, 권능, 그레이브파워, 그린그로우, 그린랜드, 그린코인토스.
- A35: **10 후보 행 / 12 원문 발췌 / 12 정확 문구 변형**. 그레이브파워(다브노자에, 13010226605)는 후보 ID/라벨만 확인됐고 원문 발췌 0건으로 기록했다.
- A1~A35 누계: **2,258 후보 행 / 2,295 원문 발췌 / 539 정확 문구 변형**.
- 모든 원문 미확보/조건 미확정 후보는 pending/non_executable. 히어로 카운터와 능력 사용, 카드 이동/복사/생성, 코인 영구/임시 변경은 별도 규칙으로 검증한다.

## APK event dispatcher 단계 착수

- `createCombatEventDispatcher`를 추가해 이벤트별 subscriber 등록, 큐 drain 후 dispatch, 등록 순서 보존, handler별 event snapshot 격리를 지원한다.
- 등록 gate는 임의의 `verified=true`가 아니라 기존 규칙 catalog의 허용 ID와 상태 tuple을 함께 확인한다: Skill1은 `manual_verified + manual + known Manual rule ID`, Skill2는 `source_card_verified + card_source + source-card-rule-implemented + known Skill2 rule ID`만 허용한다. community candidate/unknown ID는 거부한다.
- 테스트는 candidate/unknown 등록 거부, 두 권한 채널의 정상 등록, 중복 구독 거부, 순서/sequence 보존, handler event 변형이 원본 이벤트에 전파되지 않음을 확인한다.
- 이 단계는 subscriber infrastructure다. 아직 신규 카드 효과 handler를 등록하지 않았고 기존 공격 로직과 중복 실행하지 않는다. Actions #135 검증 중이므로 성공 전까지 통과로 보고하지 않는다.


## A36 및 APK event dispatcher 검증 갱신 (2026-11-05)

- A36 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a36-2026-11-05.md` — Skill1 빈도순 312~321위.
- A36: 10 후보 행 / 10 원문 발췌 / 10 정확 문구 변형.
- A1~A36 누계: **2,268 후보 행 / 2,305 원문 발췌 / 549 정확 문구 변형**.
- APK Actions #135 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41937810008. Fail-closed dispatcher 코드와 테스트를 포함한 SHA `fc3f2b9f231a34449cda48f1c457ad9f6179b5eb`에서 JS 규칙 테스트, converter, Android Debug APK build, package verification 및 artifact upload가 통과했다.
- Dispatcher 등록은 허용된 Manual Skill1 rule ID + `manual_verified/manual`, 또는 허용된 Skill2 rule ID + `source_card_verified/card_source/source-card-rule-implemented` 조합만 허용한다. community candidate, unknown rule, duplicate subscription은 거부한다.
- 이벤트 dispatch는 이벤트 순서와 sequence를 유지하고 handler마다 복사본을 전달한다. handler의 payload 수정이 원본 queued event에 전파되지 않는 테스트가 통과했다.
- 아직 dispatcher에 새 카드 효과 handler를 연결하지 않았다. 이 변경은 안전한 구독 등록/전달 기반이며 카드 효과 구현 완료로 집계하지 않는다.
- PR #28 최신 검증 SHA `fc3f2b9f231a34449cda48f1c457ad9f6179b5eb`, open/draft/unmerged. 선택형 DB29 data pack과 emulator 검증은 미실행.
- 다음 단계: 이벤트 dispatcher를 game state의 controlled drain point와 연결하되, battle resolution 단계/중복 처리/재진입 방지 계약을 먼저 테스트한다. 카드별 handler는 source/Manual authority와 카드 ID 매핑이 검증된 것부터 단위별로 연결한다.


## A38 및 APK controlled dispatch 검증 갱신 (2026-11-05)

- A38 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a38-2026-11-05.md` — Skill1 빈도순 332~341위.
- A38: 10 후보 행 / 12 원문 발췌 / 12 정확 문구 변형. 눈덩이연타와 다크아레아는 각각 카드 ID는 확인했지만 원문 발췌 0건으로 비실행 유지.
- A1~A38 누계: **2,288 후보 행 / 2,328 원문 발췌 / 572 정확 문구 변형**.
- APK Actions #136 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41938282568. Controlled drain integration과 경계 테스트 포함 SHA `ce9ff9d5b4aed6c4bc048fce4fc56230eba75c34`의 JS/converter/Android build/package 검증 통과.
- `attachCombatEventDispatcher`로 dispatcher를 게임 state에 명시적으로 연결할 수 있다. `resolveUnitAttack`는 공격 완료 시점에, `applyEffect`는 효과 처리 완료 시점에 대기 이벤트를 한 번 drain/dispatch한다. dispatcher가 연결되지 않은 기존 경로는 이벤트를 queue에 보존한다.
- Subscriber가 dispatch 중 새 이벤트를 enqueue하면 현재 drain에 재귀 포함하지 않고 다음 명시적 처리 경계까지 대기한다. 신규 카드 효과는 아직 등록하지 않았고 fail-closed gate 유지.
- PR #28 검증 SHA `ce9ff9d5b4aed6c4bc048fce4fc56230eba75c34`, open/draft/unmerged. #136에서도 emulator와 선택형 DB29 data pack 검증은 skipped.


## A42 및 APK dispatcher 안정화 갱신 (2026-11-05)

- A42 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a42-2026-11-05.md` — Skill1 빈도순 372~381위.
- A42: 10 후보 행 / 9 원문 발췌 / 9 정확 문구 변형. 매직펌프킨은 원문 발췌 0건.
- A1~A42 누계: **2,328 후보 행 / 2,371 원문 발췌 / 615 정확 문구 변형**.
- APK Actions #139 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41938848148. atomic multi-event subscription validation 수정본에서 JS 규칙 테스트, converter, Android Debug APK build, APK package validation 모두 성공.
- #137/#138 실패는 dispatcher 로직의 회귀가 아니라 테스트 fixture가 중복 조건과 subscriber 결과 수를 잘못 가정한 것이었다. #139에서는 동일 rule ID가 기존 event type에 구독된 상태에서 다중 event type 등록을 시도하도록 fixture를 바로잡았고, 등록 실패 시 앞선 event type에 부분 등록이 남지 않는 것을 검증했다.
- Dispatcher는 reentrant drain을 차단한다. handler가 현재 dispatch 중 새 이벤트를 추가하거나 nested flush를 시도해도 현재 batch를 재귀 처리하지 않고 다음 명시적 boundary에서만 전달한다.
- PR #28 최신 검증 SHA `b1b545690009c5ecaaab7af088b5596ac9ad2152`, open/draft/unmerged. 카드 효과 handler 등록/실행은 여전히 보류; 실제 DB29 pack/emulator 검증도 미실행.


## A43 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a43-2026-11-05.md` — Skill1 빈도순 382~391위 10개 그룹.
- A43: **10 후보 행 / 11 원문 발췌 / 11 정확 문구 변형**. 메탈아레아(16113028637)는 원문 발췌 0건.
- A1~A43 누계: **2,338 후보 행 / 2,382 원문 발췌 / 626 정확 문구 변형**.
- 이 누계는 원문 후보 수치다. 카드별 의미 검증, source-card/manual 승격, 실행 handler, APK regression 수치와 혼합 금지.
- APK PR #28 최신 검증은 Actions #139 성공 / SHA `b1b545690009c5ecaaab7af088b5596ac9ad2152`. Dispatcher는 verified mapping gate, atomic registration, no reentrant dispatch까지 통과했다. 실제 카드별 subscriber handler 등록은 아직 보류한다.


## A44 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a44-2026-11-05.md` — Skill1 빈도순 392~401위.
- A44: **10 후보 행 / 14 원문 발췌 / 14 정확 문구 변형**.
- A1~A44 누계: **2,348 후보 행 / 2,396 원문 발췌 / 640 정확 문구 변형**.
- 무구소환/무구장착은 동일 전쟁의여신 이름 계열이지만 장착 아이템 대응이 반대이므로 별도 규칙으로 보존한다. 묘비명파멸/미러메이즈의 히어로 카운터와 능력 사용은 분리한다.
- APK PR #28 기준: Actions #139 성공 / SHA `b1b545690009c5ecaaab7af088b5596ac9ad2152`. Fail-closed dispatcher, atomic subscription registration, reentrant dispatch guard가 통과했다. 아직 신규 효과 handler는 등록하지 않았다.


## A45 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a45-2026-11-05.md` — Skill1 빈도순 402~411위.
- A45: **10 후보 행 / 9 원문 발췌 / 9 정확 문구 변형**. 배틀타워(이엔루와르, 13010226609)는 원문 발췌 0건.
- A1~A45 누계: **2,358 후보 행 / 2,405 원문 발췌 / 649 정확 문구 변형**.
- 후보 인벤토리는 DB29의 Skill1 전용 순위 기준으로 계속 이어간다. 원문 발췌 0건, tooltip 수정 예정, 정의가 불명확한 능력은 실행 후보와 분리해 기록한다.
- APK PR #28의 마지막 검증은 Actions #139 성공 SHA `b1b545690009c5ecaaab7af088b5596ac9ad2152`. 이후 변경은 아직 없으며, PR은 open/draft/unmerged다.


## A46 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a46-2026-11-05.md` — Skill1 빈도순 412~421위.
- A46: **10 후보 행 / 13 원문 발췌 / 13 정확 문구 변형**.
- A1~A46 누계: **2,368 후보 행 / 2,418 원문 발췌 / 662 정확 문구 변형**.
- NCS 소울 소비, 상태 해제 시 파괴, 코인률 50% 변경, 공격/방어 턴 분기는 각기 별도 미검증 규칙으로 남긴다.
- APK PR #28 마지막 성공 검증은 Actions #139 / SHA `b1b545690009c5ecaaab7af088b5596ac9ad2152`. 다음 focused test는 spell/effect transaction 종료 시 destroy event가 안전하게 dispatch되는지 검증한다.


## A48 및 APK effect-dispatch 경계 검증 (2026-11-05)

- A48 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a48-2026-11-05.md` — Skill1 빈도순 432~441위.
- A48: **10 후보 행 / 12 원문 발췌 / 12 정확 문구 변형**. 빅샌드트랩(아피아타, 13010226610)은 원문 발췌 0건.
- A1~A48 누계: **2,388 후보 행 / 2,445 원문 발췌 / 689 정확 문구 변형**.
- APK Actions #140 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41939595186. Spell/effect transaction 종료 시 destruction event dispatch 테스트를 포함한 SHA `161b06e02c11d99ee950e4ea3c33890ad7076ed9`에서 JS 규칙 테스트, converter, Android Debug APK, APK ID/signature/ZIP 검증, artifact upload 전 단계 통과.
- `applyEffect`로 적 유닛이 파괴되면 `unit_destroyed(cause=effect)` 이벤트가 효과 처리가 끝난 시점에 dispatch되는 것을 검증했다. 전투 공격의 dispatch boundary와 구분한다.
- PR #28은 open/draft/unmerged. #140 역시 실제 DB29 data pack 설치/에뮬레이터/대전 테스트는 실행하지 않았다.


## A49 및 semantic-review adjudication pass 3 (2026-11-05)

### Skill1 A49
- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a49-2026-11-05.md` — Skill1 빈도순 442~451위.
- A49: **10 후보 행 / 9 원문 발췌 / 9 정확 문구 변형**. 샤이닝스파크는 원문 0건, 생명의꽃은 설명 문장으로 분리.
- A1~A49 누계: **2,398 후보 행 / 2,454 원문 발췌 / 698 정확 문구 변형**.

### Semantic review source-context adjudication pass 3
- 신규 문서: `data/reviews/fm1-carddb-29-semantic-review-adjudication-pass-3-2026-11-05.md`.
- Input queue 41 unique patterns / 54 occurrences를 카드 ID별 TextBase/TextExtra 문맥으로 재판정했다.
- **39 patterns / 52 occurrences**의 문맥 판정을 완료: 22개 디스인첸트 공통 정의 참조, 7개 아레아/히어로 카운터 참조, 2개 카드 pool, 2개 소환 프로필, 2개 named variant, 4개 조건/분기/프로필 문맥.
- **2 patterns / 2 occurrences**는 미해결 유지: 펭귄여왕투척의 `cwda!` opaque annotation, 고대의검의 단독 `상` fragment. 둘 다 실행 효과로 해석하지 않는다.
- 디스인첸트 22 패턴은 공통 TextExtra 정의를 참조하는 annotation이며 각 카드의 TextBase 효과와 분리한다. 7개 아레아/마레마는 TextBase/Extra 명칭 불일치까지 원문 그대로 보존한다.
- 이 adjudication은 source context/참조 분류를 정리한 overlay다. 실행 handler/테스트 완료로 계산하지 않고 DB29 원본을 수정하지 않는다.
- APK Actions #140 성공: https://github.com/dragonslayers-k/FM-OFFLINE/actions/runs/41939595186. Effect transaction 종료 시 destruction dispatch 테스트가 통과했다. PR #28 open/draft/unmerged.


## A50 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a50-2026-11-05.md` — Skill1 빈도순 452~461위.
- A50: **10 후보 행 / 9 원문 발췌 / 9 정확 문구 변형**. 서먼헌트(디멘션헌터, 13010241409)는 원문 발췌 0건.
- A1~A50 누계: **2,408 후보 행 / 2,463 원문 발췌 / 707 정확 문구 변형**.
- 카드 생성/소환과 랜덤 pool, NCS 소울, 핸드 공간 조건, 상대 유닛 장착은 각각 별도 규칙으로 유지하고 원문·대상·실패 경계가 확인되기 전까지 non_executable.
- Semantic-review pass 3의 41-pattern/54-occurrence adjudication은 별도 source-context overlay이며 A50 Skill1 누계와 합산하지 않는다.


## A51 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a51-2026-11-05.md` — Skill1 빈도순 462~471위.
- A51: **10 후보 행 / 11 원문 발췌 / 11 정확 문구 변형**. 성화전달은 원문 0건, 성실한준비/성지화는 효과 본문이 없는 도입 문구로 구분.
- A1~A51 누계: **2,418 후보 행 / 2,474 원문 발췌 / 718 정확 문구 변형**.
- 소울 감소/차이 피해, 히어로 카운터, 다음 턴 자원 변경은 각각 독립 규칙으로 유지하고 원문 수식/턴 경계 테스트 전까지 실행하지 않는다.


## A52 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a52-2026-11-05.md` — Skill1 빈도순 472~481위.
- A52: **10 후보 행 / 12 원문 발췌 / 12 정확 문구 변형**.
- A1~A52 누계: **2,428 후보 행 / 2,486 원문 발췌 / 730 정확 문구 변형**.
- 상태 상위 단계, 특정 마법 효과 override, 양측/핸드/필드 대상, 카드 이동, 소울 생성은 서로 다른 effect semantics로 분리하고 원문·테스트 전까지 비실행.
- 저장소 상태 재확인: T PR #9 open/unmerged, base main; APK PR #28 open/draft/unmerged, 최신 head `161b06e02c11d99ee950e4ea3c33890ad7076ed9`, Actions #140 성공.


## A53 순위 원본 정렬 정정 (2026-11-05)

- A53 파일을 원본 artifact의 `Counter.most_common()` 순위 482~491위로 다시 맞췄다. 이전 초안은 다른 정렬 결과의 그룹명을 잘못 배치했으므로 대체했다.
- 정정된 A53: 스컬윙포스, 스킬마스터리, 스킬카피, 스페이드, 스피릿스톰, 슬픈자의영광, 시드웨폰, 시련의폭풍, 시체부활, 시체파기.
- 정정 후 A53 누계는 10행 / 11발췌 / 11변형, A1~A53 누계 2,438행 / 2,497발췌 / 741변형으로 동일하다.
- 이후 모든 배치의 순위는 원본 report의 Counter insertion order / most_common()을 기준으로 고정한다. 이름순 정렬로 순위를 다시 매기지 않는다.


## A55~A56 누적 조사 갱신 (2026-11-05)

- A55 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a55-2026-11-05.md` — 원본 빈도순 502~511위. 10 후보 행 / 13 원문 발췌 / 13 정확 문구 변형.
- A56 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a56-2026-11-05.md` — 원본 빈도순 512~521위. 10 후보 행 / 10 원문 발췌 / 10 정확 문구 변형.
- A1~A56 누계: **2,468 후보 행 / 2,533 원문 발췌 / 777 정확 문구 변형**.
- A53은 별도 정정본에서 원본 Counter.most_common() 482~491위(스컬윙포스~시체파기)로 교체했다. 이후 순위는 원본 report insertion order 기준으로 고정하며 이름순 정렬을 사용하지 않는다.
- 카드별 effect 후보는 source evidence inventory 상태다. 랜덤 기술, 코인/DP 기호, 소울/유지비, 카드 삭제·소환·소유권 이동은 의미 검증 및 regression test 전까지 비실행.


## A57 누적 조사 갱신 (2026-11-05)

- 신규 문서: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a57-2026-11-05.md` — 원본 빈도순 522~531위.
- A57: **10 후보 행 / 11 원문 발췌 / 11 정확 문구 변형**. 어스아레아(16113028638)는 원문 0건.
- A1~A57 누계: **2,478 후보 행 / 2,544 원문 발췌 / 788 정확 문구 변형**.
- A53 정정본은 원본 Counter.most_common() 순위를 사용한다. 이후 모든 배치도 동일한 원본 순위로 산출한다.
- 어스브레스/어스스크림의 방체 단계별 피해, 이름 수 산식, AP/DP 기호, 지형 생성은 공식 수식/실행 테스트 전까지 비실행.


## A58~A59 누적 조사 갱신 (2026-11-05)

- A58: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a58-2026-11-05.md` — 532~541위, 10 후보 행 / 13 원문 발췌 / 13 정확 문구 변형.
- A59: `data/reviews/fm1-skill1-source-evidence-manifest-batch-a59-2026-11-05.md` — 542~551위, 10 후보 행 / 10 원문 발췌 / 10 정확 문구 변형.
- A1~A59 누계: **2,498 후보 행 / 2,567 원문 발췌 / 811 정확 문구 변형**.
- A53 정정 원칙에 따라 원본 Counter.most_common() 순위 유지. card_text 설명, 유닛 고유능력, Skill1 effect, Skill2/방어기술을 섞지 않는다.
- coin rate/코인 제거, 기술 수 기반 소환, 카드 영역 이동, NCS 소울 교체는 source context와 runtime validation을 분리한다.
