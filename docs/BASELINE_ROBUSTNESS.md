# Baseline Robustness Diagnostic

## Technical summary

- Overall guard status: **PASS**.
- The multi-hop ranking gap is explained, not removed: `HashPriorBaseline` scores 45.93 versus 24.14, a 21.79-point lead.
- The observed hash assignment is unusually favorable: only 1.8% of 4,096 deterministic salted-ID variants score as highly.
- The task-aware reference is also underpowered for this track: it finds 1 of 10 contradiction cases, while the hash baseline finds 9 by predicting a contradiction on 15 of 18 cases.
- Identifier luck alone is not the full cause: 54.9% of salted-ID variants still beat the current engine. The leaderboard order must remain an explained watchlist item until a genuinely multi-hop reference baseline is added.

## Track comparison

Low-information baselines are diagnostic references, not task-aware systems.

| Track | Task-aware rank | Task-aware score | Low-information rank | Low-information score | Status | Note |
| --- | ---: | ---: | ---: | ---: | --- | --- |
| contradiction | 1 | 100.00 | 2 | 24.11 | pass | low-information baseline does not outrank task-aware baseline |
| contradiction-adversarial | 1 | 52.37 | 2 | 25.78 | pass | low-information baseline does not outrank task-aware baseline |
| contradiction-multihop | 2 | 24.14 | 1 | 45.93 | explained watchlist | explained watchlist: the task-aware reference lacks multi-hop coverage and the observed hash assignment is unusually favorable; keep this track watchlisted before expansion |
| contradiction-controls | 1 | 100.00 | 3 | 15.68 | pass | low-information baseline does not outrank task-aware baseline |

## Detection breadth and chance alignment create the score gap

The scoring decomposition reconciles the complete leaderboard difference. Positive gaps favor the hash baseline.

| Component | Weight | Engine points | Hash points | Gap points |
| --- | ---: | ---: | ---: | ---: |
| Contradiction macro F1 | 45.0% | 6.00 | 15.20 | +9.20 |
| Type accuracy | 25.0% | 12.50 | 8.33 | -4.17 |
| Detection F1 | 20.0% | 3.64 | 14.40 | +10.76 |
| Coverage index | 10.0% | 2.00 | 8.00 | +6.00 |

Detection F1 and coverage contribute most of the lead because broad non-`none` guesses receive credit when the engine abstains on multi-hop contradictions. Type accuracy favors the engine, but not enough to offset those components.

## The observed hash score is unstable under identifier changes

Both sensitivity checks preserve the 18 expected labels and the public scoring formula.

| Sensitivity check | Samples | Median score | 95th percentile | Beat engine | At or above observed |
| --- | ---: | ---: | ---: | ---: | ---: |
| Salted identifier namespaces | 4,096 | 25.38 | 40.92 | 54.9% | 1.8% |
| Fixed hash-label mix, permuted across cases | 4,096 | 25.18 | 39.93 | 54.0% | 1.6% |

The result supports two simultaneous conclusions: the exact `45.93` score is a chance-favorable ID assignment, and the engine's missing multi-hop coverage makes the ranking vulnerable to many low-information assignments.

## Case-level comparison

| Case | Expected | Engine prediction | Hash prediction | Exact-label outcome |
| --- | --- | --- | --- | --- |
| `marked-hop-direct-001` | `direct_negation` | `none` | `temporal_conflict` | neither correct |
| `marked-hop-direct-002` | `direct_negation` | `none` | `definitional_violation` | neither correct |
| `marked-hop-direct-003` | `none` | `none` | `definitional_violation` | engine only |
| `marked-hop-property-001` | `property_mismatch` | `none` | `temporal_conflict` | neither correct |
| `marked-hop-property-002` | `property_mismatch` | `property_mismatch` | `property_mismatch` | both correct |
| `marked-hop-property-003` | `none` | `none` | `temporal_conflict` | engine only |
| `marked-hop-definition-001` | `definitional_violation` | `none` | `none` | neither correct |
| `marked-hop-definition-002` | `definitional_violation` | `none` | `definitional_violation` | hash only |
| `marked-hop-definition-003` | `none` | `none` | `temporal_conflict` | engine only |
| `marked-hop-universal-001` | `universal_counterexample` | `none` | `universal_counterexample` | hash only |
| `marked-hop-universal-002` | `universal_counterexample` | `none` | `temporal_conflict` | neither correct |
| `marked-hop-universal-003` | `none` | `none` | `none` | both correct |
| `marked-hop-temporal-001` | `temporal_conflict` | `none` | `universal_counterexample` | neither correct |
| `marked-hop-temporal-002` | `temporal_conflict` | `none` | `temporal_conflict` | hash only |
| `marked-hop-temporal-003` | `none` | `none` | `none` | both correct |
| `marked-hop-control-001` | `none` | `none` | `temporal_conflict` | engine only |
| `marked-hop-control-002` | `none` | `none` | `direct_negation` | engine only |
| `marked-hop-control-003` | `none` | `none` | `universal_counterexample` | engine only |

## Scope, data, and metric definitions

- Population: all 18 cases in `marked-bench-contradiction-multihop` v0.3.0.
- Grain: one expected and predicted contradiction label per unique case ID; 18 unique IDs were verified.
- Overall score: weighted points from contradiction macro F1 (45%), exact type accuracy (25%), binary contradiction detection F1 (20%), and contradiction-label coverage (10%).
- Comparison baseline: checked-in `ContradictionEngine` and `HashPriorBaseline` reports for the same immutable suite hash.

Expected label mix:

| Label | Expected cases | Hash predictions |
| --- | ---: | ---: |
| `none` | 8 | 3 |
| `direct_negation` | 2 | 1 |
| `property_mismatch` | 2 | 1 |
| `definitional_violation` | 2 | 3 |
| `universal_counterexample` | 2 | 3 |
| `temporal_conflict` | 2 | 7 |

## Methodology

1. Recompute the observed hash score directly from the checked-in case predictions.
2. Attribute the leaderboard gap to the four public weighted score components.
3. Generate 4,096 deterministic alternative hash assignments by prefixing each case ID with an integer namespace before SHA-256 mapping.
4. Generate 4,096 deterministic permutations of the observed hash label mix using seed `20260710`.
5. Compare each simulated score with the observed hash score and current engine score.

Run or regenerate this artifact with:

```bash
python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md
```

## Limitations and robustness checks

- This is a descriptive sensitivity analysis over a small 18-case public suite, not a claim of causal or statistical model superiority.
- The suite manifest publishes expected labels. This analysis checks scoring and baseline behavior; it does not provide resistance to answer lookup or benchmark gaming.
- A blind ranking would require a held-out evaluation split, non-revealing evaluation identifiers, and controlled access to expected labels.
- The simulation is deterministic and CI-friendly. Its thresholds intentionally fail when the engine, suite, reports, or interpretation changes, forcing a reviewer to refresh the public note.

## Recommended next steps

1. Preserve published multi-hop suite v0.3.0 and its case IDs unchanged.
2. Keep the current leaderboard marked as an explained watchlist, not evidence that the hash baseline is a stronger contradiction system.
3. Before expanding the track, add a genuinely multi-hop task-aware reference and require it to beat low-information sensitivity medians across detection, type, and coverage components.
4. If future claims need gaming resistance, design a separately versioned held-out evaluation path.

## Further questions

- Which deterministic multi-hop reasoning baseline should become the next task-aware reference?
- Should a future public release separate transparent development cases from held-out ranking cases?
