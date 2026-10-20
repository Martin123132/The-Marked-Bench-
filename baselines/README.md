# Baseline Reports

This directory stores checked-in benchmark evidence for reference systems.

Each baseline report must pass:

```bash
marked-bench --validate-report baselines/contradiction_engine_v0_1_1.json
```

The current baseline is:

- `multihop_reference_v0_3_0.json`: bounded text-only `MultiHopReference` on
  the frozen multi-hop suite. See [method, robustness evidence and limitations](../docs/MULTIHOP_REFERENCE.md).
  Run it from current repository main with
  `python -m marked_bench.contradiction.multihop_reference --report artifacts/multihop-reference.json`.
  It is not included in the earlier v0.4.10 tag and does not replace the legacy engine.

- `contradiction_engine_v0_1_0.json`: packaged symbolic `ContradictionEngine`
  on the legacy `marked-bench-contradiction-standard` suite version `0.1.0`.
- `always_none_v0_1_0.json`: intentionally weak detector that predicts `none`
  for every legacy foundation case.
- `contradiction_engine_v0_1_1.json`: packaged symbolic `ContradictionEngine`
  on the active foundation suite version `0.1.1`.
- `hash_prior_v0_1_1.json`: deterministic hash-prior reference baseline on
  the active foundation suite.
- `always_none_v0_1_1.json`: intentionally weak detector on the active
  foundation suite.
- `contradiction_engine_adversarial_v0_2_0.json`: packaged symbolic
  `ContradictionEngine` on the harder adversarial suite version `0.2.0`.
- `hash_prior_adversarial_v0_2_0.json`: deterministic hash-prior reference
  baseline on the adversarial suite.
- `always_none_adversarial_v0_2_0.json`: intentionally weak detector on the
  adversarial suite.
- `contradiction_engine_multihop_v0_3_0.json`: packaged symbolic
  `ContradictionEngine` on the linked-evidence multi-hop suite version `0.3.0`.
- `hash_prior_multihop_v0_3_0.json`: deterministic hash-prior reference
  baseline on the multi-hop suite.
- `always_none_multihop_v0_3_0.json`: intentionally weak detector on the
  multi-hop suite.
- `contradiction_engine_controls_v0_4_0.json`: packaged symbolic
  `ContradictionEngine` on the false-positive controls suite version `0.4.0`.
- `hash_prior_controls_v0_4_0.json`: deterministic hash-prior reference
  baseline on the controls suite.
- `always_none_controls_v0_4_0.json`: intentionally weak detector on the
  controls suite.
