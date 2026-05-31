# Release Notes v0.4.3

The Marked Bench v0.4.3 adds a third-party implementation kit for external
repositories that want to publish benchmark results with CI-checkable evidence.

## Added

- `marked_bench.implementation-kit.v1`, a machine-readable descriptor for
  external release adoption.
- `schemas/implementation_kit.schema.json` for validating the kit.
- `adoption/implementation_kit/github_actions_validate_result.yml`, a
  copy-ready GitHub Actions workflow for validating public result packets.
- `adoption/implementation_kit/result_claim_badge.md`, a short result-claim
  snippet template for README, model card, and release-note use.
- CLI commands:
  - `marked-bench --export-implementation-kit PATH`
  - `marked-bench --validate-implementation-kit PATH`

## Validation

- Release conformance now checks the implementation kit.
- The adoption packet now requires the implementation kit and its external CI
  workflow as public adoption artifacts.
- The artifact validator checks the kit JSON, schema, templates, and release
  paths.

## Migration Notes

External result publishers should keep using publication packets and result
claims. Repositories that publish those artifacts can now copy the workflow from
`adoption/implementation_kit/github_actions_validate_result.yml` and store
evidence under `marked-bench-result/`.
