## Summary

## What changed

- Briefly describe the benchmark, report, leaderboard, or infrastructure change.

## Why changed

- Why this change is needed now.

## Target(s) completed

- [ ] Target A
- [ ] Target B
- [ ] Target C
- [ ] Target D
- [ ] Target E
- [ ] Target F
- [ ] Target G
- [ ] Target H
- [ ] Target I
- [ ] Target J
- [ ] Target K
- [ ] Target L
- [ ] Target M
- [ ] Target N
- [ ] Target O
- [ ] Target P
- [ ] Target Q
- [ ] Target R
- [ ] Target S
- [ ] Target T
- [ ] Target U
- [ ] Target V
- [ ] Target W
- [ ] Target X
- [ ] Target Y
- [ ] Target Z
- [ ] Target AA

## Track

- [ ] `contradiction` v0.1.1
- [ ] legacy `contradiction` v0.1.0
- [ ] `contradiction-adversarial` v0.2.0
- [ ] `contradiction-multihop` v0.3.0
- [ ] `contradiction-controls` v0.4.0
- [ ] New suite or infrastructure only

## Evidence

- Files changed:
  - path/to/file_or_dir
- Report path:
- Submission metadata path:
- Submission bundle path:
- Result card path:
- Third-party evidence ledger entry:
- Report SHA-256:
- System name/version:
- Detector/model/prompt/rule configuration:
- Scoring sanity artifact path:
- Case quality artifact path:
- Baseline robustness artifact path:
- Evaluator walkthrough path:
- Submission proof path:

## Checks

- [ ] `python -m unittest discover -s tests`
- [ ] `python scripts/validate_benchmark_artifacts.py`
- [ ] `python -m marked_bench.benchmark_cli --check-standard-status`
- [ ] `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
- [ ] `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
- [ ] `python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md`
- [ ] `python scripts/check_evaluator_walkthrough.py`
- [ ] `python scripts/check_submission_proof.py --artifact docs/SUBMISSION_PROOF.md`
- [ ] `python scripts/regenerate_release_artifacts.py --check`
- [ ] `python scripts/check_review_workflow.py`
- [ ] `python scripts/check_license_notice.py`
- [ ] All new reports pass `marked-bench --validate-report PATH`
- [ ] All leaderboard submissions pass `marked-bench --validate-submission PATH`
- [ ] All result cards pass `marked-bench --validate-result-card PATH`
- [ ] Evidence ledger changes pass `marked-bench --validate-evidence-ledger PATH`
- [ ] Leaderboard regenerated when reports changed

### Scoring-related checklist

- [ ] `python scripts/check_scoring_sanity.py --artifact docs/SCORING_SANITY.md`
- [ ] Scoring artifact updated and reviewed in PR narrative

### Case-quality checklist

- [ ] `python scripts/check_case_quality.py --artifact docs/CASE_QUALITY.md`
- [ ] Case-quality artifact updated when suite cases change

## Optional reviewer-facing notes

- Add any compatibility, comparability, or claim-impact notes that reviewers should verify.
