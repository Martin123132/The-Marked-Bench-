# Third-Party Evidence

The Marked Bench should not claim external adoption until there is public,
inspectable evidence. This document defines what counts as third-party evidence
and how it is recorded.

## Evidence Ledger

The checked ledger is:

```text
adoption/third_party_evidence_ledger_v0_3_10.json
```

The current ledger may be empty. An empty ledger is valid and means no external
adoption evidence has been accepted for the release yet.

Validate it with:

```bash
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_3_10.json
```

## What Counts

A third-party evidence entry should include:

- A public result card.
- A submission bundle with report hash evidence.
- The suite ID, suite version, and suite hash.
- Submitter, system name, and system version.
- A public URL or committed repository path where the evidence can be
  inspected.
- Review evidence before `verification_status` can be `verified`.

An entry may be `pending`, `verified`, or `rejected`. It must not set
`adoption_claim` to `true` until the evidence is verified.

## Intake

External teams can open a third-party evidence issue with:

```text
.github/ISSUE_TEMPLATE/third_party_evidence.yml
```

Maintainers should only add ledger entries after checking the linked result
card and bundle. If the evidence is accepted for leaderboard claims, add or
link the review file and set `verification_status` to `verified`.

## Boundary

The ledger is an evidence record, not a marketing counter. It should stay
boringly honest: no inferred adoption, no private claims, and no entries that
cannot be inspected by someone outside the project.
