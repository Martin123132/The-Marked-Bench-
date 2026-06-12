# The Marked Bench - Development Targets

We are tracking progress with target-based checkpoints only (no deadlines).

## Active Targets

- [x] **Target A: Keep the repo release-ready at every change**
  - Every PR must pass: `python -m unittest discover -s tests`, `python scripts/validate_benchmark_artifacts.py`, and `python -m marked_bench.benchmark_cli --check-standard-status`.

- [x] **Target B: Make contributor actions predictable**
  - Every accepted PR includes a short change checklist: what changed, why it changed, validation run, and updated evidence files.

- [x] **Target C: Add one quality-improvement pass per cycle**
  - Each development cycle ships at least one improvement in case robustness, baseline diversity, diagnostics quality, or evaluator resilience.

- [x] **Target D: Keep governance and claims synchronized**
  - If public-facing benchmark claims change, update governance, benchmark artifacts, registry, and release evidence in the same change set.

- [x] **Target E: Expand benchmark coverage without breaking case stability**
  - Add coverage by introducing a new suite version (never modify existing published case IDs).

- [x] **Target F: Improve collaboration visibility**
  - Improve issue templates / labels / project flow so work can be triaged and reused by contributors.

- [x] **Target G: Improve scoring trust**
  - Add at least one extra scoring sanity check and one reviewer-facing explanation artifact for scoring-related changes.

## Checkoff Rules

1. A target is checked only after code/docs are committed and validations listed in the target are complete.
2. For each checkoff, add a short entry in `docs/DEVELOPMENT_TARGET_PROGRESS.md` with the exact files changed and validator commands run.
3. Score checks should include `python scripts/check_scoring_sanity.py` and `docs/SCORING_SANITY.md` updates when scoring logic changed.

## Progress Log

- Completed: Target A, Target B, Target C, Target D, Target E, Target F, Target G
