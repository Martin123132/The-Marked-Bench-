# Release Notes v0.3.0

The Marked Bench v0.3.0 adds the first multi-hop contradiction track and makes
it the default public target for new submissions.

## Public Tracks

| Track | Suite ID | Version | Cases | Purpose |
| --- | --- | ---: | ---: | --- |
| Foundation | `marked-bench-contradiction-standard` | `0.1.0` | 17 | Compact canonical contradiction suite. |
| Adversarial | `marked-bench-contradiction-adversarial` | `0.2.0` | 17 | Longer-context, implicit, and trap contradiction cases. |
| Multi-hop | `marked-bench-contradiction-multihop` | `0.3.0` | 18 | Linked-evidence contradiction cases requiring entity, policy, definition, numeric, universal, or temporal chaining. |

## What Changed

- Added `contradiction-multihop`, a public track for linked-evidence reasoning.
- Added multi-hop suite manifests, baselines, and leaderboard snapshots.
- Updated the machine-readable registry so `contradiction-multihop` is the
  default track.
- Updated release evidence and adoption guidance for v0.3.0.

## Included Evidence

- Versioned suite manifests with deterministic suite hashes.
- Validated baseline reports for `ContradictionEngine` and `AlwaysNoneDetector`.
- Foundation, adversarial, and multi-hop leaderboard snapshots.
- JSON schemas for reports, predictions, suite manifests, registry,
  leaderboard files, submissions, and release manifests.
- Generated technical note summarizing suite composition and baseline evidence.
- Release manifest pinning public artifacts by canonical SHA-256 digest.

## Baseline Summary

| Track | Best Baseline | Overall Score |
| --- | --- | ---: |
| Foundation | `ContradictionEngine` | 100.00 |
| Adversarial | `ContradictionEngine` | 52.37 |
| Multi-hop | `ContradictionEngine` | 24.14 |

The multi-hop track is intentionally compact but designed to expose failures in
systems that classify a premise/query pair without linking the intermediate
facts. It is the recommended default track for future comparisons.

## Migration Notes

- Use `marked-bench --suite contradiction-multihop` for the default public
  comparison target.
- Existing v0.1.0 and v0.2.0 reports remain comparable only within their own
  suite ID, version, and hash.
- Public comparisons should include `suite_id`, `suite_version`, `suite_hash`,
  report SHA-256 digest, and the release tag.
