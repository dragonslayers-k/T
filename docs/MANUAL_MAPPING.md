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

무속성 소울(MU)은 소울 비용 체계에서 별도로 관리한다. 종족(`RaceType`), 소속(`CompanyType`), 기타 타입(`EtcType`)은 사이트 enum 전체 값을 사전으로 보존한다. 매뉴얼에 모든 세부 코드의 설명이 없으면 임의로 의미를 만들지 않는다.

## 4. 유닛 능력·능력치·기술
매뉴얼 `cardability.htm`의 유닛 능력 구분에는 Gear, Magic, Beast 계열이 나온다. 현재 사이트의 `UnitType`은 기본값과 조합값을 포함하므로 원본 enum과 한국어 표시값을 함께 저장한다.

유닛의 AP, DP/DEF, HP와 코인 기술 관련 필드는 각각 분리한다. 사이트 `Skill1` 795개, `Skill2` 189개 사전은 매뉴얼 `specialability.htm`의 27개 특수 공격 기술 목록과 별도 체계로 유지한다. 이름이 비슷하다는 이유만으로 자동 통합하지 않는다.



### N/C/S(82) 유닛 스탯 표기와 RequireSoul 토큰의 구분

사용자 확인 기준으로 카드의 NCS(82) 스탯 표기는 N(Normal 공격), C(Critical 공격), S(Defensive 방어)를 뜻하며, 괄호의 8은 공격 주사위 0~8, 2는 방어 주사위 0~2 범위다. NC(80)은 S 방어 항목이 없는 표기다. 이 표기는 유닛 카드의 스탯/주사위 배치 설명이며, RequireSoul의 4문자 비용 토큰과 동일한 필드나 의미로 취급하지 않는다. NCS(82) 스탯 표기를 소울 생성·지불 규칙으로 변환하지 않는다.

RequireSoul 원본에서 별도로 관찰되는 토큰 코드 82는 원문 필드와 매뉴얼의 소울 비용 문맥에 한해서만 다룬다. 카드 화면의 NCS(82) 표기와 혼동하지 않도록 데이터 사전·테스트·UI에서 문맥을 분리한다.
### EarnSoul / RequireSoul 코드 공간 분리 — Firestore 카드 원본으로 교차확인

숫자 코드가 같아도 반드시 원본 필드의 enum namespace를 함께 확인한다.

| 원본 필드 | Enum | 코드 82 | 코드 81 / 83 | 역할 |
|---|---|---|---|---|
| `RequireSoul` | `Enum+RequireSoul` | `NCS` / `ncs.webp` | 81=`MU`; 83=`BONUS` | 카드 설치·소환 비용 토큰 |
| `EarnSoulList` | `Enum+EarnSoul` | `MU02` / `mu02.webp` | 81=`MU01`; 83=`MU03` | 지형의 소울 생산 토큰 |

실제 Firestore 카드 `16112710291`(`구름도시`)의 원본은 `RequireSoul="71018101"`, `EarnSoulList="8201"`, `MuSoul=2`다. RequireSoul은 LIGHT 1 + MU 1의 설치 비용을 나타낸다. 별도 EarnSoulList는 MU02 1개를 생산해 무소울 2개를 출력하며, MuSoul=2와 일치한다. 원문 TextExtra 역시 지형 설치에 1무소울과 1유소울을 소비한다고 설명한다.

따라서 `EarnSoulList=8201`의 MU02 생산 의미를 `RequireSoul=8201`의 NCS 비용 토큰으로 옮기거나, 그 반대로 적용해서는 안 된다. 사용자 확인의 N/C/S(82) 전투 스탯 표기 역시 두 Firestore enum과 독립된 표기다. 앱 converter의 회귀 테스트에서 EarnSoulList=8201 → MU02 출력 2와 RequireSoul=8201 → NCS 의미 검토/사용 차단을 같은 테스트 실행 안에서 별도로 확인한다.

### 코인 기술과 원본 필드 대응

Dropbox 원본 Manual.zip의 coin.htm은 C 뒤 숫자를 던지는 코인 개수로 정의한다. 예를 들어 C3은 코인 3개, 2C3은 결과값에 2를 곱한다. 매뉴얼의 예시는 AP에 +2C1, DP에 -C1을 적용할 때 코인 1개를 한 번만 던지고 동일한 결과를 AP와 DP에 각각 적용한다고 명시한다. 매뉴얼 본문이 직접 설명하는 연산은 +, -, x이며, 이 예시로 스탯마다 독립 주사위를 굴리지 않는다는 점도 확인된다. 매뉴얼 본문은 CoinType EQUAL(=)의 동작을 별도로 정의하지 않는다.

