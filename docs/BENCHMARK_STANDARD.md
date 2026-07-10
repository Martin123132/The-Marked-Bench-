# The Marked Bench Contradiction Benchmark Standard

The Marked Bench contradiction benchmark is a versioned, reproducible test
suite for systems that classify contradictions between a premise and a query.

It is meant to be a public standard for this project area: every score is tied
to a suite ID, suite version, deterministic suite hash, case list, report
schema, confusion matrix, and per-class metrics.
Published results should also include a result card that pins the report,
bundle, review status, standard publication claims, and file hashes.
Publication packets provide a self-contained folder for sharing the full
evidence chain.
Result claims provide exact citeable wording tied to the publication packet
hash, so scores are not detached from their evidence or overstated.
Implementation kits provide copy-ready external CI guidance and a
machine-readable contract for validating public result packets outside this
repository.
The standard profile maps the benchmark's own standardization requirements to
evidence files and validation commands.

## Suite Identity

- Foundation suite ID: `marked-bench-contradiction-standard`
- Foundation suite version: `0.1.1`
- Adversarial suite ID: `marked-bench-contradiction-adversarial`
- Adversarial suite version: `0.2.0`
- Multi-hop suite ID: `marked-bench-contradiction-multihop`
- Multi-hop suite version: `0.3.0`
- Controls suite ID: `marked-bench-contradiction-controls`
- Controls suite version: `0.4.0`
- Report schema: `marked_bench.contradiction-benchmark-report.v2`
- Canonical builder: `marked_bench.contradiction.benchmark_suite.build_standard_suite`

Every manifest, report, leaderboard entry, registry track, and leaderboard
submission carries `suite_hash`: a SHA-256 digest of the ordered canonical case
records. Public comparisons should pin `suite_id`, `suite_version`, and
`suite_hash`.

## What It Measures

The benchmark covers five contradiction classes plus non-contradiction controls:

- `direct_negation`
- `property_mismatch`
- `definitional_violation`
- `universal_counterexample`
- `temporal_conflict`
- `none`

Cases include stable IDs, domain tags, difficulty tags, capability tags, and
plain-language notes.

Each suite manifest includes a `profile` block with label, domain, difficulty,
capability, and tag counts. It also records basic quality gates: minimum case
count, coverage of every contradiction label, presence of control cases,
multiple domains, and multiple difficulty levels.

## Scoring

The report includes:

- `overall_score`: weighted 0-100 score.
- `type_accuracy`: exact contradiction-class accuracy across all cases.
- `contradiction_type_accuracy`: exact class accuracy on contradiction cases.
- `contradiction_macro_f1`: macro F1 across contradiction classes.
- `coverage_index`: share of contradiction classes with non-zero recall.
- `detection`: binary contradiction-vs-none metrics.
- `calibration`: binary confidence calibration from `detector_score`.
- `explanation_audit`: rationale and evidence coverage for reviewer-facing
  explanation evidence.
- `per_class`: precision, recall, F1, and support for every label.
- `slices`: diagnostic performance by domain, difficulty, capability, and tag.
- `confusion_matrix`: expected label by predicted label.
- `failures`: all missed exact-label cases.

The source tree also includes JSON schemas for public infrastructure:

- `schemas/benchmark_registry.schema.json`
- `schemas/contradiction_benchmark_report.schema.json`
- `schemas/contradiction_predictions.schema.json`
- `schemas/contradiction_suite_manifest.schema.json`
- `schemas/leaderboard.schema.json`
- `schemas/leaderboard_submission.schema.json`
- `schemas/submission_bundle.schema.json`
- `schemas/submission_review.schema.json`
- `schemas/publication_packet.schema.json`
- `schemas/result_claim.schema.json`
- `schemas/implementation_kit.schema.json`
- `schemas/standard_profile.schema.json`
- `schemas/release_manifest.schema.json`
- `schemas/result_card.schema.json`
- `schemas/conformance_report.schema.json`
- `schemas/adoption_packet.schema.json`
- `schemas/third_party_evidence_ledger.schema.json`

