# Skill1 source-to-APK gap review — A56–A60 (2026-11-06)

## Scope and comparison

This review covers manifests A56–A60, ranks 512–561 (50 Skill1 candidate labels; Skill2 excluded). APK comparison was performed against `app/src/main/assets/game/rules.js` and `tests/rules.test.cjs` on `feat/combat-event-foundation`. Exact-label search for all 50 labels returned no matches in either inspected file.

This is a bounded exact-text/source review, not a claim that all resources or runtime surfaces have been searched. This pass is evidence-only; no APK code was changed.

## Batch inventory

| Batch | Rank span | Candidate rows | Excerpts | Exact variants | Principal unresolved areas |
|---|---:|---:|---:|---:|---|
| A56 | 512–521 | 10 | 10 | 10 | Destroy/replace/equip, field and graveyard zone ownership, damage snapshot and order, AP/DP symbol semantics, DP-negative combat |
| A57 | 522–531 | 10 | 11 | 11 | Hero counter vs ability, LP/terrain arithmetic, staged damage, name count, permanent marker and identity rename, new terrain cost |
| A58 | 532–541 | 10 | 13 | 13 | Overkill propagation, hand/field/graveyard transfers, coin-rate encoding and extrema, defensive HP damage, status duration, hero effects |
| A59 | 542–551 | 10 | 10 | 10 | Graveyard consumption, enemy-owned card summon, coin modifiers, hand/resource replacement, multi-summon sequencing; one lore-only card_text |
| A60 | 552–561 | 10 | 11 | 11 | Equip source and compatibility, action lock duration, rank promotion, spawn+terrain destruction, attached-item passive effect; one zero-evidence label |

## Source blockers and non-executable distinctions

- **Zero effect excerpts:** A57 어스아레아; A60 워터바인드. Keep label-only candidates unresolved.
- **Descriptive/lore text:** A59 오백만SP excerpt is card_text, not authoritative executable effect. A60 워터스플래쉬 contains an equipment description that must remain separate from its Skill1 destruction trigger.
- **Multi-stage and resource-sensitive mechanics:** A56 암흑사제/어둠의강림; A57 어스브레스/어스스크림/얼음의칼날/엑서레센시; A58 여신의가호/연옥의동전/연합의동전/영광의기사; A59 영혼탐식/오픈스테이지/왕국의군주/용맹의폭풍; A60 워터스트림/워터스플래쉬 all require exact zone, owner, card identity, resource, order, and failure semantics before execution.
- **Rules requiring distinct primitives:** hero attack counter vs threshold ability; HP-direct vs staged DP/HP damage; overkill transfer; permanent stat marker vs numerical change; card deletion vs graveyard transfer vs hand replacement vs summon/create; coin count/rate vs coin roll; status/action lock duration; item attach trigger vs attached-item passive.
- Tooltip correction notes, descriptive paragraphs, and lore are not sufficient to promote an effect. Preserve source excerpt, interpretation, confidence, and runtime-ready status as separate evidence fields.

## Cumulative Skill1 inventory

- A1–A55: 2,458 candidate rows / 2,523 excerpts / 767 exact text variants.
- A56–A60: 50 candidate rows / 55 excerpts / 55 exact text variants.
- **A1–A60: 2,508 candidate rows / 2,578 excerpts / 822 exact text variants.**

These are source-inventory counts only. They do not mean semantic verification, executable rule coverage, APK implementation, or completion of the 15,350-card/55-field CardDB.

## Next safe gate

Continue source cross-checking in the next batches. Promote a mechanic only when card ID and authoritative effect, timing/target snapshot, ownership and zone behavior, numeric boundaries, missing-target/resource failure, and regression tests are supported. Keep DB29 immutable; do not issue DB30. Keep PR #9 and APK PR #28 open/unmerged without explicit approval.
