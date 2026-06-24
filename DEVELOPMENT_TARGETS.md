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

- [x] **Target H: Add baseline diversity**
  - Add a deterministic low-information reference baseline and include it in the active foundation leaderboard.

- [x] **Target I: Improve external submission readiness**
  - Add an end-to-end external submission walkthrough from prediction template through result claim.

- [x] **Target J: Add release notes for the 0.1.1 standard suite**
  - Document the active foundation suite expansion, compatibility boundaries, and validation commands.

- [x] **Target K: Strengthen reviewer workflow**
  - Add reviewer workflow guidance and label definitions for evidence, reproducibility, validation, and review state.

- [x] **Target L: Add case-quality diagnostics**
  - Add a case-quality check and reviewer-facing artifact for suite composition and near-duplicate diagnostics.

- [x] **Target M: Improve CLI discoverability**
  - Add suite listing and suite-info commands for public suite inspection.

- [x] **Target N: Add release automation guardrails**
  - Add a release artifact regeneration helper that writes deterministic generated evidence in dependency order.

- [x] **Target O: Add artifact drift checking**
  - Add a `--check` mode for deterministic release regeneration and wire it into CI and contributor checks.

- [x] **Target P: Extend baseline diversity across all tracks**
  - Add `HashPriorBaseline` reports and leaderboard entries for adversarial, multi-hop, and controls tracks.

- [x] **Target Q: Explain known case-quality watchlist pairs**
  - Add reviewer-facing notes for intentional near-duplicate case pairs so diagnostics separate useful contrasts from review-required drift.

- [x] **Target R: Add reviewer workflow automation**
  - Add a dependency-free check that keeps labels, review workflow docs, and PR validation commands synchronized.

- [x] **Target S: Guard company non-commercial license notices**
  - Add a licensing notice check and update public docs to direct commercial licensing discussions to the COO of TWO HANDS NETWORK LTD.

## Checkoff Rules

1. A target is checked only after code/docs are committed and validations listed in the target are complete.
2. For each checkoff, add a short entry in `docs/DEVELOPMENT_TARGET_PROGRESS.md` with the exact files changed and validator commands run.
3. Score checks should include `python scripts/check_scoring_sanity.py` and `docs/SCORING_SANITY.md` updates when scoring logic changed.

## Progress Log

- Completed: Target A, Target B, Target C, Target D, Target E, Target F, Target G
- Completed: Target H, Target I, Target J, Target K, Target L, Target M, Target N
- Completed: Target O, Target P, Target Q, Target R, Target S
