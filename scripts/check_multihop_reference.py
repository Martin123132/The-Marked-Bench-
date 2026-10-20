from __future__ import annotations

"""Reproduce the reference and text-only invariance evidence without a model."""

import argparse
from dataclasses import replace
import json
from pathlib import Path
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from marked_bench.benchmark_leaderboard import build_leaderboard
from marked_bench.contradiction.benchmark_suite import build_multihop_suite, validate_benchmark_report
from marked_bench.contradiction.multihop_reference import MultiHopReference, build_reference_report, sentences


REPORT = Path("baselines/multihop_reference_v0_3_0.json")
DOCUMENT = Path("docs/MULTIHOP_REFERENCE.md")
LEADERBOARD = Path("leaderboard/leaderboard_multihop_v0_3_0.json")
REPORTS = (
    Path("baselines/always_none_multihop_v0_3_0.json"),
    Path("baselines/hash_prior_multihop_v0_3_0.json"),
    Path("baselines/contradiction_engine_multihop_v0_3_0.json"),
    REPORT,
)


def _label(reference, claim):
    result = reference.explain(claim)
    return result.type.value if result else "none"


def _renamed(claim):
    reserved = set("A All An API Approval Context Crate Dataset Every Experiment Fleet Key Model Most Policy Quorum Record Release Request Service System The Vault".split())
    names = sorted(set(re.findall(r"\b[A-Z][A-Za-z0-9-]*\b", claim.premise + " " + claim.query)) - reserved)
    mapping = {name: f"Entity{index}" for index, name in enumerate(names)}
    if not names:
        return claim
    pattern = re.compile(r"\b(?:" + "|".join(re.escape(name) for name in sorted(names, key=len, reverse=True)) + r")\b")
    return replace(claim, premise=pattern.sub(lambda m: mapping[m[0]], claim.premise), query=pattern.sub(lambda m: mapping[m[0]], claim.query))


def audit_reference() -> dict:
    reference = MultiHopReference()
    cases = build_multihop_suite()
    expected = {}
    invariance_checks = 0
    ablation_checks = 0
    for index, case in enumerate(cases):
        claim = case.to_claim()
        prediction = _label(reference, claim)
        expected[case.id] = prediction
        variants = (
            replace(claim, id=f"opaque-{index}", domain="unrelated", metadata={"expected": "wrong", "tags": ["misleading"]}),
            replace(claim, premise=". ".join(reversed(sentences(claim.premise))) + "."),
            _renamed(claim),
            replace(claim, premise=claim.premise + " Parcel Decoy belongs to bin Spare. Bin Spare has mass 99 kg."),
        )
        for variant in variants:
            if _label(reference, variant) != prediction:
                raise ValueError(f"Reference decision changed under a meaning-preserving variant: {case.id}")
            invariance_checks += 1
        if prediction != "none":
            parts = sentences(claim.premise)
            for missing in range(len(parts)):
                reduced = replace(claim, premise=". ".join(parts[:missing] + parts[missing + 1:]))
                if _label(reference, reduced) != "none":
                    raise ValueError(f"Proof survived removal of a required source fact: {case.id}")
                ablation_checks += 1
    for case in reversed(cases):
        if _label(reference, case.to_claim()) != expected[case.id]:
            raise ValueError("Reference decisions depend on batch order")
        invariance_checks += 1
    return {"invariance_checks": invariance_checks, "required_fact_ablations": ablation_checks}


