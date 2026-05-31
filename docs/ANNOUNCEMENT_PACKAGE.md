# Announcement Package

This package gives external users the minimum public material needed to adopt,
cite, mirror, or submit results to The Marked Bench without relying on informal
instructions.

## Release Summary

The Marked Bench v0.4.2 is a reproducible contradiction-detection benchmark
release with versioned suites, pinned suite hashes, public JSON schemas,
baseline reports, leaderboard snapshots, release manifest hashing,
machine-readable conformance, checked external submission evidence, standard
result cards, a machine-readable adoption packet, and a checked third-party
evidence ledger. This release adds citeable result claims for hash-pinned score
wording and explicit overclaim boundaries.

Default track:

- Suite ID: `marked-bench-contradiction-multihop`
- Suite version: `0.3.0`
- Required comparison key: `suite_id`, `suite_version`, and `suite_hash`
- Result publication artifact: standard result card JSON
- Public packet artifact: `marked_bench.publication-packet.v1`
- Citeable claim artifact: `marked_bench.result-claim.v1`

New controls track:

- Suite ID: `marked-bench-contradiction-controls`
- Suite version: `0.4.0`
- Purpose: false-positive stress testing with contradiction anchors

## Public Link Set

- Repository: `https://github.com/Martin123132/The-Marked-Bench-`
- Current release: `https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.4.2`
- Registry: `benchmark_registry.json`
- Release manifest: `releases/marked_bench_release_v0_4_2.json`
- Conformance report: `conformance/marked_bench_conformance_v0_4_2.json`
- Adoption packet: `adoption/marked_bench_adoption_packet_v0_4_2.json`
- Third-party evidence ledger: `adoption/third_party_evidence_ledger_v0_4_2.json`
- Checked publication packet: `submissions/example_publication_packet/publication_packet.json`
- Checked result claim: `submissions/example_publication_packet/result_claim.json`
- Technical note: `docs/TECHNICAL_NOTE.md`
- Adoption guide: `docs/ADOPTION_GUIDE.md`
- Submission review rubric: `docs/SUBMISSION_REVIEW_RUBRIC.md`
- Third-party evidence protocol: `docs/THIRD_PARTY_EVIDENCE.md`

## Suggested Announcement Text

The Marked Bench v0.4.2 is now available as a public, reproducible benchmark
package for contradiction detection and classification. The release pins every
public track by suite ID, suite version, and deterministic suite hash, and it
ships validation commands for reports, submissions, result cards, publication
packets, result claims, release manifests, conformance reports, the adoption
packet, and the third-party evidence ledger. The new result claim command
creates exact score wording tied to the publication packet hash and states what
the score does not prove.

External systems can participate without importing the Python package: export a
JSONL prediction template, fill predicted labels, score it into a standard JSON
report, create a submission bundle, publish a result card or publication
packet, and generate a citeable result claim.

## Reproducibility Commands

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_2.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_2.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_2.json
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
