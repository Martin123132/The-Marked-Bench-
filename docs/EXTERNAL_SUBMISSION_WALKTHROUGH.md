# External Submission Walkthrough

This walkthrough shows the intended end-to-end shape for a third-party system
submitting a Marked Bench result.

If you have not run the evaluator yet, complete the
[five-minute evaluator walkthrough](FIVE_MINUTE_EVALUATOR_WALKTHROUGH.md)
first. It verifies installation, suite discovery, prediction scoring, and
report validation before this packaging workflow begins.

## Choose A Suite

List public suites:

```bash
marked-bench --list-suites
```

Inspect the active foundation suite:

```bash
marked-bench --suite-info contradiction
```

## Export Predictions

```bash
marked-bench --suite contradiction-multihop --export-prediction-template predictions.jsonl
```

Fill every JSONL row with `case_id`, `predicted`, and optional
`detector_score`, `rationale`, and `evidence`.

## Score Predictions

```bash
marked-bench --suite contradiction-multihop --score-predictions predictions.jsonl --system-name "your-system" --report report.json
marked-bench --validate-report report.json
```

## Package For Review

```bash
marked-bench --create-submission submission.json --submission-report report.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission submission.json
marked-bench --create-submission-bundle submission_bundle.json --bundle-submission submission.json --bundle-predictions predictions.jsonl
marked-bench --validate-submission-bundle submission_bundle.json
```

## Add Review Evidence

```bash
marked-bench --create-submission-review submission_review.json --review-bundle submission_bundle.json --reviewer reviewer-name
marked-bench --validate-submission-review submission_review.json
marked-bench --create-result-card result_card.json --result-report report.json --result-bundle submission_bundle.json --result-review submission_review.json
marked-bench --validate-result-card result_card.json
```

## Publish A Packet

```bash
marked-bench --create-publication-packet publication_packet --publication-report report.json --publication-predictions predictions.jsonl --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-publication-packet publication_packet/publication_packet.json
marked-bench --create-result-claim publication_packet/result_claim.json --claim-publication-packet publication_packet/publication_packet.json
marked-bench --validate-result-claim publication_packet/result_claim.json
```

## Reviewer Notes

- A submission is not ready until every referenced file validates.
- Disclosures should describe model, prompting, retrieval, preprocessing,
  postprocessing, training data, and runtime where applicable.
- Results are comparable only within the same `suite_id`, `suite_version`, and
  `suite_hash`.
