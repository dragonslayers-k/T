# DB29 audit #663 — E663-0014 [용의위압] status review

Date: 2026-11-06 (KST)  
Baseline: immutable `fm1-carddb-29`  
Audit run: `42173417874`  
Review branch: `feat/carddb-effect-semantic-pass`

## Cohort

The audit artifact contains seven occurrences of the exact extracted clause `[용의위압] 상태 :`. The card IDs below were matched by name to the DB29 `cards.json` snapshot (15,350 records).

| Detail ID | Card | Asset code | Faction | Chapter | Rarity | Race | Ability | Skill | AP/DP/HP |
|---|---|---|---|---|---|---|---|---|---|
| 15093028105 | 네투라 | U08105S | dark | Chapter13 | 이벤트 | 드래곤 | 야수 | 컨슘 | 9/1/10 |
| 15093028106 | 네하트라 | U08106S | fire | Chapter13 | 이벤트 | 드래곤 | 야수 | 컨슘 | 9/2/9 |
| 15093028107 | 네파다하 | U08107S | water | Chapter13 | 이벤트 | 드래곤 | 야수 | 컨슘 | 9/0/9 |
| 15093028108 | 이미피브 | U08108S | forest | Chapter13 | 이벤트 | 드래곤 | 야수 | 컨슘 | 9/1/8 |
| 15093028109 | 카디지크 | U08109S | metal | Chapter13 | 이벤트 | 드래곤 | 야수 | 컨슘 | 10/1/8 |
| 15093028110 | 루와다하 | U08110S | earth | Chapter13 | 이벤트 | 드래곤 | 야수 | 컨슘 | 8/1/9 |
| 15093028111 | 시메트라 | U08111S | light | Chapter13 | 이벤트 | 드래곤 | 야수 | 컨슘 | 8/1/10 |

All seven snapshot records list the release date 2015-09-30. The shared Chapter13 / Dragon / Beast / Consume pattern identifies a related cohort, but does not prove shared effect semantics. The snapshot records have `detailStatus=ok`, while their `텍스트` tabs are empty; only metadata is confirmed.

## Cross-reference and source access

A scan of all 716 audit clusters found no other literal `용의위압` occurrence and no other audit row for these seven IDs. Web-indexed searches for the status and card names returned no attributable card-specific effect text.

All seven detail URLs from the audit artifact were attempted and were inaccessible to the web reader:
- https://fmlunatic.com/card/15093028105
- https://fmlunatic.com/card/15093028106
- https://fmlunatic.com/card/15093028107
- https://fmlunatic.com/card/15093028108
- https://fmlunatic.com/card/15093028109
- https://fmlunatic.com/card/15093028110
- https://fmlunatic.com/card/15093028111

This is an acquisition limitation, not evidence that the pages or cards do not exist. General game reference pages do not define [용의위압] and were not used as semantic evidence.

## Unresolved semantic questions

No evidence currently establishes:
1. The exact effect or numerical modifier represented by [용의위압].
2. The recipient/target of the status.
3. The trigger and application timing.
4. Whether it is persistent, one-shot, duration-based, or tied to a separate named rule.
5. Stacking, refresh, expiration, and removal conditions.
6. Whether each of the seven card descriptions has a distinct continuation after the extracted heading.
7. Cost, target-selection, and resolution-order rules.

Required next evidence: full card-detail captures or original client/card images showing each complete effect body, plus an original manual/rule definition or reproducible engine observation. Preserve source URL, capture time, checksum, punctuation, and clause order.

## Disposition

- All seven rows remain `pending_source_review`.
- All seven effects remain `non_executable`.
- Do not infer a shared runtime status handler from cohort metadata.
- DB29 remains unchanged; do not publish DB30, merge PR #9, or run a full audit for this documentation-only review.
- This note records cohort reconciliation and blocked source acquisition; it is not semantic adjudication.

Next independent candidate: E663-0002 (`[영혼지배]상태`, nine occurrences). Do not transfer conclusions from E663-0014.
