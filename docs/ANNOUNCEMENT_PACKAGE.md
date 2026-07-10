# Announcement Package

This package gives external users the minimum public material needed to adopt,
cite, mirror, or submit results to The Marked Bench without relying on informal
instructions.

## Release Summary

The Marked Bench v0.4.9 is a trust-hardening and onboarding patch release for
the reproducible contradiction-detection benchmark. It keeps every v0.4.8
suite, case, suite hash, score formula, and leaderboard comparison boundary
unchanged while adding a deterministic explanation of the multi-hop baseline
watchlist, a checked five-minute evaluator path, and a completed example review
with an explicit non-adoption boundary.

Default track:

- Suite ID: `marked-bench-contradiction-multihop`
- Suite version: `0.3.0`
- Required comparison key: `suite_id`, `suite_version`, and `suite_hash`
- Result publication artifact: standard result card JSON
- Public packet artifact: `marked_bench.publication-packet.v1`
- Citeable claim artifact: `marked_bench.result-claim.v1`
- Standard profile artifact: `marked_bench.standard-profile.v1`
- Change-control artifact: `marked_bench.change-control.v1`
- Scoring compatibility artifact: `marked_bench.scoring-compatibility.v1`
- Scoring specification artifact: `marked_bench.scoring-spec.v1`
- External implementation artifact: `marked_bench.implementation-kit.v1`

New controls track:

- Suite ID: `marked-bench-contradiction-controls`
- Suite version: `0.4.0`
- Purpose: false-positive stress testing with contradiction anchors

## Public Link Set

- Repository: `https://github.com/Martin123132/The-Marked-Bench-`
- Current release: `https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.9`
- Registry: `benchmark_registry.json`
- Release manifest: `releases/marked_bench_release_v0_4_9.json`
- Conformance report: `conformance/marked_bench_conformance_v0_4_9.json`
- Standard profile: `standard/marked_bench_standard_profile_v0_4_9.json`
- Change-control profile: `standard/marked_bench_change_control_v0_4_9.json`
- Scoring compatibility profile: `standard/marked_bench_scoring_compatibility_v0_4_9.json`
- Scoring specification: `standard/marked_bench_scoring_spec_v0_4_9.json`
- Scoring specification document: `docs/SCORING_SPEC.md`
- Adoption packet: `adoption/marked_bench_adoption_packet_v0_4_9.json`
- Third-party evidence ledger: `adoption/third_party_evidence_ledger_v0_4_9.json`
- Implementation kit: `adoption/marked_bench_implementation_kit_v0_4_9.json`
- Implementation kit templates: `adoption/implementation_kit/`
- Checked publication packet: `submissions/example_publication_packet/publication_packet.json`
- Checked result claim: `submissions/example_publication_packet/result_claim.json`
- Technical note: `docs/TECHNICAL_NOTE.md`
- Adoption guide: `docs/ADOPTION_GUIDE.md`
- Submission review rubric: `docs/SUBMISSION_REVIEW_RUBRIC.md`
- Third-party evidence protocol: `docs/THIRD_PARTY_EVIDENCE.md`
- Standard change-control protocol: `docs/CHANGE_CONTROL.md`
- Baseline robustness diagnostic: `docs/BASELINE_ROBUSTNESS.md`
- Five-minute evaluator walkthrough: `docs/FIVE_MINUTE_EVALUATOR_WALKTHROUGH.md`
- Checked submission proof: `docs/SUBMISSION_PROOF.md`

## Suggested Announcement Text

The Marked Bench v0.4.9 is now available as a public, reproducible benchmark
package for contradiction detection and classification. This patch release
adds reviewer-facing baseline diagnostics, a five-minute evaluator walkthrough,
and a complete checked publication example whose `needs_revision` decision
demonstrates that valid evidence does not imply leaderboard acceptance. The
third-party evidence ledger remains empty, so no external adoption is claimed.

External systems can participate without importing the Python package: export a
JSONL prediction template, fill predicted labels, score it into a standard JSON
report, create a submission bundle, publish a result card or publication
packet, generate a citeable result claim, and validate both in their own CI.

## Reproducibility Commands

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
python scripts/check_baseline_robustness.py --artifact docs/BASELINE_ROBUSTNESS.md
python scripts/check_evaluator_walkthrough.py
python scripts/check_submission_proof.py --artifact docs/SUBMISSION_PROOF.md
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_9.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_9.json
marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_9.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_9.json
marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_9.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_9.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_9.json
marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_9.json
marked-bench --validate-publication-packet submissions/example_publication_packet/publication_packet.json
marked-bench --validate-result-claim submissions/example_publication_packet/result_claim.json
```

## External Result Command Path

```bash
marked-bench --suite contradiction-multihop --export-prediction-template artifacts/multihop-predictions.jsonl
marked-bench --suite contradiction-multihop --score-predictions artifacts/multihop-predictions.jsonl --system-name "SYSTEM" --report artifacts/system-report.json
marked-bench --validate-report artifacts/system-report.json
marked-bench --create-submission artifacts/system-submission.json --submission-report artifacts/system-report.json --system-version "VERSION" --submitter "SUBMITTER"
marked-bench --create-submission-bundle artifacts/system-bundle.json --bundle-submission artifacts/system-submission.json --bundle-predictions artifacts/multihop-predictions.jsonl
marked-bench --create-result-card artifacts/system-result-card.json --result-report artifacts/system-report.json --result-bundle artifacts/system-bundle.json
marked-bench --validate-result-card artifacts/system-result-card.json
marked-bench --create-publication-packet artifacts/system-publication-packet --publication-report artifacts/system-report.json --publication-predictions artifacts/multihop-predictions.jsonl --system-version "VERSION" --submitter "SUBMITTER"
marked-bench --validate-publication-packet artifacts/system-publication-packet/publication_packet.json
marked-bench --create-result-claim artifacts/system-publication-packet/result_claim.json --claim-publication-packet artifacts/system-publication-packet/publication_packet.json
marked-bench --validate-result-claim artifacts/system-publication-packet/result_claim.json
```

## Citation Wording

When citing a result, include:

- The Marked Bench release tag.
- Suite ID, suite version, and suite hash.
- Report JSON path or digest.
- Result card JSON path or digest.
- Publication packet JSON path or digest when using the one-folder workflow.
- Result claim JSON path or digest when quoting a short public score claim.
- Any submission bundle and review status used for leaderboard claims.

Use `CITATION.cff` for software citation metadata.

## Boundaries

The Marked Bench is a public benchmark package, not a broad safety
certification. Public results are comparable only when suite ID, suite version,
and suite hash match. Public suites can be overfit, so claims about broad model
reliability should be supported by additional private or third-party evidence.
