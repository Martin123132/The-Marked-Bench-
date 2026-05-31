# Standard Profiles

This directory stores the checked benchmark standard profile, change-control
profile, scoring compatibility profile, and language-neutral scoring
specification for the current release.

The standard profile is a machine-readable requirement matrix. It lists the
evidence files and validation commands that make a release reproducible,
comparable, externally adoptable, and bounded against overclaiming.
The change-control profile defines the public proposal and validation rules for
suite, schema, scoring, evidence-policy, and governance changes.
The scoring compatibility profile provides deterministic prediction vectors
and expected score summaries for independent scorer implementations.
The scoring specification defines the labels, metric formulas, rounding, and
calibration semantics those implementations must match.

Generate and validate the current profile with:

```bash
marked-bench --export-standard-profile standard/marked_bench_standard_profile_v0_4_8.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_8.json
marked-bench --export-change-control standard/marked_bench_change_control_v0_4_8.json
marked-bench --validate-change-control standard/marked_bench_change_control_v0_4_8.json
marked-bench --export-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_8.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_8.json
marked-bench --export-scoring-spec standard/marked_bench_scoring_spec_v0_4_8.json
marked-bench --validate-scoring-spec standard/marked_bench_scoring_spec_v0_4_8.json
marked-bench --export-scoring-spec-doc docs/SCORING_SPEC.md
```

Do not edit standard profiles by hand; regenerate them after changing release
paths, schemas, validation commands, governance documents, change-control rules,
scoring semantics, public tracks, or external result requirements.
