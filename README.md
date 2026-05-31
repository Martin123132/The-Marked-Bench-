# The Marked Bench

The Marked Bench is versioned benchmark infrastructure for testing whether AI
systems can detect and classify contradictions between a premise and a query.

The project is designed to become a reproducible public standard: every score
is tied to a suite ID, suite version, deterministic suite hash, immutable case
list, JSON report schema, confusion matrix, per-class metrics, confidence
calibration metrics, explanation-audit coverage, validation result, diagnostic
slice metrics, result card, result claim, standard profile, implementation
kit, scoring compatibility vectors, scoring specification, and leaderboard
entry.

## Current Tracks

| Track | Suite ID | Version | Purpose | Baseline |
| --- | --- | ---: | --- | ---: |
| Foundation | `marked-bench-contradiction-standard` | `0.1.0` | Compact canonical contradiction suite | `100.00` |
| Adversarial | `marked-bench-contradiction-adversarial` | `0.2.0` | Longer-context, implicit, and trap cases | `52.37` |
| Multi-hop | `marked-bench-contradiction-multihop` | `0.3.0` | Linked-evidence contradiction cases | `24.14` |
| Controls | `marked-bench-contradiction-controls` | `0.4.0` | False-positive distractor controls with contradiction anchors | `100.00` |

The adversarial track is intentionally not solved by the packaged symbolic
baseline. The multi-hop track is the default target for future symbolic,
neural, retrieval-augmented, and hybrid systems.
The controls track is a false-positive stress track for systems that over-call
contradictions on paraphrases, scoped negatives, time shifts, and harmless
elaborations.

## Install

```bash
pip install -e .
```

Requires Python 3.10 or newer.

## Run A Benchmark

Foundation track:

```bash
marked-bench --suite contradiction --report artifacts/foundation-report.json
```

Adversarial track:

```bash
marked-bench --suite contradiction-adversarial --report artifacts/adversarial-report.json
```

Multi-hop track:

```bash
marked-bench --suite contradiction-multihop --report artifacts/multihop-report.json
```

Control track:

```bash
marked-bench --suite contradiction-controls --report artifacts/controls-report.json
```

Validate a report before publication:

```bash
marked-bench --validate-report artifacts/adversarial-report.json
```

Export the machine-readable registry of public tracks and artifacts:

```bash
marked-bench --export-registry benchmark_registry.json
```

Export the release manifest that pins public artifact SHA-256 digests:

```bash
marked-bench --export-release-manifest releases/marked_bench_release_v0_4_7.json
```

Export the generated technical note:

```bash
marked-bench --export-technical-note docs/TECHNICAL_NOTE.md
```

Export and validate the machine-readable conformance report:

```bash
marked-bench --export-conformance-report conformance/marked_bench_conformance_v0_4_7.json
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_7.json
```

Export and validate the machine-readable benchmark standard profile:

```bash
marked-bench --export-standard-profile standard/marked_bench_standard_profile_v0_4_7.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_7.json
```

Export and validate deterministic scoring compatibility vectors:

```bash
marked-bench --export-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_7.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_7.json
```

Export and validate the language-neutral scoring specification:

```bash
marked-bench --export-scoring-spec standard/marked_bench_scoring_spec_v0_4_7.json
marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_7.json
marked-bench --export-scoring-spec-doc docs/SCORING_SPEC.md
```

Export and validate the machine-readable adoption packet for external users:

```bash
marked-bench --export-adoption-packet adoption/marked_bench_adoption_packet_v0_4_7.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_7.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_7.json
```

Export and validate the external implementation kit:

```bash
marked-bench --export-implementation-kit adoption/marked_bench_implementation_kit_v0_4_7.json
marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_7.json
```

## Score External Systems

Systems written in any language can submit predictions without importing this
package. Export a template, fill the `predicted` labels, and score it into a
full benchmark report:

```bash
marked-bench --suite contradiction-adversarial --export-prediction-template artifacts/predictions.jsonl
marked-bench --suite contradiction-adversarial --score-predictions artifacts/predictions.jsonl --system-name "my-system" --report artifacts/my-system-report.json
```

Prediction files may be JSONL or JSON. Each record needs `case_id` and
`predicted`; optional `detector_score`, `detector_note`, `rationale`, and
`evidence` fields are preserved in the final report. `detector_score` is
interpreted as binary contradiction confidence on `[0, 1]` for calibration
metrics. `rationale` and `evidence` feed the report's explanation audit so
reviewers can see whether a score is backed by inspectable reasoning evidence.

