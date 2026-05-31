# Release Notes v0.4.8

The Marked Bench v0.4.8 adds checked standard change control for public
benchmark updates. The release keeps the v0.4.7 suites, cases, scoring
semantics, and third-party evidence checks intact while adding a
machine-readable way to propose and validate suite, schema, scoring,
evidence-policy, and governance changes.

## Added

- `marked_bench.benchmark_change_control` builds and validates the public
  change-control profile.
- `schemas/change_control.schema.json` defines the profile contract.
- `standard/marked_bench_change_control_v0_4_8.json` pins the release's checked
  change-control rules.
- `docs/CHANGE_CONTROL.md` documents the proposal and validation workflow.
- `.github/ISSUE_TEMPLATE/standard_change.yml` gives external users a structured
  way to propose standard changes.
- CLI support for `--export-change-control` and `--validate-change-control`.

## Updated

- The registry, conformance report, standard profile, adoption packet,
  implementation kit, release manifest, release checklist, announcement package,
  and benchmark documentation now include change-control evidence.
- The public artifact gate validates the checked change-control profile against
  its schema and referenced evidence paths.
- The adoption packet marks standard change control as a required public
  standard claim.

## Compatibility

This release does not change benchmark cases, suite hashes, labels, score
calculation, or leaderboard comparison rules from v0.4.7. Existing v0.4.7 result
evidence remains comparable under the same suite IDs, suite versions, and suite
hashes.

## Validation

```bash
python -m unittest discover -s tests
python scripts/validate_benchmark_artifacts.py
marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_8.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_8.json
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_8.json
```
