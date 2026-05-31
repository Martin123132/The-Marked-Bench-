# The Marked Bench

The Marked Bench is versioned benchmark infrastructure for testing whether AI
systems can detect and classify contradictions between a premise and a query.

The project is designed to become a reproducible public standard: every score
is tied to a suite ID, suite version, deterministic suite hash, immutable case
list, JSON report schema, confusion matrix, per-class metrics, confidence
calibration metrics, validation result, diagnostic slice metrics, and
leaderboard entry.

## Current Tracks

| Track | Suite ID | Version | Purpose | Baseline |
| --- | --- | ---: | --- | ---: |
| Foundation | `marked-bench-contradiction-standard` | `0.1.0` | Compact canonical contradiction suite | `100.00` |
| Adversarial | `marked-bench-contradiction-adversarial` | `0.2.0` | Longer-context, implicit, and trap cases | `52.37` |
| Multi-hop | `marked-bench-contradiction-multihop` | `0.3.0` | Linked-evidence contradiction cases | `24.14` |

The adversarial track is intentionally not solved by the packaged symbolic
baseline. The multi-hop track is the default target for future symbolic,
neural, retrieval-augmented, and hybrid systems.

## Install

```bash
pip install -e .
```

Requires Python 3.10 or newer.

## Run A Benchmark

Foundation track:

```bash
marked-bench --suite contradiction --report artifacts/foundation-report.json
```

Adversarial track:

```bash
marked-bench --suite contradiction-adversarial --report artifacts/adversarial-report.json
```

Multi-hop track:

```bash
marked-bench --suite contradiction-multihop --report artifacts/multihop-report.json
```

Validate a report before publication:

```bash
marked-bench --validate-report artifacts/adversarial-report.json
```

Export the machine-readable registry of public tracks and artifacts:

```bash
marked-bench --export-registry benchmark_registry.json
```

Export the release manifest that pins public artifact SHA-256 digests:

```bash
marked-bench --export-release-manifest releases/marked_bench_release_v0_3_0.json
```

Export the generated technical note:

```bash
marked-bench --export-technical-note docs/TECHNICAL_NOTE.md
```

## Score External Systems

Systems written in any language can submit predictions without importing this
package. Export a template, fill the `predicted` labels, and score it into a
full benchmark report:

```bash
marked-bench --suite contradiction-adversarial --export-prediction-template artifacts/predictions.jsonl
marked-bench --suite contradiction-adversarial --score-predictions artifacts/predictions.jsonl --system-name "my-system" --report artifacts/my-system-report.json
```

Prediction files may be JSONL or JSON. Each record needs `case_id` and
`predicted`; optional `detector_score` and `detector_note` fields are preserved
in the final report. `detector_score` is interpreted as binary contradiction
confidence on `[0, 1]` for calibration metrics.

Create and validate leaderboard submission metadata:

```bash
marked-bench --create-submission artifacts/my-system-submission.json --submission-report artifacts/my-system-report.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission artifacts/my-system-submission.json
```

## Build Leaderboards

Foundation leaderboard:

```bash
marked-bench --build-leaderboard baselines/always_none_v0_1_0.json baselines/contradiction_engine_v0_1_0.json --leaderboard-output leaderboard/leaderboard_v0_1_0.json
```

Adversarial leaderboard:

```bash
marked-bench --build-leaderboard baselines/always_none_adversarial_v0_2_0.json baselines/contradiction_engine_adversarial_v0_2_0.json --leaderboard-output leaderboard/leaderboard_adversarial_v0_2_0.json
```

Multi-hop leaderboard:

```bash
marked-bench --build-leaderboard baselines/always_none_multihop_v0_3_0.json baselines/contradiction_engine_multihop_v0_3_0.json --leaderboard-output leaderboard/leaderboard_multihop_v0_3_0.json
```

## Checked-In Evidence

- Benchmark registry: `benchmark_registry.json`
- Release manifest: `releases/`
- Suite manifests and coverage profiles: `suites/`
- Baseline reports: `baselines/`
- Leaderboard snapshots: `leaderboard/`
- JSON schemas: `schemas/`
- Benchmark methodology: `docs/BENCHMARK_STANDARD.md`
- Benchmark card: `docs/BENCHMARK_CARD.md`
- Technical note: `docs/TECHNICAL_NOTE.md`
- Submission guide: `docs/SUBMISSION_GUIDE.md`
- Adoption guide: `docs/ADOPTION_GUIDE.md`
- Release notes: `docs/RELEASE_NOTES_v0_2_0.md`
- Current release notes: `docs/RELEASE_NOTES_v0_3_0.md`

## Quality Gates

Run these before publishing or submitting results:

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
```

The artifact validator checks that suite manifests match code, baseline reports
pass validation, the benchmark registry is current, and leaderboard snapshots
match their underlying reports. It also checks the release manifest against
the current public artifact hashes.

## Package Layout

```text
marked_bench/
    benchmark_cli.py              # CLI runner
    benchmark_leaderboard.py      # Validated leaderboard builder
    contradiction/
        benchmark_suite.py        # Versioned benchmark tracks
        engine.py                 # Symbolic baseline detector
```

This repository is intentionally benchmark-only. It does not include the wider
research utilities from the original toolkit.

## Contributing

Read `CONTRIBUTING.md` and `docs/SUBMISSION_GUIDE.md` before adding benchmark
cases, reports, or leaderboard entries. Existing public case IDs should not be
edited after publication; add new coverage through a new suite version or track.

## License

This repository currently uses the Motion-TimeSpace Non-Commercial License.
Commercial use requires a separate written license from the copyright holder.
