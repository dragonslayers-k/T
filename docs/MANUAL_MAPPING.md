# Manual.zip 분류·규칙 대응표

## 1. 기준 매뉴얼
Dropbox 원본: `/판마/Manual.zip` (약 5.1 MB, 2026-11-01 수정본). 전역 게임 규칙 추출본은 `data/rules/manual-global-gameplay-source.txt`, 구조화 카탈로그는 `data/rules/fm1-global-gameplay-catalog-v1.json`에 보존한다.

확인한 문서:
- `cardtype.htm`: 카드 종류
- `cardability.htm`: 유닛 능력 구분
- `soulcost.htm`: 소울 비용과 무속성 유지비
- `ready.htm`: 준비 단계, 지형·유닛·아이템·마법 관련 처리
- `gamerule.htm`: 게임 진행 및 승패 규칙
- `gamescreen.htm`: 화면·LP·지형 관련 설명
- `specialability.htm`: 특수 공격 기술 정의
- `coin.htm`, `deck.htm` 등 관련 규칙 문서

## 2. 카드 종류 대응 — 현재 정식 5종 분류

**현재 카드DB의 정식 분류는 지형·유니트·마법·아이템·인챈트의 5종이다.** 과거 `Manual.zip`의 `cardtype.htm`이 지형·유닛·아이템·마법 네 종류만 설명하는 것은 해당 매뉴얼의 작성 시점/판본을 반영한 역사적 자료로 취급한다. 이후 추가된 인챈트를 미분류·미지원 카드 유형으로 기록하지 않는다.

현재 분류의 기준은 FM LUNATIC의 최신 카드 분류 데이터(Firestore `Enum+Category`)와 현재 공개된 5종 카드 설명을 교차 확인한 결과다. 인챈트는 정식 다섯 번째 카드 유형이며, 효과 실행의 구현 여부와 카드 분류의 정식 여부는 서로 다른 검증 항목이다.

| 사이트 코드 | 정식 분류 | 영문 | 카드 수 | DB 상태 |
|---:|---|---|---:|---|
| 1 | 지형 | Land | 289 | 정식 분류 확정 |
| 2 | 유니트 | Unit | 8,633 | 정식 분류 확정 |
| 3 | 마법 | Magic | 3,857 | 정식 분류 확정 |
| 4 | 아이템 | Item | 1,748 | 정식 분류 확정 |
| 5 | 인챈트 | Enchant | 823 | 정식 5번째 분류 확정 |
| | **합계** | | **15,350** | |

### 인챈트의 현재 분류 정의

인챈트는 특정 슬롯에 일정 턴 동안 존재하면서 해당 슬롯에 놓인 카드에 특별한 능력을 부여하는 지속형 카드다. 일반적인 단독 사용 카드가 아니라 슬롯의 유닛·마법 등과 상호작용하는 개념이며, 대상 슬롯·발동 조건·지속시간·해제 조건은 카드별 원본 데이터와 규칙 근거를 이용해 별도로 검증한다. 알파오션처럼 유닛이 없어도 효과가 발동하는 예외도 원문 그대로 보존한다.

**중요:** 인챈트 823장은 카드 유형 측면에서 모두 정식 분류에 포함한다. 그중 개별 카드의 효과 실행이 미구현이거나 슬롯 의미가 완전히 해석되지 않은 경우에만 해당 효과/필드에 `manual_review` 또는 `effect_unmapped`를 부여한다. `manual_uncovered`를 카드 유형 자체에 부여하지 않는다.

분류 기준 참고:
- https://fmlunatic.com/cardlist
- https://www.namu.moe/w/판타지%20마스터즈
- https://www.readonly.wiki/w/판타지마스터즈

## 3. 속성·종족·소속
매뉴얼의 7대 속성 설명과 사이트 `Enum+SoulType`을 대응한다.
- DARK: 암흑
- FIRE: 불
- EARTH: 대지
- WATER: 물
- FOREST: 숲
- IRON: 금속
- LIGHT: 빛

무속성 소울(MU, RequireSoul 코드 81)은 매뉴얼에서 무속성 구슬로 설명되며, 소환 시 어떤 색으로도 지불할 수 있고 이후 매 준비 턴 유지비가 적용된다. NCS(82)와 BONUS(83)는 원본 enum 정체만 확인됐으며 매뉴얼에서 지불 의미를 확인하지 못했으므로 neutral/MU와 합치지 않는다. 종족(`RaceType`), 소속(`CompanyType`), 기타 타입(`EtcType`)은 사이트 enum 전체 값을 사전으로 보존한다. 매뉴얼에 모든 세부 코드의 설명이 없으면 임의로 의미를 만들지 않는다.

## 4. 유닛 능력·능력치·기술
매뉴얼 `cardability.htm`의 유닛 능력 구분에는 Gear, Magic, Beast 계열이 나온다. 현재 사이트의 `UnitType`은 기본값과 조합값을 포함하므로 원본 enum과 한국어 표시값을 함께 저장한다.

