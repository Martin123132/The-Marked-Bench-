# Development Target Progress Log

Use this file to check off completed targets.

## Active targets

- [x] Keep the contradiction suite API stable while introducing suite version 0.1.1 and expanding standard-case coverage.
- [x] Add the 0.1.1 suite manifest artifacts and wire them into the default benchmark registry.
- [x] Extend scoring/validation configs to include 0.1.1 suite checks and baseline/leaderboard targets.
- [x] Update schema `suite_version` enums and docs for all affected payload/validation formats.
- [x] Refresh `SCORING_SANITY` expectations after the new standard suite is added.

## Cycle notes (no timelines)

- [x] Current in-progress target: `none`
- [x] Next target after current: `identify Target X onward`
- [x] Completed targets:
  - Target A: release-ready checks completed.
  - Target B: contributor PR/checklist guidance updated.
  - Target C: standard-case coverage expanded in suite version 0.1.1.
  - Target D: registry, docs, generated release evidence, and conformance artifacts synchronized.
  - Target E: new 0.1.1 suite version added without modifying published 0.1.0 case IDs.
  - Target F: issue templates, labels, and PR flow improved.
  - Target G: scoring sanity script, test, CI step, and reviewer-facing artifact added.

## Completed cycle

- [x] Completed target: Target A through Target G
- [x] Scope:
  - `marked_bench/contradiction/benchmark_suite.py`
  - `marked_bench/benchmark_registry.py`
  - `marked_bench/benchmark_conformance.py`
  - `marked_bench/benchmark_release.py`
  - `marked_bench/benchmark_cli.py`
  - `scripts/validate_benchmark_artifacts.py`
  - `scripts/check_scoring_sanity.py`
  - `tests/test_benchmark_suite.py`
  - `tests/test_scoring_sanity.py`
  - `schemas/*`
  - `suites/`, `baselines/`, `leaderboard/`, `standard/`, `adoption/`, `conformance/`, `releases/`
  - `.github/`, `README.md`, `CONTRIBUTING.md`, `docs/*`
