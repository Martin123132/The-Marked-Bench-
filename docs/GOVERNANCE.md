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
rubric. Short public score statements should use a validated result claim so
the wording stays tied to the publication packet hash and benchmark boundaries.
External repositories should use the implementation kit workflow before making
public result claims.
Release maintainers should keep the standard profile current so benchmark
requirements stay tied to inspectable evidence, not informal promises.
Release maintainers should also keep scoring compatibility vectors current so
independent implementations can verify score calculations against the public
reference release.
Release maintainers should keep the scoring specification current whenever
labels, metric formulas, rounding, calibration, or report semantics change.
Release maintainers should keep the third-party evidence ledger strict: public
adoption claims need checked result-card, submission-bundle, review, and
result-claim evidence with current hashes.

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
