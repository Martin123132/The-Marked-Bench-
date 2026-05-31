# Conformance Reports

This directory stores checked conformance reports for The Marked Bench release
package. A conformance report is a machine-readable audit that the registry,
release manifest, suite manifests, baseline reports, leaderboards, schemas,
prediction templates, checked submission packets, result cards, publication
packets, result claims, adoption packets, evidence ledgers, implementation
kits, and scoring compatibility vectors are internally consistent.

Generate and validate the current report with:

```bash
marked-bench --export-conformance-report conformance/marked_bench_conformance_v0_4_5.json
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_5.json
```

Do not edit conformance reports by hand; regenerate them after changing any
public benchmark artifact.
