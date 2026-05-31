# Release Notes v0.3.10

The Marked Bench v0.3.10 adds a checked third-party evidence protocol for
recording external adoption without overstating it.

## Added

- Third-party evidence ledger:
  `adoption/third_party_evidence_ledger_v0_3_10.json`.
- Public schema for third-party evidence ledgers:
  `schemas/third_party_evidence_ledger.schema.json`.
- CLI support for evidence ledger export and validation:
  `--export-evidence-ledger` and `--validate-evidence-ledger`.
- Third-party evidence documentation:
  `docs/THIRD_PARTY_EVIDENCE.md`.
- GitHub issue template for external evidence intake:
  `.github/ISSUE_TEMPLATE/third_party_evidence.yml`.
- Conformance and artifact gates that keep the evidence ledger aligned with
  release, adoption, result-card, and registry evidence.

## Compatibility

No benchmark cases, labels, scoring weights, baseline reports, or suite hashes
changed in this release.

## Standardization Impact

This release makes adoption claims auditable. The checked ledger is valid even
when empty, which means the project can be public and ready for third-party
evidence without pretending external adoption has already happened.
