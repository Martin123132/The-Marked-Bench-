# Conformance Reports

This directory stores checked conformance reports for The Marked Bench release
package. A conformance report is a machine-readable audit that the registry,
release manifest, suite manifests, baseline reports, leaderboards, schemas,
prediction templates, checked submission packets, and result cards are
internally consistent.

Generate and validate the current report with:

```bash
marked-bench --export-conformance-report conformance/marked_bench_conformance_v0_3_8.json
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_3_8.json
```

Do not edit conformance reports by hand; regenerate them after changing any
public benchmark artifact.
