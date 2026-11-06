# FM1 Skill1 source-linked assertion gap: suppression and beast-tamer follow-up
- Date: 2026-11-06
- CardDB branch: `feat/carddb-effect-semantic-pass`
- APK branch inspected: `feat/combat-event-foundation`
- Scope: documentation-only gap assessment; no gameplay implementation or test result is claimed.

## Branch snapshot
- CardDB branch HEAD: `6fcf528238a628662dd2e8ebcb260be651b0e700` (DB29 source-row crosswalk follow-up).
- APK branch HEAD: `4033c1ab84c054c070ad187106a577600585503a` (data-only unit-status record foundation).
- The branch heads were fetched from GitHub during this review.

## Current verified boundary
The previous crosswalk records exact DB29 Skill1 source labels and sample card IDs. That proves source-row association, not the detailed behavior of each card in the battle engine.

The existing aggregate fixtures are not equivalent to card-local proof:
- Beast-tamer aggregate assertions use the Beast ability/tag and a target-side category; the assertion does not bind behavior to a specific card ID from the source crosswalk.
- Spell/weapon suppression assertions use target semantic tags/fixtures. They do not establish the complete meaning of a specific source card's printed effect.
- The APK normalization alias `기술봉쇄` → `봉쇄공격` is a naming bridge only. It is not sufficient to certify the ability-seal effect.

## Source-linked categories and evidence references
| Category | Exact DB29 source label / count | Crosswalk examples | Assertion gap |
|---|---|---|---|
| Beast tamer | 야수조련 / 63 | 네추럴마스터 `11011925567`; 리틀페어리 `11070625790`; 묘인족소녀 `11090725878` | Need inspect the full card text and manual clause, then a test keyed to one card’s actual rule—not merely a synthetic tag. |
| Spell suppression | 주문봉쇄 / 56 | 혼드비스트 `10010624550`; 냉기의정령 `11062225775`; 심해의인어 `11070625788` | Need establish exactly what the printed skill suppresses, its timing/target, and expiry from source/manual before coding. |
| Weapon suppression | 무기봉쇄 / 48 | 데크라프 `10010624543`; 포레스키퍼 `10020324651`; 오우거워리어 `10040724792` | Need distinguish weapon/item effects from general equipment or ability tags; require source card text and timing. |
| Ability seal | 기술봉쇄 / 203 | 환상낚시꾼 `10020324644`; 시서펜트 `10021724690`; 커시드아이 `10030324717` | Do not treat the current alias as semantic implementation; need a card-local source-linked assertion. |

## Acceptance gate for the next implementation
1. Read the complete DB29 source row/card text for a selected representative card and the matching Manual clause.
2. Record literal source wording separately from interpretation; if a condition or duration is absent/ambiguous, keep it marked unresolved.
3. Add a focused test with the real card ID/source wording and assert target, effect, timing, and expiry only where documented.
4. Confirm the test fails before implementation and passes after; run the relevant local test command and report the exact result.
5. Extend to the remaining source-linked cards only after this representative case is sound.

## Non-actions / guardrails
- No DB30 publication.
- No merge of CardDB PR #9 or APK PR #28.
- No gameplay code changed and no CI success is asserted by this document.
- This audit does not mark any of these four Skill1 rules complete or executable.
