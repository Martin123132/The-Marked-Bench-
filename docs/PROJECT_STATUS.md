# Project Status

The Marked Bench is currently in a polish and trust-hardening phase. The core
benchmark package is healthy enough to preserve and refine rather than broaden
aggressively.

## Current Health

- GitHub Benchmark CI is the required public health gate.
- Public artifacts are pinned by `releases/marked_bench_release_v0_4_8.json`.
- Conformance, standard profile, scoring compatibility, scoring specification,
  adoption packet, implementation kit, and evidence ledger checks are wired
  into validation.
- License and commercial-use notices are guarded by `scripts/check_license_notice.py`.
- Reviewer labels, workflow docs, and PR checks are guarded by
  `scripts/check_review_workflow.py`.
- Generated release artifacts are guarded by `scripts/regenerate_release_artifacts.py --check`.

## Current Watchlist

- The `HashPriorBaseline` currently outranks `ContradictionEngine` on the
  multi-hop track.
- This is documented in `docs/BASELINE_ROBUSTNESS.md` and should be treated as
  a baseline-robustness signal, not as evidence that the hash-prior baseline is
  a stronger contradiction system.
- Avoid expanding the multi-hop track until that signal is explained, reduced,
  or intentionally accepted with stronger public notes.

## Best Next Work

- Polish public onboarding before adding more benchmark surface.
- Keep docs focused on reproducibility, claims, licensing, and submission
  review.
- Prefer small guardrail improvements over new tracks until real third-party
  submissions arrive.
