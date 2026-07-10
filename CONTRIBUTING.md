# Contributing

This project is being shaped as a public AI benchmark suite. Contributions are
welcome when they improve reproducibility, scoring clarity, benchmark coverage,
or submission quality.

## Ground Rules

- Keep benchmark cases stable after publication.
- Do not edit the meaning of existing case IDs.
- Add new cases through a new suite version or new track.
- Include full JSON reports for baseline or leaderboard changes.
- Include validated submission metadata for leaderboard entries.
- Include a validated submission bundle and review rubric for accepted
  leaderboard entries.
- Update `benchmark_registry.json` when public tracks or artifact paths change.
- Regenerate `docs/TECHNICAL_NOTE.md` when public benchmark evidence changes.
- Regenerate the release manifest after changing public benchmark artifacts.
- Run the artifact validator before opening a pull request.
- Document any detector, model, prompt, rule, or preprocessing configuration
  used to create a report.

## Duplication Guard

Only benchmark artifacts in this repository are in scope for this project.
Do not add or mirror benchmark files in unrelated repositories, and do not direct
contributors there. Use issues, pull requests, and releases in this canonical
repository only.

## Local Checks

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
python -m marked_bench.benchmark_cli --check-standard-status
python scripts/check_scoring_sanity.py
python scripts/check_case_quality.py
python scripts/check_baseline_robustness.py
python scripts/check_evaluator_walkthrough.py
python scripts/check_submission_proof.py
python scripts/regenerate_release_artifacts.py --check
python scripts/check_review_workflow.py
python scripts/check_license_notice.py
```

### Scoring change checks

If scoring logic changed in this PR, also run:

```bash
python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md
```

Commit the generated `docs/SCORING_SANITY.md` artifact and include the command
output summary in your PR description.

### Suite quality checks

If suite cases changed in this PR, also run:

```bash
python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md
```

Commit the generated `docs/CASE_QUALITY.md` artifact with the case change.

## Submission Types

New evaluators should complete
`docs/FIVE_MINUTE_EVALUATOR_WALKTHROUGH.md` before preparing submission
metadata.

- Benchmark case improvement: add or refine cases in a new suite version.
- Baseline report: add a report under `baselines/` and update the matching
  leaderboard.
- Leaderboard entry: submit a validated report plus metadata explaining the
  system.
- Infrastructure: improve validation, schemas, docs, tests, or CI.

## Governance And Scope

Read `docs/GOVERNANCE.md` before changing public suite semantics. Read
`docs/BENCHMARK_CARD.md` before claiming what the benchmark does or does not
measure.

## Report Validation

Every public report must pass:

```bash
marked-bench --validate-report path/to/report.json
```

Reports that fail validation should not be merged into `leaderboard/` or
`baselines/`.
