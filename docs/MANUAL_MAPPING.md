# Manual.zip 분류·규칙 대응표

## 1. 기준 매뉴얼
Dropbox 원본: `/판마/Manual.zip` (약 5.1 MB, 2026-11-01 수정본)

확인한 문서:
- `cardtype.htm`: 카드 종류
- `cardability.htm`: 유닛 능력 구분
- `soulcost.htm`: 소울 비용과 무속성 유지비
- `ready.htm`: 준비 단계, 지형·유닛·아이템·마법 관련 처리
- `gamerule.htm`: 게임 진행 및 승패 규칙
- `gamescreen.htm`: 화면·LP·지형 관련 설명
- `specialability.htm`: 특수 공격 기술 정의
- `coin.htm`, `deck.htm` 등 관련 규칙 문서

## 2. 카드 종류 대응
매뉴얼 `cardtype.htm`에서 확인되는 기본 종류는 지형, 유닛, 아이템, 마법이다. 현재 사이트의 Firestore `Enum+Category`에는 다섯 종류가 있다.

| 사이트 코드 | 사이트 원문 | 수량 | 매뉴얼 대응 |
|---:|---|---:|---|
| 1 | LAND / 지형 | 289 | 확인 |
| 2 | UNIT / 유닛 | 8,633 | 확인 |
| 3 | MAGIC / 마법 | 3,857 | 확인 |
| 4 | ITEM / 아이템 | 1,748 | 확인 |
| 5 | ENCHANT / 인챈트 | 823 | **매뉴얼에서 직접 대응 정의 미확인** |

인챈트 823장은 DB에서 제외하지 않는다. 사이트 분류와 원문을 보존하고 `manual_uncovered` 상태로 표시한다.

## 3. 속성·종족·소속
매뉴얼의 7대 속성 설명과 사이트 `Enum+SoulType`을 대응한다.
- DARK: 암흑
- FIRE: 불
- EARTH: 대지
- WATER: 물
- FOREST: 숲
- IRON: 금속
- LIGHT: 빛

무속성 소울(MU)은 소울 비용 체계에서 별도로 관리한다. 종족(`RaceType`), 소속(`CompanyType`), 기타 타입(`EtcType`)은 사이트 enum 전체 값을 사전으로 보존한다. 매뉴얼에 모든 세부 코드의 설명이 없으면 임의로 의미를 만들지 않는다.

## 4. 유닛 능력·능력치·기술
매뉴얼 `cardability.htm`의 유닛 능력 구분에는 Gear, Magic, Beast 계열이 나온다. 현재 사이트의 `UnitType`은 기본값과 조합값을 포함하므로 원본 enum과 한국어 표시값을 함께 저장한다.

유닛의 AP, DP/DEF, HP와 코인 기술 관련 필드는 각각 분리한다. 사이트 `Skill1` 795개, `Skill2` 189개 사전은 매뉴얼 `specialability.htm`의 27개 특수 공격 기술 목록과 별도 체계로 유지한다. 이름이 비슷하다는 이유만으로 자동 통합하지 않는다.

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

혼합 속성 코드(12, 13, 14, 15, 22, 23, 24, 32, 33, 42, 43, 52, 53, 62), NCS(82), BONUS(83)는 아이콘·enum 원문과 수량은 저장하지만, 매뉴얼만으로 실제 지불 규칙을 확정할 수 없어 `manual_review`로 남긴다.

전체 15,350장의 원본 토큰 구조를 검사한 결과, 위의 순수 속성/무속성/무비용 코드로 완전히 해석되는 카드는 14,519장, 혼합·특수 코드 검토 대상은 831장이다. 이는 코드 해석 단계의 결과이지, 카드 이미지와 대조한 최종 수동 검증 완료 수량은 아니다.

## 6. LP와 지형
사이트 `RequireLP`는 지형 289장에 존재하며 0부터 4까지의 값을 enum과 연결한다. **LP 0은 명시적 0으로 저장**하며 미상이나 누락으로 바꾸지 않는다. 현재 데이터에서 LP 0 지형은 72장이다.

매뉴얼의 `gamerule.htm`과 `ready.htm` 사이에 지형 설치 횟수 설명의 충돌이 있어, LP 지불값과 턴당 설치 제한을 별도 개념으로 관리한다. 이 카드DB는 규칙 충돌을 임의로 하나로 합치지 않는다.

## 7. 텍스트와 효과
- `TextBase`: 카드 기본 텍스트 원문
- `TextExtra`: 추가 설명/보조 텍스트 원문
- 원문 HTML/개행을 보존하고, 검색용 plain text를 별도 생성한다.
- `TurnType`, `DurationType`, `Duration`은 각각 발동 시점·지속 유형·지속 수치로 분리한다.
- 효과를 실행 가능한 규칙으로 바꾸는 작업은 원문 수집과 별도의 검증 단계로 관리한다.

## 8. 검증 상태
`source_extracted`, `enum_mapped`, `manual_semantics_verified`, `image_verified`, `manual_review`, `manual_uncovered` 상태를 구분한다. 자동 추출만 된 값은 수동 검증 완료로 표시하지 않는다.
