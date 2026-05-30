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
