# Announcement Package

This package gives external users the minimum public material needed to adopt,
cite, mirror, or submit results to The Marked Bench without relying on informal
instructions.

## Release Summary

The Marked Bench v0.3.9 is a reproducible contradiction-detection benchmark
release with versioned suites, pinned suite hashes, public JSON schemas,
baseline reports, leaderboard snapshots, release manifest hashing,
machine-readable conformance, checked external submission evidence, standard
result cards, and a machine-readable adoption packet.

Default track:

- Suite ID: `marked-bench-contradiction-multihop`
- Suite version: `0.3.0`
- Required comparison key: `suite_id`, `suite_version`, and `suite_hash`
- Result publication artifact: standard result card JSON

## Public Link Set

- Repository: `https://github.com/Martin123132/The-Marked-Bench-`
- Current release: `https://github.com/Martin123132/The-Marked-Bench-/releases/tag/v0.3.9`
- Registry: `benchmark_registry.json`
- Release manifest: `releases/marked_bench_release_v0_3_9.json`
- Conformance report: `conformance/marked_bench_conformance_v0_3_9.json`
- Adoption packet: `adoption/marked_bench_adoption_packet_v0_3_9.json`
- Technical note: `docs/TECHNICAL_NOTE.md`
- Adoption guide: `docs/ADOPTION_GUIDE.md`
- Submission review rubric: `docs/SUBMISSION_REVIEW_RUBRIC.md`

## Suggested Announcement Text

The Marked Bench v0.3.9 is now available as a public, reproducible benchmark
package for contradiction detection and classification. The release pins every
public track by suite ID, suite version, and deterministic suite hash, and it
ships validation commands for reports, submissions, result cards, release
manifests, conformance reports, and the adoption packet itself.

External systems can participate without importing the Python package: export a
JSONL prediction template, fill predicted labels, score it into a standard JSON
report, create a submission bundle, and publish a result card.

## Reproducibility Commands

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_3_9.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_3_9.json
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
```

## Citation Wording

When citing a result, include:

- The Marked Bench release tag.
- Suite ID, suite version, and suite hash.
- Report JSON path or digest.
- Result card JSON path or digest.
- Any submission bundle and review status used for leaderboard claims.

Use `CITATION.cff` for software citation metadata.

## Boundaries

The Marked Bench is a public benchmark package, not a broad safety
certification. Public results are comparable only when suite ID, suite version,
and suite hash match. Public suites can be overfit, so claims about broad model
reliability should be supported by additional private or third-party evidence.
