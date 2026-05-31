# Leaderboard Submissions

This directory is reserved for reviewed third-party leaderboard submission
metadata. A submission JSON should reference a validated benchmark report,
pin the report SHA-256 digest, and disclose enough system details for reviewers
to understand what was evaluated.

Create and validate a submission file with:

```bash
marked-bench --create-submission submissions/my-system.json --submission-report baselines/my-system-report.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission submissions/my-system.json
```

Do not merge submission metadata unless both the submission and referenced
report validate.

`example_external_jsonl/` is a checked external-style submission packet. It
contains JSONL predictions, the scored report, leaderboard submission metadata,
the submission bundle, a review file, and a result card. Validate it with:

```bash
marked-bench --validate-submission-bundle submissions/example_external_jsonl/example_external_submission_bundle.json
marked-bench --validate-submission-review submissions/example_external_jsonl/example_external_submission_review.json
marked-bench --validate-result-card submissions/example_external_jsonl/example_external_result_card.json
```
