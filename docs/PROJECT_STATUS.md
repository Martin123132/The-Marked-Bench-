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
- Multi-hop baseline interpretation is guarded by deterministic score decomposition and identifier-sensitivity checks in `scripts/check_baseline_robustness.py`.
- The five-minute evaluator path is exercised end-to-end by `scripts/check_evaluator_walkthrough.py`.
- The complete checked submission chain and non-adoption boundary are guarded by `scripts/check_submission_proof.py`.

## Current Watchlist

- The `HashPriorBaseline` currently outranks `ContradictionEngine` on the
  multi-hop track.
- Target X explains the ranking as two combined effects: the engine finds only
  one of ten multi-hop contradictions, and the checked-in hash assignment is an
  unusually favorable identifier-to-label alignment.
- The detailed evidence in `docs/BASELINE_ROBUSTNESS.md` treats this as an
  explained watchlist, not evidence that the hash-prior baseline is a stronger
  contradiction system.
- Preserve suite v0.3.0 unchanged. Before expanding the track, add a genuinely
  multi-hop task-aware reference; use a held-out evaluation path if future
  ranking claims need resistance to answer lookup.

## Best Next Work

- Prepare the next release from the completed trust-hardening and onboarding
  targets before adding more benchmark surface.
- Keep docs focused on reproducibility, claims, licensing, and submission
  review.
- Prefer onboarding and real third-party submission evidence over new tracks.
