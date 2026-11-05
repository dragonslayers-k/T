# Skill2 source evidence audit — pass 1 (DB29 / 2026-11-05)

## Scope and result

Input: `gap-reports/skill2-execution-review.jsonl` and `rules/fm1-skill2-execution-catalog-v1.json` from the DB29 semantic review artifact (run #430).

- Skill2 candidate card rows: **377**
- Candidate rule groups: **8**
- Rows with at least one matched card-local reference: **369**
- Rows with actual `additional_text` evidence: **368**
- Rows with only `card_text` noise and no `additional_text` effect excerpt: **1**
- Rows with no matched card-local excerpt: **8**
- `card_local_evidence_references`: 375 total references = 368 `additional_text` + 7 `card_text`.
- All 377 rows still have `mapping_status=inferred`; 369 are medium confidence and 8 low confidence. **No row is source-card-verified.**
- Therefore none of these 377 inferred card mappings may be promoted to executable by this audit. The 8 rule definitions are candidate semantics, not blanket card mapping approvals.

## Per-rule inventory

| Skill2 | Rule ID | Candidate rows | Additional-text rows | Missing rows | Distinct effect-text variants |
|---|---|---:|---:|---:|---:|
| 기선제압 | `inferred_skill2_18` | 181 | 175 | 5 | 6 |
| 헌신방어 | `inferred_skill2_175` | 66 | 63 | 3 | 6 |
| 얼라이디펜스 | `inferred_skill2_100` | 44 | 44 | 0 | 3 |
| 레이셜디펜스 | `inferred_skill2_44` | 35 | 35 | 0 | 2 |
| 강한헌신방어 | `inferred_skill2_3` | 28 | 28 | 0 | 2 |
| 격노 | `inferred_skill2_5` | 20 | 20 | 0 | 2 |
| 홀리오오라 | `inferred_skill2_181` | 2 | 2 | 0 | 2 |
| 프레셔 | `inferred_skill2_166` | 1 | 1 | 0 | 1 |
| **합계** | | **377** | **368** | **8** | **24 rule-local variants** |

The 7 `card_text` references are not Skill2 effect evidence; they are item ability/build-up descriptions or flavor prose. Six of those cards also have separate `additional_text` evidence; one row has only the card_text excerpt and must remain unsupported.

## Eight missing card-local evidence rows

| Card ID | Name | Skill2 | Enum | Note |
|---|---|---|---:|---|
| 12111426500 | 신비의바다 | 기선제압 | 18 | no matched Skill2 effect excerpt |
| 16102628565 | 마왕 | 기선제압 | 18 | TextBase/TextExtra confirmed empty |
| 16110928590 | 불의정령여왕 | 기선제압 | 18 | TextBase/TextExtra confirmed empty |
| 6121340763 | 고대나무뿌리 | 기선제압 | 18 | item; TextExtra empty; no matched excerpt |
| 8080640943 | 용기의정령 | 기선제압 | 18 | item; TextExtra empty; no matched excerpt |
| 14031227302 | 순수한레비 | 헌신방어 | 175 | TextBase empty; no matched Skill2 excerpt |
| 16110228578 | 설원고양이 | 헌신방어 | 175 | TextBase/TextExtra confirmed empty |
| 16112328609 | 어둠기사 | 헌신방어 | 175 | TextBase empty; no matched Skill2 excerpt |

"No matched excerpt" is not proof that the skill does not function. It means this artifact does not contain card-local evidence sufficient to support the mapping. Do not infer a card's effect from its enum label alone.

## Source-text variant review

### 기선제압 — 6 additional-text variants / 175 rows

| Occurrences | Exact source wording |
|---:|---|
| 133 | 적군이 아군보다 이하 레벨일 경우 데미지를 1 덜 받는다. |
| 16 | 적군이 아군보다 이하 레벨인 경우 상대 AP로 인한 데미지를 1 덜 받는다. |
| 6 | 방어시, 상대의 레벨이 자신보다 이하면 받는 데미지를 1 감소시킨다. |
| 1 | 방어시, 상대의 레벨이 자신보다 낮은 경우 받는 데미지를 1 감소시킨다. |
| 18 | 방어시, 상대의 레벨 수치가 자신 레벨 수치 이하이면 자신이 받는 데미지를 1 감소시킨다. |
| 1 | 적군LV이 아군 이하일 경우 데미지를 1 덜 받는다 |

**Semantic boundary:** the 16-row variant explicitly limits reduction to damage caused by the opponent's AP; other variants say damage more generally. Strict "lower than" and inclusive "less than or equal" wording also differ. Do not silently collapse these into one condition without authoritative rule text.

### 헌신방어 — 6 additional-text variants / 63 rows

| Occurrences | Exact source wording |
|---:|---|
| 45 | 자신 파괴시 아군 필드 다음 유닛 공방체 +1 |
| 12 | 자신 파괴시 아군 필드 다음 유닛 공방체 +1. |
| 1 | 자신 파괴시 아군필드 다음 유닛 공방체 +1 |
| 3 | 자신 파괴시 아군 필드 다음 유닛 공방체+1 |
| 1 | 자신 파괴시, 아군 필드 다음 유닛의 AP/DP/HP를 1 증가시킨다. |
| 1 | 자신 파괴시 아군 다음 유닛 공방체 +1 |

The current catalog interpretation is the next friendly field unit after the destroyed slot, with AP/DP/HP +1. Confirm field ordering, gaps, and whether the "next" unit wraps before widening card mappings.

### 얼라이디펜스 — 3 variants / 44 rows

- 40: 방어시, 자신을 제외한 자신과 동일한 소속의 필드 유닛 수 만큼 받는 데미지 감소.
- 2: same wording with a whitespace split in "데 미지".
- 2: explicitly says other friendly field units with the same affiliation.

**Semantic boundary:** verify affiliation identity field and whether only friendly field units count; exclude the defending unit itself.

### 레이셜디펜스 — 2 variants / 35 rows

- 30: 방어시, 자신을 제외한 자신과 동일한 종족의 필드 유닛 수 만큼 받는 데미지 감소.
- 5: explicitly says other friendly field units with the same race.

**Semantic boundary:** verify race field and friendly-side scope; exclude the defending unit itself.

### 강한헌신방어 — 2 variants / 28 rows

- 21: 자신 파괴시, 아군 필드 유닛 전체의 공방체가 1증가한다.
- 7: 자신 파괴시, 아군 필드 유닛 전체의 공방체를 1씩 증가시킨다.

The catalog interpretation is AP/DP/HP +1 for all surviving friendly field units. Confirm destroyed unit exclusion and battle-only temporary duration.

### 격노 — 2 actual effect variants / 20 rows

- 19: 방어시 적군 유닛에게 자신이 공격을 받으면 자신의 HP가 깎인 수치만큼 AP 상승.
- 1: 방어시 적군 유닛의 공격을 받으면 HP가 깎인 수치만큼 AP 상승.

One extra card_text reference for 고대의반지 (9071541045) is an item-build-up/flavor annotation, not a Skill2 effect. The catalog's actual-HP-damage and defender-survives conditions must be covered by tests; do not count the card_text excerpt as corroboration.

### 홀리오오라 — 2 variants / 2 rows

- 1: 방어시 적군 유닛의 AP가 자신 방/체 합 1/2 이하일경우에는 데미지를 입지 않는다.
- 1: same wording explicitly adds "절반(내림)".

**Semantic boundary:** the explicit second wording supports floor((DP+HP)/2), but the first wording does not specify rounding. Keep the rounding rule as a testable assumption until a manual/source authority confirms it.

### 프레셔 — 1 variant / 1 row

- 방어시, 아군 필드 빈공간수 절반(내림) 만큼 받은 데미지를 감소시킨다.

Only one card-local occurrence. Verify empty-slot count timing and floor rounding; do not extrapolate to unseen card mappings.

## Mapping and runtime policy

1. All 377 rows remain inferred. Do not convert `mapping_status` to `source_card_verified` based on a shared skill label or a group-level text match.
2. Card-local `additional_text` is evidence for a candidate mechanic, not by itself proof that every card with the enum shares identical runtime semantics.
3. Exclude `card_text` lore/item-build-up annotations from executable Skill2 evidence.
4. Keep Skill1, Skill2, defense skill, and item-granted abilities as separate data axes.
5. For each card mapping require card ID + source URL + exact source excerpt + authoritative rule identity + regression test before execution.
6. Existing engine allowlist remains fail-closed: source-card-verified status, card_source authority, source-card-rule-implemented execution status, and exact Skill2 rule-name match are all required.
7. No DB29 mutation, DB30 publication, main merge, or PR merge is authorized by this audit.

## Next focused tests

- 기선제압: attacker level equal/lower/higher; general damage vs AP-origin damage wording.
- 헌신방어: destroyed slot with next unit, gap, no next unit, field-order semantics.
- 얼라이디펜스/레이셜디펜스: zero/one/multiple matching allies, self exclusion, side/race/affiliation mismatch.
- 강한헌신방어: all survivors, destroyed unit excluded, temporary stat cleanup.
- 격노: actual HP loss 0/positive, defender survives/dies, additional damage and AP roll order.
- 홀리오오라: odd/even DP+HP totals, exact threshold, damage prevention interaction.
- 프레셔: 0/1/2/3/4 empty slots and floor boundary.
