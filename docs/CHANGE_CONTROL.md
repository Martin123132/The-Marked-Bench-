# Change Control

The Marked Bench should evolve through public, versioned, evidence-backed
changes. This document describes the human process; the machine-readable
profile is `standard/marked_bench_change_control_v0_4_8.json`.

## What Requires A Proposal

Open a standard-change issue or pull request before changing:

- released case text, labels, IDs, or suite membership
- public suite manifests, suite hashes, or track identity
- report, prediction, submission, result-card, claim, adoption, evidence, or
  release schemas
- scoring labels, metrics, weights, rounding, calibration, or score semantics
- release conformance, standard-profile, adoption, implementation-kit, or
  evidence-ledger rules
- governance, review, release, or claim-boundary policy

Small typo fixes in prose can be handled in pull requests, but any change that
affects comparison, validation, scoring, or public claims should use the
standard-change path.

## Compatibility Rules

- Released case IDs keep their meaning.
- If a released case meaning changes, publish a new suite version or new track.
- Suite hash mismatches block direct score comparison.
- Schema changes update the schema file and release notes.
- Scoring changes update the scoring specification and compatibility vectors.
- Evidence-policy changes update the adoption packet, implementation kit,
  standard profile, evidence ledger, and conformance report.

## Required Evidence

Every standard-changing pull request should include:

- the public proposal link
- affected artifacts and schemas
- compatibility impact
- regenerated release artifacts
- validation output from the artifact gate and relevant CLI validators
- release notes for the new public release

## Validation

```bash
marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_8.json
python scripts/validate_benchmark_artifacts.py
python -m unittest discover -s tests
```
