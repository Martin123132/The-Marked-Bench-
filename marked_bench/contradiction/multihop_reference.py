from __future__ import annotations

"""Bounded, text-only symbolic reference; not a general language reasoner.

Inference reads only premise/query text. IDs are used solely for output routing.
Unsupported wording and ambiguous proofs return no detected contradiction.
"""

from collections import defaultdict, deque
from dataclasses import dataclass
from datetime import date
from decimal import Decimal
import re

from .engine import Claim, Contradiction, ContradictionType


WORDS = dict(zip(
    "zero one two three four five six seven eight nine ten eleven twelve".split(),
    range(13),
))
NUMBER = r"(?:\d+(?:,\d{3})*(?:\.\d+)?|zero|one|two|three|four|five|six|seven|eight|nine|ten|eleven|twelve)"
DAY = r"\d{4}-\d{2}-\d{2}"
ROLES = (
    "context profile|approval profile|collection|shipment|service|platform|policy|"
    "profile|model|crate|parcel|dataset|system|record|release|request|experiment|"
    "fleet|vault|key|bin"
)


def sentences(text: str) -> list[str]:
    return [part.strip().rstrip(".!?") for part in re.split(r"(?<=[.!?])\s+", text.strip()) if part.strip()]


def _clean(text: str) -> str:
    return " ".join(text.lower().strip().rstrip(".!?").split())


def _entity(text: str) -> str:
    text = re.sub(r"^(?:the|a|an) ", "", _clean(text))
    text = re.sub(rf"^(?:{ROLES}) ", "", text)
    return re.sub(r" evaluation$", "", text)


def _category(text: str) -> str:
    text = _entity(text)
    return text[:-1] if text.endswith("s") and not text.endswith("ss") else text


def _number(text: str) -> Decimal:
    return Decimal(WORDS[text]) if text in WORDS else Decimal(text.replace(",", ""))


def _quantity(text: str) -> tuple[str, Decimal] | None:
    if "mass" in text:
        matches = re.findall(rf"({NUMBER})\s+(kg|kilograms?|lb|pounds?)\b", text)
        if len(matches) == 1:
            amount, unit = matches[0]
            kilograms = _number(amount) * (Decimal("0.45359237") if unit in {"lb", "pound", "pounds"} else 1)
            return ("calibrated_mass" if "calibrat" in text else "mass", kilograms)
    if "maximum context window" in text:
        matches = re.findall(rf"({NUMBER})\s+tokens?\b", text)
        if len(matches) == 1:
            return "maximum_context", _number(matches[0])
    return None


@dataclass(frozen=True)
class Proof:
    type: ContradictionType
    reason: str
    premises: tuple[str, ...]


@dataclass(frozen=True)
class _Fact:
    kind: str
    owner: str
    values: tuple
    source: str


