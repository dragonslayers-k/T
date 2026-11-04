# #444 효과 미해결 67건 1차 분류표

기준: Actions #444, immutable `fm1-carddb-29`  
원본: semantic-review artifact `13323730248` / run `41831469993`  
이 문서는 67개 패턴을 원문 형태로 고정하고 검토 순서를 정하기 위한 **1차 후보 분류**다. 아래 분류는 게임 규칙 검증 완료를 의미하지 않으며, 이 문서만으로 어떤 행도 verified/executable로 승격하지 않는다.

## 분류 집계

- 총 67개 고유 텍스트 패턴.
- 기존 audit 분류: `conditional_or_reference_candidate` 8건, `unparsed_effect_text` 59건.
- 불완전 문구·원문 추가 확인: 4건
- 카드 메타·덱/수집 규칙 후보: 13건
- 조건·수량·분류 규칙 후보: 14건
- 실제 효과·발동조건 후보: 15건
- 명명 능력·카드 참조 후보: 21건

## 처리 원칙

1. card ID와 카드 상세 URL을 기준으로 원문 TextBase/TextExtra를 확인한다.
2. 효과 문장과 설명/참조 문장이 한 줄에 섞이면 원문을 보존한 채 기계 판독 가능한 부분만 별도 추출한다.
3. 발동 조건, 대상, 수량, 지속시간 중 하나라도 불명확하면 non-executable로 둔다.
4. 명명 스킬은 해당 카드의 상세 페이지와 정의 카드의 근거를 연결한다. 다른 카드에서 의미를 가져오지 않는다.
5. 이 분류표를 기준으로 테스트 케이스를 추가한 뒤, 한 번의 회귀 테스트와 한 번의 DB29 전체 감사로 확인한다.

## 67개 원문 목록