For a high-level summary of intended use, non-use, limitations, and
reproducibility expectations, see `docs/BENCHMARK_CARD.md`.
For a generated release summary with suite hashes, composition, baselines, and
reproducibility commands, see `docs/TECHNICAL_NOTE.md`.

The current overall score weights are:

- 45% contradiction macro F1
- 25% type accuracy
- 20% binary detection F1
- 10% class coverage

This keeps the benchmark from rewarding detectors that merely say
"contradiction" without identifying the kind of contradiction.

Slice metrics are included for diagnosis and review. They are not additional
leaderboard weights in the current release, but they make it clear whether a
system is failing specific difficulty bands, domains, capabilities, or tags.

`detector_score` is interpreted as confidence that the case contains a
contradiction. It must be a finite value from 0 to 1. The report includes
binary Brier score, expected calibration error, confidence bins, mean
confidence, and empirical positive rate.

## Run The Baseline

```bash
python -m marked_bench.examples.benchmark_standard_demo
```

The demo writes:

```text
artifacts/marked_bench_contradiction_benchmark_report.json
```

`artifacts/` is ignored because reports are generated evidence, not source.

After installing the package, the command-line runner is:

```bash
marked-bench --report artifacts/marked_bench_contradiction_benchmark_report.json
```

Use `--json` to print the full report to stdout.

Validate an existing report before leaderboard submission:

```bash
marked-bench --validate-report artifacts/marked_bench_contradiction_benchmark_report.json
```

Build a leaderboard from valid reports:

```bash
marked-bench --build-leaderboard baselines/always_none_v0_1_1.json baselines/hash_prior_v0_1_1.json baselines/contradiction_engine_v0_1_1.json --leaderboard-output leaderboard/leaderboard_v0_1_1.json
```

Export the registry that points to every public track, schema, suite manifest,
baseline, and leaderboard:

```bash
marked-bench --export-registry benchmark_registry.json
```

Export the release manifest that pins public benchmark artifacts by SHA-256:

```bash
marked-bench --export-release-manifest releases/marked_bench_release_v0_4_9.json
```

Export and validate the release conformance report:

```bash
marked-bench --export-conformance-report conformance/marked_bench_conformance_v0_4_9.json
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_9.json
```

Export and validate the benchmark standard profile:

```bash
marked-bench --export-standard-profile standard/marked_bench_standard_profile_v0_4_9.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_9.json
```

Export and validate the standard change-control profile:

```bash
marked-bench --export-change-control standard/marked_bench_change_control_v0_4_9.json
marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_9.json
```

Export and validate deterministic scoring compatibility vectors:

```bash
marked-bench --export-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_9.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_9.json
```

Export and validate the language-neutral scoring specification:

```bash
marked-bench --export-scoring-spec standard/marked_bench_scoring_spec_v0_4_9.json
marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_9.json
marked-bench --export-scoring-spec-doc docs/SCORING_SPEC.md
```

Export and validate the external adoption packet:

```bash
marked-bench --export-adoption-packet adoption/marked_bench_adoption_packet_v0_4_9.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_9.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_9.json
```

Export and validate the third-party implementation kit:

```bash
marked-bench --export-implementation-kit adoption/marked_bench_implementation_kit_v0_4_9.json
marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_9.json
```

Run the harder adversarial track:

```bash
marked-bench --suite contradiction-adversarial --report artifacts/marked_bench_contradiction_adversarial_report.json
```

Run the multi-hop track:

```bash
marked-bench --suite contradiction-multihop --report artifacts/marked_bench_contradiction_multihop_report.json
```

Run the false-positive controls track:

```bash
marked-bench --suite contradiction-controls --report artifacts/marked_bench_contradiction_controls_report.json
```

The active checked-in foundation symbolic baseline lives at:

```text
baselines/contradiction_engine_v0_1_1.json
```

The active checked-in foundation reference baseline lives at:

