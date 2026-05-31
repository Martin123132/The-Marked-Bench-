# Release Notes v0.4.4

The Marked Bench v0.4.4 adds a benchmark standard profile: a checked,
machine-readable requirement matrix for release quality, comparability,
external adoption, and claim boundaries.

## Added

- `marked_bench.standard-profile.v1`, a standard profile descriptor for the
  release.
- `schemas/standard_profile.schema.json` for validating standard profiles.
- `standard/marked_bench_standard_profile_v0_4_4.json`, the checked current
  standard profile.
- CLI commands:
  - `marked-bench --export-standard-profile PATH`
  - `marked-bench --validate-standard-profile PATH`

## Validation

- Release conformance now checks the standard profile.
- The artifact validator checks the profile JSON, schema, referenced evidence
  paths, and validation commands.
- The adoption packet and implementation kit now reference the standard
  profile as part of the public release contract.

## Migration Notes

Use the standard profile when auditing whether a release is reproducible,
comparable, externally adoptable, and bounded against overclaiming. Existing
publication packets and result claims continue to validate unchanged after
regeneration against the v0.4.4 release ID.
