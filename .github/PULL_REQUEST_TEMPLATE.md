## Summary

Describe the benchmark, report, leaderboard, or infrastructure change.

## Track

- [ ] `contradiction` v0.1.0
- [ ] `contradiction-adversarial` v0.2.0
- [ ] `contradiction-multihop` v0.3.0
- [ ] `contradiction-controls` v0.4.0
- [ ] New suite or infrastructure only

## Evidence

- Report path:
- Submission metadata path:
- Submission bundle path:
- Result card path:
- Third-party evidence ledger entry:
- Report SHA-256:
- System name/version:
- Detector/model/prompt/rule configuration:

## Checks

- [ ] `python -m unittest discover -s tests`
- [ ] `python scripts/validate_benchmark_artifacts.py`
- [ ] All new reports pass `marked-bench --validate-report PATH`
- [ ] All leaderboard submissions pass `marked-bench --validate-submission PATH`
- [ ] All result cards pass `marked-bench --validate-result-card PATH`
- [ ] Evidence ledger changes pass `marked-bench --validate-evidence-ledger PATH`
- [ ] Leaderboard regenerated when reports changed