```text
baselines/hash_prior_v0_1_1.json
```

The checked-in adversarial, multi-hop, and controls reference baselines live at:

```text
baselines/hash_prior_adversarial_v0_2_0.json
baselines/hash_prior_multihop_v0_3_0.json
baselines/hash_prior_controls_v0_4_0.json
```

The legacy foundation symbolic baseline remains available at:

```text
baselines/contradiction_engine_v0_1_0.json
```

The active checked-in foundation suite manifest lives at:

```text
suites/marked_bench_contradiction_standard_v0_1_1.json
```

The legacy foundation suite manifest remains available at:

```text
suites/marked_bench_contradiction_standard_v0_1_0.json
```

The checked-in adversarial suite manifest lives at:

```text
suites/marked_bench_contradiction_adversarial_v0_2_0.json
```

The checked-in multi-hop suite manifest lives at:

```text
suites/marked_bench_contradiction_multihop_v0_3_0.json
```

The checked-in controls suite manifest lives at:

```text
suites/marked_bench_contradiction_controls_v0_4_0.json
```

## Score A Custom Detector

```python
from marked_bench.contradiction.benchmark_suite import evaluate_standard_suite


def detect(claim):
    # Return Contradiction(...) or None.
    ...


report = evaluate_standard_suite(detect, system_name="my-detector")
print(report["overall_score"])
```

For systems outside Python, export a JSONL prediction template and score it
back into the same report schema:

```bash
marked-bench --suite contradiction-adversarial --export-prediction-template artifacts/predictions.jsonl
marked-bench --suite contradiction-adversarial --score-predictions artifacts/predictions.jsonl --system-name "my-detector" --report artifacts/my-detector.json
```

Every leaderboard entry should also include submission metadata that pins the
report SHA-256 digest, suite identity, score, submitter, system version, and
method disclosures:

```bash
marked-bench --create-submission artifacts/my-detector-submission.json --submission-report artifacts/my-detector.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission artifacts/my-detector-submission.json
```

Accepted leaderboard entries should also have a structured review file:

```bash
marked-bench --create-submission-review artifacts/my-detector-review.json --review-bundle artifacts/my-detector-bundle.json --reviewer reviewer-name
marked-bench --validate-submission-review artifacts/my-detector-review.json
```

The standard review rubric is documented in
`docs/SUBMISSION_REVIEW_RUBRIC.md`.

Published results should include a result card:

```bash
marked-bench --create-result-card artifacts/my-detector-result-card.json --result-report artifacts/my-detector.json --result-bundle artifacts/my-detector-bundle.json --result-review artifacts/my-detector-review.json
marked-bench --validate-result-card artifacts/my-detector-result-card.json
```

Public result folders can be created in one command:

```bash
marked-bench --create-publication-packet artifacts/my-detector-publication-packet --publication-report artifacts/my-detector.json --publication-predictions artifacts/predictions.jsonl --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-publication-packet artifacts/my-detector-publication-packet/publication_packet.json
```

Public result claims can be created from publication packets:

```bash
marked-bench --create-result-claim artifacts/my-detector-publication-packet/result_claim.json --claim-publication-packet artifacts/my-detector-publication-packet/publication_packet.json
marked-bench --validate-result-claim artifacts/my-detector-publication-packet/result_claim.json
```

External repositories can copy
`adoption/implementation_kit/github_actions_validate_result.yml` into
`.github/workflows/marked-bench-result.yml` to validate a checked
`marked-bench-result/publication_packet.json` and
`marked-bench-result/result_claim.json` against the pinned benchmark release.

The checked example under `submissions/example_external_jsonl/` shows the full
external packet shape: JSONL predictions, scored report, submission metadata,
bundle manifest, structured review file, and result card.
The checked example under `submissions/example_publication_packet/` shows the
one-command publication packet and result claim shape.

