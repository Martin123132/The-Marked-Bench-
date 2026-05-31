# Scoring Specification

Project: The Marked Bench.

This document is generated from the machine-readable scoring spec. It is the language-neutral contract for independent scorers.

## Identity

- Release: `marked-bench-contradiction-standard-release-0.4.6`
- Default track: `contradiction-multihop`
- Schema: `marked_bench.scoring-spec.v1`

## Labels

- `direct_negation`
- `property_mismatch`
- `definitional_violation`
- `universal_counterexample`
- `temporal_conflict`
- `none`

## Input Contract

- `prediction_order_is_ignored`: True
- `all_case_ids_required_once`: True
- `unknown_case_ids_are_invalid`: True
- `missing_case_ids_are_invalid`: True
- `duplicate_case_ids_are_invalid`: True
- `detector_score_range`: [0.0, 1.0]
- `detector_score_default`: 0.0
- `detector_score_semantics`: Binary contradiction confidence on [0, 1].
- `label_aliases`: {'no_contradiction': 'none', 'non_contradiction': 'none', 'not_contradiction': 'none', 'null': 'none'}

## Scoring Pipeline

1. Normalize predicted labels to lowercase snake_case and apply label aliases.
2. Validate that each canonical case_id appears exactly once.
3. For each case, compute type_correct as predicted == expected.
4. For each case, compute detection_correct from contradiction-vs-none polarity.
5. Build a full label confusion matrix using expected labels as rows and predicted labels as columns.
6. Compute per-label precision, recall, f1, and support from the confusion matrix.
7. Compute binary contradiction detection metrics from none-vs-non-none polarity.
8. Compute calibration metrics from detector_score and expected contradiction polarity.
9. Compute slice metrics by domain, difficulty, capability, and tag.
10. Compute the weighted overall score and failure list.

## Metric Definitions

- `type_accuracy`: exact_type_correct / case_count
- `contradiction_type_accuracy`: exact_type_correct_on_non_none_cases / non_none_case_count
- `per_class_precision`: true_positive / max(true_positive + false_positive, 1)
- `per_class_recall`: true_positive / max(true_positive + false_negative, 1)
- `per_class_f1`: 2 * precision * recall / max(precision + recall, 1e-9)
- `contradiction_macro_f1`: mean(per_class_f1 for contradiction labels with support > 0)
- `binary_detection_precision`: binary_true_positive / max(binary_true_positive + binary_false_positive, 1)
- `binary_detection_recall`: binary_true_positive / max(binary_true_positive + binary_false_negative, 1)
- `binary_detection_f1`: 2 * precision * recall / max(precision + recall, 1e-9)
- `coverage_index`: contradiction labels with support > 0 and recall > 0 divided by contradiction label count
- `calibration_brier_score`: mean((detector_score - expected_binary_contradiction) ** 2)
- `calibration_ece`: sum(bin_count / total * abs(mean_confidence - empirical_positive_rate)) over 10 bins
- `overall_score`: round(100 * (0.45 * contradiction_macro_f1 + 0.25 * type_accuracy + 0.20 * binary_detection_f1 + 0.10 * coverage_index), 2)

## Overall Score Weights

- `contradiction_macro_f1`: 0.45
- `type_accuracy`: 0.25
- `binary_detection_f1`: 0.2
- `coverage_index`: 0.1

## Compatibility

Independent implementations should validate against `standard/marked_bench_scoring_compatibility_v0_4_6.json`.

```bash
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_6.json
```

## Public Tracks

| Track | Suite ID | Version | Cases | Suite Hash |
| --- | --- | ---: | ---: | --- |
| contradiction | `marked-bench-contradiction-standard` | `0.1.0` | 17 | `8c1f80ff67874af54869bab2e361b3cc7416ce1d86f80ff583636a55e3462765` |
| contradiction-adversarial | `marked-bench-contradiction-adversarial` | `0.2.0` | 17 | `454c1aff69d5028224549dfc14fd8e6c10818251d0abf8becf36f0856b2dbd67` |
| contradiction-multihop | `marked-bench-contradiction-multihop` | `0.3.0` | 18 | `07a2bb9c0e8356d1cdab98b5b1b35a3c8bd29beff695816dfb151dbb5f6d0d1f` |
| contradiction-controls | `marked-bench-contradiction-controls` | `0.4.0` | 18 | `33a0777f6f93504bde517d922f46c24c1d93992256bfe95b32287695babfb08a` |
