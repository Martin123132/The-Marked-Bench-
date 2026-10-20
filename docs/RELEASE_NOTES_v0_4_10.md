# Release Notes: v0.4.10

This patch release hardens submission handling and adds cross-platform,
installed-package checks. Published suites, case IDs, suite hashes, and scoring
semantics are unchanged. The existing noncommercial and commercial licensing
terms, including the company contact, are unchanged.

## Submission Boundary

- Reject parent traversal and outside absolute paths before bundle creation
  reads submissions or predictions.
- Reject outside report references in nested submission metadata before loading
  reports during bundle creation or validation.
- Resolve filesystem links before checking containment; test Windows junctions
  and POSIX directory symlinks.
- Check manifest file paths before opening or hashing their contents.
- Preserve absolute paths that resolve inside the bundle root for CLI
  compatibility; generated manifests still use portable relative paths.

Standalone report/submission APIs intentionally allow explicitly selected
files. Bundle containment applies to the bundle workflow, not a general
filesystem sandbox. Validate untrusted bundles in a stable, isolated directory;
concurrent hostile filesystem mutation is not covered by these checks.

## Validation Hardening

- Distinguish JSON booleans from numbers in constant and enum validation.
- Enforce array bounds and prefix schemas used by the scoring contract.
- Reject non-finite numbers and report unknown suites as validation failures.
- Normalize generated text newlines for Windows/POSIX reproducibility.

## Cross-Platform Installation

CI covers Windows and Ubuntu on Python 3.10, 3.11, 3.12, 3.13, and 3.14.
Each job runs the full suite and release gates, builds a wheel from a temporary
source copy, installs it in a fresh virtual environment, and exercises the
console entry point outside the checkout. The installed run checks the pinned
suite hash, checked-example score, report validation, and prediction export.

Run locally with:

```bash
python -m unittest discover -s tests
python scripts/check_installed_package.py
python scripts/validate_benchmark_artifacts.py
python scripts/regenerate_release_artifacts.py --check
```

The wheel check needs package-index access for build/runtime dependencies.
It does not invoke a model or provider.

## Claims And Remaining Targets

Automated installation checks are not independent third-party adoption.
The next target requires a real external evaluator, their own predictions,
recorded environment and suite identity, and an honest submission review.
The multi-hop baseline watchlist remains open. Forge Bridge scope preservation
remains a separate pilot, not a benchmark result.
