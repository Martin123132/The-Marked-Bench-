# Adoption

This directory stores the machine-readable adoption packet for the current
public benchmark release, plus the implementation kit for external CI users.
The benchmark standard profile lives under `standard/`.

The adoption packet is the compact handoff file for external users, mirrors,
reviewers, and announcement posts. It names the release manifest, conformance
report, default track, required artifacts, submission paths, result-card
requirements, result-claim requirements, implementation kit paths, and
validation commands.

Generate and validate the current packet with:

```bash
marked-bench --export-adoption-packet adoption/marked_bench_adoption_packet_v0_4_4.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_4.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_4.json
marked-bench --export-implementation-kit adoption/marked_bench_implementation_kit_v0_4_4.json
marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_4.json
marked-bench --export-standard-profile standard/marked_bench_standard_profile_v0_4_4.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_4.json
```

Do not edit adoption packets by hand; regenerate them after changing public
release, conformance, result-card, result-claim, implementation-kit, or
adoption documentation.
