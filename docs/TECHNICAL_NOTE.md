# Technical Note

Project: The Marked Bench.

This note summarizes the checked benchmark release artifacts for `contradiction-detection`. It is generated from the suite manifests, baseline reports, leaderboards, and benchmark registry.

## Public Tracks

| Track | Suite ID | Version | Cases | Suite Hash | Baseline Best |
| --- | --- | ---: | ---: | --- | ---: |
| contradiction | `marked-bench-contradiction-standard` | `0.1.0` | 17 | `8c1f80ff67874af54869bab2e361b3cc7416ce1d86f80ff583636a55e3462765` | 100.00 |
| contradiction-adversarial | `marked-bench-contradiction-adversarial` | `0.2.0` | 17 | `454c1aff69d5028224549dfc14fd8e6c10818251d0abf8becf36f0856b2dbd67` | 52.37 |
| contradiction-multihop | `marked-bench-contradiction-multihop` | `0.3.0` | 18 | `07a2bb9c0e8356d1cdab98b5b1b35a3c8bd29beff695816dfb151dbb5f6d0d1f` | 24.14 |

## Suite Composition

### contradiction

- Cases: 17
- Contradiction cases: 11
- Control cases: 6
- Difficulties: easy=9, medium=8
- Domains: biology=1, geometry=2, governance=4, language=1, math=1, measurement=2, operations=2, safety=3, science=1
- Labels: definitional_violation=2, direct_negation=3, none=6, property_mismatch=2, temporal_conflict=2, universal_counterexample=2
- Quality gates: min_cases=15, requires_all_contradiction_labels=True, requires_control_cases=True, requires_multiple_difficulties=True, requires_multiple_domains=True

### contradiction-adversarial

- Cases: 17
- Contradiction cases: 11
- Control cases: 6
- Difficulties: hard=10, medium=7
- Domains: ai_safety=2, benchmarking=1, data_governance=2, geometry=2, governance=1, math=1, measurement=2, operations=3, security=3
- Labels: definitional_violation=2, direct_negation=3, none=6, property_mismatch=2, temporal_conflict=2, universal_counterexample=2
- Quality gates: min_cases=15, requires_all_contradiction_labels=True, requires_control_cases=True, requires_multiple_difficulties=True, requires_multiple_domains=True

### contradiction-multihop

- Cases: 18
- Contradiction cases: 10
- Control cases: 8
- Difficulties: expert=4, hard=7, medium=7
- Domains: ai_safety=2, benchmarking=2, compliance=1, data_governance=2, governance=1, infrastructure=1, measurement=2, operations=3, privacy=1, records=1, research=1, security=1
- Labels: definitional_violation=2, direct_negation=2, none=8, property_mismatch=2, temporal_conflict=2, universal_counterexample=2
- Quality gates: min_cases=15, requires_all_contradiction_labels=True, requires_control_cases=True, requires_multiple_difficulties=True, requires_multiple_domains=True

## Baseline Evidence

| Track | System | Overall | Type Acc. | Detection F1 | Brier | ECE | Failures |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: |
| contradiction | ContradictionEngine | 100.00 | 1.0000 | 1.0000 | 0.0340 | 0.1282 | 0 |
| contradiction | AlwaysNoneDetector | 8.82 | 0.3529 | 0.0000 | 0.6471 | 0.6471 | 11 |
| contradiction-adversarial | ContradictionEngine | 52.37 | 0.5882 | 0.5333 | 0.4367 | 0.4835 | 7 |
| contradiction-adversarial | AlwaysNoneDetector | 8.82 | 0.3529 | 0.0000 | 0.6471 | 0.6471 | 11 |
| contradiction-multihop | ContradictionEngine | 24.14 | 0.5000 | 0.1818 | 0.5050 | 0.5167 | 9 |
| contradiction-multihop | AlwaysNoneDetector | 11.11 | 0.4444 | 0.0000 | 0.5556 | 0.5556 | 10 |

## Reproducibility Contract

- Suite comparisons must pin `suite_id`, `suite_version`, and `suite_hash`.
- Public reports must pass `marked-bench --validate-report REPORT`.
- Leaderboard submissions must pass `marked-bench --validate-submission SUBMISSION`.
- Published results should include `marked-bench --validate-result-card CARD`.
- Accepted entries should pass `marked-bench --validate-submission-review REVIEW`.
- Public release artifacts are pinned by `releases/marked_bench_release_v0_3_10.json`.
- Release conformance is captured by `conformance/marked_bench_conformance_v0_3_10.json`.
- External adoption metadata is captured by `adoption/marked_bench_adoption_packet_v0_3_10.json`.
- Third-party evidence is recorded by `adoption/third_party_evidence_ledger_v0_3_10.json`.
- Repository artifact drift is checked by `python scripts/validate_benchmark_artifacts.py`.

## Current Limitations

- Current suites are compact public English-language tracks.
- Public cases can be overfit; hidden/private evaluation remains future work.
- Baseline systems are reference points, not claims of state-of-the-art performance.

## Registry

The machine-readable registry is `benchmark_registry.json`.
