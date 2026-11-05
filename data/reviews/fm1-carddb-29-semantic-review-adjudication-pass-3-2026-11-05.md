# DB29 semantic-review adjudication — pass 3 (source-context complete / reference normalization)

## 기준 및 범위

- Input: 2026-11-04 semantic review context artifact의 `semantic-review-pending-queue.jsonl` (41 unique patterns / 54 occurrences).
- Evidence: 각 occurrence의 카드 ID, `TextBase`, `TextExtra`, clause index, source URL.
- 이 문서는 원문 문맥을 기준으로 기존 pending 분류를 검토한 추가 판정이다. DB29 source field를 수정하지 않으며 DB30 발행·runtime 승격을 승인하지 않는다.
- Source context와 runtime semantics를 분리한다. 문맥이 복원되어도 수치/순서/대상/실패 처리 테스트 전에는 `pending_engine_test` 또는 `non_executable_reference` 상태다.

## 결과 요약

| 판정 | 고유 패턴 | occurrence | 의미 |
|---|---:|---:|---|
| Shared disenchant rule reference resolved | 22 | 23 | 22개 문구는 공통 TextExtra 정의 참조/분류표시. 독립 효과가 아님 |
| Named area / hero-counter reference resolved | 7 | 7 | 아레아/마레마 3카운터 히어로 능력 참조 |
| Card-pool reference resolved | 2 | 8 | 지정 카드 목록. 독립 효과가 아닌 선택 pool/reference |
| Summon profile reference resolved | 2 | 8 | 에카마엘 7종 공통 프로필과 모래형상 프로필을 분리 |
| Named card-variant reference resolved | 2 | 2 | C형 변형 카드명/전환 참조 |
| Condition/branch/profile context resolved | 4 | 4 | 라이트닝버그, 녹음의습격, 황제의일갈, 추억 |
| Opaque source annotation pending | 1 | 1 | `cwda!`는 의미 미확인 |
| Incomplete source fragment pending | 1 | 1 | `상`은 문장 중간의 절단/포맷 잔여 가능성, 단정 불가 |
| **합계** | **41** | **54** | **39개 패턴 / 52 occurrence의 source context 판정 완료, 2개 / 2 occurrence 미해결** |

## 1. 공통 디스인첸트 규칙 참조 — 22 patterns / 23 occurrences

다음 22 pattern ID는 카드별 TextBase의 `◇ 디스인첸트 카드` 표기 또는 동일 명칭 변형과, TextExtra의 공통 정의를 확인했다. 이 태그/인용문을 카드 고유 효과로 다시 파싱하지 않는다.

공통 정의 원문은 `fm1-disenchant-shared-rule-v1.json` 및 2026-11-05 디스인첸트 focused validation batch와 연결한다. 핵심 정의는 디스인첸트 카드가 필드에 존재할 때 인첸트 발동 페이즈에 카드 수만큼 양측 필드 첫 인첸트부터 순서대로 파괴한다는 것이다. 개별 디스펠의 TextBase 효과는 각각 별도 규칙으로 남긴다.

Pattern IDs:
- `5bbd71cd5e652d02` — 화룡의분노(3062730277), 지축변경(4111730687)
- `839e622dec75b37a` — 스펠카운터(4062530566)
- `cf496fbe1a4ad7b0` — 숙명(12070432965)
- `a89c167e47d6d1a6` — 이그조스트리(4121530702)
- `ac99e5a38665171f` — 성직자암살(4072130593)
- `7824c438fd6b1a5c` — 천계의심판(4111730690)
- `de567b286c4932e6` — 청사의시선(12070432961)
- `315583fe67130afe` — 연행(12070432959)
- `e413b817f58df766` — 숨막히는공격(12070432963)
- `1c167e2486441070` — 매직블랙홀(7020731304)
- `83d8fccfa54ce720` — 회오리장막(7020731319)
- `ac655a5a0d2e8f7c` — 고귀한생명(12070432969)
- `b940d63fea79ba65` — 사막의감시(12070432967)
- `e24af7068b6972ba` — 칠색조의가호(14012233385)
- `dc1c1158b89fec26` — 킬링타임(6120631255)
- `021bd824961a80e4` — 복수의준비(12070432957)
- `e5a1a195f573cc15` — 불가침조약(4111730684)
- `0e5b31a93f6d48f2` — 그리핀출몰(9020431914)
- `c0399da6ece0425c` — 파이어플래쉬(4062530563)
- `bd862ece40b0c729` — 프로즌노바(3062730281)
- `369637133f626c14` — 그룹차징(5090730915)
- `e6d9caade4df19f0` — 시스카이(15042933603)

