# DB29 low-confidence effect text triage — pass 1 (11 conditional/reference candidates)

## Scope

Input: DB29 run #430 `gap-reports/effect-review-queue.jsonl`.

- 206 low-confidence patterns total: 195 `unparsed_effect_text`, 11 `conditional_or_reference_candidate`.
- All 206 remain `pending_manual_semantic_review` in the source report.
- This pass triages only the 11 conditional/reference candidates. It does not promote any pattern to an executable rule and does not modify DB29.
- Direct fmlunatic card-page retrieval for the candidate URLs was unavailable in this review environment; search-index lookup did not return corroborating excerpts. The classifications below therefore rely only on the extracted source snippets and card IDs in the DB29 artifact.

## Adjudication

| Pattern ID | Card ID / name | Source snippet | Triage result | Runtime status |
|---|---|---|---|---|
| `13ec90bd4a784258` | 13010233093 준비된매복 | 4레벨 이상시 재생생 되지 않음. | Incomplete condition/continuation fragment. Preserve typo as source; do not assume whether "재생성" or a specific object is intended. | unresolved / non-executable |
| `1bf125406d77bcfa` | 3062730289 간절한기도 | 레벨3 이하 아군 장비, 마법 전체는 순화능력을 갖는다. [lore] | Named ability grant to friendly equipment/spells of level ≤3; bracketed prayer is flavor. Need authoritative definition of "순화능력" and eligible card types. | reference candidate / pending definition |
| `f40c7f6d92a7a8f1` | 11050432565 포메이션제로 | 베타: 아군 필드 알파, 베타, 감마, 델타, 오메가 유닛 전체 AP 상향고정 (영구히) | Explicit named-formation stat-marker effect. Need exact unit-name matching and "상향고정" marker semantics. | effect candidate / pending tests |
| `8e21d2b3765dca61` | 13070333254 소매치기체포 | 사파이어 : 언커먼. | Rarity/variant metadata, not an executable effect. | metadata reference / non-executable |
| `ec52d44db669c8b1` | 12071826357 글라디오나 | 아이템/인첸트 : 소드맨 1장, 포위공격 1장. | Named card-pool/quantity reference. Does not define trigger or selection rule by itself. | pool reference / pending linkage |
| `c76a77578ebf9b53` | 9012123779 두얼굴의신 | 야누스가면(만능능력)○ : 야누스, 0/*/0 | Named ability/stat profile. Preserve marker notation and field order; do not infer AP/DP/HP meaning or trigger from this fragment alone. | profile reference / pending context |
| `1141aa19576db2a3` | 15040133597 아쿠아웨이브 | 얼음꽃 : +2 / ▲2 / 0 | Named item/effect stat profile. The stat-field mapping and trigger are not in this fragment. | profile reference / pending context |
| `889cc1c0c8cc48ad` | 13041726794 라리슈어 | 전쟁의주인 : 알려지지 않은 미지의 힘입니다. | Explicitly unknown power description. No mechanic can be inferred. | opaque / non-executable |
| `f4ee4020dcd72dea` | 14070233472 소중한부화 | 피닉스의알 : 피닉스. / 티라노의알 : 티라노. | Named egg-to-unit mapping/reference. Need the trigger, selection rule, and exact card IDs from full source context. | card mapping reference / pending linkage |
| `803fd97369e9dc32` | 13082827041 흉성의군주 | 핸드 슬롯 1이 3레벨이상 카드인 경우 | Incomplete condition fragment. Requires the following effect clause and target/result. | unresolved / non-executable |
| `bfbf1439319b4d48` | 13041726793 오르브웨크 | 혼돈의주관자 : 알려지지 않은 미지의 힘입니다. | Explicitly unknown power description. No mechanic can be inferred. | opaque / non-executable |

## Triage totals

| Triage class | Patterns |
|---|---:|
| Incomplete condition/continuation fragments | 2 |
| Named ability/effect candidate needing definition | 1 |
| Explicit stat-marker effect candidate | 1 |
| Metadata/rareness reference | 1 |
| Card pool/quantity reference | 1 |
| Named stat/profile references | 2 |
| Opaque unknown-power descriptions | 2 |
| Card-to-card mapping reference | 1 |
| **Total** | **11** |

## Remaining low-confidence queue

- 195 `unparsed_effect_text` patterns remain unadjudicated in this pass.
- Do not treat the 11 triaged candidates as completed effects: 6 are reference/profile/metadata records, 2 are opaque, 2 are incomplete, and 1 requires a named ability definition.
- The `포메이션제로` marker candidate and `간절한기도` named ability grant require exact source context and regression tests before implementation.
- Preserve original source strings, card IDs, clause indices, and URLs. No auto-normalization of marker notation, rarity labels, or named profiles.
- DB29 immutable, DB30 not published, main/PRs remain unmerged.