Firestore 원본 필드 대응은 다음과 같다.
- ATKCoin / DEFCoin / HPCoin: C개수 및 배율 표현식(예: C3, 2C2)
- ATKCoinType / DEFCoinType / HPCoinType: Enum+CoinType 연산 유형
- ATKCoinCount / DEFCoinCount / HPCoinCount: 코인 개수 대조 필드
- Enum+CoinType raw codes: 1 NONE, 2 PLUS(+), 3 MINUS(-), 4 X(x), 5 EQUAL(=). 코드 1~4는 매뉴얼의 연산 설명과 대응한다. 코드 5 EQUAL은 enum 이름/기호만 확인되며 매뉴얼에 실행 의미가 없다. 앱은 대입(set)을 enum-inferred 후보로만 보존하고 AP/DP/HP 런타임 연산에는 적용하지 않는다.

런타임 변환 시 원본 문자열·유형·개수를 함께 보존하고, 표현식의 C 개수와 CoinCount가 불일치하거나 연산 유형이 누락된 경우 임의 보정하지 않고 review 상태로 둔다. 이 코인 연산은 N/C/S(82) 표기 자체와 혼동하지 않으며, N/C/S 표기의 N·C·S는 사용자 확인에 따른 Normal 공격·Critical 공격·Defensive 방어 스탯 범주다. 반면 코인 표현식 C3의 C는 매뉴얼 정의대로 Coin(코인)이며, 두 표기의 C는 문맥이 다르다.

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

혼합 속성 코드 14종(12, 13, 14, 15, 22, 23, 24, 32, 33, 42, 43, 52, 53, 62)은 색상 조합 후보를 해독하지만, 현재 Release #27 원본에는 독립적으로 대조할 정규화 비용 참조 필드가 없어 `mapping_review`로 남긴다. 이전 PR 문서에 38개 사례와 14,282건을 교차 검증했다고 기재되어 있었으나, 재현 실행에서 참조 비용 행은 0건이었다. 카드 ID·원본 코드·기대 비용을 가진 검증 fixture가 다시 확보되기 전까지 `source_cross_validated`를 부여하지 않는다. RequireSoul 원본의 코드 81(MU), 82(NCS), 83(BONUS)은 서로 다른 비용 토큰으로 보존한다. Dropbox 원본 `/판마/Manual.zip`의 `soulcost.htm`은 이름을 특정하지 않은 색 없는 무속성 구슬의 소환·유지 규칙을 설명한다. enum 이름 MU(81)는 무속성의 후보 대응이지만, enum icon과 Manual 이미지의 픽셀 대조가 끝나지 않았으므로 이 연결은 런타임에서 `implemented_inferred`로만 표시한다. 유닛 유지비는 MU(81) 후보 토큰에만 연결한다. NCS(82)는 Manual 본문에는 정의되어 있지 않지만, 2017년 커뮤니티 특수능력 정리에는 NCS소울이 별도 소환 자원/비용으로 사용되는 사례가 다수 기록되어 있다. 따라서 NCS 토큰은 `ncs_soul` 자원 후보로 분류하되 `community_documented_candidate`로만 표시한다. 실제 NCS소울 풀의 생성·보유·지불·대체 규칙은 미확정이므로 `semantic_review`와 런타임 차단을 유지하며, 무소울/MU로 환산하지 않는다. BONUS(83)는 별도 검토 상태다. 사용자가 정의한 카드 스탯 표기 NCS(82)와 Firestore `RequireSoul` enum의 NCS(82)는 서로 다른 필드/문맥이며 동일한 규칙으로 합치지 않는다.

반면 추출된 `soulcost.htm` 본문은 BONUS(83)의 지불·생성 규칙을 정의하지 않는다. BONUS는 별도 `bonus` 토큰으로 보존하고 `semantic_review`로 남기며, NCS/neutral에 합산하거나 플레이 가능한 중립 비용으로 추정하지 않는다. 매뉴얼 이미지의 BONUS 아이콘 범례를 확인하기 전까지 이 상태를 유지한다.

DB29 감사 기준 RequireSoul 코드 82의 NCS 토큰은 351장, 코드 83의 BONUS 토큰은 439장이고 11장은 두 토큰을 함께 가진다(합집합 779장). RequireSoul 코드 82만 포함한 340장도 Manual 직접 근거가 없어 semantic_review로 유지하며, BONUS를 포함한 439장은 검토 대상으로 남는다. 혼합 속성 코드 52장의 `mapping_review`는 별도 유지한다.

DB29 전체 감사에서 15,350장의 RequireSoul 토큰 문자열은 모두 토큰 단위로 식별·파싱되었다(`soul_known=1`). 이 값은 원문 토큰 인식 완료를 뜻하며, BONUS 의미나 혼합 속성의 독립 비용 대조가 끝났다는 뜻은 아니다.

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
`source_extracted`, `enum_mapped`, `enum_decoded`, `mapping_review`, `semantic_review`, `source_cross_validated`, `current_taxonomy_verified`, `manual_semantics_verified`, `image_verified`, `manual_review`, `effect_unmapped` 상태를 구분한다. 자동 추출만 된 값은 수동 검증 완료로 표시하지 않는다. `current_taxonomy_verified`는 다섯 카드 유형이 현재 분류 사전과 일치한다는 뜻이며, 카드별 효과 구현 완료를 의미하지 않는다.


