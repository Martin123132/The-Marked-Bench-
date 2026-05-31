# Standard Profiles

This directory stores the checked benchmark standard profile and scoring
compatibility profile for the current release.

The standard profile is a machine-readable requirement matrix. It lists the
evidence files and validation commands that make a release reproducible,
comparable, externally adoptable, and bounded against overclaiming.
The scoring compatibility profile provides deterministic prediction vectors
and expected score summaries for independent scorer implementations.

Generate and validate the current profile with:

```bash
marked-bench --export-standard-profile standard/marked_bench_standard_profile_v0_4_5.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_5.json
marked-bench --export-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_5.json
marked-bench --validate-scoring-compatibility standard/marked_bench_scoring_compatibility_v0_4_5.json
```

Do not edit standard profiles by hand; regenerate them after changing release
paths, schemas, validation commands, governance documents, scoring semantics,
public tracks, or external result requirements.
