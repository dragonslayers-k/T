# DB29 RequireSoul review-image export — Actions #809

Date: 2026-11-07 (UTC)

## Execution record

- Repository: `dragonslayers-k/T`
- PR: #9, still open and unmerged
- Commit: `ecc91560594d51ba94f1f502a79f7f0106da6c1d`
- Workflow run: [#809](https://github.com/dragonslayers-k/T/actions/runs/42357466809)
- Result: `success`
- Trigger: pull_request with the temporary `[soul-image-evidence]` title selector; the selector was removed after the run completed.
- Lightweight regression suite: passed.
- DB29 source-card and image archive download: passed.
- Focused exporter: passed.
- Artifact upload: passed.

## Exporter contract and resulting evidence

The exporter targets cards with RequireSoul tokens in the 14 hybrid codes or special codes NCS(82)/BONUS(83), excluding ordinary MU-only costs. Its success contract requires exactly 831 distinct target cards and a complete, valid small+large image pair for each target: 1,662 WebP images, with no missing or invalid images. Since the export step completed successfully, the run met that contract. It does not assign payment semantics or modify DB29.

Artifact: `fm1-soul-cost-image-evidence-809.zip`  
Artifact ID: `13567929182`  
Size: `26,171,298` bytes  
SHA-256: `7b5c9277110a10f07e2e4fa5d49c7b6873a727f7e6178aa2b987731eec8d3180`  
Expiration: `2026-11-21T08:55:16Z`

The artifact contains the image evidence bundle, `image-manifest.jsonl`, `target-cards.jsonl`, and `image-audit-summary.json` as specified by the exporter. Preserve this artifact before its expiry if it is needed beyond the retention period.

## Regression safeguard added

A test was added to ensure `EarnSoul` MU02 (code 82) does not cause a card to enter the RequireSoul NCS review queue. The test explicitly checks that selection is based on the RequireSoul namespace only.

## Remaining review boundary

The export proves asset retrieval, file integrity, and card-to-image selection under the exporter contract. It is not a human visual review of the cost glyphs. NCS, BONUS, and hybrid payment semantics remain blocked pending actual icon comparison and authoritative rule/client evidence. DB29 remains immutable; no DB30, release, or PR merge was made.
