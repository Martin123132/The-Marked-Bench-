# Releases

This directory stores checked benchmark release manifests. A release manifest
pins public benchmark artifacts by path, byte count, and SHA-256 digest so a
published release can be audited or reproduced from the repository contents.

Generate the current manifest with:

```bash
marked-bench --export-release-manifest releases/marked_bench_release_v0_4_9.json
```

Do not edit release manifests by hand; regenerate them after changing public
schemas, suites, reports, leaderboards, benchmark source, tests, or governance
documents.
