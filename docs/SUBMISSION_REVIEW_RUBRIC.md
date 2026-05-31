# Submission Review Rubric

This rubric standardizes how leaderboard submissions are reviewed after report,
submission metadata, and bundle validation pass.

## Review Flow

1. Validate the report:

```bash
marked-bench --validate-report REPORT
```

2. Validate the submission metadata:

```bash
marked-bench --validate-submission SUBMISSION
```

3. Validate the submission bundle:

```bash
marked-bench --validate-submission-bundle BUNDLE
```

4. Create a structured review file:

```bash
marked-bench --create-submission-review REVIEW --review-bundle BUNDLE --reviewer REVIEWER
```

5. Fill the rubric scores and validate the review:

```bash
marked-bench --validate-submission-review REVIEW
```

## Rubric

Each dimension is scored from 0 to 2.

| Dimension | 0 | 1 | 2 |
| --- | --- | --- | --- |
| Reproducibility | Missing or broken evidence. | Evidence mostly works but has minor ambiguity. | Bundle, hashes, report, suite identity, and commands reproduce cleanly. |
| Disclosure quality | Major method details missing. | Method is partly disclosed. | Model, prompting, preprocessing, retrieval, postprocessing, training data, and runtime are clear. |
| Score integrity | Score cannot be trusted. | Score validates but has review concerns. | Score is backed by a valid report with no unexplained mismatch. |
| Explanation coverage | No usable rationale/evidence. | Some cases have rationale or evidence. | Rationale and evidence are broad enough for meaningful review. |
| Evidence quality | Evidence does not support labels. | Evidence is mixed or too vague. | Evidence quotes or references support predicted labels without leaking expected labels. |
| Limitations | No limitations stated. | Limitations are vague. | Known limitations, failure modes, and benchmark-use caveats are clear. |

An accepted submission should normally score at least 9 out of 12 and have no
zero-score dimension. Lower scores should be marked `needs_revision` or
`reject`.

## Review Decisions

- `needs_review`: rubric is not complete yet.
- `accept`: rubric is complete and meets the acceptance recommendation.
- `needs_revision`: submission is promising but needs clearer evidence,
  disclosures, or fixes.
- `reject`: submission fails a core review dimension.

The review file is a governance artifact. It does not change the primary
benchmark score; it records why a leaderboard entry should or should not be
accepted.
