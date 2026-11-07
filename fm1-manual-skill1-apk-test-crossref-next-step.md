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
| normal_attack | 일반공격 | 68 | 5 | Exact label match complete; dedicated baseline/negative/boundary cases needed |
| defense_bypass | 방어무시 | 234 | 12 | Partial runtime evidence; map exact source and boundaries |
| fatal_attack | 치명공격 | 153 | 3 | Partial evidence; post-attack HP and HP=0 edge |
| piercing_attack | 관통공격 | 172 | 2 | Partial evidence; DP marker and overflow-to-HP |
| weaken_attack | 약화공격 | 141 | 3 | Pending marker/temporary-stat coverage |
| petrify_attack | 석화공격 | 120 | 3 | Pending set-AP-zero / DP increase markers |
| vampiric_attack | 흡혈공격 | 115 | 4 | Pending actual HP damage, DP block, cap and marker |
| aging_attack | 노화공격 | 53 | 2 | Exact label match complete; duration/expiry boundaries needed |
| charge_attack | 돌진공격 | 189 | 3 | Exact label match complete; trigger/target semantics need dedicated cases |
| beast_tamer | 야수조련 | 63 | 2 | Partial runtime evidence; source-grounded boundaries |
| bravery_attack | 용맹공격 | 221 | 4 | Partial; AP threshold and AP-zero exception |
| regeneration | 재생능력 | 157 | 2 | Exact label match complete; timing/cap/marker boundaries needed |
| frenzy_attack | 광분공격 | 110 | 3 | Partial; trigger and ordering |
| consecutive_attack | 연속공격 | 116 | 2 | Exact label match complete; repeated attack order/stop conditions need dedicated cases |
| fear_attack | 공포공격 | 167 | 4 | Partial; level threshold and AP-zero exception |
| charm_attack | 매료공격 | 127 | 2 | Pending target eligibility and duration |
| ability_seal | 기술봉쇄 | 203 | 2 | Pending exact scope (skill/ability) |
| spell_suppression | 주문봉쇄 | 56 | 1 | Exact label match complete; spell timing/scope tests needed |
| weapon_suppression | 무기봉쇄 | 48 | 1 | Exact label match complete; equipment scope tests needed |
| copy_attack | 공격복제 | 48 | 1 | Partial; copied state and action ordering |
| shield_break | 방패파괴 | 96 | 6 | Partial; alias normalization is not semantic coverage |
| curse_attack | 저주공격 | 84 | 2 | Exact label match complete; effect/duration tests needed |
| defensive_use | 방어이용 | 164 | 3 | Exact label match complete; defensive timing tests needed |
| taunt_attack | 조롱공격 | 47 | 2 | Exact label match complete; target-selection tests needed |
| confusion_attack | 혼란공격 | 94 | 2 | Partial; deterministic target resolution |
| stealth_attack | 은폐공격 | 86 | 3 | Pending visibility/targeting interaction |
| defense_convert | 방어변환 | 26 | 1 | Partial; source-specific conversion limits |

## Reconciliation and next execution gate
- Counts show source-label presence only. No rule is promoted by this matrix.
- Runtime audit identified focused or aggregate evidence for defense bypass, fatal, piercing, beast tamer, bravery, frenzy, fear, copy, shield break, confusion, and defense conversion. Aggregate tests do not establish exact rule-id completeness.
- Next, create a per-rule evidence packet: exact DB29 card ID, Skill1 label, verbatim source text, detail URL; Manual clause/exception; expected output and timing; positive, negative, boundary, interaction assertions; engine handler and test result.
- Source-unmatched rows stay explicitly pending. No guessed card IDs; Skill1 and Skill2 remain separate.
- Prioritize inspecting existing test bodies for the partial-evidence subset, then match exact card-source rows from the immutable DB29 artifact before implementation.

## 2026-11-05 reconciliation — existing work carried forward

### Completed exact-label matching (do not repeat)

Actions #571 produced `FM1-Manual-Skill1-DB29-Source-Match.zip` and the report `fm1-manual-skill-db29-source-match-2026-11-05.json`.

- Match method: Unicode NFKC normalization + whitespace removal, then exact canonical label or catalog alias only.
- Manual rules matched: **27/27**.
- Exact DB29 Skill1 rows: **3,158**.
- Rules without exact label rows: **0**.
- Substring/inferred matching used: **0**.
- Source URL missing among matched rows: **0**.
- Runtime-executable rules: **0** (correctly still pending engine validation).

Every rule now has a representative exact card ID, card name, Skill1 source enum, exact label and detail URL in the updated `fm1-manual-skill-engine-test-spec-2026-11-05.json`. The full 3,158-row match inventory remains in the #571 artifact. Do not rerun A1~A75 or the 27-rule label match as a new task.

### Current APK evidence inspected

- APK PR #28 branch: `feat/combat-event-foundation`, HEAD `221b3e9a8cf2ea8ccc386a5c0037303181b94441`.
- Actions #181 passed at the same SHA, including JS rules, converter, DB29 data ZIP, Debug APK build, emulator installation and 15,350-card import/WebView smoke path.
- Current `tests/rules.test.cjs`: 112 top-level tests.
- Existing Manual Skill1 tests include: one 25-rule aggregate behavior test; a 27-rule canonical-ID/name catalog check; a source-name alias execution test for defense bypass, ability seal, spell suppression, weapon suppression, copy and defense conversion; fail-closed metadata tests; focused defense-bypass and fatal-attack boundary tests; bravery/fear level/AP-zero tests.
- These are meaningful existing tests, not 27 complete rule-specific positive/negative/boundary/interaction suites. Keep per-rule coverage pending where those assertions do not exist.

### Correct next step

Use the completed exact-match inventory as the starting index. Build rule-specific evidence packets and tests from the representative card IDs and Manual clauses. Prioritize rules whose current handler only appears in the 25-rule aggregate test or has no independent negative/boundary case; do not repeat source-name matching. Keep Skill2 and inferred Skill1 candidates in separate lanes.

## Safety
DB29 remains immutable. No DB30, main merge, or PR merge. This document only records traceability; runtime and card source data are unchanged.