**별도 보존:** 각 카드의 TextBase effect, 카드명 뒤 대괄호 안의 lore/flavor 문장은 공통 디스인첸트 정의와 합치지 않는다. 예외로 재생성 효과가 있는 디스펠의 성공 판정, 인첸트 슬롯 처리, 양측 파괴 순서와 카운트 snapshot은 엔진 검증 대상이다. 모든 23 occurrence는 runtime pending.

## 2. Named area / hero-counter references — 7 patterns / 7 occurrences

각 카드의 TextBase에는 LP=0 시 AP/HP 및 hero point 증가가 있고, TextExtra에는 3카운터 사용 시 LP 1을 지불하고 백필드 지형을 교체하는 별도 능력이 적혀 있다. TextBase의 이름과 TextExtra의 이름이 다르게 표기된 항목도 있으므로 원문 문자열을 보존한다.

| Pattern ID | Card ID / name | TextBase label | TextExtra ability label |
|---|---|---|---|
| `f9049299119cb6b0` | 16112610278 스컬시티 | 다크마레마 | 다크아레아 |
| `327f4c47871c6609` | 16112610283 지나간자리 | 머스마레마 | 어스아레아 |
| `97934a59c18dd67c` | 16112610282 초복합연구실 | 메탈마레마 | 메탈아레아 |
| `28386de8f17ad3ee` | 16112610280 생환의도시 | 워터마레마 | 워터아레아 |
| `772e1ef990796eef` | 16112610279 강자의왕국 | 파이어마레마 | 파이어아레아 |
| `6b241c7fecddb732` | 16112610281 숲의안식처 | 포레스마레마 | 포레스아레아 |
| `9a33edf7012c9271` | 16112610284 클라우드시티 | 폴리아레아 | 홀리아레아 |

**판정:** 이 패턴들은 명명된 아레아/히어로 카운터 능력 참조로 문맥을 복원했다. 이름 alias를 자동 통합하지 않는다. LP 조건, 지형 교체 대상/순서, 영구성, hero point 연계는 별도 focused tests 전까지 pending.

## 3. Card-pool references — 2 patterns / 8 occurrences

- `b8ddb2d0e1f2521e` (7 occurrences): 엘리트아이바 계열 7장(14012227224~14012227230)의 코스튬체인지 기술에서 랜덤 장착 가능한 아이템 목록: 블러드본랜스, 루비소드, 레드아이스링, 네추럴링, 생명의물약, 번개의모래, 그리핀석상. 목록 자체는 pool data이며 효과는 적 1 파괴 → 아이템 미장착 아군 다음 행동가능 유닛에게 지정 아이템 랜덤 장착 → 일러스트/공격기술 변경이다. 코스튬리턴과 콜드윈터는 별도 effect/state.
- `5fe169892b95ee55` (1 occurrence): 사케크리에(13112727128)의 자연의분노 기술에서 롯트, 장생수, 맨이터롯트N, 이모탈트리, 손드트리, 뮤턴트엔트, 에인션트엔트 목록. 이는 조건부 소환 pool reference이며, 지형 교체 성공/실패와 상대 유닛 레벨 일치 조건을 별도 처리한다.

**판정:** 두 목록은 reference/pool로 문맥 복원. 이름을 임의로 정규화하거나 모든 pool 카드가 동등하게 선택된다고 추정하지 않는다.

## 4. Summon profiles — 2 patterns / 8 occurrences