| # | Card ID | 카드명 | 기존 분류 | 1차 후보 분류 | 원문 텍스트 | 카드 상세 |
|---:|---|---|---|---|---|---|
| 1 | 8111923702 | 라이트닝버그 | unparsed_effect_text | 불완전 문구·원문 추가 확인 | AP1이상으로 공격시, 상대 유닛이 장비/야수면 3턴간 | [원문](https://fmlunatic.com/card/8111923702) |
| 2 | 13010233113 | 펭귄여왕투척 | unparsed_effect_text | 불완전 문구·원문 추가 확인 | cwda! | [원문](https://fmlunatic.com/card/13010233113) |
| 3 | 16112610278 | 스컬시티 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ※ 다크마레아(3카운터) [끝없이 해골이 쏟아지는 도시.] | [원문](https://fmlunatic.com/card/16112610278) |
| 4 | 16060133760 | 광분의전이 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ※ 독종족 카드(유닛,마법,아이템)에 "광분의전이"카드도 포함됩니다. | [원문](https://fmlunatic.com/card/16060133760) |
| 5 | 16112610283 | 지나간자리 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ※ 머스마레마(3카운터) [투스샌드웜이 지나간 자리.] | [원문](https://fmlunatic.com/card/16112610283) |
| 6 | 15060933630 | 무한의제물 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동 후 다크파워 히어로 +1 [어둠의 피조물이여, 일어나라.] | [원문](https://fmlunatic.com/card/15060933630) |
| 7 | 14010833378 | 눈물 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동시 아군 핸드/필드가 모두 블라토브 유닛이면 마법 대상 +1. [아버지... 보고싶어요.] | [원문](https://fmlunatic.com/card/14010833378) |
| 8 | 13071033261 | 녹음의습격 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동시 이름종류수에 따라 특 별 효과가 발동한다(특이사항) | [원문](https://fmlunatic.com/card/13071033261) |
| 9 | 13071033261 | 녹음의습격 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동시 핸드 / 필드 플랜트 종족 유닛의 이름 수 종류가 5이상이면 | [원문](https://fmlunatic.com/card/13071033261) |
| 10 | 15060933635 | 무거운사명 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동후 랜드파워 히어로 +1 [그녀를 이어 대지의 왕이 될...] | [원문](https://fmlunatic.com/card/15060933635) |
| 11 | 15060933636 | 빛의인도자 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동후 세인트파워 히어로 +1 [좌절에서 일어나 전쟁의 종언을 위해 빛의 길을 인도하리라.] | [원문](https://fmlunatic.com/card/15060933636) |
| 12 | 15060933632 | 근원의힘 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동후 워터파워 히어로 +1 [그녀에게 다가가지 못하게 해야 해요. 근원의 힘을 지켜냅시다.] | [원문](https://fmlunatic.com/card/15060933632) |
| 13 | 15060933631 | 루데스의희생 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동후 파이어파워 히어로 +1 [그렇게 슬피 울지 마세요. 이 아이들을 부탁해요. 그 옛날 저와함께 한 약속, 잊지 말아 주세요. 나의 군주, 나의 사랑... 루크.] | [원문](https://fmlunatic.com/card/15060933631) |
| 14 | 15060933633 | 동조하는숲 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 발동후 포레스트파워 히어로+1 [잊혀진 자가 깨어나자, 혼고에의 자손들이 나타나기 시작했다.] | [원문](https://fmlunatic.com/card/15060933633) |
| 15 | 14030533415 | 황제의일갈 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ※ 실패시. | [원문](https://fmlunatic.com/card/14030533415) |
| 16 | 11081732687 | 다운사이즈 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※ 아군 핸드에 "거대화" 존재시 마법 대상 +1 [그것은 원하는 상대의 크기를 축소시키는 마법이다.] | [원문](https://fmlunatic.com/card/11081732687) |
| 17 | 14022627282 | 에네퍼브렌 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ※ 에네퍼브렌C | [원문](https://fmlunatic.com/card/14022627282) |
| 18 | 16112610280 | 생환의도시 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ※ 워터마레마(3카운터) [강력한 바다 영수와 고대 문명.] | [원문](https://fmlunatic.com/card/16112610280) |
| 19 | 16112610279 | 강자의왕국 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ※ 파이어마레마(3카운터) [강자만의 질서, 강자만의 왕국.] | [원문](https://fmlunatic.com/card/16112610279) |
| 20 | 16112610281 | 숲의안식처 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ※ 포레스마레마 (3카운터) [세계수의 아래 울창한 안식처.] | [원문](https://fmlunatic.com/card/16112610281) |
| 21 | 14022627279 | 샤일루어비스 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ※ 해당 상태는 카드 번호를 기준으로 체크하며, 샤일루어비스의 이름이 바뀌어 필드에 존재하여도 다른 카드가 샤일루어비스로 바뀌지 않습니다. | [원문](https://fmlunatic.com/card/14022627279) |
| 22 | 15050633608 | 퓨리파이어샷 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ※ 화염광분 카드 | [원문](https://fmlunatic.com/card/15050633608) |
| 23 | 15060933634 | 의도된접근 | unparsed_effect_text | 실제 효과·발동조건 후보 | ※발동후 메탈파워 히어로 +1. [며칠전, 오빠가 보급부대를 습격했어요. 한동안은 병사들이 굶고 있을 거에요.] | [원문](https://fmlunatic.com/card/15060933634) |
| 24 | 12070432964 | 파이널어택 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ▶ "기가스XG"는 울티밋퓨전 마법을 사용하여 확보할 수 있습니다. | [원문](https://fmlunatic.com/card/12070432964) |
| 25 | 10120150495 | 아마딘상회 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ▶ 대지아이템 중 에피소드 1-15, 1레벨에 해당하는 아이템만 해당합니다. | [원문](https://fmlunatic.com/card/10120150495) |
| 26 | 14111227709 | 바이칼츠 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ▶ 동일한 이름, 다른 사용수량(4U/1U)인 카드를 덱에 넣는 경우 마지막에 넣은 카드의 사용수량을 따르게됩니다. 바이칼츠(에픽,1U)를 먼저 넣은 후 바이칼츠(언커,4U)을 넣어주시길 바랍니다. | [원문](https://fmlunatic.com/card/14111227709) |
| 27 | 11030232509 | 마법영창 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ▶ 마법영창 카드 제외. | [원문](https://fmlunatic.com/card/11030232509) |
| 28 | 8102931810 | 사탕혹은골탕 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ▶ 사탕혹은골탕 카드는 할로윈데이 관련 이벤트(2008년) 카드입니다. | [원문](https://fmlunatic.com/card/8102931810) |
| 29 | 14121027751 | 자크더애로우 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 섀도우스킬(더애로우) - ○○, | [원문](https://fmlunatic.com/card/14121027751) |
| 30 | 9120250309 | 숨겨진함정 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ▶ 슬롯 유닛에 따라 다른 효과. | [원문](https://fmlunatic.com/card/9120250309) |
| 31 | 8080631758 | 오덴의눈물 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ▶ 아이템 레벨에 따라 해당 보석카드로 바뀝니다. | [원문](https://fmlunatic.com/card/8080631758) |
| 32 | 4062530568 | 요정의호출 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | ▶ 유니크, 시크릿, 프라이즈 등급, C랭크이상 카드 제외. | [원문](https://fmlunatic.com/card/4062530568) |
| 33 | 14062527447 | 이미티르 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 이미티르C는 통찰 섀도우스킬과 A변환 섀도우쉬프트를 가지고 있습니다. | [원문](https://fmlunatic.com/card/14062527447) |
| 34 | 14062527448 | 이위바듀프 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 이위바듀프C는 통찰 섀도우스킬과 A변환 섀도우쉬프트를 가지고 있습니다. | [원문](https://fmlunatic.com/card/14062527448) |
| 35 | 8060431704 | 로페촌의축제 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ▶ 적 필드 카드 1의 레벨에 따라 다른 효과. | [원문](https://fmlunatic.com/card/8060431704) |
| 36 | 11050432579 | 추억 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ▶ 조건에 따른 이서리얼의 능력. | [원문](https://fmlunatic.com/card/11050432579) |
| 37 | 8100131795 | 실수의원인 | unparsed_effect_text | 실제 효과·발동조건 후보 | ▶ 즉, 적 필드에 암흑속성카드 2장, 불속성카드 2장이 있을 경우에는 아무 효과가 없습니다. | [원문](https://fmlunatic.com/card/8100131795) |
| 38 | 14062527449 | 파네네이즈 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 파네네이즈C는 통찰 섀도우스킬과 A변환 섀도우쉬프트를 가지고 있습니다. | [원문](https://fmlunatic.com/card/14062527449) |
| 39 | 14062527445 | 파이웰 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 파이웰C는 통찰 섀도우스킬과 A변환 섀도우쉬프트를 가지고 있습니다. | [원문](https://fmlunatic.com/card/14062527445) |
| 40 | 14062527446 | 페페브즈 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 페페브즈C는 통찰 섀도우스킬과 A변환 섀도우쉬프트를 가지고 있습니다. | [원문](https://fmlunatic.com/card/14062527446) |
| 41 | 14062527450 | 핏 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 핏C는 통찰 섀도우스킬과 A변환 섀도우쉬프트를 가지고 있습니다. | [원문](https://fmlunatic.com/card/14062527450) |
| 42 | 14062527444 | 헤데퀘이스 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶ 헤데퀘이스C는 통찰 섀도우스킬과 A변환 섀도우쉬프트를 가지고 있습니다. | [원문](https://fmlunatic.com/card/14062527444) |
| 43 | 14031227301 | 열정의홀던 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ▶섀도우쉬프트(레비의의지) - ○○○. | [원문](https://fmlunatic.com/card/14031227301) |
| 44 | 13112727128 | 사케크리에 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ◆ 롯트, 장생수, 맨이터롯트N, 이모탈트리, 손드트리, 뮤턴트엔트, 에인션트엔트. | [원문](https://fmlunatic.com/card/13112727128) |
| 45 | 9020431914 | 그리핀출몰 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ◇ 디스인첸트 카드. [그리핀과의 사투.] | [원문](https://fmlunatic.com/card/9020431914) |
| 46 | 4062530566 | 스펠카운터 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ◇디스인챈트 카드 [누가 더 빠르게 시전하는 자가 큰 영향을 미치지.] | [원문](https://fmlunatic.com/card/4062530566) |
| 47 | 7020731319 | 회오리장막 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ◇디스인첸트 카드 [모래 마법의 장막.] | [원문](https://fmlunatic.com/card/7020731319) |
| 48 | 9010731883 | 모래의형상화 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ★ 모래형상 유닛(야수, 골렘, 돌진공격). | [원문](https://fmlunatic.com/card/9010731883) |
| 49 | 15040133597 | 아쿠아웨이브 | conditional_or_reference_candidate | 조건·수량·분류 규칙 후보 | ★ 얼음꽃 : +2 / ▲2 / 0 | [원문](https://fmlunatic.com/card/15040133597) |
| 50 | 16082428485 | 카르마엘 | unparsed_effect_text | 명명 능력·카드 참조 후보 | ★★★ 해당카드는 하급, 중급 등 에카마엘 상태를 보유하지 않고 있습니다.★★★ | [원문](https://fmlunatic.com/card/16082428485) |
| 51 | 14111227709 | 바이칼츠 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ☆ 상성. | [원문](https://fmlunatic.com/card/14111227709) |
| 52 | 16083133807 | 빛의은혜 | unparsed_effect_text | 조건·수량·분류 규칙 후보 | ☆ 아군 핸드/필드 카드 중 같은레벨카드 수가 동일 하면, 더 높은 레벨로 체크합니다. | [원문](https://fmlunatic.com/card/16083133807) |
| 53 | 9012123779 | 두얼굴의신 | conditional_or_reference_candidate | 명명 능력·카드 참조 후보 | ☆ 야누스가면(만능능력)○ : 야누스, 0/*/0 | [원문](https://fmlunatic.com/card/9012123779) |
| 54 | 3062730289 | 간절한기도 | conditional_or_reference_candidate | 명명 능력·카드 참조 후보 | 레벨3 이하 아군 장비, 마법 전체는 순화능력을 갖는다. [두려운 마음을 없애시며, 이들이 용사의 힘으로 칼을 들어 전장을 누비게 하시오소서] | [원문](https://fmlunatic.com/card/3062730289) |
| 55 | 5072740578 | 프리즘스틱 | unparsed_effect_text | 명명 능력·카드 참조 후보 | 무지개발산공격 [참 신기하군요 구슬을 통해 나오는 무지갯빛을 보면 어떤 일이라도 해낼 수 있을것 같은 느낌이 드는군요.] | [원문](https://fmlunatic.com/card/5072740578) |
| 56 | 15050633608 | 퓨리파이어샷 | unparsed_effect_text | 카드 메타·덱/수집 규칙 후보 | 블레이즈스탭, 정령의화염, 퓨리라이드, 화염의용술사, 버닝래빗, 불새의둥지, 불의노래, 퓨리파이어샷 (2015.5.6 발매기준) | [원문](https://fmlunatic.com/card/15050633608) |
| 57 | 13070333254 | 소매치기체포 | conditional_or_reference_candidate | 카드 메타·덱/수집 규칙 후보 | 사파이어 : 언커먼. | [원문](https://fmlunatic.com/card/13070333254) |
| 58 | 9071541048 | 고대의검 | unparsed_effect_text | 불완전 문구·원문 추가 확인 | 상 | [원문](https://fmlunatic.com/card/9071541048) |
| 59 | 16041228308 | 나샤트라 | unparsed_effect_text | 불완전 문구·원문 추가 확인 | 스피릿스톰 : | [원문](https://fmlunatic.com/card/16041228308) |
| 60 | 2051530015 | 폭풍우 | unparsed_effect_text | 실제 효과·발동조건 후보 | 아군 적군 전체 HP- 전투 필드 10개의 공간 중 양쪽 모두 비어있는 공간 수. [폭풍이 모든 것을 같기갈기 찢어놓기 시작했다. 모두가 폭풍이 빨리 지나가기만을 바라고 있었다.] | [원문](https://fmlunatic.com/card/2051530015) |
| 61 | 9030431921 | 위험한충동 | unparsed_effect_text | 실제 효과·발동조건 후보 | 아군 필드 유닛 1이 마법 유닛이면 적 필드 유닛 1의 능력에 따라 효과 발생, [당신과 나는, 위험해요. 이 미로 만큼이나, 알 수 없는 사이죠. 당신은 행복한 미래를 약속하지만, 그 선택에 후회하지 않을 자신이 있나요?] | [원문](https://fmlunatic.com/card/9030431921) |
| 62 | 11020132489 | 감격 | unparsed_effect_text | 실제 효과·발동조건 후보 | 아군필드 금속 속성 유닛 전체 공체+1. 적군필드 유닛 전체 공체-1 [... 모든 상처의 치료는 결국 사람과 시간이다. 사람들의 관심과 사랑, 그리고 충분한 시간만 있다면 그 어떤 상처도 치유되기 마련이다. 그것이 인간의 힘이고 삶의 진실이다.] | [원문](https://fmlunatic.com/card/11020132489) |
| 63 | 12071826357 | 글라디오나 | conditional_or_reference_candidate | 카드 메타·덱/수집 규칙 후보 | 아이템/인첸트 : 소드맨 1장, 포위공격 1장. | [원문](https://fmlunatic.com/card/12071826357) |
| 64 | 13041726794 | 라리슈어 | conditional_or_reference_candidate | 명명 능력·카드 참조 후보 | 전쟁의주인 : 알려지지 않은 미지의 힘입니다. | [원문](https://fmlunatic.com/card/13041726794) |
| 65 | 9080532061 | 빛의강림 | unparsed_effect_text | 명명 능력·카드 참조 후보 | 체인라이트닝 - 체인라이트닝 - 라이트닝볼트 순서로 필드에 나열됩니다. | [원문](https://fmlunatic.com/card/9080532061) |
| 66 | 14070233472 | 소중한부화 | conditional_or_reference_candidate | 명명 능력·카드 참조 후보 | 피닉스의알 : 피닉스. / 티라노의알 : 티라노. | [원문](https://fmlunatic.com/card/14070233472) |
| 67 | 13041726793 | 오르브웨크 | conditional_or_reference_candidate | 명명 능력·카드 참조 후보 | 혼돈의주관자 : 알려지지 않은 미지의 힘입니다. | [원문](https://fmlunatic.com/card/13041726793) |