- [x] Validation run:
  - `python -m unittest discover -s tests`
  - `python scripts/validate_benchmark_artifacts.py`
  - `python -m marked_bench.benchmark_cli --check-standard-status`
  - `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
  - `python -m marked_bench.benchmark_cli --validate-report baselines/contradiction_engine_v0_1_1.json`
  - `python -m marked_bench.benchmark_cli --validate-report baselines/always_none_v0_1_1.json`
  - `git diff --check`
- [x] Evidence/notes:
  - Foundation suite `0.1.1` adds six new cases while legacy `0.1.0` remains validated.
  - Active foundation artifacts now point to `suites/marked_bench_contradiction_standard_v0_1_1.json`, `baselines/*_v0_1_1.json`, and `leaderboard/leaderboard_v0_1_1.json`.
  - `docs/SCORING_SANITY.md` records both legacy `0.1.0` and active `0.1.1` scoring checks.
- [x] Checked by:
  - Codex

## Completed cycle 4

- [x] Completed target: Target T through Target W
- [x] Scope:
  - `scripts/check_baseline_robustness.py`
  - `scripts/regenerate_release_artifacts.py`
  - `scripts/check_review_workflow.py`
  - `marked_bench/benchmark_release.py`
  - `scripts/validate_benchmark_artifacts.py`
  - `.github/workflows/benchmark-ci.yml`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `CONTRIBUTING.md`
  - `README.md`
  - `docs/BASELINE_ROBUSTNESS.md`
  - `docs/PROJECT_STATUS.md`
  - `docs/MAINTAINER_HANDOFF.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/REVIEW_WORKFLOW.md`
  - `leaderboard/README.md`
  - `DEVELOPMENT_TARGETS.md`
- [x] Validation run:
  - `python -m unittest discover -s tests`
  - `python scripts/validate_benchmark_artifacts.py`
  - `python -m marked_bench.benchmark_cli --check-standard-status`
  - `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
  - `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
  - `python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md`
  - `python scripts/regenerate_release_artifacts.py --check`
  - `python scripts/check_review_workflow.py`
  - `python scripts/check_license_notice.py`
- [x] Evidence/notes:
  - Added public project status and maintainer handoff docs.
  - Added baseline robustness artifact generation and CI guard.
  - Documented the multi-hop hash-prior result as a watchlist item before future expansion.
  - Kept the cycle focused on polish and trust-hardening rather than new benchmark surface.
- [x] Checked by:
  - Codex

## Current cycle 7

- [x] Completed target: Target Z
- [x] Scope:
  - `submissions/example_publication_packet/submission_review.json`
  - `submissions/example_publication_packet/result_card.json`
  - `submissions/example_publication_packet/publication_packet.json`
  - `submissions/example_publication_packet/result_claim.json`
  - `docs/SUBMISSION_PROOF.md`
  - `scripts/check_submission_proof.py`
  - `scripts/regenerate_release_artifacts.py`
  - `marked_bench/benchmark_release.py`
  - `tests/test_benchmark_suite.py`
  - `submissions/README.md`
  - `docs/THIRD_PARTY_EVIDENCE.md`
  - `docs/EXTERNAL_SUBMISSION_WALKTHROUGH.md`
  - `README.md`
  - `.github/workflows/benchmark-ci.yml`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `CONTRIBUTING.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/REVIEW_WORKFLOW.md`
  - `scripts/check_review_workflow.py`
  - `docs/MAINTAINER_HANDOFF.md`
  - `DEVELOPMENT_TARGETS.md`
  - `docs/PROJECT_STATUS.md`
  - `docs/DEVELOPMENT_TARGET_PROGRESS.md`
  - `releases/marked_bench_release_v0_4_8.json`
  - `conformance/marked_bench_conformance_v0_4_8.json`
- [x] Validation run:
  - `python -m unittest discover -s tests`
  - `python scripts/validate_benchmark_artifacts.py`
  - `python -m marked_bench.benchmark_cli --check-standard-status`
  - `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
  - `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
  - `python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md`
  - `python scripts/check_evaluator_walkthrough.py`
  - `python scripts/check_submission_proof.py --artifact docs/SUBMISSION_PROOF.md`
  - `python scripts/regenerate_release_artifacts.py --check`
  - `python scripts/check_review_workflow.py`
  - `python scripts/check_license_notice.py`
- [x] Evidence/notes:
  - Completed the checked example rubric with an 8/12 `needs_revision` decision rather than presenting a valid packet as an accepted result.
  - Regenerated the result card, publication packet, and result claim from that human-authored decision.
  - Verified every schema, canonical file hash, suite identity field, review state, publication boundary, and citation claim.
  - Kept the third-party evidence ledger empty and explicitly separated internal workflow proof from external adoption evidence.
- [x] Checked by:
  - Codex

## Current cycle 6

- [x] Completed target: Target Y
- [x] Scope:
  - `docs/FIVE_MINUTE_EVALUATOR_WALKTHROUGH.md`
  - `scripts/check_evaluator_walkthrough.py`
  - `README.md`
  - `docs/EXTERNAL_SUBMISSION_WALKTHROUGH.md`
  - `.github/workflows/benchmark-ci.yml`
  - `.github/PULL_REQUEST_TEMPLATE.md`
  - `CONTRIBUTING.md`
  - `docs/RELEASE_CHECKLIST.md`
  - `docs/REVIEW_WORKFLOW.md`
  - `scripts/check_review_workflow.py`
  - `docs/MAINTAINER_HANDOFF.md`
  - `marked_bench/benchmark_release.py`
  - `DEVELOPMENT_TARGETS.md`
  - `docs/PROJECT_STATUS.md`
  - `docs/DEVELOPMENT_TARGET_PROGRESS.md`
  - `releases/marked_bench_release_v0_4_8.json`
  - `conformance/marked_bench_conformance_v0_4_8.json`
- [x] Validation run:
  - `python -m unittest discover -s tests`
  - `python scripts/validate_benchmark_artifacts.py`
  - `python -m marked_bench.benchmark_cli --check-standard-status`
  - `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
  - `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
  - `python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md`
  - `python scripts/check_evaluator_walkthrough.py`
  - `python scripts/regenerate_release_artifacts.py --check`
  - `python scripts/check_review_workflow.py`
  - `python scripts/check_license_notice.py`
- [x] Evidence/notes:
  - Added a five-minute path from installation and suite discovery through checked-example scoring, report validation, and prediction-template export.
  - Exercised every evaluator step in a temporary directory so CI does not write disposable artifacts into the repository.
  - Kept the longer submission walkthrough as the next path for metadata, review, result-card, and publication packaging.
  - Added the walkthrough and its checker to public release evidence and maintainer/reviewer health gates.
- [x] Checked by:
  - Codex

## Current cycle 5

- [x] Completed target: Target X
- [x] Scope:
  - `scripts/check_baseline_robustness.py`
  - `tests/test_baseline_robustness.py`
  - `docs/BASELINE_ROBUSTNESS.md`
  - `docs/PROJECT_STATUS.md`
  - `DEVELOPMENT_TARGETS.md`
  - `docs/DEVELOPMENT_TARGET_PROGRESS.md`
  - `releases/marked_bench_release_v0_4_8.json`
- [x] Validation run:
  - `python -m unittest discover -s tests`
  - `python scripts/validate_benchmark_artifacts.py`
  - `python -m marked_bench.benchmark_cli --check-standard-status`
  - `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
  - `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
  - `python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md`
  - `python scripts/regenerate_release_artifacts.py --check`
  - `python scripts/check_review_workflow.py`
  - `python scripts/check_license_notice.py`
- [x] Evidence/notes:
  - Reproduced the 45.93 multi-hop hash-prior score from checked-in case predictions.
  - Reconciled its 21.79-point lead across all four weighted score components.
  - Added deterministic salted-ID and fixed-label-mix sensitivity checks plus case-level evidence.
  - Classified the ranking as an explained watchlist caused by both weak task-aware multi-hop coverage and a chance-favorable hash assignment.
  - Preserved all published suite v0.3.0 cases and IDs unchanged.
- [x] Checked by:
  - Codex

## Current cycle 3

- [x] Completed target: Target O through Target S
- [x] Implementation scope prepared:
  - `scripts/regenerate_release_artifacts.py`
  - `scripts/check_case_quality.py`
  - `scripts/check_review_workflow.py`
  - `scripts/check_license_notice.py`
  - `marked_bench/benchmark_registry.py`
  - `marked_bench/benchmark_conformance.py`
  - `marked_bench/benchmark_release.py`
  - `scripts/validate_benchmark_artifacts.py`
  - `tests/test_benchmark_suite.py`
  - `tests/test_scoring_sanity.py`
  - `baselines/hash_prior_adversarial_v0_2_0.json`
  - `baselines/hash_prior_multihop_v0_3_0.json`
  - `baselines/hash_prior_controls_v0_4_0.json`
  - `leaderboard/leaderboard_adversarial_v0_2_0.json`
  - `leaderboard/leaderboard_multihop_v0_3_0.json`
  - `leaderboard/leaderboard_controls_v0_4_0.json`
  - `.github/`, `README.md`, `CONTRIBUTING.md`, `docs/*`
  - `COMMERCIAL-LICENSE.md`, `NOTICE.md`, `CITATION.cff`
- [x] Validation run:
  - `python -m unittest discover -s tests`
  - `python scripts/validate_benchmark_artifacts.py`
  - `python -m marked_bench.benchmark_cli --check-standard-status`
  - `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
  - `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
  - `python scripts/regenerate_release_artifacts.py --check`
  - `python scripts/check_review_workflow.py`
  - `python scripts/check_license_notice.py`
  - `python -m marked_bench.benchmark_cli --validate-report baselines/hash_prior_adversarial_v0_2_0.json`
  - `python -m marked_bench.benchmark_cli --validate-report baselines/hash_prior_multihop_v0_3_0.json`
  - `python -m marked_bench.benchmark_cli --validate-report baselines/hash_prior_controls_v0_4_0.json`
- [x] Evidence/notes:
  - Prepared artifact drift checking as a CI/contributor guard.
  - Extended the deterministic hash-prior baseline plan across every public track.
  - Added reviewer notes for intentional near-duplicate case-quality pairs.
  - Added review workflow and license notice guard scripts.
- [x] Checked by:
  - Codex

## Completed cycle 2

- [x] Completed target: Target H through Target N
- [x] Scope:
  - `marked_bench/benchmark_cli.py`
  - `marked_bench/benchmark_registry.py`
  - `marked_bench/benchmark_release.py`
  - `marked_bench/benchmark_conformance.py`
  - `scripts/check_case_quality.py`
  - `scripts/regenerate_release_artifacts.py`
  - `scripts/validate_benchmark_artifacts.py`
  - `tests/test_benchmark_suite.py`
  - `tests/test_scoring_sanity.py`
  - `baselines/hash_prior_v0_1_1.json`
  - `leaderboard/leaderboard_v0_1_1.json`
  - `docs/CASE_QUALITY.md`
  - `docs/EXTERNAL_SUBMISSION_WALKTHROUGH.md`
  - `docs/RELEASE_NOTES_v0_1_1.md`
  - `docs/REVIEW_WORKFLOW.md`
  - `.github/labels.yml`
- [x] Validation run:
  - `python -m unittest discover -s tests`
  - `python scripts/validate_benchmark_artifacts.py`
  - `python -m marked_bench.benchmark_cli --check-standard-status`
  - `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
  - `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
  - `python scripts/regenerate_release_artifacts.py`
  - `python -m marked_bench.benchmark_cli --validate-report baselines/hash_prior_v0_1_1.json`
  - `git diff --check`
- [x] Evidence/notes:
  - Added `HashPriorBaseline` as a deterministic reference baseline and included it in the active foundation leaderboard.
  - Added `--list-suites` and `--suite-info` for CLI suite discovery.
  - Added case-quality diagnostics and release-regeneration helper scripts.
  - Added external submission walkthrough, reviewer workflow, labels, and `0.1.1` release notes.
- [x] Checked by:
  - Codex

## Completion template

- [ ] Completed target: `<target text>`
- [ ] Scope:
  - `path/edited`
- [ ] Validation run:
  - `command`
- [ ] Evidence/notes:
  - `what changed and why`
- [ ] Checked by:
