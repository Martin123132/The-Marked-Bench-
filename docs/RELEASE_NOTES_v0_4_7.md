# Release Notes v0.4.7

The Marked Bench v0.4.7 hardens the third-party evidence gate for external
adoption claims.

## Added

- Evidence-ledger requirements now state that submission-bundle hashes and
  review hashes are part of the public evidence contract.
- Evidence-ledger validation now loads and validates referenced submission
  bundles and submission reviews, not only result cards and result claims.
- Evidence-ledger validation now rejects unsafe relative paths, missing bundle
  evidence, bad bundle or review hashes, mismatched suite/system metadata, and
  adoption claims that are not backed by verified accepted review evidence.
- Submission-review schema coverage now includes the false-positive controls
  track.

## Updated

- Current release paths move from v0.4.6 to v0.4.7.
- The benchmark registry, standard profile, adoption packet, implementation
  kit, conformance report, release manifest, announcement package, and
  third-party evidence documentation now point at v0.4.7 artifacts.
- The checked empty evidence ledger remains valid, but future non-empty
  entries must provide stronger machine-checkable evidence.

## Compatibility

Suite contents, case IDs, scoring formulas, scoring compatibility vectors, and
the language-neutral scoring specification are unchanged from v0.4.6. This
release strengthens the public evidence validator around external adoption.

## Validation

```bash
marked-bench --validate-evidence-ledger adoption/third_party_evidence_ledger_v0_4_7.json
marked-bench --validate-conformance-report conformance/marked_bench_conformance_v0_4_7.json
python scripts/validate_benchmark_artifacts.py
```
