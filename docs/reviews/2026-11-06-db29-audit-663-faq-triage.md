# DB29 audit #663 — FAQ/help-text disposition (first batch)

- Source: main audit #663, run ID `42173417874`
- Source commit: `75584d92ac4b4812f94d99fbc34f1360ea68eaf7`
- Immutable source tag: `fm1-carddb-29`
- Queue slice: 6 exact text patterns / 26 card-clause rows from 1,249 low-confidence effect rows.
- Scope: literal text classification only. No FAQ content was fetched and no game mechanic was inferred.

## Disposition

All 26 rows are literal pointers to FAQ/support, or to a lookup in the FAQ. They do not themselves specify a self-contained action, target, condition, value, or resolution rule. Therefore:

- retain the original raw clause, card ID, clause index, and source detail URL;
- classify as `external_faq_or_support_pointer`;
- exclude the clause from executable effect modeling (`executable=false`);
- do not claim the underlying effect is solved: any mechanic linked from the FAQ remains pending until its content is retrieved and independently verified.

## Patterns

| Cluster | Rows | Literal text |
|---|---:|---|
| E663-0001 | 9 | FAQ에서 “아이템빌드업” 검색 안내 |
| E663-0054 | 7 | “자세한 사항은 FAQ를 참고” |
| E663-0064 | 7 | 상태 설명을 FAQ에서 참조하라는 안내 |
| E663-0176 | 1 | 정령 특수기술 효과를 FAQ 검색으로 확인 |
| E663-0180 | 1 | 상성 카드 전체 목록의 FAQ 안내 |
| E663-0181 | 1 | 자세한 내용·조건의 FAQ 검색 안내 |

The exact original text and all 26 card IDs/source URLs are retained in the audit artifact `fm1-carddb-29-low-confidence-effect-cluster-triage-663.json` and the generated detailed disposition JSON. This summary does not replace either source.

## Verification boundary

This is a conservative disposition of the visible literal text, not a source-grounded resolution of mechanics hidden behind the FAQ. DB29 remains unchanged; DB30 is not published.