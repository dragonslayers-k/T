# DB29 audit #663 — P1 source-snapshot crosswalk, batch 1

Date: 2026-11-06  
Baseline: immutable DB29 / audit #663 / source SHA `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`  
Review branch: `feat/carddb-effect-semantic-pass`  
Input snapshot: Library `cards.json`, captured 2026-11-01; 15,350 records; 59,464,588 bytes; SHA-256 `76346a8bc28bc70d04d4173b0f715337fea515729cd5e327f61271c9ed163a5c`.

## Scope and evidence level

This pass compares the audit #663 candidates to the archived card-data snapshot. It verifies the corresponding snapshot record and its printed card metadata. It does **not** independently retrieve the live FMLunatic detail pages, the original game client, or an authoritative rules manual. The web reader could not access the referenced FMLunatic detail URLs during this pass.

For the five unit examples, the source-ID-to-asset-code association follows the date/suffix pattern in the candidate detail IDs and snapshot asset codes. Treat this as a snapshot crosswalk, not an independently validated live-page mapping. The effect clause itself is present in audit #663's raw queue but is absent from these snapshot card `text` fields; that missing surrounding source text remains an evidence gap.

## Candidate A — 모래돌풍 / E663-0621

Audit row:
- Detail ID: `7050231385`
- Snapshot asset code: `M01385S`
- Snapshot name/type: 모래돌풍 / 마법
- Snapshot `detailStatus`: `ok`
- Faction/attribute: earth / 대지
- Rarity / episode: 언커먼 / Episode12
- Trigger and duration in snapshot description: 방어 / 1턴
- Raw effect text in audit queue: `적 필드 유닛이 2마리 이상이고 모두 같은 종류의 유닛일 경우 적 전체 AP, HP는 적 필드 빈 공간 수가 된다. 종류가 다를 경우 효과 없음. [모두 대피하도록 해!]`

### Confirmed from the snapshot
- The matching card record is a spell, with the same name and the same effect text in the snapshot.
- The snapshot supplies activation timing (방어) and stated duration (1턴), which were not included in the batch-1 note's initial excerpt.

### Still unresolved
- “같은 종류” identity key: race, unit ability, card name, asset identity, or another game classification.
- Whether the count includes special/hidden/otherwise excluded units.
- When empty field slots are sampled relative to resolution.
- Whether AP/HP are assigned as absolute values or altered by a delta; the engine's exact operation is not specified by the wording alone.
- Whether “적 전체” includes every enemy unit and how duration/reversion interacts with other effects.
- Need a live detail-page/manual evidence capture and a focused engine test before adjudication.

Disposition: `pending_source_review` / `non_executable`.

## Candidate B — same-name hand prerequisite / post-activation AP or HP threshold

The five audit IDs crosswalk by date/suffix to these archived unit records:

| Audit detail ID | Snapshot asset code | Name | Race | Affiliation | Unit ability | Skill in snapshot |
|---|---|---|---|---|---|---|
| `11011925566` | `U05566S` | 티니아 | 스피릿 | 없음 | 마법 | 없음 |
| `11011925567` | `U05567S` | 네추럴마스터 | 휴먼 | 드루이드 | 장비 | 야수조련 |
| `11011925568` | `U05568S` | 아크위자드 | 휴먼 | 위자드 | 마법 | 방어무시 |
| `11011925569` | `U05569S` | 레스베르크 | 자이언트 | 없음 | 장비 | 없음 |
| `11011925570` | `U05570S` | 골드드래곤 | 드래곤 | 노블 | 야수 | 없음 |

All five snapshot records report `detailStatus=ok`. Their recorded effect clause from the audit queue is:

`(핸드에 자신과 같은 이름을 가진 유닛이 없을 경우나 해당 유닛의 AP나 HP가 발동 후 0이하가 되는 경우 아무 효과 없음).`

### Crosswalk finding
- These five cards are **not one shared identity/class** in the archived card data: they have different names, races, affiliations, unit abilities, and in several cases distinct skills.
- The audit wording appears as a repeated clause across five separately identified cards. This is evidence of shared wording only; it does not establish identical surrounding effects or the exact meaning of “자신” and “해당 유닛.”
- The snapshot contains card stats/metadata but does not include this condition in the corresponding `text` fields. It therefore cannot resolve the clause's scope or timing.

### Still unresolved
- Whether “자신과 같은 이름” compares display name, asset/card family, or another rule-defined identity.
- Whether “해당 유닛” means the effect source, activated unit, or a referenced target.
- What “발동 후” means in the resolution sequence (cost payment, activation, first clause, or final resolution).
- Whether “아무 효과 없음” cancels the entire effect or only a specific clause, and whether the condition is global or per target.
- Individual full source pages and surrounding clauses for all five IDs must be captured before grouping them into one executable rule.

Disposition for all five: `pending_source_review` / `non_executable`. No executable rule is promoted.

## Candidate C — 프리징 / E663-0548

Audit row:
- Detail ID: `6080231185`
- Snapshot asset code: `M01185S`
- Snapshot name/type: 프리징 / 마법
- Snapshot `detailStatus`: `ok`
- Faction/attribute: water / 물
- Rarity / episode: 스페셜 / Episode10
- Trigger and duration in snapshot description: 방어 / 1턴
- Exact audit text: `아군필드 유닛 수+1로 적필드 유닛 전체 공체를 나눔. (대림) 적 필드 유닛 5이상 이면 적 전체 행동불능. [많은 군사를 보냈으나, 여신이 지배하는 차가운 땅은 지나갈 수 없습니다.]`

### Confirmed from the snapshot
- The snapshot preserves the exact spelling `(대림)`; do not silently correct it to `(내림)`.
- The card is a defensive spell with stated one-turn duration.

### Still unresolved
- Meaning of `공체` and exact AP/DP/HP mapping.
- Whether the division applies individually or across an aggregate, and rounding behavior.
- Whether “적 필드 유닛 5이상” is evaluated before or after the division and what units are counted.
- Meaning, duration, and removal of `행동불능`; whether all enemy units are eligible.
- Full live-page/manual evidence and engine assertions are required.

Disposition: `pending_source_review` / `non_executable`.

## Batch outcome

| Candidate | Snapshot identity crosswalk | Timing/duration found | Semantics adjudicated | Executable |
|---|---:|---:|---:|---:|
| 모래돌풍 | Yes, snapshot record | 방어 / 1턴 | No | No |
| Five same-name clause cards | Date/suffix crosswalk; live mapping not independently confirmed | Not supplied by this snapshot | No | No |
| 프리징 | Yes, snapshot record | 방어 / 1턴 | No | No |

This pass adds source-snapshot identity and metadata evidence, but **does not close any effect-semantic queue item**. No DB29 source data, release artifact, executable interpretation, or completion count is changed.

## Next focused step

Acquire the live source-page HTML/card image or a manual excerpt for the five unit cards and the two spell cards. Capture the exact surrounding text and source timestamp/checksum. Then adjudicate only fields directly supported by those sources; build positive/negative/boundary engine tests only after target identity, timing, operation, duration, and “no effect” scope are resolved.