Create and validate leaderboard submission metadata:

```bash
marked-bench --create-submission artifacts/my-system-submission.json --submission-report artifacts/my-system-report.json --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-submission artifacts/my-system-submission.json
```

Create a standardized review rubric for a validated submission bundle:

```bash
marked-bench --create-submission-review artifacts/my-system-review.json --review-bundle artifacts/my-system-submission-bundle.json --reviewer reviewer-name
marked-bench --validate-submission-review artifacts/my-system-review.json
```

Create and validate a standard result card for publication or citation:

```bash
marked-bench --create-result-card artifacts/my-system-result-card.json --result-report artifacts/my-system-report.json --result-bundle artifacts/my-system-submission-bundle.json --result-review artifacts/my-system-review.json
marked-bench --validate-result-card artifacts/my-system-result-card.json
```

Create a self-contained public publication packet in one command:

```bash
marked-bench --create-publication-packet artifacts/my-system-publication-packet --publication-report artifacts/my-system-report.json --publication-predictions artifacts/predictions.jsonl --system-version "1.0.0" --submitter "name-or-org"
marked-bench --validate-publication-packet artifacts/my-system-publication-packet/publication_packet.json
```

Create a citeable result claim from that packet:

```bash
marked-bench --create-result-claim artifacts/my-system-publication-packet/result_claim.json --claim-publication-packet artifacts/my-system-publication-packet/publication_packet.json
marked-bench --validate-result-claim artifacts/my-system-publication-packet/result_claim.json
```

Create a complete external-submission example:

```bash
python -m marked_bench.examples.external_submission_demo
marked-bench --validate-submission-bundle artifacts/external_submission_demo/example_external_submission_bundle.json
marked-bench --validate-submission-review artifacts/external_submission_demo/example_external_submission_review.json
```

A checked copy of that workflow is committed under
`submissions/example_external_jsonl/` so adopters can inspect a full prediction,
report, submission, bundle, review, and result-card packet without generating
one first.
A checked one-command publication packet is committed under
`submissions/example_publication_packet/`.

## Build Leaderboards

Foundation leaderboard:

```bash
marked-bench --build-leaderboard baselines/always_none_v0_1_0.json baselines/contradiction_engine_v0_1_0.json --leaderboard-output leaderboard/leaderboard_v0_1_0.json
```

Adversarial leaderboard:

```bash
marked-bench --build-leaderboard baselines/always_none_adversarial_v0_2_0.json baselines/contradiction_engine_adversarial_v0_2_0.json --leaderboard-output leaderboard/leaderboard_adversarial_v0_2_0.json
```

Multi-hop leaderboard:

```bash
marked-bench --build-leaderboard baselines/always_none_multihop_v0_3_0.json baselines/contradiction_engine_multihop_v0_3_0.json --leaderboard-output leaderboard/leaderboard_multihop_v0_3_0.json
```

Controls leaderboard:

```bash
marked-bench --build-leaderboard baselines/always_none_controls_v0_4_0.json baselines/contradiction_engine_controls_v0_4_0.json --leaderboard-output leaderboard/leaderboard_controls_v0_4_0.json
```

## Checked-In Evidence

