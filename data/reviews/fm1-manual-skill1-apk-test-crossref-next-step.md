# Manual Skill1 × APK test traceability matrix — 2026-11-05

## Scope and state
- Immutable baseline: fm1-carddb-29. No DB29 changes, DB30 publication, main merge, or PR merge.
- Exact Manual Skill1 label match: 27 rules / 3,158 DB29 Skill1 source rows.
- Formal spec: 27 definitions, 0 executable, 0 card-specific source matches, 108 design-only cases (4 conceptual cases per rule).
- Every rule remains pending_engine_test.
- “Test mentions” are literal references in FM-OFFLINE/tests/rules.test.cjs. They are not assertion counts, coverage, or pass results.

## Rule matrix

| rule_id | Manual label | Exact DB29 rows | Test mentions | Status / gap |
|---|---|---:|---:|---|
| normal_attack | 일반공격 | 68 | 5 | Pending source match + dedicated cases |
| defense_bypass | 방어무시 | 234 | 12 | Partial runtime evidence; map exact source and boundaries |
| fatal_attack | 치명공격 | 153 | 3 | Partial evidence; post-attack HP and HP=0 edge |
| piercing_attack | 관통공격 | 172 | 2 | Partial evidence; DP marker and overflow-to-HP |
| weaken_attack | 약화공격 | 141 | 3 | Pending marker/temporary-stat coverage |
| petrify_attack | 석화공격 | 120 | 3 | Pending set-AP-zero / DP increase markers |
| vampiric_attack | 흡혈공격 | 115 | 4 | Pending actual HP damage, DP block, cap and marker |
| aging_attack | 노화공격 | 53 | 2 | Pending source match and duration |
| charge_attack | 돌진공격 | 189 | 3 | Pending source match, trigger and target semantics |
| beast_tamer | 야수조련 | 63 | 2 | Partial runtime evidence; source-grounded boundaries |
| bravery_attack | 용맹공격 | 221 | 4 | Partial; AP threshold and AP-zero exception |
| regeneration | 재생능력 | 157 | 2 | Pending source match, timing, cap and marker |
| frenzy_attack | 광분공격 | 110 | 3 | Partial; trigger and ordering |
| consecutive_attack | 연속공격 | 116 | 2 | Pending repeated attack order and stop conditions |
| fear_attack | 공포공격 | 167 | 4 | Partial; level threshold and AP-zero exception |
| charm_attack | 매료공격 | 127 | 2 | Pending target eligibility and duration |
| ability_seal | 기술봉쇄 | 203 | 2 | Pending exact scope (skill/ability) |
| spell_suppression | 주문봉쇄 | 56 | 1 | Pending source match and spell timing |
| weapon_suppression | 무기봉쇄 | 48 | 1 | Pending source match and equipment scope |
| copy_attack | 공격복제 | 48 | 1 | Partial; copied state and action ordering |
| shield_break | 방패파괴 | 96 | 6 | Partial; alias normalization is not semantic coverage |
| curse_attack | 저주공격 | 84 | 2 | Pending source match, effect and duration |
| defensive_use | 방어이용 | 164 | 3 | Pending source match and defensive timing |
| taunt_attack | 조롱공격 | 47 | 2 | Pending source match and target selection |
| confusion_attack | 혼란공격 | 94 | 2 | Partial; deterministic target resolution |
| stealth_attack | 은폐공격 | 86 | 3 | Pending visibility/targeting interaction |
| defense_convert | 방어변환 | 26 | 1 | Partial; source-specific conversion limits |

## Reconciliation and next execution gate
- Counts show source-label presence only. No rule is promoted by this matrix.
- Runtime audit identified focused or aggregate evidence for defense bypass, fatal, piercing, beast tamer, bravery, frenzy, fear, copy, shield break, confusion, and defense conversion. Aggregate tests do not establish exact rule-id completeness.
- Next, create a per-rule evidence packet: exact DB29 card ID, Skill1 label, verbatim source text, detail URL; Manual clause/exception; expected output and timing; positive, negative, boundary, interaction assertions; engine handler and test result.
- Source-unmatched rows stay explicitly pending. No guessed card IDs; Skill1 and Skill2 remain separate.
- Prioritize inspecting existing test bodies for the partial-evidence subset, then match exact card-source rows from the immutable DB29 artifact before implementation.

## Safety
DB29 remains immutable. No DB30, main merge, or PR merge. This document only records traceability; runtime and card source data are unchanged.
