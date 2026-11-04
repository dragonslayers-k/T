# DB29 low-confidence effect review — triage pass 1

**Artifact:** Actions #430, `gap-reports/effect-review-queue.jsonl` and `effect-low-confidence-summary.json`.  
**Input:** 206 unique text patterns: 195 `unparsed_effect_text`, 11 `conditional_or_reference_candidate`.  
**Purpose:** identify source fragments that deserve human semantic review first. This is triage only; it does not reclassify the source records or authorize implementation.

## Priority A — existing conditional/reference candidates (11)

| Card ID | Card | Exact source fragment |
|---|---|---|
| 13010233093 | 준비된매복 | 4레벨 이상시 재생생 되지 않음. |
| 3062730289 | 간절한기도 | 레벨3 이하 아군 장비, 마법 전체는 순화능력을 갖는다. |
| 11050432565 | 포메이션제로 | 베타 : 아군 필드 알파, 베타, 감마, 델타, 오메가 유닛 전체 AP 상향고정 (영구히) |
| 13070333254 | 소매치기체포 | 사파이어 : 언커먼. |
| 12071826357 | 글라디오나 | 아이템/인첸트 : 소드맨 1장, 포위공격 1장. |
| 9012123779 | 두얼굴의신 | 야누스가면(만능능력)○ : 야누스, 0/*/0 |
| 15040133597 | 아쿠아웨이브 | 얼음꽃 : +2 / ▲2 / 0 |
| 13041726794 | 라리슈어 | 전쟁의주인 : 알려지지 않은 미지의 힘입니다. |
| 14070233472 | 소중한부화 | 피닉스의알 : 피닉스. / 티라노의알 : 티라노. |
| 13082827041 | 흉성의군주 | 핸드 슬롯 1이 3레벨이상 카드인 경우 |
| 13041726793 | 오르브웨크 | 혼돈의주관자 : 알려지지 않은 미지의 힘입니다. |

Some entries are clearly incomplete labels, stat notation, or explanatory text rather than complete effects. Keep them pending until the complete card-local TextBase/TextExtra context is reviewed.

## Priority B — unparsed fragments with apparent conditions or operations

| Card ID | Card | Exact source fragment | Review issue |
|---|---|---|---|
| 8111923702 | 라이트닝버그 | AP1이상으로 공격시, 상대 유닛이 장비/야수면 3턴간 | Truncated duration/effect; recover adjacent text |
| 7070431414 | 바르덱의양보 | 단, 조건은 필드 앞번호부터 1, 2, 3의 레벨만 합. | Formula scope and referenced effect missing |
| 5113030979 | 칼날의눈보라 | 마법 효과로 공체를 각각 나눈 값 중 소수점 이하 값이 있을 경우 올림으로 처리합니다. | Rounding rule; identify operands and affected stats |
| 13020633124 | 극적인탈출 | 발동시 아군 필드에 "극적인탈출" 존재하면 게임에서 삭제한다. | Self-reference / removal timing |
| 13091733304 | 난폭한비행 | 발동시 아군 필드에 이 마법을 제외한 마법 중 난폭한비행이 없는 경우에 효과 발동 | Presence condition and scope |
| 14010833378 | 눈물 | 발동시 아군 핸드/필드가 모두 블라토브 유닛이면 마법 대상 +1. | “all” scope and target-count semantics |
| 13071033261 | 녹음의습격 | 발동시 이름종류수에 따라 특 별 효과가 발동한다(특이사항) | Missing referenced table/definition |
| 13071033261 | 녹음의습격 | 발동시 핸드 / 필드 플랜트 종족 유닛의 이름 수 종류가 5이상이면 | Name-count formula and relation to first fragment |
| 12110733033 | 에인션트타임 | 상대 유닛 AP/DP가 0 이하로 내려가지 않습니다. | Stat floor / prevention semantics |
| 3032130211 | 집중공격 | 소수점 이하 자리수 반올림. | Rounding rule; operands and order missing |
| 5101330951 | 트리탄퀘이크 | 순속성 조건 충족하면 유니크 특수능력 발동 | “순속성” and unique-skill reference missing |
| 11081732687 | 다운사이즈 | 아군 핸드에 "거대화" 존재시 마법 대상 +1 | Card-presence condition and target count |
| 4062530568 | 요정의호출 | 유니크, 시크릿, 프라이즈 등급, C랭크이상 카드 제외. | Exclusion list; determine which selection/pool it constrains |
| 4031930491 | 사지분리고문 | 적 필드 빈공간 2이상 존재하지 않는 경우, 발동실패합니다. | Field capacity and failure condition |
| 12040432904 | 포제션 | 적 필드 카드가 2이상 이여야 발동 | Minimum enemy field count |
| 11050432579 | 추억 | 조건에 따른 이서리얼의 능력. | Referenced conditional profile; link to profile evidence |
| 11060132585 | 미숙한소환 | 핸드 빈공간 수 조건 | Hand-space threshold omitted |
| 12112141399 | 승리의팬던트 | 환상폭발기술 [당신의 승리를 증명하는 포상입니다. 사악하고 부정한 환상을 파괴하는 힘을 담고 있습니다. 이것 이 먼 길을 가야할 당신에게 커다란 힘이 되어줄 것입니다.] | Skill/ability label vs flavor text; mechanic not present in this fragment |

## Review rules

1. These fragments are not complete effect definitions. Recover full card-local source text before interpretation.
2. For every candidate, record exact card ID, source field, clause index, full surrounding text, and source URL.
3. Separate mechanic text, named-card references, status explanations, flavor, historical notices, and formatting artifacts.
4. Do not infer a formula from a rounding note without identifying its numerator, denominator, and operation order.
5. Do not implement fragments whose referenced table/profile/card list is missing.
6. Preserve original 206-pattern queue classification until a reviewed, evidence-backed adjudication is committed.

## Next pass

Start with complete card context for 라이트닝버그, 녹음의습격, 추억, and the two rounding fragments. These have the clearest potential to unlock executable semantics once their missing context is recovered. Keep all other entries pending.
