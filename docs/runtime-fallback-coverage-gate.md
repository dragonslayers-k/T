# Runtime fallback coverage gate

The card database must distinguish source-confirmed values from inferred gameplay fallbacks. Every runtime-required field must resolve to a usable value or an explicit safe fallback; provenance, confidence, and evidence must remain separately recorded. Do not modify DB29. Validate the full 15,350-card × 55-field matrix, SQLite integrity, cost token semantics, effect execution safety, and image/reference integrity before publishing a new DB version.
