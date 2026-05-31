# Release Notes v0.2.0

The Marked Bench v0.2.0 is the first benchmark-only public release.

## Public Tracks

| Track | Suite ID | Version | Cases | Purpose |
| --- | --- | ---: | ---: | --- |
| Foundation | `marked-bench-contradiction-standard` | `0.1.0` | 17 | Compact canonical contradiction suite. |
| Adversarial | `marked-bench-contradiction-adversarial` | `0.2.0` | 17 | Longer-context, implicit, and trap contradiction cases. |

## Included Evidence

- Versioned suite manifests with deterministic suite hashes.
- Validated baseline reports for `ContradictionEngine` and `AlwaysNoneDetector`.
- Foundation and adversarial leaderboard snapshots.
- JSON schemas for reports, predictions, suite manifests, registry,
  leaderboard files, submissions, and release manifests.
- Generated technical note summarizing suite composition and baseline evidence.
- Release manifest pinning public artifacts by canonical SHA-256 digest.

## Baseline Summary

| Track | Best Baseline | Overall Score |
| --- | --- | ---: |
| Foundation | `ContradictionEngine` | 100.00 |
| Adversarial | `ContradictionEngine` | 52.37 |

The adversarial track is intentionally not solved by the packaged symbolic
baseline. It is the recommended default track for comparing future systems.

## Migration Notes

- The benchmark-only repository uses the `marked_bench` Python package and the
  `marked-bench` command.
- Earlier broad toolkit files are not part of this repository.
- Public comparisons should use `suite_id`, `suite_version`, and `suite_hash`;
  package names and command names are not sufficient evidence.
