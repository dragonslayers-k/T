# DB29 Manual Skill1 source-card evidence sample — 2026-11-05

## Why this exists
This is a focused follow-on to the exact Skill1 audit, to anchor each Manual rule to concrete immutable DB29 card IDs. It is a **sample index**, not a complete 3,158-row export and not semantic/runtime approval.

## Provenance
- Immutable release: `fm1-carddb-29`
- Actions run #558: https://github.com/dragonslayers-k/T/actions/runs/41960519675
- Source-match artifact ID: `13384922100` (file: `fm1-manual-skill-db29-source-match-2026-11-05.json`)
- Artifact summary: 27 Manual rules; 27/27 have exact Skill1 source rows; 3,158 matched card rows; zero runtime-executable rules.
- Matching rule: Unicode NFKC normalization + whitespace removal, then canonical Manual label or explicit catalog alias equality. No substring/name inference.
- Card detail URL pattern is retained by the report per card: `https://fmlunatic.com/card/{card_id}`.

## Rule-level sample index
Each row lists total exact matching rows and three sample card IDs/names from the report. Samples do not imply all cards share identical contextual behavior; runtime is not promoted.

| rule_id | Manual label | Exact rows | Sample card ID : name |
|---|---|---:|---|
| normal_attack | 일반공격 | 68 | 10020341112 은룡의검; 10050441143 악마의항아리; 10060141149 마녀의비약 |
| defense_bypass | 방어무시 | 234 | 10091525193 카오틱비스트; 10091525203 워락커맨더; 10091525210 태세킬러 |
| fatal_attack | 치명공격 | 153 | 10012024612 선더골렘; 10040724800 어세신; 10042124825 정글수인 |
| piercing_attack | 관통공격 | 172 | 10091525214 블랙유니콘; 10100625250 실리데몬; 10100625284 엘더유니콘 |
| weaken_attack | 약화공격 | 141 | 10091525190 이블크로우; 10091525198 선더닛시; 10091525208 스톤홀더 |
| petrify_attack | 석화공격 | 120 | 10010624589 파프니르; 10020324638 데몬; 10030324714 커시드아이 |
| vampiric_attack | 흡혈공격 | 115 | 10010624542 다크카운티스; 10010624549 리빙블러드; 10012024607 플레임뱀프 |
| aging_attack | 노화공격 | 53 | 13020626691 타락자; 14043027368 좀비제작자; 14091727606 좀비솔져 |
| charge_attack | 돌진공격 | 189 | 10010624588 패스파인더; 10030324733 고대의순록; 10031724757 기간틱훼일 |
| beast_tamer | 야수조련 | 63 | 11011925567 네추럴마스터; 11070625790 리틀페어리; 11090725878 묘인족소녀 |
| bravery_attack | 용맹공격 | 221 | 10010624545 타투파이터; 10091525201 정글전사; 10091525205 전투닭 |
| regeneration | 재생능력 | 157 | 10010624560 울프라이더; 10091525206 스톤아머; 10092925234 어스홀더 |
| frenzy_attack | 광분공격 | 110 | 10010624538 다크퍼밀리어; 10020324630 뱀파이어; 10030324712 바일데몬 |
| consecutive_attack | 연속공격 | 116 | 10050441142 트윈스컬소드; 10060124895 이블사이더; 10080425067 더블블레이드 |
| fear_attack | 공포공격 | 167 | 10050424835 다크프리스트; 10120125448 북해의무법자; 11040625646 이블자이언트 |
| charm_attack | 매료공격 | 127 | 10020324637 데몬; 10030324724 윈드메이커; 10060124928 바니트 |
| ability_seal | 기술봉쇄 | 203 | 10020324644 환상낚시꾼; 10021724690 시서펜트; 10030324717 커시드아이 |
| spell_suppression | 주문봉쇄 | 56 | 10010624550 혼드비스트; 11062225775 냉기의정령; 11070625788 심해의인어 |
| weapon_suppression | 무기봉쇄 | 48 | 10010624543 데크라프; 10020324651 포레스키퍼; 10040724792 오우거워리어 |
| copy_attack | 공격복제 | 48 | 10050441147 진실의거울; 10100625259 드림이터; 11020125588 사막주술사 |
| shield_break | 방패파괴 | 96 | 10010624551 해적전투원; 10091525199 스트롱빈; 10091525202 메탈팬더 |
| curse_attack | 저주공격 | 84 | 10030324708 다크조커; 10030324711 비토르; 10031724755 스컬윙제너럴 |
| defensive_use | 방어이용 | 164 | 10010624568 포춘텔러; 10010624591 필기엔; 10030324730 볼드리솔져 |
| taunt_attack | 조롱공격 | 47 | 10030324709 다크조커; 11050425688 갬블러조커; 11120726043 콩 |
| confusion_attack | 혼란공격 | 94 | 10040724804 견습수도사; 10092025225 브로큰노움; 11080325818 순욱 |
| stealth_attack | 은폐공격 | 86 | 10040724812 블라인드랩터; 10060124927 샌드터틀; 11050425694 드래곤터틀 |
| defense_convert | 방어변환 | 26 | 10010624563 리듬포이; 10030324725 윈드메이커; 10040724779 룬메이커 |

## Next review gate
1. Read each sampled card's original Skill1 and source URL in the immutable report.
2. Compare the Manual rule definition and exceptions against actual APK handler behavior.
3. Create dedicated positive, negative, boundary, and interaction assertions only where source text gives a deterministic expected result.
4. Keep ambiguous / context-dependent behavior non-executable.
5. Expand this sample index into a complete per-card linked review queue before any promotion.

## No-release guard
DB29 remains immutable; DB30 is not issued; no `main` merge or PR merge is authorized by this audit.