# Adoption

This directory stores the machine-readable adoption packet for the current
public benchmark release.

The adoption packet is the compact handoff file for external users, mirrors,
reviewers, and announcement posts. It names the release manifest, conformance
report, default track, required artifacts, submission paths, result-card
requirements, and validation commands.

Generate and validate the current packet with:

```bash
marked-bench --export-adoption-packet adoption/marked_bench_adoption_packet_v0_4_1.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_1.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_1.json
```

Do not edit adoption packets by hand; regenerate them after changing public
release, conformance, result-card, or adoption documentation.
