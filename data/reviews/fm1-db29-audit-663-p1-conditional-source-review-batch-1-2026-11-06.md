# DB29 audit #663 — P1 conditional/formula source review (batch 1)

Date: 2026-11-06  
Baseline: immutable DB29 / audit #663 / source SHA 75584d92ac4b4812f94d99fbc34f1360ea68eaf7  
Work branch: feat/carddb-effect-semantic-pass  
Purpose: source-backed review queue organization only. This document does **not** approve an executable handler, alter DB29, or publish DB30.

## Scope and handling

The audit #663 low-confidence queue contains 1,249 effect rows across 716 normalized text patterns. Its deterministic triage labels are candidate organization, not semantic adjudication. This batch focuses on explicit conditional phrases with card-level IDs and exact source URLs retrieved from the audit queue.

For every candidate, preserve exact Korean source text, punctuation, parenthetical clauses, card ID/name/type and source detail URL. Do not infer unstated timing, duration, target selection or engine operation. Retain pending_source_review and non_executable until evidence closes required fields.

## Candidate A — field composition and empty-space formula

- Audit cluster: E663-0621
- Card: 7050231385 / 모래돌풍 / 마법
- Source: https://fmlunatic.com/card/7050231385
- Exact source text:
  > 적 필드 유닛이 2마리 이상이고 모두 같은 종류의 유닛일 경우 적 전체 AP, HP는 적 필드 빈 공간 수가 된다. 종류가 다를 경우 효과 없음. [모두 대피하도록 해!]
- Queue status: pending_source_review; execution: non_executable

### Explicitly stated
- Enemy field unit count is at least two.
- All those units are the same “kind.”
- On the qualifying branch, enemy-wide AP and HP are assigned the enemy field's empty-space count.
- On the nonqualifying branch, the text says no effect.

### Unresolved
- Does “enemy field unit” include unusual/hidden/subtype cards?
- Does “same kind” mean card identity, class, race, or another game-defined classification?
- Is empty-space count sampled before resolution, after slot changes, or at a defined trigger?
- Is AP/HP set (replace) or changed by delta? “된다” needs engine confirmation.
- Duration, revert behavior, and interaction with subsequent effects are unstated.
- Confirm from the full source record that this clause is effect body, not explanatory text.

## Candidate B — same-name hand prerequisite and post-activation zero threshold

- Audit examples:
  - 11011925566 / 티니아 / 유닛
  - 11011925567 / 네추럴마스터 / 유닛
  - 11011925568 / 아크위자드 / 유닛
  - 11011925569 / 레스베르크 / 유닛
  - 11011925570 / 골드드래곤 / 유닛
- Source example: https://fmlunatic.com/card/11011925566
- Exact clause from queue:
  > (핸드에 자신과 같은 이름을 가진 유닛이 없을 경우나 해당 유닛의 AP나 HP가 발동 후 0이하가 되는 경우 아무 효과 없음).
- Queue status: pending_source_review; execution: non_executable

### Explicitly stated
- A hand prerequisite checks for a unit with the same name as “self.”
- A second no-effect condition refers to AP or HP after activation, at or below zero.

### Unresolved
- Does “self” mean source unit, activated unit, or linked target?
- Does “same name” compare localized display name, card ID family, or source-defined identity?
- What does “after activation” mean: after cost payment, initial effect, all clauses, or resolution?
- Is the no-effect condition checked once globally or per target/clause?
- Does “no effect” cancel only the referenced effect or every clause?
- The five cards require individual surrounding-text review; shared wording does not prove identical full effects.

## Candidate C — explicit field-count threshold and incapacitation

- Audit source example: 6080231185 / 프리징 / 마법
- Source: https://fmlunatic.com/card/6080231185
- Exact source text:
  > 아군필드 유닛 수+1로 적필드 유닛 전체 공체를 나눔. (대림) 적 필드 유닛 5이상 이면 적 전체 행동불능. [많은 군사를 보냈으나, 여신이 지배하는 차가운 땅은 지나갈 수 없습니다.]
- Queue status: pending_source_review; execution: non_executable

### Explicitly stated
- A formula involving allied field unit count plus one and division of enemy field units' “공체.”
- Enemy field unit count is at least five.
- The stated consequence is enemy-wide incapacitation.

### Unresolved
- Exact engine stat mapping of “공체.”
- Integer rounding: “대림” may be a typo/variant; do not silently normalize it to “내림.”
- Whether division is per enemy, aggregate, or selected subset.
- Whether incapacitation condition is checked before or after formula changes.
- Duration, removal, target eligibility and ordering are not specified.

## Batch disposition

| Candidate | Source-backed text captured | Identity verified | Rule adjudicated | Executable |
|---|---:|---:|---:|---:|
| E663-0621 모래돌풍 | Yes | Card ID + URL in queue | No | No |
| Same-name / post-activation zero clause | Yes | Five IDs; surrounding text not yet crosschecked | No | No |
| 프리징 field-count threshold | Yes | Card ID + URL in queue | No | No |

This batch advances source-aware decomposition, not semantic completion. Do not increment completed/executable counts from this document. Next: obtain complete card source records/manual evidence, settle timing and classification questions, then create narrowly scoped engine assertions only for fully evidenced behavior.