class _Knowledge:
    def __init__(self, premise: str) -> None:
        self.edges: dict[str, list[tuple[str, str]]] = defaultdict(list)
        self.facts: list[_Fact] = []
        for original in sentences(premise):
            self._parse(_clean(original), original)

    def _parse(self, text: str, source: str) -> None:
        def fact(kind: str, owner: str, *values) -> None:
            self.facts.append(_Fact(kind, _entity(owner), values, source))

        match = re.fullmatch(r"(.+?) (?:is assigned to|belongs to|was evaluated under|is classified as) (.+)", text)
        if not match:
            match = re.fullmatch(r"(.+?) is (?:a|an) (.+)", text)
        if not match:
            match = re.fullmatch(r"(.+?) used ((?:[a-z-]+ )?profile .+)", text)
        if match:
            self.edges[_entity(match[1])].append((_entity(match[2]), source))
        match = re.fullmatch(r"(.+?) inherits (.+?) from (.+)", text)
        if match:
            self.edges[_entity(match[1])].append((_entity(match[3]), source))
            self.edges[_entity(match[3])].append((_entity(match[2]), source))

        for pattern in (
            r"(.+?) has (?:a )?maximum context window of .+",
            r"(.+?) manifest lists assigned .+? mass as .+",
            r"(.+?) has (?:calibrated )?mass .+",
        ):
            match = re.fullmatch(pattern, text)
            quantity = _quantity(text)
            if match and quantity:
                fact("quantity", match[1], *quantity)
                break

        match = re.fullmatch(r"(?:a|an) (.+?) is defined as .+?cannot be (?:modified|edited|changed) after (.+)", text)
        if match:
            fact("immutable_definition", match[1], match[2])
        match = re.fullmatch(r"all .+? in (.+?) are immutable after (.+)", text)
        if match:
            fact("immutable_universal", match[1], match[2])
        match = re.fullmatch(r"(?:every|all) (.+?) must (?:pass|complete) (.+?) before (.+)", text)
        if match:
            fact("review", _category(match[1]), match[2], match[3])
        match = re.fullmatch(rf"(.+?) requires at least ({NUMBER}) (.+)", text)
        if match:
            fact("minimum", match[1], _number(match[2]), match[3])
        match = re.fullmatch(rf"(.+?) had exactly ({NUMBER}) (.+)", text)
        if match:
            fact("count", match[1], _number(match[2]), match[3])
        match = re.fullmatch(r"(.+?) used (manual|automated) approval for (?:all )?launches from (\d{4}) through (\d{4})", text)
        if match and int(match[3]) <= int(match[4]):
            fact("interval", match[1], match[2], int(match[3]), int(match[4]))
        match = re.fullmatch(r"(.+?) launched under (.+?) in (\d{4})", text)
        if match:
            fact("launch", match[1], _entity(match[2]), int(match[3]))
        match = re.fullmatch(rf"(.+?) replaced (.+?) as the (.+?) on ({DAY})", text)
        if match:
            try:
                fact("replacement", match[2], _entity(match[1]), match[3], date.fromisoformat(match[4]))
            except ValueError:
                pass
        match = re.fullmatch(rf"(.+?) was processed on ({DAY})", text)
        if match:
            try:
                fact("event_date", match[1], date.fromisoformat(match[2]))
            except ValueError:
                pass

    def reachable(self, subject: str) -> dict[str, tuple[str, ...]]:
        paths: dict[str, tuple[str, ...]] = {subject: ()}
        queue = deque([subject])
        while queue:
            current = queue.popleft()
            for destination, evidence in sorted(self.edges.get(current, [])):
                if destination not in paths:
                    paths[destination] = (*paths[current], evidence)
                    queue.append(destination)
        return paths


