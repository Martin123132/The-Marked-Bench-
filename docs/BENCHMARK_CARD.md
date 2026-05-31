# Benchmark Card

## Name

The Marked Bench: contradiction detection tracks.

## Purpose

The benchmark measures whether a system can identify and classify contradictions
between a premise and a query. It is aimed at reasoning-system evaluation,
AI-safety tooling, symbolic-neural hybrid research, and contradiction-training
pipelines.

## Current Tracks

| Track | Suite ID | Version | Cases | Description |
| --- | --- | ---: | ---: | --- |
| Foundation | `marked-bench-contradiction-standard` | `0.1.0` | 17 | Compact canonical cases across five contradiction classes and controls. |
| Adversarial | `marked-bench-contradiction-adversarial` | `0.2.0` | 17 | Longer-context and adversarial cases with implicit contradictions and distractors. |
| Multi-hop | `marked-bench-contradiction-multihop` | `0.3.0` | 18 | Linked-evidence cases requiring entity, policy, temporal, or definition chaining. |

Suite manifests include machine-readable coverage profiles for labels,
domains, difficulties, capabilities, and tags.

## Labels

- `direct_negation`
- `property_mismatch`
- `definitional_violation`
- `universal_counterexample`
- `temporal_conflict`
- `none`

## Primary Metrics

- Overall score, 0-100.
- Exact type accuracy.
- Contradiction-only macro F1.
- Binary contradiction-vs-none F1.
- Confidence calibration Brier score and expected calibration error.
- Class coverage index.
- Diagnostic slice metrics by domain, difficulty, capability, and tag.
- Confusion matrix and failure list.

The overall score weights are documented in `docs/BENCHMARK_STANDARD.md`.

## Intended Use

- Compare contradiction detectors on the same stable public suite.
- Track whether systems correctly identify the kind of contradiction, not only
  whether something seems inconsistent.
- Provide baseline reports and public evidence for future leaderboard entries.
- Let non-Python systems submit JSON or JSONL predictions for scoring.
- Support research into symbolic, neural, and hybrid reasoning systems.

## Not Intended For

- Claims about general intelligence.
- Safety certification of deployed systems.
- Legal, medical, or financial decision-making.
- Evaluating all forms of truthfulness or hallucination.

## Known Limitations

- The current suites are compact and English-only.
- Cases are public, so leaderboard results should be interpreted as public-test
  performance rather than hidden-test performance.
- The baseline detector is symbolic and narrow; it is included as a reference
  implementation, not as a target architecture.
- The adversarial suite is still small and should grow through versioned tracks.
- The multi-hop suite is public and compact; hidden/private splits remain future
  work.

## Data And Privacy

The checked-in suites are synthetic examples. They do not require network
access, API keys, private datasets, or user data.

## Reproducibility

All public reports must include:

- suite ID and version
- deterministic suite hash
- full canonical case list
- one case result per canonical case
- aggregate metrics
- confusion matrix
- failures

Reports are validated with:

```bash
marked-bench --validate-report PATH
```

Repository artifacts are validated with:

```bash
python scripts/validate_benchmark_artifacts.py
```

The checked release manifest under `releases/` records SHA-256 digests for
public benchmark artifacts.
