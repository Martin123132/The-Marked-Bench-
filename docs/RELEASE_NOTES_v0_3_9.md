# Release Notes v0.3.9

The Marked Bench v0.3.9 adds a checked external adoption and announcement
package for public benchmark uptake.

## Added

- Machine-readable adoption packet:
  `adoption/marked_bench_adoption_packet_v0_3_9.json`.
- Public schema for adoption packets:
  `schemas/adoption_packet.schema.json`.
- CLI support for adoption packet export and validation:
  `--export-adoption-packet` and `--validate-adoption-packet`.
- Announcement package with release links, citation wording, reproducibility
  commands, and external result workflow:
  `docs/ANNOUNCEMENT_PACKAGE.md`.
- Artifact and conformance checks that keep the adoption packet aligned with
  the current release evidence.

## Compatibility

No suite cases, suite versions, labels, scoring weights, or baseline reports
changed in this release. Existing v0.3.8 result cards remain comparable when
they pin the same suite ID, suite version, and suite hash.

## Standardization Impact

This release makes external adoption more concrete: users can now validate not
only benchmark reports and result cards, but also the public handoff packet that
names the canonical release, artifacts, submission channels, validation gates,
and citation requirements.