External prediction records may include `rationale` and `evidence`. `rationale`
is the system's short explanation for the predicted label. `evidence` is a list
of quoted or named premise/query spans that support the decision. These fields
do not change the primary score in v0.3.3, but the report includes
`explanation_audit` coverage so reviewers can separate bare labels from
inspectable submissions.

## Standardization Rules

- Do not edit the meaning of existing case IDs after publication.
- Add cases by bumping `SUITE_VERSION`.
- Keep all reports JSON serializable.
- Report every failure, not only aggregate scores.
- Compare systems only when they use the same `suite_id` and `suite_version`.
- Treat `suite_hash` mismatches as incompatible results even if the version
  string is the same.
- Preserve non-contradiction controls so false positives remain visible.
- Reject leaderboard reports that do not pass the built-in validator.
- Require result cards for externally cited or ranked results.
- Require publication packets when a result is shared as a self-contained
  public evidence folder.
- Require result claims when a benchmark score is cited as a short public
  statement or badge.
- Keep the implementation kit current when release paths, schemas, or public
  result-validation commands change.
- Keep the standard profile current when benchmark-standard requirements,
  evidence paths, or validation commands change.
- Keep the change-control profile current when suite, schema, scoring, evidence,
  or governance intake rules change.
- Keep scoring compatibility vectors current when scoring semantics, public
  tracks, or expected score summaries change.
- Keep the scoring specification current when labels, formulas, rounding,
  calibration, or report semantics change.
- Keep `python scripts/validate_benchmark_artifacts.py` passing after any
  baseline, suite, or leaderboard change.
- Keep `python scripts/regenerate_release_artifacts.py --check` passing after
  generated release evidence changes.
- Keep `python scripts/check_license_notice.py` passing after license,
  citation, notice, or README licensing text changes.
- Keep checked public JSON artifacts conformant with the schemas under
  `schemas/`.

## Current Status

Version `0.1.0` is the original foundation suite. Version `0.1.1` expands the
foundation suite with additional status, unit, definition, evidence, temporal,
and elaboration cases while preserving existing published case IDs. Version
`0.2.0` adds an adversarial track with longer context, implicit contradictions,
paraphrase traps, and distractor controls. Version `0.3.0` adds a multi-hop track for linked-evidence
contradictions. Release `0.3.3` upgrades public report and prediction schemas
for rationale/evidence audit fields and aligns schemas with the default
multi-hop track. Release `0.3.4` adds structured submission review rubrics for
leaderboard governance. Release `0.3.5` adds dependency-free schema
conformance checks for checked public artifacts. Release `0.3.6` adds a
checked external-style submission packet and validates it as part of the normal
artifact gate. Release `0.3.7` adds a machine-readable conformance report for
the full release package. Release `0.3.8` adds standardized result cards for
publishable benchmark results. Release `0.3.9` adds a checked adoption packet
and announcement package so external users have a validated public handoff.
Release `0.3.10` adds a checked third-party evidence ledger so adoption claims
can be recorded without overstating unverified use. Version `0.4.0` adds a
false-positive controls track for paraphrases, scoped negatives, time shifts,
and harmless elaborations. Release `0.4.1` adds one-command publication packets
for self-contained public result evidence. Release `0.4.2` adds result claims
so public score statements are hash-pinned and bounded. Release `0.4.3` adds
the third-party implementation kit so external repositories can validate
publication packets and result claims in their own CI. Release `0.4.4` adds a
standard profile that turns benchmark-standard requirements into a checked
evidence matrix. Release `0.4.5` adds deterministic scoring compatibility
vectors so independent implementations can validate their score calculations
against the reference release. Release `0.4.6` adds a language-neutral scoring
specification for metric formulas, rounding, and calibration. Release `0.4.7`
hardens third-party evidence validation for bundles, reviews, and optional
result claims. Release `0.4.8` adds a checked standard change-control profile
and public standard-change intake path. Release `0.4.9` adds deterministic
baseline diagnostics, checked evaluator onboarding, and a completed example
review with an explicit non-adoption boundary. The next step toward a larger
public standard is real third-party submissions and independent review evidence.
