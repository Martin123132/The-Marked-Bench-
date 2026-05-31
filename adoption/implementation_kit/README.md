# Third-Party Implementation Kit

This kit is for teams that want to publish a Marked Bench result from their own
repository while keeping the score, evidence files, and citation wording
machine-checkable.

## Files

- `github_actions_validate_result.yml`: copy this into an external repository
  as `.github/workflows/marked-bench-result.yml`.
- `result_claim_badge.md`: copy the snippet into a README, model card, or
  release note after replacing the placeholders.
- `adoption/marked_bench_implementation_kit_v0_4_4.json`: machine-readable
  descriptor for this kit.

## Expected External Layout

```text
marked-bench-result/
    publication_packet.json
    result_claim.json
```

The publication packet should be created with:

```bash
marked-bench --create-publication-packet marked-bench-result --publication-report REPORT --publication-predictions PREDICTIONS --system-version VERSION --submitter SUBMITTER
```

The result claim should be created with:

```bash
marked-bench --create-result-claim marked-bench-result/result_claim.json --claim-publication-packet marked-bench-result/publication_packet.json
```

## CI Contract

External CI should install the exact release tag and validate both public
artifacts:

```bash
python -m pip install git+https://github.com/Martin123132/The-Marked-Bench-.git@v0.4.4
marked-bench --validate-publication-packet marked-bench-result/publication_packet.json
marked-bench --validate-result-claim marked-bench-result/result_claim.json
```

The score should only be compared with other results that use the same
`suite_id`, `suite_version`, and `suite_hash`.
