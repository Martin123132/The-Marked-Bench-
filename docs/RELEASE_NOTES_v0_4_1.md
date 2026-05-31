# Release Notes v0.4.1

The Marked Bench v0.4.1 adds a one-command public publication packet workflow
for external benchmark results.

## Added

- New `marked_bench.publication-packet.v1` schema in
  `schemas/publication_packet.schema.json`.
- New CLI workflow:
  `marked-bench --create-publication-packet PACKET_DIR --publication-report REPORT --system-version VERSION --submitter SUBMITTER`.
- New validator:
  `marked-bench --validate-publication-packet PACKET_DIR/publication_packet.json`.
- New checked example packet under `submissions/example_publication_packet/`
  containing the copied report, optional predictions, submission metadata,
  review bundle, review rubric, result card, packet manifest, and file hashes.

## Changed

- Release, conformance, adoption, evidence, registry, and technical-note
  artifacts now advertise the publication packet workflow.
- Artifact validation now checks the committed publication packet end to end.

## Compatibility

- Existing suite IDs, case IDs, suite versions, and suite hashes are unchanged.
- The v0.4.0 false-positive controls track remains the current controls track.
