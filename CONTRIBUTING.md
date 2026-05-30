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
- Update `benchmark_registry.json` when public tracks or artifact paths change.
- Regenerate `docs/TECHNICAL_NOTE.md` when public benchmark evidence changes.
- Regenerate the release manifest after changing public benchmark artifacts.
- Run the artifact validator before opening a pull request.
- Document any detector, model, prompt, rule, or preprocessing configuration
  used to create a report.

## Local Checks

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
```

## Submission Types

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
