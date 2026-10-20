# Project Status

The Marked Bench is currently in a polish and trust-hardening phase. The core
benchmark package is healthy enough to preserve and refine rather than broaden
aggressively.

## Current Health

- GitHub Benchmark CI is the required public health gate.
- Public artifacts are pinned by `releases/marked_bench_release_v0_4_10.json`.
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
- The separate bounded `MultiHopReference` links typed facts rather than using
  IDs or tags. Its results, invariance checks and limitations are recorded in
  `docs/MULTIHOP_REFERENCE.md`. It does not erase the legacy engine watchlist.
- Preserve suite v0.3.0 unchanged. A held-out evaluation path is still required
  if future ranking claims need resistance to answer lookup.

## Best Next Work

Follow targets AB through AF in `DEVELOPMENT_TARGETS.md`, in order:

1. Completed in v0.4.10: publish submission boundary and validation hardening.
2. Completed in v0.4.10: Windows/Linux CI across Python 3.10 through 3.14,
   including isolated wheel-install reproducibility.
3. Open for volunteers: obtain a genuinely independent evaluator run and reviewed submission
   through https://github.com/Martin123132/The-Marked-Bench-/issues/11.
4. Completed on main after v0.4.10: the bounded task-aware reference scores
   84.00, detects 8/10 contradictions, and makes no false positives on the
   eight controls. Suite v0.3.0 remains unchanged; volunteer intake stays open.
5. Qualify Forge Bridge instruction scope separately from benchmark scores.

Do not count internal tests as external adoption. Prefer these trust and
usability targets over new benchmark tracks, dashboards, or a broad refactor.
