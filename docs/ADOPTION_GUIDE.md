# Adoption Guide

This guide is for teams that want to use The Marked Bench as a reproducible
contradiction-detection benchmark.

## Pin The Evaluation

Every published result should pin:

- suite ID
- suite version
- suite hash
- report schema
- exact report JSON
- result card JSON
- result claim JSON for short public score statements
- standard profile version for benchmark-standard requirements
- implementation kit version when using the external CI workflow
- explanation-audit coverage, when rationale/evidence fields are submitted

The current default public track is `contradiction-multihop`:

```bash
marked-bench --suite contradiction-multihop --export-prediction-template predictions.jsonl
marked-bench --suite contradiction-multihop --score-predictions predictions.jsonl --system-name "your-system" --report your-system-report.json
marked-bench --validate-report your-system-report.json
```

Do not compare systems across different suite hashes.

## Submit A Result

1. Generate or score a full report.
2. Validate the report.
3. Generate submission metadata.
4. Build and validate a submission bundle.
5. Disclose model, prompting, preprocessing, retrieval, postprocessing,
   training data, and runtime details.
6. Include `rationale` and `evidence` in prediction records when the system can
   expose its decision basis.

```bash
marked-bench --create-submission your-submission.json --submission-report your-system-report.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission your-submission.json
marked-bench --create-submission-bundle your-submission-bundle.json --bundle-submission your-submission.json
marked-bench --validate-submission-bundle your-submission-bundle.json
marked-bench --create-result-card your-result-card.json --result-report your-system-report.json --result-bundle your-submission-bundle.json
marked-bench --validate-result-card your-result-card.json
```

If you want one public folder that contains the copied report, optional
predictions, submission metadata, bundle, review template, result card, and
hash manifest, use the publication packet command:

```bash
marked-bench --create-publication-packet your-publication-packet --publication-report your-system-report.json --publication-predictions predictions.jsonl --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-publication-packet your-publication-packet/publication_packet.json
```

Create a result claim when you need a short, citeable score statement. The
claim pins the exact wording to the publication packet hash and records what
the score does not prove:

```bash
marked-bench --create-result-claim your-publication-packet/result_claim.json --claim-publication-packet your-publication-packet/publication_packet.json
marked-bench --validate-result-claim your-publication-packet/result_claim.json
```

Leaderboard entries without a valid report, submission file, and submission
bundle should not be ranked.

Accepted leaderboard entries should also have a validated submission review
file using `docs/SUBMISSION_REVIEW_RUBRIC.md`.

For a complete local example that writes predictions, report, submission
metadata, bundle evidence, and a review template, run:

```bash
python -m marked_bench.examples.external_submission_demo
```

A checked example packet is committed under `submissions/example_external_jsonl/`.
Use it as the reference shape for external JSONL predictions, scored reports,
submission metadata, bundle evidence, review files, and result cards.
`submissions/example_publication_packet/` shows the one-command publication
packet shape and the checked result-claim shape.

## Use The Implementation Kit

External repositories can copy the workflow template from:

```text
adoption/implementation_kit/github_actions_validate_result.yml
```

Use it with this layout:

```text
marked-bench-result/
    publication_packet.json
    result_claim.json
```

The machine-readable kit descriptor is:

```bash
marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_8.json
```

## Check Release Conformance

Before adopting or mirroring a release package, validate the checked
conformance report:

```bash
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_8.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_8.json
marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_8.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_8.json
marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_8.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_8.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_8.json
marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_8.json
```

The conformance report is the single machine-readable pass/fail artifact for
registry, manifest, schema, leaderboard, baseline, prediction-template, and
checked-submission consistency.
The standard profile is the machine-readable requirement matrix for the
benchmark standard itself: it names the evidence files and validation commands
that make a release reproducible, comparable, externally adoptable, and
bounded.
The change-control profile is the machine-readable proposal and compatibility
process for suite, schema, scoring, evidence-policy, and governance changes.
The scoring compatibility profile provides deterministic prediction vectors
and expected score summaries for every public track so independent
implementations can check their scoring math.
The scoring specification defines the metric formulas, rounding, calibration,
and report semantics needed for independent scoring implementations.
The adoption packet is the machine-readable handoff file for external users:
it names the release, default track, public artifacts, validation commands,
submission channels, and citation requirements.
The third-party evidence ledger is the public record for verified external
adoption evidence. It can be valid while empty; that means no external evidence
has been accepted yet.
The implementation kit is the copy-ready contract for external CI checks,
result-claim snippets, and version-pinned installation commands.

Official adoption requests should also follow
[docs/STANDARDIZATION_STATUS.md](docs/STANDARDIZATION_STATUS.md), which defines
what claim level is justified for public score communication.

## Cite The Benchmark

Use `CITATION.cff` and include the release tag, suite ID, suite version, and
suite hash in papers, benchmark reports, or model cards.

## Maintain Compatibility

- Keep existing case IDs stable after release.
- Add new coverage through a new suite version or track.
- Regenerate suite manifests, reports, leaderboards, registry, technical note,
  change-control profile, and release manifest after public artifact changes.
- Run `python scripts/validate_benchmark_artifacts.py` before publishing.
