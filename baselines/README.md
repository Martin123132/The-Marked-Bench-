# Baseline Reports

This directory stores checked-in benchmark evidence for reference systems.

Each baseline report must pass:

```bash
marked-bench --validate-report baselines/contradiction_engine_v0_1_0.json
```

The current baseline is:

- `contradiction_engine_v0_1_0.json`: packaged symbolic `ContradictionEngine`
  on `marked-bench-contradiction-standard` suite version `0.1.0`.
- `always_none_v0_1_0.json`: intentionally weak detector that predicts `none`
  for every case.
- `contradiction_engine_adversarial_v0_2_0.json`: packaged symbolic
  `ContradictionEngine` on the harder adversarial suite version `0.2.0`.
- `always_none_adversarial_v0_2_0.json`: intentionally weak detector on the
  adversarial suite.
