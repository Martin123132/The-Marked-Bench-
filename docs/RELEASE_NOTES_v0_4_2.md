# Release Notes v0.4.2

The Marked Bench v0.4.2 adds machine-checkable result claims for citeable
benchmark score statements.

## Added

- New `marked_bench.result-claim.v1` schema in
  `schemas/result_claim.schema.json`.
- New CLI workflow:
  `marked-bench --create-result-claim CLAIM --claim-publication-packet PACKET`.
- New validator:
  `marked-bench --validate-result-claim CLAIM`.
- New checked example claim at
  `submissions/example_publication_packet/result_claim.json`.

## Changed

- Conformance and artifact validation now check the committed result claim.
- Adoption and third-party evidence materials now distinguish result cards,
  publication packets, result claims, and verified adoption evidence.
- The technical note and registry now advertise result-claim commands and
  schemas.

## Compatibility

- Existing suite IDs, case IDs, suite versions, and suite hashes are unchanged.
- The result claim is an evidence wrapper around a publication packet; it does
  not change scoring.
