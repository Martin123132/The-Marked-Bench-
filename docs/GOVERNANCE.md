# Governance

The benchmark should remain reproducible, versioned, and evidence-first.

## Case Stability

Published case IDs are stable. Do not change the meaning of an existing case ID.
If a case must be corrected, add a new suite version and document the reason.

## New Tracks

New tracks should include:

- suite ID
- suite version
- suite manifest
- report validation support
- baseline reports
- leaderboard snapshot
- tests
- documentation

## Leaderboard Entries

Leaderboard entries must come from reports that pass the built-in validator.
Claims without full JSON reports should not be ranked. Accepted entries should
also have a validated submission bundle and a completed submission review
rubric.

## Review Priorities

1. Reproducibility.
2. Clear labels and failure evidence.
3. Resistance to trivial shortcuts.
4. Useful coverage across contradiction types.
5. Transparent limitations.

Use `docs/SUBMISSION_REVIEW_RUBRIC.md` for public leaderboard acceptance
decisions.

## Disputes

If a case label is disputed, open an issue with:

- case ID
- current label
- proposed label
- reasoning
- examples or counterexamples

Do not silently edit checked-in suite manifests.