## 2026-11-07 정정 — NCS/MU 교차판정 철회

기존 문서의 RequireSoul 코드 82 NCS를 Manual 무속성 규칙에 연결한 판정은 직접 근거가 부족해 철회했다. Manual은 무속성 구슬을 설명하지만 NCS라는 enum 문자열을 정의하지 않는다. enumtable은 MU(81), NCS(82), BONUS(83)를 별도 RequireSoul 항목으로 구분한다. 따라서 NCS(82)는 원본 토큰·수량만 보존하고 semantic_review로 유지한다. MU(81)는 무속성의 후보 대응으로 유지하되 이미지 교차확인이 끝날 때까지 inferred 상태로 표시한다. NCS(82) 유닛 스탯 약어와 RequireSoul enum NCS(82)는 같은 이름을 공유할 뿐 서로 다른 문맥이다.



## 2026-11-07 — StatType / RankType / NCS namespace audit

Firestore exposes separate source fields `ATKStatType`, `DEFStatType`, and `HPStatType`, each mapped through `Enum+StatType`. The current enumtable values are:

| code | enum | icon | handling |
|---:|---|---|---|
| 1 | NONE | 없음 | no marker |
| 11 | CONST | ★ | Manual-defined: cannot be changed |
| 12 | UP | ▲ | Manual-defined: cannot decrease |
| 13 | DOWN | ▼ | Manual-defined: cannot increase |
| 21 | FRONT | F | preserve; semantics unverified |
| 22 | BACK | B | preserve; semantics unverified |
| 23 | HAND | H | preserve; semantics unverified |
| 24 | TURN | T | preserve; semantics unverified |
| 31 | PLUS | + | preserve; semantics unverified |
| 32 | MINUS | - | preserve; semantics unverified |
| 33 | EQUAL | = | preserve; semantics unverified |

Manual `cardability.htm` explicitly defines the star and up/down triangle restrictions. It does not define runtime semantics for FRONT/BACK/HAND/TURN/PLUS/MINUS/EQUAL; these remain source-preserved and must not be guessed. The app pack builder now emits `sourceStatTech` from all three raw fields and the app maps only raw codes 11/12/13 to Manual-defined restrictions; raw code 1 is NONE.

Keep these namespaces separate:
- User-confirmed N/C/S(82) shorthand: N=Normal attack, C=Critical attack, S=Defense; (82)=attack dice 0–8 and defense dice 0–2. No exact Firestore source field for this shorthand has yet been demonstrated, so it is not synthesized from other fields.
- `RequireSoul` enum NCS(82): a separate source token; remains `semantic_review`, not a stat profile and not the Manual neutral bead.
- `RankType` enum: separate rank metadata (N/C/B/A/S); it is not used to derive the N/C/S unit-stat shorthand.
- Manual coin notation C (e.g. C3): Coin, not the C in N/C/S.
- Manual `치명공격기술` special skill: a named combat ability, not automatically equivalent to the C category in the user-defined N/C/S shorthand.

No automatic conversion is allowed between these fields merely because labels overlap.


## 2026-11-07 — TextExtra-only status/resource effects (Klub variants)

Firestore livecardlist records `16120828657`–`16120828663` share a `TextExtra` effect block that names `전력봉인`, applies `중급열사` for three turns, and says that when `중급열사` activates it removes one `유소울` or `NCS소울`, increases upkeep by one, and decreases DP by one. These are literal card-source descriptions, not definitions found in the reviewed Manual pages. They are not the same thing as the user-confirmed N/C/S(82) stat shorthand.

For one source variant (`16120828663`), `Skill1=51` maps to `관통공격`, `Skill2=129` maps to `절해라`, while `TextExtra` separately describes `전력봉인` and `중급열사`. Do not relabel Skill2=129 as 중급열사. Its `RequireSoul=71048103` is 4 light + 3 MU candidate cost; it does not contain RequireSoul NCS(82), showing that the NCS소울 text is not simply this card's summon-cost token.

No reviewed Manual page or independent web result defined the `NCS소울` resource pool, its production, or the exact status lifecycle. Keep the raw TextExtra, mark these effects source-text-defined but runtime-unverified, and do not implement a generic NCS stat/soul conversion. Open questions: which effect produces NCS소울; whether `유소울` and `NCS소울` are separate pools; activation timing; how the three-turn duration counts; how permanent AP/DP=0 interacts with reset; and how the status's upkeep is charged.