def build_evidence(root: Path = ROOT) -> tuple[dict, str]:
    report = build_reference_report()
    validation = validate_benchmark_report(report)
    if not validation["valid"]:
        raise ValueError(f"Reference report is invalid: {validation['errors']}")
    audit = audit_reference()
    rows = report["case_results"]
    true_positive = sum(row["expected"] != "none" and row["predicted"] != "none" for row in rows)
    false_positive = sum(row["expected"] == "none" and row["predicted"] != "none" for row in rows)
    correct = sum(row["type_correct"] for row in rows)
    legacy = json.loads((root / REPORTS[2]).read_text(encoding="utf-8-sig"))
    prior = json.loads((root / REPORTS[1]).read_text(encoding="utf-8-sig"))
    if true_positive < 6 or false_positive or report["overall_score"] <= max(legacy["overall_score"], prior["overall_score"]):
        raise ValueError("Reference failed the declared breadth, control or low-information comparison gate")
    lines = [
        "# Multi-Hop Symbolic Reference", "",
        "This is a bounded, development-suite-aware reference, not a general English reasoner,",
        "a blind evaluation, independent adoption, or evidence of model superiority.", "",
        "Available on repository main after v0.4.10. The published v0.4.10 tag remains unchanged.", "",
        "## Reproduced results", "",
        f"- Frozen suite: `{report['suite_id']}` v{report['suite_version']} ({report['case_count']} cases).",
        f"- Suite hash: `{report['suite_hash']}`.",
        f"- MultiHopReference score: **{report['overall_score']:.2f}**; exact labels: **{correct}/18**.",
        f"- Contradictions detected: **{true_positive}/10**; false positives on controls: **{false_positive}/8**.",
        f"- Unchanged legacy engine: **{legacy['overall_score']:.2f}**; unchanged hash-prior: **{prior['overall_score']:.2f}**.",
        f"- Meaning-preserving checks passed: **{audit['invariance_checks']}**.",
        f"- Required-source-fact removal checks passed: **{audit['required_fact_ablations']}**.", "",
        "## What the reference does", "",
        "It parses a small documented vocabulary into directed membership/inheritance links and typed facts.",
        "A breadth-first closure carries properties and class rules to the query subject, retaining source sentences.",
        "Separate joins compare reviewer counts with minimum definitions and event dates with applicable temporal rules.",
        "Returned contradictions include their reasoning rule and source evidence in the report.", "",
        "Supported forms include `X belongs to Y`, `X is assigned to Y`, `X was evaluated under Y`,",
        "`X is a CATEGORY`, `X is classified as CATEGORY`, profile use and explicit inheritance.",
        "Typed facts cover maximum context windows, calibrated/uncalibrated mass (kg/lb conversion),",
        "post-publication immutability, universal pre-production reviews, minimum reviewer counts,",
        "closed fleet-launch year intervals and dated current-endpoint replacement.", "",
        "## Robustness checks", "",
        "Each public case is rerun with opaque IDs and misleading metadata, reversed premise sentences,",
        "consistently renamed entity names, and disconnected quantity distractors. Batch order is also reversed.",
        "For each detected public contradiction, removing either required premise must remove the proof.",
        "Unit tests additionally use newly authored entities, quantities, threshold boundaries, unit conversions,",
        "longer inheritance chains, cycles, conflicting quantities, non-universal statements and date boundaries.",
        "These are internal metamorphic and synthetic tests, not a held-out evaluation split.", "",
        "## Boundaries", "",
        "- Inference reads premise/query text only. IDs route outputs; expected labels, tags and domains do not select rules.",
        "- The grammar was developed with the public suite visible. High development-set scores do not establish generalization.",
        "- Inherited permission/validity polarity and unrestricted paraphrases are unsupported in this first reference.",
        "- No proof maps to the benchmark's `none` label; it is not proof that the statements are consistent.",
        "- The fixed 0.85 confidence is uncalibrated. Timing fields are zeroed for deterministic artifacts, not a speed claim.",
        "- Ambiguous categories, quantities or dates can cause abstention. The parser is not a general temporal or legal rule system.",
        "- The historical engine/hash-prior diagnostic remains valid for that pair; its weakness is not erased by the new reference.",
        "- Keep suite cases, IDs, hashes and scoring unchanged. Blind ranking needs a separately designed held-out evaluation.", "",
        "## Reproduce", "", "```bash",
        "python -m marked_bench.contradiction.multihop_reference --report artifacts/multihop-reference.json",
        "python -m marked_bench.benchmark_cli --validate-report artifacts/multihop-reference.json",
        "python scripts/check_multihop_reference.py",
        "python -m unittest discover -s tests",
        "```", "",
        "Regenerate checked evidence with `python scripts/regenerate_release_artifacts.py`.",
        "No network or provider/model invocation is required for reference inference or these checks.", "",
        "## Case-level predictions", "",
        "| Case | Expected | Predicted | Source sentences |",
        "| --- | --- | --- | ---: |",
    ]
    lines.extend(f"| {r['case_id']} | {r['expected']} | {r['predicted']} | {len(r['evidence'])} |" for r in rows)
    return report, "\n".join(lines) + "\n"


def regenerate_multihop_reference(root: Path = ROOT) -> None:
    root = root.resolve()
    report, document = build_evidence(root)
    (root / REPORT).write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    leaderboard = build_leaderboard(root / path for path in REPORTS)
    leaderboard["created_at"] = 0.0
    for entry in leaderboard["entries"]:
        entry["report_path"] = Path(entry["report_path"]).relative_to(root).as_posix()
    (root / LEADERBOARD).write_text(json.dumps(leaderboard, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    (root / DOCUMENT).write_text(document, encoding="utf-8", newline="\n")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args()
    if args.write:
        regenerate_multihop_reference()
    report, document = build_evidence()
    if json.loads((ROOT / REPORT).read_text(encoding="utf-8")) != report:
        raise ValueError("Checked reference report is stale")
    if (ROOT / DOCUMENT).read_text(encoding="utf-8") != document:
        raise ValueError("Checked reference documentation is stale")
    print(f"Multi-hop reference passed: {report['overall_score']:.2f}; {audit_reference()}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
