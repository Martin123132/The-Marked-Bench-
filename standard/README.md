# Standard Profile

This directory stores the checked benchmark standard profile for the current
release.

The standard profile is a machine-readable requirement matrix. It lists the
evidence files and validation commands that make a release reproducible,
comparable, externally adoptable, and bounded against overclaiming.

Generate and validate the current profile with:

```bash
marked-bench --export-standard-profile standard/marked_bench_standard_profile_v0_4_4.json
marked-bench --validate-standard-profile standard/marked_bench_standard_profile_v0_4_4.json
```

Do not edit standard profiles by hand; regenerate them after changing release
paths, schemas, validation commands, governance documents, or external result
requirements.