### Enumtable raw-code convention

The outer map key in the Firestore enumtable is an index, not necessarily the numeric value stored in a card field. For the fields audited here, use the first integer in each enum row as the raw code: `StatType` = 1 NONE, 11 CONST, 12 UP, 13 DOWN, 21 FRONT, 22 BACK, 23 HAND, 24 TURN, 31 PLUS, 32 MINUS, 33 EQUAL; `CoinType` = 1 NONE, 2 PLUS, 3 MINUS, 4 X, 5 EQUAL. Do not use outer keys 0–10 or 0–4 as field values.


### EarnSoul / RequireSoul code-82 namespace split

The Firestore enumtable defines `EarnSoul` raw code 82 as `MU02` (two neutral souls produced per token), while `RequireSoul` raw code 82 is the separate `NCS` token. The user-confirmed `NCS(82)` notation is a third, unrelated unit-stat shorthand (N/C/S with attack dice 0–8 and defense dice 0–2). A fourth literal, `NCS소울`, appears in some `TextExtra` effects and remains a separate source-text resource question. These meanings must never be joined by the shared number/string alone. The app's `parse_earn_soul_list` already decodes `EarnSoul` 8201 as two neutral output; converter self-tests cover it separately from `RequireSoul` 8201 review handling.


## 2026-11-07 — Corrected runtime overlay and hybrid candidate storage

The prior runtime overlay contradicted its own source-review policy: NCS(82), BONUS(83), hybrid tokens, and unknown/missing costs were assigned generic neutral runtime costs and marked `playable=true`. The overlay now sets `runtimeCostKnown=false`, an empty runtime cost, `runtimeCostStatus=semantic_review_blocked`, and `playable=false` for unresolved costs. Only source-backed pure colors, explicit no-cost, and the inferred MU(81) neutral crosswalk remain playable.

The shared RequireSoul parser no longer adds both component colors of a hybrid icon to the normalized `colors` totals. It retains the component names only on the token as candidate metadata. Thus a hybrid token is not persisted as two required colors and is not treated as one generic neutral soul either. The app pack converter follows the same rule. DB29 source rows and the published DB29 ZIP are unchanged; this is a parser/overlay correction only.

The runtime overlay policy now explicitly blocks unresolved NCS/BONUS/hybrid/unknown costs instead of applying generic payment. This supersedes the earlier `fallback_payable` language in the cost-overlay work log.


## 2026-11-07 — Manual soul-cost rule, scoped to MU candidate

The Dropbox Manual.zip `soulcost.htm` states that the Soul Cost rule applies only to Unit cards carrying the colorless/neutral bead. The bead is payable at summon by spending any generated attribute soul; from the next preparation phase onward, the same amount is recurring unit upkeep. If the player cannot pay, the unpaid amount destroys that many cards from the deck. This is a unit-only recurring rule: a neutral bead on a land/item/spell/enchant is not automatically recurring upkeep.

The Firestore `RequireSoul` enum separately identifies MU(81), NCS(82), and BONUS(83). MU(81) is the inferred crosswalk candidate to the Manual neutral bead; the icon pixel comparison remains outstanding. NCS(82), BONUS(83), and all hybrid pair codes remain non-executable until independent payment evidence is found. The user's N/C/S(82) combat-stat shorthand is a fourth, separate context and is never used as a RequireSoul mapping.


## 2026-11-07 — NCS소울 community evidence, candidate only

The 2017-01-30 Inven community post “이쯤에서 카드특수능력을 마구찍는 판마를보자(강스압)” describes NCS소울 as a distinct resource used by card effects:
- “소울체인지” converts a YuSoul on an allied hand card to NCS.
- “중급 열사” consumes one YuSoul or NCS소울 and increases upkeep.
- Several effects move an enemy unit to the hand using NCS소울, create cards “as NCS소울”, replace hand cards with NCS-soul-cost cards, or convert an NCS soul into permanent upkeep.
- “망자의항해” creates an NCS소울 card; “신입생환영회” converts one NCS soul to upkeep; “홀리데이” gives a unit from a hand card its native YuSoul level or NCS soul for a colorless unit.

Reference (community documentation, not official Manual): https://www.inven.co.kr/board/hs/3509/1426815 (Equinoxx, 2017-01-30).

This evidence is sufficient to distinguish NCS소울 from ordinary MU/neutral soul and from the user's N/C/S(82) stat shorthand. It supports a `community_documented_candidate` resource classification for the RequireSoul NCS enum token, but it does not establish the canonical resource ledger, generation timing, exact payment procedure, or interactions with MU upkeep. The token therefore remains `semantic_review`, is represented as a separate `ncs_soul` candidate, and is blocked from runtime play. Never translate it into neutral soul or treat it as NCS stat dice.
