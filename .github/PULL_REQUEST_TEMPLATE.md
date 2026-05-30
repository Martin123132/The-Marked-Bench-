## Summary

Describe the benchmark, report, leaderboard, or infrastructure change.

## Track

- [ ] `contradiction` v0.1.0
- [ ] `contradiction-adversarial` v0.2.0
- [ ] New suite or infrastructure only

## Evidence

- Report path:
- Submission metadata path:
- Report SHA-256:
- System name/version:
- Detector/model/prompt/rule configuration:

## Checks

- [ ] `python -m unittest discover -s tests`
- [ ] `python scripts/validate_benchmark_artifacts.py`
- [ ] All new reports pass `marked-bench --validate-report PATH`
- [ ] All leaderboard submissions pass `marked-bench --validate-submission PATH`
- [ ] Leaderboard regenerated when reports changed
