# Checked Submission Proof

Overall status: **PASS**

## Proof boundary

This is an internally maintained, external-style example that proves the public submission machinery.
It is not an independent third-party result and it is not evidence of external adoption.
The evidence ledger remains `awaiting-third-party-evidence` with 0 entries.

## Pinned result identity

| Field | Value |
| --- | --- |
| System | `ExampleExternalJsonl` `demo-1.0` |
| Submitter | `The Marked Bench Examples` |
| Suite | `marked-bench-contradiction-multihop` v0.3.0 |
| Suite hash | `07a2bb9c0e8356d1cdab98b5b1b35a3c8bd29beff695816dfb151dbb5f6d0d1f` |
| Cases | 18 |
| Overall score | 11.11 |

## Completed reviewer decision

Reviewer `example-reviewer` recorded `needs_revision` with a 8/12 rubric and `needs_revision` recommendation.
The decision is intentionally not `accept`: the packet and score reproduce, but the placeholder all-none system does not provide substantive model disclosure, case-specific reasoning, or a complete failure-mode analysis.

| Rubric dimension | Score | Reviewer note |
| --- | ---: | --- |
| Reproducibility | 2/2 | Bundle, report, predictions, hashes, suite identity, and validation commands reproduce deterministically. |
| Disclosure Quality | 1/2 | All disclosure fields are populated, but they describe a placeholder no-model system rather than a substantive implementation. |
| Score Integrity | 2/2 | The 11.11 score reproduces from the checked all-none predictions with no unexplained metric mismatch. |
| Explanation Coverage | 1/2 | Rationale and evidence fields cover every case, but the rationale is identical rather than case-specific. |
| Evidence Quality | 1/2 | Evidence quotes are present, but the generic all-none rationale does not connect that evidence to each prediction. |
| Limitations | 1/2 | The packet identifies itself as an example, but it does not provide a substantive failure-mode analysis. |

## Validated artifact chain

| Role | Path | Schema or format | Validation | SHA-256 |
| --- | --- | --- | --- | --- |
| predictions | `submissions/example_publication_packet/predictions.jsonl` | `JSONL prediction records` | PASS | `e6ccdf33f7104b261ac52005881786cdbb25496a695410724e3a7001328261ce` |
| report | `submissions/example_publication_packet/report.json` | `marked_bench.contradiction-benchmark-report.v2` | PASS | `9028699a80c286fb644d9a7212209d452c5e5e0cbc8303c06599fb4950017c83` |
| submission | `submissions/example_publication_packet/submission.json` | `marked_bench.leaderboard-submission.v1` | PASS | `16dcd97f63498051f2aa7cecdb2362379b8f8e9cce5f6bf5d754f54d42780b4f` |
| submission bundle | `submissions/example_publication_packet/submission_bundle.json` | `marked_bench.leaderboard-submission-bundle.v1` | PASS | `ad4e2ff41796e55d2577fd6d056cae589e952c2d023ac1422186af146a72162a` |
| submission review | `submissions/example_publication_packet/submission_review.json` | `marked_bench.submission-review.v1` | PASS | `ecbe2aa60d0f00d428b04046900379f35fe8fecf49cfc57f39f67986c539a3d7` |
| result card | `submissions/example_publication_packet/result_card.json` | `marked_bench.result-card.v1` | PASS | `e726577943559f5fcbef4eae2b1124664651af556f8e7fcb57e1413cfe4cd67c` |
| publication packet | `submissions/example_publication_packet/publication_packet.json` | `marked_bench.publication-packet.v1` | PASS | `51863e64a69b5fbe6346c7cb54c818854bd62e2db6de099181ebe8666f635624` |
| result claim | `submissions/example_publication_packet/result_claim.json` | `marked_bench.result-claim.v1` | PASS | `6b4c207d20709c6c781f32cc4aa0b6dc73ce4acd4d58f7d83a2ca6569562cf9e` |

## Publication outcome

- Result-card accepted for leaderboard: `false`.
- Reviewer decision complete: `true`.
- Self-contained packet validates for publication: `true`.
- Bounded result claim validates for citation: `true`.
- Third-party adoption evidence: `false`; that requires a separate verified evidence-ledger entry.

A valid publication packet can document a weak or rejected system result. Publication readiness means the evidence is complete and internally consistent; it does not imply leaderboard acceptance or model quality.

## Reproduce the proof

```bash
marked-bench --validate-report submissions/example_publication_packet/report.json
marked-bench --validate-submission submissions/example_publication_packet/submission.json
marked-bench --validate-submission-bundle submissions/example_publication_packet/submission_bundle.json
marked-bench --validate-submission-review submissions/example_publication_packet/submission_review.json
marked-bench --validate-result-card submissions/example_publication_packet/result_card.json
marked-bench --validate-publication-packet submissions/example_publication_packet/publication_packet.json
marked-bench --validate-result-claim submissions/example_publication_packet/result_claim.json
python scripts/check_submission_proof.py --artifact docs/SUBMISSION_PROOF.md
```

## Limitations

- The example is produced and reviewed by the project, not by an independent evaluator.
- Its all-none predictions intentionally demonstrate a valid but weak result.
- The proof confirms schemas, hashes, identity, review state, and claim boundaries; it does not establish adoption.