유닛의 AP, DP/DEF, HP와 코인 기술 관련 필드는 각각 분리한다. 사이트 `Skill1`/`Skill2` 사전은 매뉴얼 `specialability.htm`의 27개 특수 공격 기술 목록과 별도 체계로 유지한다. 이름이 비슷하다는 이유만으로 자동 통합하지 않는다. 카드 원문 설명 근거가 없는 24개 이름 기반 추정 기술은 `nameBasedGuess`, low confidence, `executable=false`로 유지한다. 전역 게임 규칙 15개는 별도 `game_rule_catalog` 항목으로 적재하며 카드 기술 enum과 혼합하지 않는다.

## 5. 소울 비용 코드 판독
사이트 원본 `RequireSoul`은 4문자 단위 토큰의 연결 문자열로 확인됐다. 각 토큰은 앞 2자리의 소울 종류 코드와 뒤 2자리의 수량으로 분리한다. 원본 문자열은 절대 덮어쓰지 않는다.

일반 색상/무속성 매핑:
| 코드 | 사이트 enum | 정규화 |
|---:|---|---|
| 11 | DARK | dark |
| 21 | FIRE | fire |
| 31 | WATER | water |
| 41 | FOREST | forest |
| 51 | IRON | iron |
| 61 | EARTH | earth |
| 71 | LIGHT | light |
| 81 | MU | neutral |
| 01 | NONE | 명시적 비용 없음(수량 00일 때) |

혼합 속성 코드 14종(12, 13, 14, 15, 22, 23, 24, 32, 33, 42, 43, 52, 53, 62)은 enum 색상 조합 정체를 해독하지만, 실제 지불 규칙(두 색 모두 요구/한쪽 대체 지불)은 독립 근거가 없어 `mapping_review`로 남긴다. 이전 PR 문서에 38개 사례와 14,282건을 교차 검증했다고 기재되어 있었으나, 재현 실행에서 참조 비용 행은 0건이었다. 카드 ID·원본 코드·기대 비용을 가진 검증 fixture가 다시 확보되기 전까지 `source_cross_validated`를 부여하지 않는다. NCS(82)와 BONUS(83)는 별도 토큰으로 저장하고, 지불·생성 의미는 `semantic_review`로 남긴다.

Release #27 전체 감사에서 15,350장의 RequireSoul 토큰 문자열은 모두 토큰 단위로 식별·파싱되었다(`soul_known=1`). 혼합 코드가 포함된 52장은 `mapping_review`, NCS 또는 BONUS가 포함된 779장은 `semantic_review`로 구분한다. 이 집계는 코드 구문과 enum 토큰 인식 결과이며, 혼합 조합의 독립 비용 대조나 특수 자원의 게임 규칙 검증, 카드 이미지와의 수동 대조가 완료됐다는 뜻은 아니다.

## 6. LP와 지형
사이트 `RequireLP`는 지형 289장에 존재하며 0부터 4까지의 값을 enum과 연결한다. **LP 0은 명시적 0으로 저장**하며 미상이나 누락으로 바꾸지 않는다. 현재 데이터에서 LP 0 지형은 72장이다.

매뉴얼의 `gamerule.htm` 요약은 LP 수만큼 지형을 배치한다고 설명하지만 `ready.htm` 상세 절차는 턴당 1장으로 적어 충돌한다. 이 내용은 `terrain_placement_limit_conflict` (`manual_conflict`, non-playable)로 양쪽 원문을 보존한다. LP 비용과 턴당 설치 제한을 임의로 하나로 합치지 않는다.

## 7. 텍스트와 효과
- `TextBase`: 카드 기본 텍스트 원문
- `TextExtra`: 추가 설명/보조 텍스트 원문
- 원문 HTML/개행을 보존하고, 검색용 plain text를 별도 생성한다.
- `TurnType`, `DurationType`, `Duration`은 각각 발동 시점·지속 유형·지속 수치로 분리한다.
- 효과를 실행 가능한 규칙으로 바꾸는 작업은 원문 수집과 별도의 검증 단계로 관리한다.

## 8. 전역 게임 규칙 및 검증 상태
`fm1-global-gameplay-catalog-v1.json`에는 매뉴얼 근거 전역 규칙 15개를 별도 적재한다. 여기에는 MU 유지비, 소울 부족 시 덱 파괴, 코인 표기/단일 굴림 공유, AP/DP/HP 기호, 준비/전투 순서, 덱 공격/패배 규칙이 포함된다. 매뉴얼 충돌 규칙은 `manual_conflict`로 남기며 15개 전역 규칙과 27개 특수 공격 기술 모두 엔진 검증 전까지 `pending_engine_test`, `playableByDefault=false`다.

`source_extracted`, `enum_mapped`, `enum_decoded`, `mapping_review`, `semantic_review`, `source_cross_validated`, `current_taxonomy_verified`, `manual_semantics_verified`, `image_verified`, `manual_review`, `effect_unmapped`, `manual_conflict` 상태를 구분한다. 자동 추출만 된 값은 수동 검증 완료로 표시하지 않는다. `current_taxonomy_verified`는 다섯 카드 유형이 현재 분류 사전과 일치한다는 뜻이며, 카드별 효과 구현 완료를 의미하지 않는다.