- `1281196d90b8c905` (7 occurrences): 에카마엘 7장 키뇨엘/라드비엘/쿠두루스엘/피드엘/올피리엘/산치엘/마이엘. 1~3챕터, 같은 레벨·속성 무작위 구성, 랭크 카드 포함/이벤트 등급 제외, 에카마엘 지형 수 홀짝 보너스. 기존 Ecaemael profile catalog와 연결하되 후보 풀/제외 카드/무작위 구성은 별도 검증.
- `14f9984f95b70270` (1 occurrence): 모래의형상화(9010731883)의 모래형상 프로필. 야수/골렘/돌진공격, 소환 유소울=턴 일의자리, 무소울=십의자리, AP=소각장 유닛 수, DP=핸드 유닛 수, HP=백필드 지형 수, 최대 레벨 10. 에카마엘 프로필과 합치지 않는다.

**판정:** profile reference context complete. 실제 소환 계산/랜덤 후보/턴 수치 경계는 engine tests 전까지 pending.

## 5. Card variant references — 2 patterns / 2 occurrences

- `ac958ad20571c5bd` — 에네퍼브렌C: 에네퍼브렌의 섀도우오라(야수의습격) 사용 후 변형된 카드/기술 참조.
- `2e0e433bbc59c599` — 여왕엘류이드C: 여왕엘류이드의 섀도우오라(변화) 등으로 교체되는 variant 및 불안정한힘/환상 능력 참조.

**판정:** `C` suffix는 named variant reference로 문맥 확인. 별도 card ID를 추정해 만들지 않으며, 변형 전후 identity/instance/effect state를 runtime에서 검증해야 한다.

## 6. Condition / branch / profile context resolved — 4 patterns / 4 occurrences

- `ac59fb25a5696940` 라이트닝버그(8111923702): AP 1+ 공격, 대상이 장비/야수이면 중급중독 3턴. 상태 정의 HP-3. 만능능력 설명은 별도 metadata.
- `351525db0d5b2cbb` 녹음의습격(13071033261): 핸드+필드 Plant 유닛 distinct-name count, target level/공방체합 선택, 가시풀 장착·종족 변경·이동, distinct-name 5/6 분기. 기존 source-expansion pass2 판정과 연결.
- `301c96ab44070fed` 황제의일갈(14030533415): 적 소각장 맨 위 마법을 deck point 50~150 조건으로 소환. 실패 조건은 해당 마법 부재 또는 아군 필드 공간 부족. 실패 시 유지비 1 이상인 아군 유닛 유지비 1 영구 제거. 두 실패 조건과 fallback branch를 별도 보존.
- `bfa9cd5ed2238e2c` 추억(11050432579): 아군 필드 마법학교 유닛이 1개 이상이고 모두 마법학교 소속일 때 조건부 이서리얼 소환. 유소울/무소울/AP/DP/HP/코인/일러스트는 TextExtra의 카운트 공식에 따름. 메를린 존재 분기는 별도 Growing 및 graveyard 이동. 기존 source-expansion pass2 판정과 연결.

**판정:** context-missing blocker 해소. 수치, target, status, failure, ordering tests 전까지 runtime pending.

## 7. Unresolved source fragments — 2 patterns / 2 occurrences

- `f41dfd55352a6ebd` 펭귄여왕투척(13010233113)의 `cwda!`: 주변 TextBase/TextExtra는 펭귄 유닛 이동, 속박, HP damage와 아나스타샤 예외를 설명하지만 이 token의 뜻은 확인할 수 없다. source annotation으로 보존하며 effect로 취급하지 않는다.
- `3c2d6ddb4a94f1f3` 고대의검(9071541048)의 `상`: TextExtra의 “AP1이상으로 공격시…” 뒤에 아이템빌드업 설명이 이어지는 곳에 남은 단독 조각이다. `상성` 또는 다른 단어의 절단이라고 단정하지 않는다. 원본 렌더링/수집기 HTML line break 확인 전까지 unresolved.

## 실행/데이터 반영 규칙

1. 원본 pending queue와 DB29 card text는 수정하지 않는다. 본 문서는 adjudication overlay다.
2. shared reference, card pool, named area/hero-counter, summon profile, card variant는 그 자체로 실행 가능한 효과가 아니다.
3. 실제 TextBase effect는 카드별 source mapping과 runtime handler/test를 별도로 가진다.
4. source context resolved는 semantic implementation complete와 다르다. engine test, ordering, card ID mapping, failure path가 통과해야만 execution gate를 변경한다.
5. DB29 immutable, DB30 미발행, main 미병합 원칙 유지.
