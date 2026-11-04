# Skill1 source evidence index — Batch A2 (DB29)

**Source basis:** CardDB Actions #430 `gap-reports/inferred-skill-report.jsonl`, summarized in the Batch A review queue.  
**State:** inferred; semantic review pending.  
**Scope:** 환상제어, 약탈공격, 컨슘.  
This is a review triage record, not source authority, rule promotion, runtime implementation, or DB29 modification.

## Evidence policy
- Preserve card IDs and source URLs; verify full exact excerpts against the archived #430 artifact before executable test fixtures are authored.
- Keep variants separate when trigger, timing, or target semantics differ.
- Candidate frequency prioritizes review only; it does not establish truth.
- No candidate may become playable or Manual-authoritative from this index alone.

## 환상제어 — 68 candidate rows

| Sample card ID | Card name | Card source |
|---|---|---|
| 10050424833 | 확인 대상 카드 | https://fmlunatic.com/card/10050424833 |
| 10050424839 | 확인 대상 카드 | https://fmlunatic.com/card/10050424839 |
| 10050424846 | 확인 대상 카드 | https://fmlunatic.com/card/10050424846 |

**Observed mechanic summary:** AP 1 이상 공격 시 상태보유 적의 AP/DP를 0으로 하고 HP를 1로 설정한다.

**Unresolved semantics:** “상태보유”의 실제 상태 마커 정의; AP/DP=0과 HP=1의 적용 순서; 이미 HP 0 또는 파괴 예정인 대상; 보호 효과와 상호작용; 공격 실패/무효화 시 발동 여부.

## 약탈공격 — 61 candidate rows

| Sample card ID | Card name | Card source |
|---|---|---|
| 10020324682 | 확인 대상 카드 | https://fmlunatic.com/card/10020324682 |
| 10030324707 | 확인 대상 카드 | https://fmlunatic.com/card/10030324707 |
| 10070724973 | 확인 대상 카드 | https://fmlunatic.com/card/10070724973 |

**Observed mechanic summary:** AP 1 이상 공격 시 양측 코인 수의 차이만큼 추가 피해. The source report distinguishes a common wording pattern and a shortened variant; they must not be unified before confirming the coin field and comparison direction.

**Unresolved semantics:** attacker/defender coin source; difference sign and lower-bound behavior; when bonus damage is added relative to DP; coin changes during attack; coin ties and negative differences.

## 컨슘 — 50 candidate rows

| Sample card ID | Card name | Card source |
|---|---|---|
| 10020324655 | 확인 대상 카드 | https://fmlunatic.com/card/10020324655 |
| 10021724693 | 확인 대상 카드 | https://fmlunatic.com/card/10021724693 |
| 10030324726 | 확인 대상 카드 | https://fmlunatic.com/card/10030324726 |

**Observed mechanic summary:** On destruction of an enemy unit at level 2 or below, the opposing unit's HP is absorbed. One separate source wording explicitly describes HP gain before attack; keep this as a distinct timing variant.

**Unresolved semantics:** which unit receives absorbed HP; whether amount is current or base HP; whether the trigger requires this attacker to cause destruction; simultaneous destruction; HP cap; level boundary (2/3); whether the pre-attack variant is a distinct rule.

## Required evidence gate before engine implementation
1. Recover and preserve exact source excerpts for all sample IDs from the #430 artifact (or verified source snapshots).
2. Resolve trigger and target/timing semantics with authoritative/version-specific evidence.
3. Define positive, negative, boundary, and protection/interaction tests per mechanic.
4. Link test fixtures to exact card IDs and URLs.
5. Keep all three inferred and disabled until evidence and runtime tests are approved.

**Disposition:** no executable engine assertion is authored in this batch; semantics remain pending.