# DB29 audit #663 — E663-0012 cohort expansion and source-access disposition

- Date: 2026-11-06
- Immutable source: `fm1-carddb-29`; audit run `42173417874`; source commit `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`
- Review branch: `feat/carddb-effect-semantic-pass`
- Library artifact: `fm1-db29-low-confidence-effect-cluster-triage-663.json` (916,554 bytes; 7 occurrences for E663-0012)

## Correction to the previous five-card scope

The audit cluster E663-0012 contains **seven**, not five, card rows. The previous contextual review covered TINIA and the prior crosswalk covered five selected examples, but the two preceding rows must also remain in the cohort. This document restores the complete cluster inventory; it does not imply that the seven cards share the same effect body.

| Detail ID | Card name | Clause index | Detail URL |
|---|---|---:|---|
| 11011925564 | 스컬아머킹 | 3 | https://fmlunatic.com/card/11011925564 |
| 11011925565 | 인페르노스톤 | 3 | https://fmlunatic.com/card/11011925565 |
| 11011925566 | 티니아 | 3 | https://fmlunatic.com/card/11011925566 |
| 11011925567 | 네추럴마스터 | 5 | https://fmlunatic.com/card/11011925567 |
| 11011925568 | 아크위자드 | 5 | https://fmlunatic.com/card/11011925568 |
| 11011925569 | 레스베르크 | 3 | https://fmlunatic.com/card/11011925569 |
| 11011925570 | 골드드래곤 | 3 | https://fmlunatic.com/card/11011925570 |

Exact repeated clause in the audit queue:

`(핸드에 자신과 같은 이름을 가진 유닛이 없을 경우나 해당 유닛의 AP나 HP가 발동 후 0이하가 되는 경우 아무 효과 없음).`

The source queue marks all seven as `unparsed_effect_text` / `inferred`; cluster status remains `pending_source_review` / `non_executable`.

## What this pass actually verified

1. The full audit JSON was inspected programmatically; E663-0012 has seven occurrences and the table above is the complete card-row inventory in that artifact.
2. The live FMLunatic detail URLs for all four non-TINIA members queried in this pass (IDs 11011925567–11011925570) could not be opened by the available web reader. The same limitation was already observed for the first members. This is a source-access limitation, not evidence that the pages or cards do not exist.
3. Search results did not produce independently attributable full effect text for 스컬아머킹, 인페르노스톤, 네추럴마스터, 아크위자드, 레스베르크, or 골드드래곤. A general card-list page is not a substitute for their card detail records.
4. TINIA's secondary fan-maintained article provides one card-specific contextual example (Chapter 4 TINIA / Shadow Aura / same-name allied hand unit / -3 AP and HP followed by +3 AP and HP). It is not official evidence and must not be generalized to the other six cards.

## Required next evidence, card by card

For each of the seven IDs, acquire at least one complete card-detail capture (HTML or screenshot/image with URL and capture time) that includes the entire effect text, not only the repeated parenthetical. Where available, cross-check against an original client/card image or official manual. Record source checksum and preserve exact punctuation and clause order.

Only after those captures exist should the review compare:
- which unit is the source/actor and which same-name unit is selected from hand;
- the operation applied to that hand unit and the actor;
- whether AP and HP are both changed, and by what amount;
- the exact point at which the 0-or-less condition is checked;
- whether "아무 효과 없음" suppresses the entire effect or a sub-clause;
- cost payment, target selection, and resolution order.

The TINIA article can serve as a hypothesis to test, not as a template to fill the six missing card texts.

## Disposition / protection

- Cohort inventory: corrected to 7.
- Card-specific semantic adjudication: TINIA partial secondary-source context only; remaining six unresolved.
- Executable assertions: none authorized.
- All seven remain `pending_source_review` / `non_executable`.
- No completion count increment.
- DB29 and Release/tag `fm1-carddb-29`: unchanged.
- DB30: not published.
- PR #9: open; no merge.
