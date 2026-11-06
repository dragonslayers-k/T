# FM1 Manual Skill1 piercing attack — overflow / DP-marker boundary audit
Date: 2026-11-06

## Evidence and source provenance

- Primary rules source: Dropbox `/판마/Manual.zip`, `specialability.htm`, section 4 (관통공격기술): the attack destroys defender DP by the attacker's AP; when defender DP reaches zero, remaining AP deals HP damage.
- Shared stat-marker source in the same Manual file: `*` blocks all changes; `△` prevents decreases but still permits increases; `▽` prevents increases but still permits decreases.
- T Manual Skill1 specification: `fm1-manual-skill-engine-test-spec-2026-11-05.json`, blob `833a8bc14525e54c6ed595f47c4c37e316395363`. For `piercing_attack`, it records canonical label `관통공격`, 172 exact DB29 Skill1 label rows, and representative card 블랙유니콘 / `10091525214` / Skill1 source value 51 / exact label match. It also explicitly keeps `effect_excerpt_status=pending_card_local_semantic_packet`, `runtime_status=pending_engine_test`, and `exact_db29_source_text=null`.
- The specification records the card detail URL `https://fmlunatic.com/card/10091525214`; the page could not be independently retrieved in this pass. Do not claim a card-local effect text packet was recovered.
- The APK rule fixtures inject Manual mapping metadata directly. They test the engine rule branch and do not establish SQLite→converter→release pack→Android import lineage for this card.

## Test matrix — APK PR #28

Representative fixture: 블랙유니콘 / `10091525214` / Skill1 `관통공격` / `piercing_attack`.

| Attacker AP | Defender DP | Marker | Expected / asserted result | Meaning |
|---:|---:|---|---|---|
| 4 | 2 | none | DP 0, HP damage 2 | DP breaks; remaining AP overflows to HP |
| 2 | 4 | none | DP 2 remains, HP damage 0 | AP cannot destroy more DP than it has |
| 3 | 0 | none | HP damage 3 | DP is already zero; all AP reaches HP |
| 3 | 3 | none | DP 0, HP damage 0 | exact boundary: all AP is consumed breaking DP |
| 4 | -2 | none | DP remains -2, HP damage 4 | conservative interpretation: already-below-zero DP is exhausted; negative magnitude is not added as bonus damage |
| 4 | 2 | △ | DP remains 2, HP damage 0 | protected DP cannot be decreased; no DP-break overflow occurs |
| 4 | 2 | ▽ | DP 0, HP damage 2 | marker blocks increases only; the decrease required for piercing remains legal |

The negative-DP result is an explicit conservative runtime interpretation, not a verbatim piercing-specific statement from Manual §4. Manual §4 does not define whether negative DP should modify overflow beyond the attacker's printed AP. The test intentionally prevents a generic `AP - negative DP` bonus from being invented.

## Failure found and correction

- Commit `c665a105de796bb4eb10a60bdf1650990e52f2bd`, Actions #356 / run `42221573459`: failed one assertion (236 tests, 1 failure). The new `△` case expected 0 HP damage but actual HP damage was 4. The existing handler treated a blocked DP decrease as if no DP had been consumed and incorrectly passed all AP through to HP.
- Corrective commit `6d736aa9e56c677aa7f2dcbfe94571b9a54d818b`, Actions #357 / run `42221699683`: success; 236 JS tests / 0 failures; Python converter 13 tests / OK.
- Runtime now carries AP overflow to HP only if defender DP was already at/below zero or positive DP was actually reduced to zero. When a marker blocks the positive-DP decrease, the DP remains and HP overflow is zero. A `▽` marker still permits decrease.

## Scope and limits

- #357 includes the focused JS rules and Python converter checks. DB29 pack generation, Gradle/APK, signature/ZIP, and emulator steps were skipped by the lightweight PR CI policy.
- No source-row mapping, Skill1 authority, converter output, SQLite source row, DB29 tag or Release was changed.
- This audit does not promote the rule to end-to-end DB29 source execution. The T specification's card-local semantic packet remains pending; exact source label matching (172 rows) is not semantic approval.
- DB29 remains preserved; DB30 remains unpublished; T PR #9/#12/#13 and APK PR #28/#26/#25/#9 remain open and unmerged.
