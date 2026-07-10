# Five-Minute Evaluator Walkthrough

Use this path to prove the evaluator works before connecting your own system.
It installs the local package, inspects the public multi-hop suite, scores the
checked example predictions, validates the resulting report, and exports a
fresh prediction template.

Run every command from the repository root.

## 1. Install The Evaluator

```bash
pip install -e .
```

The package requires Python 3.10 or newer.

## 2. Inspect The Target Suite

```bash
marked-bench --list-suites
marked-bench --suite-info contradiction-multihop
```

The suite information should identify
`marked-bench-contradiction-multihop` v0.3.0 with 18 cases and a pinned suite
hash. Record the suite ID, version, and hash with every result you publish.

## 3. Score A Checked Example

Create a disposable output directory, score the committed example predictions,
and validate the generated report:

```bash
python -c "from pathlib import Path; Path('artifacts/quickstart').mkdir(parents=True, exist_ok=True)"
marked-bench --suite contradiction-multihop --score-predictions submissions/example_external_jsonl/predictions.jsonl --system-name "QuickstartExample" --report artifacts/quickstart/report.json
marked-bench --validate-report artifacts/quickstart/report.json
```

Success means the report validates and records the same suite identity as the
checked example. The example deliberately predicts `none` for every case, so
its 11.11 score is a plumbing check, not a quality target.

## 4. Export Your Prediction Template

```bash
marked-bench --suite contradiction-multihop --export-prediction-template artifacts/quickstart/predictions.jsonl
```

Fill every row's `predicted` field. You can also provide `detector_score`,
`rationale`, and `evidence`; these fields feed calibration and explanation
audits in the final report.

Score your completed file with:

```bash
marked-bench --suite contradiction-multihop --score-predictions artifacts/quickstart/predictions.jsonl --system-name "your-system" --report artifacts/quickstart/your-system-report.json
marked-bench --validate-report artifacts/quickstart/your-system-report.json
```

## 5. Know What You Have Proved

After this walkthrough you have:

- confirmed the CLI can discover the public suites;
- pinned the multi-hop suite identity;
- scored predictions without importing Python package internals;
- produced and validated a complete benchmark report; and
- exported the exact input shape required for your own system.

This does not create a leaderboard-ready submission. Continue with the
[external submission walkthrough](EXTERNAL_SUBMISSION_WALKTHROUGH.md) to add
submission metadata, a bundle, review evidence, a result card, and a public
publication packet.

## Troubleshooting

If the `marked-bench` command is not available after installation, use the
module form while you check the active Python environment:

```bash
python -m marked_bench.benchmark_cli --list-suites
```

If report validation fails, do not publish the score. Check that every
prediction case ID belongs to the selected suite and that the file covers all
cases exactly once.

## Licensing

The repository uses the PolyForm Noncommercial License 1.0.0. Personal and
non-commercial use is permitted under that license. Commercial use requires a
separate written commercial license from TWO HANDS NETWORK LTD; see
[LICENSE](../LICENSE) for the current terms and contact details.