- Benchmark registry: `benchmark_registry.json`
- Release manifest: `releases/`
- Conformance report: `conformance/marked_bench_conformance_v0_4_7.json`
- Standard profile: `standard/marked_bench_standard_profile_v0_4_7.json`
- Scoring compatibility profile: `standard/marked_bench_scoring_compatibility_v0_4_7.json`
- Scoring specification: `standard/marked_bench_scoring_spec_v0_4_7.json`
- Scoring specification document: `docs/SCORING_SPEC.md`
- Adoption packet: `adoption/marked_bench_adoption_packet_v0_4_7.json`
- Third-party evidence ledger: `adoption/third_party_evidence_ledger_v0_4_7.json`
- Implementation kit: `adoption/marked_bench_implementation_kit_v0_4_7.json`
- Implementation kit templates: `adoption/implementation_kit/`
- Suite manifests and coverage profiles: `suites/`
- Baseline reports: `baselines/`
- Leaderboard snapshots: `leaderboard/`
- JSON schemas: `schemas/`
- Benchmark methodology: `docs/BENCHMARK_STANDARD.md`
- Benchmark card: `docs/BENCHMARK_CARD.md`
- Technical note: `docs/TECHNICAL_NOTE.md`
- Submission guide: `docs/SUBMISSION_GUIDE.md`
- Submission bundle schema: `schemas/submission_bundle.schema.json`
- Submission review schema: `schemas/submission_review.schema.json`
- Result card schema: `schemas/result_card.schema.json`
- Publication packet schema: `schemas/publication_packet.schema.json`
- Result claim schema: `schemas/result_claim.schema.json`
- Implementation kit schema: `schemas/implementation_kit.schema.json`
- Standard profile schema: `schemas/standard_profile.schema.json`
- Scoring compatibility schema: `schemas/scoring_compatibility.schema.json`
- Scoring specification schema: `schemas/scoring_spec.schema.json`
- Adoption packet schema: `schemas/adoption_packet.schema.json`
- Third-party evidence ledger schema: `schemas/third_party_evidence_ledger.schema.json`
- Checked external submission packet: `submissions/example_external_jsonl/`
- Checked publication packet: `submissions/example_publication_packet/`
- Adoption guide: `docs/ADOPTION_GUIDE.md`
- Announcement package: `docs/ANNOUNCEMENT_PACKAGE.md`
- Third-party evidence protocol: `docs/THIRD_PARTY_EVIDENCE.md`
- Submission review rubric: `docs/SUBMISSION_REVIEW_RUBRIC.md`
- Release notes: `docs/RELEASE_NOTES_v0_2_0.md`
- Current release notes: `docs/RELEASE_NOTES_v0_4_7.md`

## Quality Gates

Run these before publishing or submitting results:

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
```

The artifact validator checks that suite manifests match code, baseline reports
pass validation, the benchmark registry is current, and leaderboard snapshots
match their underlying reports. It also checks the release manifest against
the current public artifact hashes and checks public JSON artifacts against
their public schemas.
The checked external submission packet is also validated end-to-end so its
JSONL predictions, report, submission bundle, review file, and file hashes stay
consistent.
Checked result cards are validated against their referenced reports, bundles,
reviews, hashes, and standard publication claims.
Checked publication packets are validated against their copied reports,
submissions, bundles, reviews, result cards, and file hashes.
Checked result claims are validated against publication packets so public
score wording stays tied to exact hashes and explicit boundaries.
The conformance report provides one machine-readable pass/fail artifact for
the full release package.
The standard profile is validated so the benchmark's own standardization
requirements stay explicit, evidence-backed, and current.
The scoring compatibility profile is validated so independent implementations
can prove they produce the same scores from the same prediction vectors.
The scoring specification is validated so independent implementations have a
language-neutral contract for labels, metrics, rounding, and calibration.
The adoption packet is validated so external handoff, announcement, and
citation material stays pinned to the same release evidence.
The third-party evidence ledger is validated so adoption claims stay separate
from unverified interest or private anecdotes.
The implementation kit is validated so external CI templates, result-claim
snippets, and pinned release paths stay aligned with the current release.

## Package Layout

```text
marked_bench/
    benchmark_adoption.py         # Adoption packet export/validation
    benchmark_cli.py              # CLI runner
    benchmark_evidence.py         # Third-party evidence ledger validation
    benchmark_implementation.py   # External implementation kit validation
    benchmark_scoring_compatibility.py # Scoring compatibility vectors
    benchmark_scoring_spec.py     # Language-neutral scoring spec
    benchmark_standard_profile.py # Benchmark standard profile validation
    benchmark_leaderboard.py      # Validated leaderboard builder
    benchmark_publication.py      # One-command public result packets
    benchmark_claim.py            # Citeable result claim validation
    examples/
        external_submission_demo.py # End-to-end external JSONL workflow
    contradiction/
        benchmark_suite.py        # Versioned benchmark tracks
        engine.py                 # Symbolic baseline detector
```

This repository is intentionally benchmark-only. It does not include the wider
research utilities from the original toolkit.

## Contributing

Read `CONTRIBUTING.md` and `docs/SUBMISSION_GUIDE.md` before adding benchmark
cases, reports, or leaderboard entries. Existing public case IDs should not be
edited after publication; add new coverage through a new suite version or track.

## License

This repository currently uses The Marked Bench Non-Commercial License.
Commercial use requires a separate written license from the copyright holder.