class MultiHopReference:
    """Stateless graph joins with explicit quantities, definitions and dates.

The fixed 0.85 detector score is an uncalibrated rule confidence, not a learned
probability. No claim IDs, metadata, domain tags or expected labels select rules.
"""

    def explain(self, claim: Claim) -> Proof | None:
        knowledge = _Knowledge(claim.premise)
        query = _clean(claim.query)
        match = re.match(r"(.+?) (?:used|has|was|entered|satisfied) ", query)
        if not match:
            return None
        subject = _entity(match[1])
        paths = knowledge.reachable(subject)
        facts = knowledge.facts
        candidates: list[Proof] = []

        def add(label: ContradictionType, reason: str, *evidence: str) -> None:
            candidates.append(Proof(label, reason, tuple(sorted(set(evidence)))))

        quantity = _quantity(query)
        if quantity and re.fullmatch(r".+? (?:used|has) .+", query):
            relevant = [f for f in facts if f.kind == "quantity" and f.owner in paths and f.values[0] == quantity[0]]
            values = {f.values[1] for f in relevant}
            if len(values) == 1 and abs(next(iter(values)) - quantity[1]) > Decimal("0.000001"):
                for f in relevant:
                    add(ContradictionType.PROPERTY_MISMATCH, "Linked property differs after canonical unit conversion.", *paths[f.owner], f.source)

        mutation = re.search(r"\bwas (?:modified|edited|changed) after (.+)", query)
        if mutation:
            phase = mutation[1].split(" while ")[0]
            for f in facts:
                if f.owner in paths and f.values == (phase,):
                    if f.kind == "immutable_definition":
                        add(ContradictionType.DEFINITIONAL_VIOLATION, "Classification inherits a no-modification definition for this phase.", *paths[f.owner], f.source)
                    elif f.kind == "immutable_universal":
                        add(ContradictionType.UNIVERSAL_COUNTEREXAMPLE, "Membership inherits universal immutability for this phase.", *paths[f.owner], f.source)

        omitted_review = re.fullmatch(r".+? entered (.+?) without (.+)", query)
        if omitted_review:
            for f in facts:
                if f.kind == "review" and f.owner in paths and f.values == (omitted_review[2], omitted_review[1]):
                    add(ContradictionType.UNIVERSAL_COUNTEREXAMPLE, "A category member entered the phase without the universally required review.", *paths[f.owner], f.source)

        qualification = re.fullmatch(r".+? satisfied (.+)", query)
        if qualification:
            for rule in facts:
                if rule.kind != "minimum" or rule.owner != _entity(qualification[1]):
                    continue
                counts = [f for f in facts if f.kind == "count" and f.owner == subject and f.values[1] == rule.values[1]]
                values = {f.values[0] for f in counts}
                if len(values) == 1 and next(iter(values)) < rule.values[0]:
                    for count in counts:
                        add(ContradictionType.DEFINITIONAL_VIOLATION, "The observed count is below the qualification's required minimum.", rule.source, count.source)

        mode = re.fullmatch(r".+? used (manual|automated) approval at launch", query)
        launches = [f for f in facts if f.kind == "launch" and f.owner == subject]
        if mode and len({f.values for f in launches}) == 1:
            launch = sorted(launches, key=lambda f: f.source)[0]
            intervals = [f for f in facts if f.kind == "interval" and f.owner == launch.values[0] and f.values[1] <= launch.values[1] <= f.values[2]]
            modes = {f.values[0] for f in intervals}
            if len(modes) == 1 and mode[1] not in modes:
                for interval in intervals:
                    add(ContradictionType.TEMPORAL_CONFLICT, "The launch belongs to the fleet inside its incompatible approval interval.", launch.source, interval.source)

        endpoint = re.fullmatch(r".+? used (.+?) as the (.+)", query)
        events = [f for f in facts if f.kind == "event_date" and f.owner == subject]
        if endpoint and len({f.values for f in events}) == 1:
            event = sorted(events, key=lambda f: f.source)[0]
            replacements = [f for f in facts if f.kind == "replacement" and f.values[1] == endpoint[2] and f.values[2] <= event.values[0]]
            if replacements:
                latest = max(f.values[2] for f in replacements)
                current = [f for f in replacements if f.values[2] == latest]
                versions = {f.values[0] for f in current}
                if len(versions) == 1 and _entity(endpoint[1]) not in versions:
                    for replacement in current:
                        add(ContradictionType.TEMPORAL_CONFLICT, "The event follows the latest declared replacement of the current endpoint.", event.source, replacement.source)

        if len({proof.type for proof in candidates}) != 1:
            return None
        return min(candidates, key=lambda proof: (len(proof.premises), proof.reason, proof.premises))

    def detect(self, claim: Claim) -> Contradiction | None:
        proof = self.explain(claim)
        if proof is None:
            return None
        return Contradiction(
            claim_id=claim.id, type=proof.type,
            note=proof.reason + " Evidence: " + " | ".join(proof.premises),
            repair_suggestion="Reconcile the linked facts, scope and queried assertion.",
            score=0.85,
        )


def build_reference_report() -> dict:
    """Score the reference separately from inference; stabilize only timings."""
    from .benchmark_suite import build_multihop_suite, evaluate_prediction_records

    reference = MultiHopReference()
    records = []
    for case in build_multihop_suite():
        proof = reference.explain(case.to_claim())
        records.append({
            "case_id": case.id,
            "predicted": proof.type.value if proof else "none",
            "detector_score": 0.85 if proof else 0.0,
            "rationale": proof.reason if proof else "No supported, unambiguous contradiction proof was found.",
            "evidence": list(proof.premises) if proof else [],
        })
    report = evaluate_prediction_records(records, system_name="MultiHopReference", suite="contradiction-multihop")
    report["created_at"] = 0.0
    report["duration_seconds"] = 0.0
    return report


def main() -> int:
    import argparse
    import json
    from pathlib import Path

    parser = argparse.ArgumentParser(description="Run the bounded text-only multi-hop reference on frozen suite v0.3.0.")
    parser.add_argument("--report", type=Path, required=True)
    args = parser.parse_args()
    report = build_reference_report()
    args.report.parent.mkdir(parents=True, exist_ok=True)
    args.report.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8", newline="\n")
    print(f"MultiHopReference: {report['overall_score']:.2f}; report: {args.report}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
