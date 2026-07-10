# Release Notes v0.4.9

The Marked Bench v0.4.9 packages the trust-hardening, evaluator onboarding,
and checked submission-proof work completed after v0.4.8. It is a patch
release: public suites, case IDs, suite hashes, labels, scoring semantics, and
leaderboard comparison rules are unchanged.

## Added

- A deterministic multi-hop baseline diagnostic that decomposes the 21.79-point
  hash-prior lead, tests identifier sensitivity, and preserves case-level
  evidence in `docs/BASELINE_ROBUSTNESS.md`.
- A five-minute evaluator walkthrough plus a CI check that exercises suite
  discovery, suite inspection, example scoring, report validation, and
  prediction-template export.
- A checked submission proof covering the report, submission, bundle, completed
  review, result card, publication packet, result claim, and third-party
  evidence-ledger boundary.
- Focused regression coverage for the multi-hop diagnostic and deterministic
  regeneration of submission-proof dependents.

## Updated

- The example publication review now records an 8/12 `needs_revision` decision.
  Its packet remains valid for publication, but it is not accepted for the
  leaderboard and is not third-party adoption evidence.
- Project status, maintainer handoff, contributor guidance, reviewer workflow,
  release checks, and public evidence links now include the new guardrails.
- GitHub workflows use `actions/checkout@v7` and `actions/setup-python@v6`,
  matching the current Node runtime supported by the official actions.
- Citation metadata and all current release, conformance, standard, adoption,
  implementation-kit, and evidence-ledger paths now point to v0.4.9.

## Known Watchlist

- `HashPriorBaseline` still ranks above `ContradictionEngine` on the multi-hop
  track. The ranking is now explained as a chance-favorable identifier
  assignment combined with weak task-aware multi-hop coverage; it is not
  evidence that hashing performs contradiction reasoning.
- The third-party evidence ledger remains empty. This release makes no external
  adoption claim.

## Compatibility

This release does not change any benchmark suite or scoring contract from
v0.4.8. Existing results remain comparable when their suite ID, suite version,
and suite hash match. Consumers can adopt v0.4.9 for stronger diagnostics,
onboarding, evidence review, and release guardrails without regenerating model
predictions.

## Validation

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
python -m marked_bench.benchmark_cli --check-standard-status
python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md
python scripts/check_evaluator_walkthrough.py
python scripts/check_submission_proof.py --artifact docs/SUBMISSION_PROOF.md
python scripts/regenerate_release_artifacts.py --check
python scripts/check_review_workflow.py
python scripts/check_license_notice.py
```

## Licensing

The PolyForm Noncommercial License 1.0.0 and commercial-licensing requirement
are unchanged. Personal and non-commercial use remains permitted; commercial
use requires a separate written licence from TWO HANDS NETWORK LTD.
