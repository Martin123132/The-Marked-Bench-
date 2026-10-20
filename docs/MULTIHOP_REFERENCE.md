# Multi-Hop Symbolic Reference

This is a bounded, development-suite-aware reference, not a general English reasoner,
a blind evaluation, independent adoption, or evidence of model superiority.

Available on repository main after v0.4.10. The published v0.4.10 tag remains unchanged.

## Reproduced results

- Frozen suite: `marked-bench-contradiction-multihop` v0.3.0 (18 cases).
- Suite hash: `07a2bb9c0e8356d1cdab98b5b1b35a3c8bd29beff695816dfb151dbb5f6d0d1f`.
- MultiHopReference score: **84.00**; exact labels: **16/18**.
- Contradictions detected: **8/10**; false positives on controls: **0/8**.
- Unchanged legacy engine: **24.14**; unchanged hash-prior: **45.93**.
- Meaning-preserving checks passed: **90**.
- Required-source-fact removal checks passed: **16**.

## What the reference does

It parses a small documented vocabulary into directed membership/inheritance links and typed facts.
A breadth-first closure carries properties and class rules to the query subject, retaining source sentences.
Separate joins compare reviewer counts with minimum definitions and event dates with applicable temporal rules.
Returned contradictions include their reasoning rule and source evidence in the report.

Supported forms include `X belongs to Y`, `X is assigned to Y`, `X was evaluated under Y`,
`X is a CATEGORY`, `X is classified as CATEGORY`, profile use and explicit inheritance.
Typed facts cover maximum context windows, calibrated/uncalibrated mass (kg/lb conversion),
post-publication immutability, universal pre-production reviews, minimum reviewer counts,
closed fleet-launch year intervals and dated current-endpoint replacement.

## Robustness checks

Each public case is rerun with opaque IDs and misleading metadata, reversed premise sentences,
consistently renamed entity names, and disconnected quantity distractors. Batch order is also reversed.
For each detected public contradiction, removing either required premise must remove the proof.
Unit tests additionally use newly authored entities, quantities, threshold boundaries, unit conversions,
longer inheritance chains, cycles, conflicting quantities, non-universal statements and date boundaries.
These are internal metamorphic and synthetic tests, not a held-out evaluation split.

## Boundaries

- Inference reads premise/query text only. IDs route outputs; expected labels, tags and domains do not select rules.
- The grammar was developed with the public suite visible. High development-set scores do not establish generalization.
- Inherited permission/validity polarity and unrestricted paraphrases are unsupported in this first reference.
- No proof maps to the benchmark's `none` label; it is not proof that the statements are consistent.
- The fixed 0.85 confidence is uncalibrated. Timing fields are zeroed for deterministic artifacts, not a speed claim.
- Ambiguous categories, quantities or dates can cause abstention. The parser is not a general temporal or legal rule system.
- The historical engine/hash-prior diagnostic remains valid for that pair; its weakness is not erased by the new reference.
- Keep suite cases, IDs, hashes and scoring unchanged. Blind ranking needs a separately designed held-out evaluation.

## Reproduce

```bash
python -m marked_bench.contradiction.multihop_reference --report artifacts/multihop-reference.json
python -m marked_bench.benchmark_cli --validate-report artifacts/multihop-reference.json
python scripts/check_multihop_reference.py
python -m unittest discover -s tests
```

Regenerate checked evidence with `python scripts/regenerate_release_artifacts.py`.
No network or provider/model invocation is required for reference inference or these checks.

## Case-level predictions

| Case | Expected | Predicted | Source sentences |
| --- | --- | --- | ---: |
| marked-hop-direct-001 | direct_negation | none | 0 |
| marked-hop-direct-002 | direct_negation | none | 0 |
| marked-hop-direct-003 | none | none | 0 |
| marked-hop-property-001 | property_mismatch | property_mismatch | 2 |
| marked-hop-property-002 | property_mismatch | property_mismatch | 2 |
| marked-hop-property-003 | none | none | 0 |
| marked-hop-definition-001 | definitional_violation | definitional_violation | 2 |
| marked-hop-definition-002 | definitional_violation | definitional_violation | 2 |
| marked-hop-definition-003 | none | none | 0 |
| marked-hop-universal-001 | universal_counterexample | universal_counterexample | 2 |
| marked-hop-universal-002 | universal_counterexample | universal_counterexample | 2 |
| marked-hop-universal-003 | none | none | 0 |
| marked-hop-temporal-001 | temporal_conflict | temporal_conflict | 2 |
| marked-hop-temporal-002 | temporal_conflict | temporal_conflict | 2 |
| marked-hop-temporal-003 | none | none | 0 |
| marked-hop-control-001 | none | none | 0 |
| marked-hop-control-002 | none | none | 0 |
| marked-hop-control-003 | none | none | 0 |
