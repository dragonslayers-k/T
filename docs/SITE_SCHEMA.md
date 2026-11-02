# 실제 사이트 데이터 구조 확인서

## 1. 데이터 원본
- 목록 URL: `https://fmlunatic.com/cardlist`
- Firebase 프로젝트: `fmdb-bcb70`
- Database: `(default)`
- 카드 컬렉션: `livecardlist`
- 설정 컬렉션: `liveappsetting`
- 분류 사전 문서: `liveappsetting/enumtable`
- Firestore aggregation count: **15,350**
- 카드 조회: `documents:runQuery`, NumID 내림차순, 페이지당 50개, 커서 방식
- 전체 수집 예상 페이지: **307**

## 2. 카드 ID와 개별 주소
Firestore 문서의 마지막 경로 요소가 카드의 기본 ID다. 실제 수집 문서에서 `ID` 값과 문서 ID가 일치한다. `KIND`는 카드 고유 ID가 아니라 이미지 파일을 찾는 데 쓰는 카드 종류 내 이미지 번호다.

개별 카드 주소는 사이트 자체 URL 복사 기능의 경로 규칙을 따른다.

`https://fmlunatic.com/card/{Firestore document ID}`

카드 레코드에는 목록 주소와 개별 카드 주소를 별도로 저장한다.

## 3. 카드 분류 수량
| Category enum | 사이트 표시 | 수량 |
|---:|---|---:|
| 1 | 지형 (LAND) | 289 |
| 2 | 유닛 (UNIT) | 8,633 |
| 3 | 마법 (MAGIC) | 3,857 |
| 4 | 아이템 (ITEM) | 1,748 |
| 5 | 인챈트 (ENCHANT) | 823 |
| | **합계** | **15,350** |

## 4. 원본 필드 인벤토리
실제 Firestore 카드 문서에서 55개 필드명이 확인됐다. 필드 존재 여부와 원본 값은 모두 카드별로 보존한다.

| 필드 | 문서 수 | 필드 | 문서 수 |
|---|---:|---|---:|
| ID, NumID, Name | 15,350 | Category, SoulType | 15,350 |
| RareType, RareUI | 15,350 | RaceType, CompanyType | 15,350 |
| EtcType, Episode | 15,350 | DeckLimit, BuyGrade | 15,350 |
| LV, CardUISoul | 15,350 | NameCombo, NameCount | 15,350 |
| SP, GP, DeckPoint | 15,350 | ReleaseDate | 15,350 |
| KIND, SortedID, Tags | 15,350 | RequireSoul | 15,350 |
| TextBase, TextExtra | 15,350 | ATK, DEF, HP | 10,381 |
| ATKStatType, DEFStatType, HPStatType | 10,381 | Skill1, Skill2, UnitType | 10,381 |
| ATKCoin, DEFCoin, HPCoin | 8,633 | ATKCoinType, DEFCoinType, HPCoinType | 8,633 |
| ATKCoinCount, DEFCoinCount, HPCoinCount | 8,633 | RankType | 8,633 |
| Duration, DurationType, TurnType | 4,680 | CoinOption, ProbOption | 1,748 |
| EnchantSlot | 823 | RequireLP, MuSoul, EarnSoulList | 289 |

## 5. 분류 사전
`enumtable`에는 32개 `Enum+` 그룹과 6개 `Column+` 그룹이 있다. Firestore에서 배열/맵으로 저장된 각 항목을 원본 그대로 보존한다. `Category`, `SoulType`, `RaceType`, `CompanyType`, `EtcType`, `RareType`, `Episode`, `DeckLimit`, `BuyGrade`, `UnitType`, `Skill1`, `Skill2`, `TurnType`, `DurationType`, `EnchantSlot` 등은 카드 필드의 코드값을 해석하는 데 사용한다.

`Skill1`에는 795개, `Skill2`에는 189개의 사전 항목이 있다. 이 값들을 매뉴얼의 27개 특수 공격 기술과 동일한 개념으로 단정하지 않는다.

## 6. 이미지 주소 규칙
Storage bucket: `https://storage.googleapis.com/fmdb-bcb70.appspot.com/`

사이트 코드에서 확인한 이미지 경로 생성 규칙:
- Category enum의 `ImageSmall` 또는 `ImageLarge` 기본 경로
- `KIND`를 1000으로 나눈 몫을 2자리 폴더로 사용
- `ImagePrefix` + `KIND` 5자리 + `S`(소형) 또는 `L`(대형) + `.webp`

예: `cardlist/magic/large/03/M03861L.webp`

카드별 원본 이미지 URL, 로컬 파일 경로, 파일 크기, SHA-256, 다운로드 상태를 저장한다. 작은 이미지와 큰 이미지를 별도 레코드로 관리한다.

## 7. 데이터 해석 주의
- `KIND`는 이미지 번호이므로 카드 기본키로 쓰지 않는다.
- enum 코드 원본과 표시 이름을 별도 저장한다.
- `RequireSoul`은 4자리 토큰의 연결 문자열로 관찰된다. 각 토큰은 2자리 코드와 2자리 수량이다. 토큰 의미가 확인되지 않은 경우 색상 비용으로 추정하지 않는다.
- `RequireLP=0`은 유효한 명시값이다.
- Firestore 원본과 UI에서 보이는 값이 다르면 양쪽을 보존하고 대조 결과를 기록한다.
