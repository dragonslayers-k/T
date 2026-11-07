# DB29 source-to-runtime crosswalk — Beast Tamer / Spell Suppression / Weapon Suppression

Date: 2026-11-07 (KST)  
Immutable input: `fm1-carddb-29` (15,350-card source snapshot; no DB30)  
Review branch: `feat/carddb-effect-semantic-pass`  
Purpose: connect exact DB29 source records to existing Manual Skill1 runtime mappings and APK assertions. This is provenance reconciliation, not a new rule promotion.

## Evidence chain

For the three rows below, the Android data pack generated from the DB29 SQLite release preserves:
- exact `sourceCardUrl` and `sourceFields.Skill1/Skill2`;
- separate source Skill1 label and enum value;
- `specialSkillRuleId`, `specialSkillMappingStatus=manual_verified`, and `specialSkillRuleAuthority=manual`;
- normalized runtime metadata consumed by the app's Manual Skill1 authorization gate.

The app PR adds these three exact DB29 IDs to `verify-db29-skill1-runtime-normalization.cjs`. The validator now checks source label, Skill1 enum, source-card URL, and the original source-description clause before confirming the normalized Manual mapping. Existing `tests/rules.test.cjs` contains dedicated target-ability / AP-marker boundaries for these exact IDs. This separates (a) source-to-mapping lineage from (b) the engine behavior assertion.

## Card-level crosswalk

| DB29 ID / card | Source Skill1 / enum | Source URL | Manual rule ID | Exact source clause |
|---|---|---|---|---|
| `11011925567` 네추럴마스터 | 야수조련 / `450` | https://fmlunatic.com/card/11011925567 | `beast_tamer` | `AP1 이상으로 공격시 상대가 야수면 상대는 AP,DP=0.` |
| `10010624550` 혼드비스트 | 주문봉쇄 / `602` | https://fmlunatic.com/card/10010624550 | `spell_suppression` | `AP1 이상으로 공격시 상대가 마법이면 상대는 AP,DP=0 이 된다.` |
| `10010624543` 데크라프 | 무기봉쇄 / `224` | https://fmlunatic.com/card/10010624543 | `weapon_suppression` | `AP1 이상으로 공격시 상대가 장비면 상대는 AP,DP=0 이 된다.` |

Source data also retains the original Skill2 enum `1` / label `없음` for each row. Costs are source-enum decoded and marked known in the generated DB29 Android pack: Natural Master `forest 4 + neutral 3`, Hound Beast `fire 3 + neutral 2`, and Deckraf `dark 3 + neutral 2`. Cost verification is independent from effect verification.

## Explicit boundary

- The rule mappings above are backed by exact Manual Skill1 labels and their card-specific source clauses.
- The APK test boundaries check target ability match/non-match, attacker AP=0 no-trigger, and target AP marker `△` blocks / `▽` permits the AP reduction.
- These assertions do not certify every interaction, duration, or every card that shares the same Skill1 label.
- 네추럴마스터's source description also includes a separate `섀도우오라` activation: cost, repeat-use surcharge, same-name hand-unit prerequisite, AP/HP exchange, and the no-effect threshold. That is a separate effect clause; it is **not** implied executable by the `beast_tamer` Skill1 mapping and remains out of scope for this crosswalk.
- No new rule handler, card mapping, runtime disposition, or SQLite row is promoted by this document.

## Disposition

This closes a narrowly defined source-lineage gap for three Manual Skill1 mappings. The next step is to reconcile source-linked cases with the engine authorization/effect timing in a dedicated end-to-end test, and then continue with the next independently evidenced Manual rule. DB29 remains immutable; DB30 is not published; PR #9 and PR #28 remain unmerged.
