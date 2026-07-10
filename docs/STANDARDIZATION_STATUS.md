# Standardization Status

This repository is not just another benchmark bundle.  
Its goal is to behave as a **public standard for reproducible contradiction
benchmarking**.

We use a visible maturity model so teams can tell which level of claim is valid.

## Standard Levels

### Tier 0 - Public Baseline

- Public tracks are versioned and documented.
- All case IDs are stable within published suite versions.
- Report schemas, score formats, and baselines are available under `schemas/`,
  `suites/`, and `baselines/`.
- Release and conformance evidence can be validated by command, including
  `--validate-conformance-report`.

### Tier 1 - Standard Profile

- Tier 0 artifacts above, plus all profile artifacts:
  - Standard profile
  - Change-control profile
  - Scoring compatibility profile
  - Scoring specification
  - Adoption packet
  - Implementation kit
- All listed artifacts are versioned in the current release and pass their
  validators.
- Every public result claim and publication packet is schema-valid and
  verifiable from hashes in the checked artifacts.

### Tier 2 - External-Verified

- Tier 1 artifacts above, plus at least one verified third-party adoption entry.
- External parties provide public evidence through the third-party evidence issue
  intake and maintainers validate the referenced artifacts.
- Verification includes:
  - result card
  - submission bundle
  - review file (when claimed)
  - optional result claim for public short score statements
  - optional implementation-kit validation result
- The third-party evidence ledger must record only entries that can be externally
  inspected.

## What this means today

The current release is published as a **public benchmark-standard package** with
machine-readable evidence for Tier 1 requirements.
Tier 2 requires verified third-party entries and grows as more teams publish accepted
adoption submissions.

## How to claim official adoption

Use the existing evidence workflow:

1. Generate your packet through the normal CLI flow (report, submission bundle,
   result card, and optional review + result claim).
2. Validate all outputs with the corresponding `marked-bench --validate-*` command.
3. Open a third-party evidence intake issue using
   `.github/ISSUE_TEMPLATE/third_party_evidence.yml`.
4. Include public URLs and validation output so maintainers can verify the entry.
5. The ledger is updated only after review and artifact checks pass.

When your evidence is accepted, the ledger status becomes the public proof of
alignment with this standardization program.

## Fast checks for standard compliance

At minimum for standard status:

```bash
marked-bench --check-standard-status
marked-bench --check-standard-status --json
```

```bash
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_9.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_9.json
marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_9.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_9.json
marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_9.json
marked-bench --validate-adoption-packet adoption/marked_bench_adoption_packet_v0_4_9.json
marked-bench --validate-implementation-kit adoption/marked_bench_implementation_kit_v0_4_9.json
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_9.json
```

Keep this page updated as the release moves toward stronger Tier 2 verification.
