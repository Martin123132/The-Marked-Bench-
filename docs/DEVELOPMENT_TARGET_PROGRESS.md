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
- [x] Next target after current: `none`
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

## Completion template

- [ ] Completed target: `<target text>`
- [ ] Scope:
  - `path/edited`
- [ ] Validation run:
  - `command`
- [ ] Evidence/notes:
  - `what changed and why`
- [ ] Checked by:
