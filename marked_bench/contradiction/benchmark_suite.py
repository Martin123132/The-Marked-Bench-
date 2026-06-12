from __future__ import annotations

"""Versioned benchmark suite for contradiction-detection systems.

The suite is intentionally model-agnostic: any detector that accepts a
``Claim`` and returns a ``Contradiction`` or ``None`` can be scored.
"""

from collections.abc import Sequence as SequenceABC
from dataclasses import asdict, dataclass
import hashlib
import json
import math
import time
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from .engine import Claim, Contradiction, ContradictionEngine, ContradictionType


SUITE_ID = "marked-bench-contradiction-standard"
SUITE_VERSION = "0.1.1"
STANDARD_SUITE_V0_1_0_VERSION = "0.1.0"
ADVERSARIAL_SUITE_ID = "marked-bench-contradiction-adversarial"
ADVERSARIAL_SUITE_VERSION = "0.2.0"
MULTIHOP_SUITE_ID = "marked-bench-contradiction-multihop"
MULTIHOP_SUITE_VERSION = "0.3.0"
CONTROL_SUITE_ID = "marked-bench-contradiction-controls"
CONTROL_SUITE_VERSION = "0.4.0"
REPORT_SCHEMA = "marked_bench.contradiction-benchmark-report.v2"
VALIDATION_SCHEMA = "marked_bench.contradiction-benchmark-validation.v1"
SUITE_MANIFEST_SCHEMA = "marked_bench.contradiction-suite-manifest.v1"
PREDICTION_SCHEMA = "marked_bench.contradiction-predictions.v2"
LEGACY_PREDICTION_SCHEMAS = {"marked_bench.contradiction-predictions.v1"}
DEFAULT_SUITE = "standard"

Detector = Callable[[Claim], Contradiction | None]


@dataclass(frozen=True)
class BenchmarkCase:
    """A stable benchmark case with expected contradiction label."""

    id: str
    premise: str
    query: str
    expected: ContradictionType
    domain: str
    difficulty: str
    capability: str
    tags: tuple[str, ...] = ()
    note: str = ""

    def to_claim(self) -> Claim:
        return Claim(
            id=self.id,
            premise=self.premise,
            query=self.query,
            domain=self.domain,
            metadata={
                "difficulty": self.difficulty,
                "capability": self.capability,
                "tags": list(self.tags),
            },
        )

    def to_record(self) -> dict[str, Any]:
        record = asdict(self)
        record["expected"] = self.expected.value
        record["tags"] = list(self.tags)
        return record


def build_standard_suite_v0_1_0() -> list[BenchmarkCase]:
    """Return the published v0.1.0 foundation contradiction cases."""

    return [
        BenchmarkCase(
            "marked-direct-001",
            "Not all safety checks passed",
            "All safety checks passed",
            ContradictionType.DIRECT_NEGATION,
            "safety",
            "easy",
            "negation_scope",
            ("negation", "surface"),
            "Query affirms a premise-level negation.",
        ),
        BenchmarkCase(
            "marked-direct-002",
            "The reactor is stable",
            "The reactor is not stable",
            ContradictionType.DIRECT_NEGATION,
            "safety",
            "easy",
            "predicate_negation",
            ("negation", "predicate"),
            "Query inserts a direct predicate negation.",
        ),
        BenchmarkCase(
            "marked-direct-003",
            "The audit log is complete",
            "The audit log is incomplete",
            ContradictionType.DIRECT_NEGATION,
            "governance",
            "medium",
            "lexical_antonym",
            ("negation", "adversarial"),
            "Lexical antonym contradiction without an explicit 'not'.",
        ),
        BenchmarkCase(
            "marked-property-001",
            "Water boils at 100C",
            "Water boils at 95C",
            ContradictionType.PROPERTY_MISMATCH,
            "science",
            "easy",
            "numeric_property",
            ("numeric", "property"),
            "Same property, different numeric value.",
        ),
        BenchmarkCase(
            "marked-property-002",
            "The package mass is 5 kilograms",
            "The package mass is 5 pounds",
            ContradictionType.PROPERTY_MISMATCH,
            "measurement",
            "medium",
            "unit_consistency",
            ("unit", "property"),
            "Same raw number under incompatible unit systems.",
        ),
        BenchmarkCase(
            "marked-property-003",
            "The threshold is 0.80",
            "The threshold is 0.80 after calibration",
            ContradictionType.NONE,
            "measurement",
            "easy",
            "numeric_control",
            ("control", "numeric"),
            "Same numeric property with added context, not a contradiction.",
        ),
        BenchmarkCase(
            "marked-definition-001",
            "Triangles have three sides",
            "Triangle false three sides",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "geometry",
            "easy",
            "definition_check",
            ("definition", "geometry"),
            "Query denies a definitional triangle property.",
        ),
        BenchmarkCase(
            "marked-definition-002",
            "A prime number has exactly two positive divisors",
            "Prime number even false for 2",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "math",
            "medium",
            "exception_sensitive_definition",
            ("definition", "math"),
            "Tests prime-definition handling around the even-number exception.",
        ),
        BenchmarkCase(
            "marked-definition-003",
            "Squares have four equal sides",
            "This square has four equal sides",
            ContradictionType.NONE,
            "geometry",
            "easy",
            "definition_control",
            ("control", "definition"),
            "Definition is affirmed rather than denied.",
        ),
        BenchmarkCase(
            "marked-universal-001",
            "All mammals give live birth",
            "Platypus is a mammal that lays eggs",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "biology",
            "medium",
            "counterexample_detection",
            ("universal", "counterexample"),
            "Known counterexample challenges a universal claim.",
        ),
        BenchmarkCase(
            "marked-universal-002",
            "All deployed agents require approval",
            "A counterexample exists: test agents are deployed automatically",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "governance",
            "easy",
            "explicit_counterexample",
            ("universal", "policy"),
            "Explicit counterexample language challenges a universal rule.",
        ),
        BenchmarkCase(
            "marked-universal-003",
            "Most deployed agents require approval",
            "Some test agents are deployed automatically",
            ContradictionType.NONE,
            "governance",
            "medium",
            "quantifier_control",
            ("control", "quantifier"),
            "Non-universal quantifier allows exceptions.",
        ),
        BenchmarkCase(
            "marked-temporal-001",
            "Always in 1950 the system used manual routing",
            "In 2020 the system used automated routing",
            ContradictionType.TEMPORAL_CONFLICT,
            "operations",
            "easy",
            "temporal_scope",
            ("temporal", "scope"),
            "Time-dependent claim conflicts with an 'always' quantifier.",
        ),
        BenchmarkCase(
            "marked-temporal-002",
            "Always in 2019 the policy required review",
            "In 2024 the policy no longer required review",
            ContradictionType.TEMPORAL_CONFLICT,
            "governance",
            "medium",
            "policy_drift",
            ("temporal", "policy"),
            "Policy statement changed across dated contexts.",
        ),
        BenchmarkCase(
            "marked-temporal-003",
            "In 1950 the system used manual routing",
            "In 2020 the system used automated routing",
            ContradictionType.NONE,
            "operations",
            "medium",
            "temporal_control",
            ("control", "temporal"),
            "Different dates without universal scope can both be true.",
        ),
        BenchmarkCase(
            "marked-control-001",
            "The model answered in English",
            "The model answered in English with citations",
            ContradictionType.NONE,
            "language",
            "easy",
            "non_contradiction",
            ("control", "language"),
            "Added detail should not be treated as a contradiction.",
        ),
        BenchmarkCase(
            "marked-control-002",
            "The safety review is pending",
            "The safety review is waiting for approval",
            ContradictionType.NONE,
            "safety",
            "medium",
            "semantic_paraphrase",
            ("control", "paraphrase"),
            "Near-paraphrase control case.",
        ),
    ]


def build_standard_suite_v0_1_1() -> list[BenchmarkCase]:
    """Return the expanded v0.1.1 foundation contradiction cases."""

    return [
        *build_standard_suite_v0_1_0(),
        BenchmarkCase(
            "marked-v011-direct-001",
            "The export is approved",
            "The export is rejected",
            ContradictionType.DIRECT_NEGATION,
            "governance",
            "easy",
            "review_status_antonym",
            ("negation", "status", "v0.1.1"),
            "Approved/rejected polarity expands direct-negation status coverage.",
        ),
        BenchmarkCase(
            "marked-v011-property-001",
            "The crate mass is 12 kg",
            "The crate mass is 12 lb",
            ContradictionType.PROPERTY_MISMATCH,
            "measurement",
            "medium",
            "compact_unit_conflict",
            ("unit", "property", "v0.1.1"),
            "Compact kg/lb mismatch broadens unit-conflict coverage.",
        ),
        BenchmarkCase(
            "marked-v011-definition-001",
            "Triangles have three sides",
            "Triangle false three sides in this record",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "geometry",
            "easy",
            "explicit_definition_denial",
            ("definition", "geometry", "v0.1.1"),
            "Direct definition denial expands explicit malformed-query coverage.",
        ),
        BenchmarkCase(
            "marked-v011-universal-001",
            "All submitted reports include evidence",
            "A counterexample exists: one submitted report lacks evidence",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "benchmarking",
            "medium",
            "evidence_counterexample",
            ("universal", "counterexample", "v0.1.1"),
            "Evidence-related counterexample adds benchmark governance coverage.",
        ),
        BenchmarkCase(
            "marked-v011-temporal-001",
            "Always in 2021 the queue used manual review",
            "In 2024 the queue used automated review",
            ContradictionType.TEMPORAL_CONFLICT,
            "operations",
            "medium",
            "review_mode_drift",
            ("temporal", "scope", "v0.1.1"),
            "Reviewer workflow drift expands temporal policy coverage.",
        ),
        BenchmarkCase(
            "marked-v011-control-001",
            "The report includes rationale",
            "The report includes rationale and evidence",
            ContradictionType.NONE,
            "benchmarking",
            "easy",
            "evidence_elaboration_control",
            ("control", "evidence", "v0.1.1"),
            "Added evidence detail should not be treated as a contradiction.",
        ),
    ]


def build_standard_suite() -> list[BenchmarkCase]:
    """Return the latest foundation contradiction cases for The Marked Bench."""

    return build_standard_suite_v0_1_1()


def build_adversarial_suite() -> list[BenchmarkCase]:
    """Return the adversarial contradiction track for The Marked Bench.

    This track is intentionally harder than the foundation suite. It uses
    longer context, implicit contradictions, paraphrase traps, and distractors
    that simple surface rules should not fully solve.
    """

    return [
        BenchmarkCase(
            "marked-adv-direct-001",
            "The incident report says the access token remained valid through the review window.",
            "The same review summary later states the access token was invalid during the review window.",
            ContradictionType.DIRECT_NEGATION,
            "security",
            "hard",
            "implicit_polarity",
            ("adversarial", "negation", "long_context"),
            "Contradiction is expressed through valid/invalid paraphrase in longer context.",
        ),
        BenchmarkCase(
            "marked-adv-direct-002",
            "A policy note records the export as permitted for research users.",
            "The compliance memo describes the same export as forbidden for research users.",
            ContradictionType.DIRECT_NEGATION,
            "governance",
            "hard",
            "policy_antonym",
            ("adversarial", "negation", "policy"),
            "Permitted/forbidden conflict without an explicit negation marker.",
        ),
        BenchmarkCase(
            "marked-adv-direct-003",
            "The deployment checklist marks rollback as possible after the migration.",
            "The final release note says rollback is impossible after the migration.",
            ContradictionType.DIRECT_NEGATION,
            "operations",
            "hard",
            "modal_antonym",
            ("adversarial", "negation", "modal"),
            "Possible/impossible modal contradiction.",
        ),
        BenchmarkCase(
            "marked-adv-property-001",
            "The benchmark card reports median latency of 240 ms for model A under load.",
            "The comparison paragraph reports median latency of 410 ms for model A under the same load.",
            ContradictionType.PROPERTY_MISMATCH,
            "benchmarking",
            "hard",
            "numeric_same_condition",
            ("adversarial", "numeric", "same_entity"),
            "Same metric and condition, different numeric values.",
        ),
        BenchmarkCase(
            "marked-adv-property-002",
            "The shipping manifest lists the crate mass as 12 kg after calibration.",
            "The audit copy lists the crate mass as 12 lb after calibration.",
            ContradictionType.PROPERTY_MISMATCH,
            "measurement",
            "medium",
            "unit_conflict_with_context",
            ("adversarial", "unit", "property"),
            "Same quantity and raw value under incompatible units.",
        ),
        BenchmarkCase(
            "marked-adv-property-003",
            "The shipping manifest lists the crate mass as 12 kg before calibration.",
            "The audit copy lists the crate mass as 12 kg after calibration.",
            ContradictionType.NONE,
            "measurement",
            "medium",
            "condition_shift_control",
            ("control", "property", "context_shift"),
            "Context changed; the value and unit agree, so this is not a contradiction.",
        ),
        BenchmarkCase(
            "marked-adv-definition-001",
            "The glossary defines a triangle as a polygon with exactly three sides.",
            "The generated explanation says a triangle can have four sides while remaining a triangle.",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "geometry",
            "hard",
            "definition_paraphrase",
            ("adversarial", "definition", "geometry"),
            "Query violates a definitional property without using the word false.",
        ),
        BenchmarkCase(
            "marked-adv-definition-002",
            "The math note says a prime number has exactly two positive divisors.",
            "The answer claims 9 is prime because it has divisors 1, 3, and 9.",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "math",
            "hard",
            "definition_application",
            ("adversarial", "definition", "math"),
            "The query's own divisor list violates the prime definition.",
        ),
        BenchmarkCase(
            "marked-adv-definition-003",
            "The glossary defines a square as a figure with four equal sides.",
            "The caption describes the tile as a square with four equal sides and a blue border.",
            ContradictionType.NONE,
            "geometry",
            "medium",
            "definition_elaboration_control",
            ("control", "definition", "elaboration"),
            "Additional visual detail does not violate the definition.",
        ),
        BenchmarkCase(
            "marked-adv-universal-001",
            "All production agents must pass human approval before release.",
            "The exception log says emergency production agents bypass human approval before release.",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "ai_safety",
            "hard",
            "implicit_counterexample",
            ("adversarial", "universal", "approval"),
            "A bypassing subclass counters the universal approval claim.",
        ),
        BenchmarkCase(
            "marked-adv-universal-002",
            "Every archived dataset is immutable after publication.",
            "A correction entry says archived dataset A17 was edited after publication.",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "data_governance",
            "hard",
            "instance_counterexample",
            ("adversarial", "universal", "data"),
            "Specific edited instance counters an every/immutable universal.",
        ),
        BenchmarkCase(
            "marked-adv-universal-003",
            "Most archived datasets are immutable after publication.",
            "A correction entry says archived dataset A17 was edited after publication.",
            ContradictionType.NONE,
            "data_governance",
            "medium",
            "non_universal_control",
            ("control", "universal", "quantifier"),
            "Most allows exceptions; this should not be scored as a contradiction.",
        ),
        BenchmarkCase(
            "marked-adv-temporal-001",
            "The vendor page says the API has always required token signing since 2018.",
            "The migration note says token signing was introduced in 2022.",
            ContradictionType.TEMPORAL_CONFLICT,
            "security",
            "hard",
            "temporal_always_since",
            ("adversarial", "temporal", "security"),
            "Always-since claim conflicts with a later introduction date.",
        ),
        BenchmarkCase(
            "marked-adv-temporal-002",
            "The runbook says the service always used manual review in 2019.",
            "The audit says the same service used automated review in 2021.",
            ContradictionType.TEMPORAL_CONFLICT,
            "operations",
            "medium",
            "temporal_scope_drift",
            ("adversarial", "temporal", "operations"),
            "A broad always claim conflicts with a later dated state.",
        ),
        BenchmarkCase(
            "marked-adv-temporal-003",
            "The service used manual review in 2019.",
            "The service used automated review in 2021.",
            ContradictionType.NONE,
            "operations",
            "medium",
            "temporal_change_control",
            ("control", "temporal", "state_change"),
            "A system can change across time without contradiction.",
        ),
        BenchmarkCase(
            "marked-adv-control-001",
            "The model declined the unsafe request and offered a safe alternative.",
            "The model refused the unsafe request while suggesting a safe alternative.",
            ContradictionType.NONE,
            "ai_safety",
            "medium",
            "paraphrase_control",
            ("control", "paraphrase", "safety"),
            "Near-paraphrase should remain non-contradictory.",
        ),
        BenchmarkCase(
            "marked-adv-control-002",
            "The audit found no evidence that private keys left the vault.",
            "The audit did not prove that private keys left the vault.",
            ContradictionType.NONE,
            "security",
            "hard",
            "negation_scope_control",
            ("control", "negation", "scope"),
            "Two cautious negative claims are compatible.",
        ),
    ]


def build_multihop_suite() -> list[BenchmarkCase]:
    """Return the multi-hop contradiction track for The Marked Bench.

    Cases in this track require linking two or more facts before the expected
    contradiction label is visible. This makes the track a better target for
    retrieval-augmented, graph, and long-context reasoning systems.
    """

    return [
        BenchmarkCase(
            "marked-hop-direct-001",
            (
                "Service Orion inherits export policy P7 from platform Atlas. "
                "Policy P7 says research-user exports are permitted."
            ),
            "The Orion release note says research-user exports are forbidden.",
            ContradictionType.DIRECT_NEGATION,
            "governance",
            "expert",
            "policy_chain_negation",
            ("multihop", "negation", "policy", "entity_linking"),
            "The policy must be linked through Atlas before permitted/forbidden conflict is visible.",
        ),
        BenchmarkCase(
            "marked-hop-direct-002",
            (
                "Key K-42 belongs to vault Alpha. Vault Alpha records say resident keys "
                "remained valid during the audit window."
            ),
            "The audit summary says K-42 was invalid during the audit window.",
            ContradictionType.DIRECT_NEGATION,
            "security",
            "hard",
            "membership_polarity",
            ("multihop", "negation", "security", "entity_linking"),
            "The key inherits vault validity before the valid/invalid conflict appears.",
        ),
        BenchmarkCase(
            "marked-hop-direct-003",
            (
                "Experiment E5 used approval profile Gold. Approval profile Gold allows "
                "offline review for internal replication studies."
            ),
            "Experiment E5 used offline review for an internal replication study.",
            ContradictionType.NONE,
            "research",
            "medium",
            "permission_chain_control",
            ("multihop", "control", "policy"),
            "The query is licensed by the inherited approval profile.",
        ),
        BenchmarkCase(
            "marked-hop-property-001",
            (
                "Model Delta was evaluated under context profile C8. Context profile C8 "
                "has a maximum context window of 8,192 tokens."
            ),
            "The Delta evaluation used a 32,768 token maximum context window under profile C8.",
            ContradictionType.PROPERTY_MISMATCH,
            "benchmarking",
            "hard",
            "profile_numeric_link",
            ("multihop", "numeric", "benchmarking", "entity_linking"),
            "The numeric mismatch depends on linking Delta to profile C8.",
        ),
        BenchmarkCase(
            "marked-hop-property-002",
            (
                "Crate C17 is assigned to shipment Route-9. The Route-9 manifest lists "
                "assigned crate mass as 12 kg after calibration."
            ),
            "Crate C17 has calibrated mass 12 lb on Route-9.",
            ContradictionType.PROPERTY_MISMATCH,
            "measurement",
            "hard",
            "inherited_unit_conflict",
            ("multihop", "unit", "property", "entity_linking"),
            "The unit mismatch is inherited through the shipment assignment.",
        ),
        BenchmarkCase(
            "marked-hop-property-003",
            (
                "Crate C17 is assigned to shipment Route-9. The Route-9 manifest lists "
                "assigned crate mass as 12 kg after calibration."
            ),
            "Crate C17 has calibrated mass 12 kg on Route-9.",
            ContradictionType.NONE,
            "measurement",
            "medium",
            "inherited_property_control",
            ("multihop", "control", "property"),
            "The inherited quantity and unit match.",
        ),
        BenchmarkCase(
            "marked-hop-definition-001",
            (
                "A sealed record is defined as a record that cannot be modified after "
                "publication. Dataset Ledger-4 is classified as a sealed record."
            ),
            "Ledger-4 was modified after publication while remaining a sealed record.",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "data_governance",
            "expert",
            "classification_definition",
            ("multihop", "definition", "data"),
            "The definition must be applied to the classified dataset.",
        ),
        BenchmarkCase(
            "marked-hop-definition-002",
            (
                "Quorum approval requires at least three independent reviewers. Release R19 "
                "had exactly two independent reviewers."
            ),
            "Release R19 satisfied quorum approval.",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "compliance",
            "hard",
            "threshold_definition",
            ("multihop", "definition", "numeric"),
            "The release fails the quorum definition through the reviewer count.",
        ),
        BenchmarkCase(
            "marked-hop-definition-003",
            (
                "A sealed record is defined as a record whose content cannot be modified "
                "after publication. Dataset Ledger-4 received an external citation note."
            ),
            "Ledger-4 received a citation note without changing its sealed content.",
            ContradictionType.NONE,
            "data_governance",
            "medium",
            "definition_boundary_control",
            ("multihop", "control", "definition"),
            "A metadata note does not necessarily modify sealed content.",
        ),
        BenchmarkCase(
            "marked-hop-universal-001",
            (
                "Every high-risk deployment must pass red-team review before production. "
                "System Nova is a high-risk deployment."
            ),
            "System Nova entered production without red-team review.",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "ai_safety",
            "expert",
            "universal_membership_counterexample",
            ("multihop", "universal", "safety", "entity_linking"),
            "The universal rule applies through Nova's high-risk membership.",
        ),
        BenchmarkCase(
            "marked-hop-universal-002",
            (
                "All records in collection Beta are immutable after publication. Record B7 "
                "belongs to collection Beta."
            ),
            "Record B7 was edited after publication.",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "records",
            "hard",
            "collection_counterexample",
            ("multihop", "universal", "data", "entity_linking"),
            "A specific collection member counters the universal immutability claim.",
        ),
        BenchmarkCase(
            "marked-hop-universal-003",
            (
                "Most high-risk deployments pass red-team review before production. "
                "System Nova is a high-risk deployment."
            ),
            "System Nova entered production without red-team review.",
            ContradictionType.NONE,
            "ai_safety",
            "hard",
            "non_universal_membership_control",
            ("multihop", "control", "universal", "quantifier"),
            "Most allows exceptions, so the Nova fact is not a contradiction.",
        ),
        BenchmarkCase(
            "marked-hop-temporal-001",
            (
                "Fleet Delta used manual approval for all launches from 2019 through 2022. "
                "System Sable launched under Fleet Delta in 2020."
            ),
            "System Sable used automated approval at launch.",
            ContradictionType.TEMPORAL_CONFLICT,
            "operations",
            "expert",
            "temporal_membership_scope",
            ("multihop", "temporal", "operations", "entity_linking"),
            "The launch date and fleet membership put Sable inside the manual-approval interval.",
        ),
        BenchmarkCase(
            "marked-hop-temporal-002",
            (
                "API v2 replaced API v1 as the current endpoint on 2021-06-01. Request Q "
                "was processed on 2022-02-10."
            ),
            "Request Q used API v1 as the current endpoint.",
            ContradictionType.TEMPORAL_CONFLICT,
            "infrastructure",
            "hard",
            "replacement_date_conflict",
            ("multihop", "temporal", "api"),
            "The request date falls after the replacement date.",
        ),
        BenchmarkCase(
            "marked-hop-temporal-003",
            (
                "Fleet Delta used manual approval for launches from 2019 through 2022. "
                "Fleet Delta adopted automated approval for launches in 2023."
            ),
            "A Fleet Delta launch used automated approval in 2023.",
            ContradictionType.NONE,
            "operations",
            "medium",
            "temporal_transition_control",
            ("multihop", "control", "temporal"),
            "The query falls after the documented transition.",
        ),
        BenchmarkCase(
            "marked-hop-control-001",
            (
                "The benchmark registry points the default track to contradiction-multihop. "
                "The adoption guide tells users to pin suite ID, version, and hash."
            ),
            "The adoption guide asks users to pin reproducibility metadata for the default track.",
            ContradictionType.NONE,
            "benchmarking",
            "medium",
            "benchmark_metadata_control",
            ("multihop", "control", "benchmarking"),
            "The query summarizes the linked registry and adoption-guide facts.",
        ),
        BenchmarkCase(
            "marked-hop-control-002",
            (
                "The incident board says ticket T11 is unresolved. The handoff note says "
                "unresolved tickets remain open until an owner closes them."
            ),
            "Ticket T11 remains open until an owner closes it.",
            ContradictionType.NONE,
            "operations",
            "medium",
            "state_inheritance_control",
            ("multihop", "control", "state"),
            "The query follows from the unresolved-ticket rule.",
        ),
        BenchmarkCase(
            "marked-hop-control-003",
            (
                "Dataset Echo is a public synthetic dataset. The privacy policy says public "
                "synthetic datasets contain no private user records."
            ),
            "Dataset Echo contains no private user records.",
            ContradictionType.NONE,
            "privacy",
            "medium",
            "privacy_chain_control",
            ("multihop", "control", "privacy"),
            "The query follows from the dataset classification and privacy policy.",
        ),
    ]


def build_control_suite() -> list[BenchmarkCase]:
    """Return a false-positive control track for contradiction detectors.

    This track stresses non-contradiction distractors while retaining anchor
    contradictions for every public label so ordinary scoring remains
    comparable with the other tracks.
    """

    return [
        BenchmarkCase(
            "marked-ctrl-direct-001",
            "The audit packet is complete",
            "The audit packet is incomplete",
            ContradictionType.DIRECT_NEGATION,
            "governance",
            "easy",
            "anchor_negation",
            ("control-track", "anchor", "negation"),
            "Anchor direct-negation case to keep contradiction detection visible.",
        ),
        BenchmarkCase(
            "marked-ctrl-property-001",
            "Water boils at 100C in the reference note",
            "Water boils at 95C in the reference note",
            ContradictionType.PROPERTY_MISMATCH,
            "science",
            "easy",
            "anchor_numeric_property",
            ("control-track", "anchor", "numeric"),
            "Anchor numeric property mismatch.",
        ),
        BenchmarkCase(
            "marked-ctrl-definition-001",
            "Triangles have three sides",
            "Triangle false three sides in this glossary",
            ContradictionType.DEFINITIONAL_VIOLATION,
            "geometry",
            "easy",
            "anchor_definition",
            ("control-track", "anchor", "definition"),
            "Anchor definitional violation.",
        ),
        BenchmarkCase(
            "marked-ctrl-universal-001",
            "All sandbox agents require approval before launch",
            "A counterexample exists: sandbox agent S9 launched without approval",
            ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
            "ai_safety",
            "medium",
            "anchor_universal",
            ("control-track", "anchor", "universal"),
            "Anchor universal-counterexample case.",
        ),
        BenchmarkCase(
            "marked-ctrl-temporal-001",
            "Always in 2021 the service used manual approval",
            "In 2024 the service used automated approval",
            ContradictionType.TEMPORAL_CONFLICT,
            "operations",
            "medium",
            "anchor_temporal",
            ("control-track", "anchor", "temporal"),
            "Anchor temporal conflict.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-001",
            "The deployment gate is enabled for staging",
            "The deployment gate is enabled for staging after the policy update",
            ContradictionType.NONE,
            "operations",
            "easy",
            "elaboration_control",
            ("control-track", "control", "elaboration"),
            "Added temporal context does not reverse the staging gate state.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-002",
            "The audit found no evidence that keys left the vault",
            "The audit did not prove that keys left the vault",
            ContradictionType.NONE,
            "security",
            "hard",
            "negation_scope_control",
            ("control-track", "control", "negation_scope"),
            "Two cautious negative claims are compatible.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-003",
            "Most sandbox agents require review before launch",
            "Some sandbox agents launch automatically during tests",
            ContradictionType.NONE,
            "ai_safety",
            "medium",
            "quantifier_control",
            ("control-track", "control", "quantifier"),
            "A non-universal quantifier allows exceptions.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-004",
            "The service used manual approval in 2021",
            "The service used automated approval in 2024",
            ContradictionType.NONE,
            "operations",
            "medium",
            "temporal_change_control",
            ("control-track", "control", "temporal"),
            "A system can change across years without contradiction.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-005",
            "The threshold is 0.80 before calibration",
            "The threshold is 0.80 after calibration",
            ContradictionType.NONE,
            "measurement",
            "medium",
            "same_value_context_control",
            ("control-track", "control", "numeric"),
            "Same numeric value under a changed condition is not a mismatch.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-006",
            "The crate mass is 12 kg before repacking",
            "The crate mass is 12 kg after repacking",
            ContradictionType.NONE,
            "measurement",
            "easy",
            "same_unit_control",
            ("control-track", "control", "unit"),
            "Same value and unit should not trigger the unit-conflict rule.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-007",
            "The model declined the unsafe request and offered a safe alternative",
            "The model refused the unsafe request while offering a safe alternative",
            ContradictionType.NONE,
            "ai_safety",
            "medium",
            "paraphrase_control",
            ("control-track", "control", "paraphrase"),
            "Near-paraphrase should remain non-contradictory.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-008",
            "The policy is pending approval",
            "The policy is awaiting approval",
            ContradictionType.NONE,
            "governance",
            "easy",
            "state_paraphrase_control",
            ("control-track", "control", "paraphrase"),
            "Pending and awaiting approval are compatible states.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-009",
            "Triangles have three sides",
            "The shape is a triangle with three sides and a red outline",
            ContradictionType.NONE,
            "geometry",
            "easy",
            "definition_elaboration_control",
            ("control-track", "control", "definition"),
            "Additional visual detail does not violate the definition.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-010",
            "Dataset Echo is synthetic",
            "Dataset Echo is a synthetic dataset used for testing",
            ContradictionType.NONE,
            "data_governance",
            "easy",
            "entity_elaboration_control",
            ("control-track", "control", "dataset"),
            "The query elaborates the same dataset classification.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-011",
            "The invoice total is 95 dollars before tax",
            "The invoice total is 95 dollars before tax and fees",
            ContradictionType.NONE,
            "finance",
            "medium",
            "numeric_scope_control",
            ("control-track", "control", "numeric"),
            "The same scoped amount is repeated with extra accounting context.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-012",
            "The incident was resolved by rollback",
            "The incident was resolved after rollback completed",
            ContradictionType.NONE,
            "operations",
            "easy",
            "causal_paraphrase_control",
            ("control-track", "control", "operations"),
            "The query restates the same resolution path.",
        ),
        BenchmarkCase(
            "marked-ctrl-control-013",
            "The cache refresh happened after deploy",
            "The cache refresh happened after the deployment completed",
            ContradictionType.NONE,
            "operations",
            "easy",
            "event_paraphrase_control",
            ("control-track", "control", "operations"),
            "Equivalent event order with different wording.",
        ),
    ]


def build_suite(suite: str = DEFAULT_SUITE) -> list[BenchmarkCase]:
    """Return cases for a named public suite."""

    key = _suite_key(suite)
    if key == "controls":
        return build_control_suite()
    if key == "multihop":
        return build_multihop_suite()
    if key == "adversarial":
        return build_adversarial_suite()
    if key == "standard-v0.1.0":
        return build_standard_suite_v0_1_0()
    return build_standard_suite()


def evaluate_standard_suite(
    detector: ContradictionEngine | Detector | None = None,
    cases: Sequence[BenchmarkCase] | None = None,
    *,
    system_name: str = "ContradictionEngine",
    suite: str = DEFAULT_SUITE,
) -> dict[str, Any]:
    """Evaluate a detector and return a JSON-serializable report."""

    suite_cases = list(cases or build_suite(suite))
    suite_id, suite_version = _suite_identity(suite)
    suite_hash = suite_case_hash(suite_cases)
    detect = _resolve_detector(detector)
    started_at = time.time()
    case_results = []

    for case in suite_cases:
        detected = detect(case.to_claim())
        predicted = detected.type if detected else ContradictionType.NONE
        case_results.append(
            {
                "case_id": case.id,
                "domain": case.domain,
                "difficulty": case.difficulty,
                "capability": case.capability,
                "tags": list(case.tags),
                "expected": case.expected.value,
                "predicted": predicted.value,
                "type_correct": predicted == case.expected,
                "detection_correct": _is_contradiction(predicted) == _is_contradiction(case.expected),
                "detector_score": detected.score if detected else 0.0,
                "detector_note": detected.note if detected else None,
                "rationale": detected.note if detected else None,
                "evidence": [],
            }
        )

    scores = _score_case_results(case_results)

    return {
        "schema": REPORT_SCHEMA,
        "suite_id": suite_id,
        "suite_version": suite_version,
        "suite_hash": suite_hash,
        "system_name": system_name,
        "created_at": round(started_at, 3),
        "duration_seconds": round(time.time() - started_at, 6),
        "case_count": len(case_results),
        "overall_score": scores["overall_score"],
        "metrics": scores["metrics"],
        "explanation_audit": _explanation_audit(case_results),
        "confusion_matrix": scores["confusion_matrix"],
        "failures": scores["failures"],
        "case_results": case_results,
        "suite_cases": [case.to_record() for case in suite_cases],
    }


def evaluate_prediction_records(
    predictions: Iterable[Mapping[str, Any]],
    *,
    system_name: str,
    suite: str = DEFAULT_SUITE,
    cases: Sequence[BenchmarkCase] | None = None,
) -> dict[str, Any]:
    """Score external predictions and return a public benchmark report.

    Prediction records must cover every canonical case exactly once. Each
    record needs a ``case_id`` and a ``predicted`` label. Optional
    ``detector_score``, ``detector_note``, ``rationale``, and ``evidence``
    fields are copied into the final report. ``detector_note`` is retained for
    compatibility; ``rationale`` is the preferred reviewer-facing explanation
    field.
    """

    suite_cases = list(cases or build_suite(suite))
    suite_id, suite_version = _suite_identity(suite)
    suite_hash = suite_case_hash(suite_cases)
    started_at = time.time()
    prediction_by_case = _normalize_prediction_records(predictions, suite_cases)
    case_results = []

    for case in suite_cases:
        prediction = prediction_by_case[case.id]
        predicted = prediction["predicted"]
        case_results.append(
            {
                "case_id": case.id,
                "domain": case.domain,
                "difficulty": case.difficulty,
                "capability": case.capability,
                "tags": list(case.tags),
                "expected": case.expected.value,
                "predicted": predicted,
                "type_correct": predicted == case.expected.value,
                "detection_correct": _is_contradiction(predicted) == _is_contradiction(case.expected),
                "detector_score": prediction["detector_score"],
                "detector_note": prediction["detector_note"],
                "rationale": prediction["rationale"],
                "evidence": prediction["evidence"],
            }
        )

    scores = _score_case_results(case_results)

    return {
        "schema": REPORT_SCHEMA,
        "suite_id": suite_id,
        "suite_version": suite_version,
        "suite_hash": suite_hash,
        "system_name": system_name,
        "created_at": round(started_at, 3),
        "duration_seconds": round(time.time() - started_at, 6),
        "case_count": len(case_results),
        "overall_score": scores["overall_score"],
        "metrics": scores["metrics"],
        "explanation_audit": _explanation_audit(case_results),
        "confusion_matrix": scores["confusion_matrix"],
        "failures": scores["failures"],
        "case_results": case_results,
        "suite_cases": [case.to_record() for case in suite_cases],
    }


def evaluate_prediction_file(
    path: str | Path,
    *,
    system_name: str,
    suite: str = DEFAULT_SUITE,
) -> dict[str, Any]:
    """Load an external prediction file and score it as a benchmark report."""

    payload = _load_prediction_payload(path)
    _validate_prediction_submission_metadata(payload, suite)
    return evaluate_prediction_records(
        _prediction_records_from_payload(payload, path),
        system_name=system_name,
        suite=suite,
    )


def write_benchmark_report(report: Mapping[str, Any], path: str | Path) -> None:
    """Write a benchmark report as stable, sorted JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(report, indent=2, sort_keys=True), encoding="utf-8")


def build_suite_manifest(cases: Sequence[BenchmarkCase] | None = None, suite: str = DEFAULT_SUITE) -> dict[str, Any]:
    """Return the canonical suite as a standalone data manifest."""

    suite_cases = list(cases or build_suite(suite))
    suite_id, suite_version = _suite_identity(suite)
    return {
        "schema": SUITE_MANIFEST_SCHEMA,
        "suite_id": suite_id,
        "suite_version": suite_version,
        "suite_hash": suite_case_hash(suite_cases),
        "case_count": len(suite_cases),
        "labels": _label_values(),
        "profile": build_suite_profile(suite_cases),
        "cases": [case.to_record() for case in suite_cases],
        "scoring": {
            "overall_score_weights": {
                "contradiction_macro_f1": 0.45,
                "type_accuracy": 0.25,
                "binary_detection_f1": 0.20,
                "coverage_index": 0.10,
            }
        },
    }


def build_suite_profile(cases: Sequence[BenchmarkCase] | None = None, suite: str = DEFAULT_SUITE) -> dict[str, Any]:
    """Return coverage and composition metadata for a public suite."""

    suite_cases = list(cases or build_suite(suite))
    label_values = _label_values()
    contradiction_labels = [label.value for label in ContradictionType if label != ContradictionType.NONE]
    return {
        "case_count": len(suite_cases),
        "contradiction_case_count": sum(1 for case in suite_cases if case.expected != ContradictionType.NONE),
        "control_case_count": sum(1 for case in suite_cases if case.expected == ContradictionType.NONE),
        "label_counts": _case_counter((case.expected.value for case in suite_cases), keys=label_values),
        "domain_counts": _case_counter(case.domain for case in suite_cases),
        "difficulty_counts": _case_counter(case.difficulty for case in suite_cases),
        "capability_counts": _case_counter(case.capability for case in suite_cases),
        "tag_counts": _case_counter(tag for case in suite_cases for tag in case.tags),
        "quality_gates": {
            "min_cases": 15,
            "requires_all_contradiction_labels": all(
                any(case.expected.value == label for case in suite_cases) for label in contradiction_labels
            ),
            "requires_control_cases": any(case.expected == ContradictionType.NONE for case in suite_cases),
            "requires_multiple_domains": len({case.domain for case in suite_cases}) >= 3,
            "requires_multiple_difficulties": len({case.difficulty for case in suite_cases}) >= 2,
        },
    }


def write_suite_manifest(path: str | Path, cases: Sequence[BenchmarkCase] | None = None, suite: str = DEFAULT_SUITE) -> None:
    """Write the canonical suite manifest as stable, sorted JSON."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(build_suite_manifest(cases, suite=suite), indent=2, sort_keys=True), encoding="utf-8")


def load_benchmark_report(path: str | Path) -> dict[str, Any]:
    """Load a benchmark report JSON file."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def suite_case_hash(cases: Sequence[BenchmarkCase] | Sequence[Mapping[str, Any]]) -> str:
    """Return a deterministic SHA-256 hash for an ordered suite case list."""

    records = [_case_hash_record(case) for case in cases]
    payload = json.dumps(records, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def build_suite_hash(cases: Sequence[BenchmarkCase] | None = None, suite: str = DEFAULT_SUITE) -> str:
    """Return the canonical suite hash for a named public suite."""

    return suite_case_hash(list(cases or build_suite(suite)))


def load_prediction_records(path: str | Path) -> list[dict[str, Any]]:
    """Load JSON or JSONL prediction records from disk."""

    return _prediction_records_from_payload(_load_prediction_payload(path), path)


def build_prediction_template(
    cases: Sequence[BenchmarkCase] | None = None,
    suite: str = DEFAULT_SUITE,
) -> dict[str, Any]:
    """Return a fillable prediction submission template."""

    suite_cases = list(cases or build_suite(suite))
    suite_id, suite_version = _suite_identity(suite)
    return {
        "schema": PREDICTION_SCHEMA,
        "suite_id": suite_id,
        "suite_version": suite_version,
        "suite_hash": suite_case_hash(suite_cases),
        "labels": _label_values(),
        "predictions": [_prediction_template_record(case) for case in suite_cases],
    }


def write_prediction_template(
    path: str | Path,
    cases: Sequence[BenchmarkCase] | None = None,
    suite: str = DEFAULT_SUITE,
) -> None:
    """Write a fillable prediction template as JSON or JSONL."""

    output_path = Path(path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    template = build_prediction_template(cases, suite=suite)
    if output_path.suffix.lower() in {".jsonl", ".ndjson"}:
        lines = (json.dumps(record, sort_keys=True) for record in template["predictions"])
        output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
        return
    output_path.write_text(json.dumps(template, indent=2, sort_keys=True), encoding="utf-8")


def validate_benchmark_report(
    report: Mapping[str, Any],
    cases: Sequence[BenchmarkCase] | None = None,
    suite: str | None = None,
) -> dict[str, Any]:
    """Validate a public benchmark report against the canonical suite.

    Validation recomputes all aggregate metrics from the submitted case results
    and rejects mismatched suite metadata, edited suite cases, missing cases,
    invalid labels, and inconsistent claimed scores.
    """

    suite_key = _suite_key(suite or _suite_key_from_report(report))
    suite_id, suite_version = _suite_identity(suite_key)
    suite_cases = list(cases or build_suite(suite_key))
    canonical_ids = [case.id for case in suite_cases]
    canonical_by_id = {case.id: case for case in suite_cases}
    errors: list[str] = []
    warnings: list[str] = []

    _expect_equal(report, "schema", REPORT_SCHEMA, errors)
    _expect_equal(report, "suite_id", suite_id, errors)
    _expect_equal(report, "suite_version", suite_version, errors)
    _expect_equal(report, "suite_hash", suite_case_hash(suite_cases), errors)
    _expect_equal(report, "case_count", len(suite_cases), errors)

    submitted_cases = report.get("suite_cases")
    if not isinstance(submitted_cases, list):
        errors.append("suite_cases must be included as a list")
    else:
        submitted_case_ids = [str(case.get("id")) for case in submitted_cases if isinstance(case, Mapping)]
        if submitted_case_ids != canonical_ids:
            errors.append("suite_cases must match the canonical case order and IDs")
        for submitted_case in submitted_cases:
            if not isinstance(submitted_case, Mapping):
                errors.append("suite_cases entries must be objects")
                continue
            case_id = str(submitted_case.get("id"))
            canonical = canonical_by_id.get(case_id)
            if canonical is None:
                errors.append(f"unknown suite case: {case_id}")
                continue
            if dict(submitted_case) != canonical.to_record():
                errors.append(f"suite case was modified: {case_id}")

    case_results = report.get("case_results")
    normalized_results: list[dict[str, Any]] = []
    if not isinstance(case_results, list):
        errors.append("case_results must be included as a list")
    else:
        result_ids = [str(item.get("case_id")) for item in case_results if isinstance(item, Mapping)]
        if result_ids != canonical_ids:
            errors.append("case_results must match the canonical case order and IDs")
        labels = set(_label_values())
        for item in case_results:
            if not isinstance(item, Mapping):
                errors.append("case_results entries must be objects")
                continue
            case_id = str(item.get("case_id"))
            canonical = canonical_by_id.get(case_id)
            if canonical is None:
                errors.append(f"unknown case result: {case_id}")
                continue
            expected = str(item.get("expected"))
            predicted = str(item.get("predicted"))
            if expected not in labels:
                errors.append(f"{case_id}: invalid expected label {expected!r}")
            if predicted not in labels:
                errors.append(f"{case_id}: invalid predicted label {predicted!r}")
            if expected != canonical.expected.value:
                errors.append(f"{case_id}: expected label does not match canonical suite")
            if item.get("tags") != list(canonical.tags):
                errors.append(f"{case_id}: tags do not match canonical suite")
            if predicted not in labels:
                continue
            type_correct = predicted == canonical.expected.value
            detection_correct = _is_contradiction(predicted) == _is_contradiction(canonical.expected.value)
            if item.get("type_correct") != type_correct:
                errors.append(f"{case_id}: type_correct is inconsistent with expected/predicted")
            if item.get("detection_correct") != detection_correct:
                errors.append(f"{case_id}: detection_correct is inconsistent with expected/predicted")
            try:
                detector_score = _normalize_detector_score(item.get("detector_score", 0.0))
                detector_note = _normalize_optional_text(item.get("detector_note"))
                rationale = _normalize_optional_text(item.get("rationale", detector_note))
                evidence = _normalize_evidence(item.get("evidence", []))
            except ValueError as exc:
                errors.append(f"{case_id}: {exc}")
                continue
            normalized_results.append(
                {
                    "case_id": case_id,
                    "domain": canonical.domain,
                    "difficulty": canonical.difficulty,
                    "capability": canonical.capability,
                    "tags": list(canonical.tags),
                    "expected": canonical.expected.value,
                    "predicted": predicted,
                    "type_correct": type_correct,
                    "detection_correct": detection_correct,
                    "detector_score": detector_score,
                    "detector_note": detector_note,
                    "rationale": rationale,
                    "evidence": evidence,
                }
            )

    if not errors and normalized_results:
        recomputed = _score_case_results(normalized_results)
        _expect_equal(report, "overall_score", recomputed["overall_score"], errors)
        _expect_equal(report, "metrics", recomputed["metrics"], errors)
        _expect_equal(report, "explanation_audit", _explanation_audit(normalized_results), errors)
        _expect_equal(report, "confusion_matrix", recomputed["confusion_matrix"], errors)
        _expect_equal(report, "failures", recomputed["failures"], errors)
        if not report.get("system_name"):
            warnings.append("system_name is empty")

    return {
        "schema": VALIDATION_SCHEMA,
        "suite_id": suite_id,
        "suite_version": suite_version,
        "valid": not errors,
        "errors": errors,
        "warnings": warnings,
        "summary": {
            "system_name": report.get("system_name"),
            "case_count": report.get("case_count"),
            "overall_score": report.get("overall_score"),
            "failure_count": len(report.get("failures", [])) if isinstance(report.get("failures"), list) else None,
        },
    }


def _resolve_detector(detector: ContradictionEngine | Detector | None) -> Detector:
    if detector is None:
        return ContradictionEngine().detect
    if isinstance(detector, ContradictionEngine):
        return detector.detect
    return detector


def _load_prediction_payload(path: str | Path) -> Any:
    input_path = Path(path)
    text = input_path.read_text(encoding="utf-8")
    if input_path.suffix.lower() in {".jsonl", ".ndjson"}:
        return _load_jsonl_prediction_records(text, input_path)
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return _load_jsonl_prediction_records(text, input_path)


def _prediction_records_from_payload(payload: Any, path: str | Path) -> list[dict[str, Any]]:
    if isinstance(payload, list):
        records = payload
    elif isinstance(payload, Mapping):
        if payload.get("schema") not in {None, PREDICTION_SCHEMA, *LEGACY_PREDICTION_SCHEMAS}:
            raise ValueError(f"{path}: unsupported prediction schema {payload.get('schema')!r}")
        records = payload.get("predictions")
    else:
        records = None
    if not isinstance(records, list):
        raise ValueError(f"{path}: prediction file must be a list or an object with a predictions list")
    normalized = []
    for index, record in enumerate(records, start=1):
        if not isinstance(record, Mapping):
            raise ValueError(f"{path}: prediction #{index} must be an object")
        normalized.append(dict(record))
    return normalized


def _load_jsonl_prediction_records(text: str, path: Path) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for line_number, line in enumerate(text.splitlines(), start=1):
        stripped = line.strip()
        if not stripped:
            continue
        try:
            record = json.loads(stripped)
        except json.JSONDecodeError as exc:
            raise ValueError(f"{path}: invalid JSONL on line {line_number}: {exc}") from exc
        if not isinstance(record, Mapping):
            raise ValueError(f"{path}: JSONL line {line_number} must be an object")
        records.append(dict(record))
    return records


def _validate_prediction_submission_metadata(payload: Any, suite: str) -> None:
    if not isinstance(payload, Mapping):
        return
    suite_id, suite_version = _suite_identity(suite)
    suite_hash = build_suite_hash(suite=suite)
    errors = []
    if payload.get("schema") not in {None, PREDICTION_SCHEMA, *LEGACY_PREDICTION_SCHEMAS}:
        errors.append(f"unsupported prediction schema {payload.get('schema')!r}")
    if "suite_id" in payload and payload.get("suite_id") != suite_id:
        errors.append(f"suite_id mismatch: expected {suite_id!r}, got {payload.get('suite_id')!r}")
    if "suite_version" in payload and payload.get("suite_version") != suite_version:
        errors.append(f"suite_version mismatch: expected {suite_version!r}, got {payload.get('suite_version')!r}")
    if "suite_hash" in payload and payload.get("suite_hash") != suite_hash:
        errors.append(f"suite_hash mismatch: expected {suite_hash!r}, got {payload.get('suite_hash')!r}")
    if errors:
        raise ValueError("; ".join(errors))


def _normalize_prediction_records(
    predictions: Iterable[Mapping[str, Any]],
    suite_cases: Sequence[BenchmarkCase],
) -> dict[str, dict[str, Any]]:
    canonical_ids = [case.id for case in suite_cases]
    canonical_id_set = set(canonical_ids)
    prediction_by_case: dict[str, dict[str, Any]] = {}
    errors: list[str] = []

    for index, prediction in enumerate(predictions, start=1):
        if not isinstance(prediction, Mapping):
            errors.append(f"prediction #{index} must be an object")
            continue
        case_id = str(prediction.get("case_id") or "").strip()
        if not case_id:
            errors.append(f"prediction #{index} is missing case_id")
            continue
        if case_id not in canonical_id_set:
            errors.append(f"{case_id}: unknown case_id")
            continue
        if case_id in prediction_by_case:
            errors.append(f"{case_id}: duplicate prediction")
            continue
        if "predicted" not in prediction:
            errors.append(f"{case_id}: missing predicted label")
            continue
        try:
            label = _normalize_prediction_label(prediction.get("predicted"))
            detector_score = _normalize_detector_score(prediction.get("detector_score", 0.0))
        except ValueError as exc:
            errors.append(f"{case_id}: {exc}")
            continue
        try:
            detector_note = _normalize_optional_text(prediction.get("detector_note"))
            rationale = _normalize_optional_text(prediction.get("rationale", detector_note))
            evidence = _normalize_evidence(prediction.get("evidence", []))
        except ValueError as exc:
            errors.append(f"{case_id}: {exc}")
            continue
        prediction_by_case[case_id] = {
            "predicted": label,
            "detector_score": detector_score,
            "detector_note": detector_note,
            "rationale": rationale,
            "evidence": evidence,
        }

    missing = [case_id for case_id in canonical_ids if case_id not in prediction_by_case]
    if missing:
        errors.append(f"missing predictions: {', '.join(missing)}")
    if errors:
        raise ValueError("Invalid prediction records: " + "; ".join(errors))
    return prediction_by_case


def _normalize_prediction_label(raw_label: Any) -> str:
    if isinstance(raw_label, ContradictionType):
        value = raw_label.value
    elif raw_label is None:
        value = ContradictionType.NONE.value
    else:
        value = str(raw_label).strip().lower().replace("-", "_")
    aliases = {
        "no_contradiction": ContradictionType.NONE.value,
        "non_contradiction": ContradictionType.NONE.value,
        "not_contradiction": ContradictionType.NONE.value,
        "null": ContradictionType.NONE.value,
    }
    value = aliases.get(value, value)
    if value not in set(_label_values()):
        raise ValueError(f"invalid predicted label {raw_label!r}")
    return value


def _normalize_detector_score(raw_score: Any) -> float:
    if raw_score is None:
        return 0.0
    if isinstance(raw_score, bool):
        raise ValueError("detector_score must be numeric")
    try:
        score = float(raw_score)
    except (TypeError, ValueError) as exc:
        raise ValueError("detector_score must be numeric") from exc
    if not math.isfinite(score):
        raise ValueError("detector_score must be finite")
    if score < 0.0 or score > 1.0:
        raise ValueError("detector_score must be between 0 and 1")
    return score


def _normalize_optional_text(raw_value: Any) -> str | None:
    if raw_value is None:
        return None
    value = str(raw_value).strip()
    return value or None


def _normalize_evidence(raw_evidence: Any) -> list[str]:
    if raw_evidence is None:
        return []
    if isinstance(raw_evidence, str):
        value = raw_evidence.strip()
        return [value] if value else []
    if not isinstance(raw_evidence, SequenceABC) or isinstance(raw_evidence, (bytes, bytearray)):
        raise ValueError("evidence must be a string or a list of strings")
    evidence = []
    for item in raw_evidence:
        if item is None:
            continue
        value = str(item).strip()
        if value:
            evidence.append(value)
    return evidence


def _prediction_template_record(case: BenchmarkCase) -> dict[str, Any]:
    return {
        "case_id": case.id,
        "premise": case.premise,
        "query": case.query,
        "predicted": ContradictionType.NONE.value,
        "detector_score": 0.0,
        "detector_note": "",
        "rationale": "",
        "evidence": [],
    }


def _case_counter(values: Iterable[str], keys: Sequence[str] | None = None) -> dict[str, int]:
    counts = {key: 0 for key in (keys or [])}
    for value in values:
        key = str(value)
        counts[key] = counts.get(key, 0) + 1
    return dict(sorted(counts.items()))


def _case_hash_record(case: BenchmarkCase | Mapping[str, Any]) -> dict[str, Any]:
    if isinstance(case, BenchmarkCase):
        return case.to_record()
    return dict(case)


def _suite_identity(suite: str) -> tuple[str, str]:
    key = _suite_key(suite)
    if key == "controls":
        return CONTROL_SUITE_ID, CONTROL_SUITE_VERSION
    if key == "multihop":
        return MULTIHOP_SUITE_ID, MULTIHOP_SUITE_VERSION
    if key == "adversarial":
        return ADVERSARIAL_SUITE_ID, ADVERSARIAL_SUITE_VERSION
    if key == "standard-v0.1.0":
        return SUITE_ID, STANDARD_SUITE_V0_1_0_VERSION
    return SUITE_ID, SUITE_VERSION


def _suite_key(suite: str) -> str:
    normalized = str(suite or DEFAULT_SUITE).strip().lower().replace("_", "-")
    aliases = {
        "contradiction": "standard",
        "contradiction-v0.1.1": "standard",
        "standard": "standard",
        "standard-v0.1.1": "standard",
        SUITE_ID: "standard",
        f"{SUITE_ID}:{SUITE_VERSION}": "standard",
        "contradiction-v0.1.0": "standard-v0.1.0",
        "standard-v0.1.0": "standard-v0.1.0",
        f"{SUITE_ID}:{STANDARD_SUITE_V0_1_0_VERSION}": "standard-v0.1.0",
        "contradiction-adversarial": "adversarial",
        "adversarial": "adversarial",
        ADVERSARIAL_SUITE_ID: "adversarial",
        f"{ADVERSARIAL_SUITE_ID}:{ADVERSARIAL_SUITE_VERSION}": "adversarial",
        "contradiction-multihop": "multihop",
        "multi-hop": "multihop",
        "multihop": "multihop",
        MULTIHOP_SUITE_ID: "multihop",
        f"{MULTIHOP_SUITE_ID}:{MULTIHOP_SUITE_VERSION}": "multihop",
        "contradiction-controls": "controls",
        "controls": "controls",
        "control": "controls",
        "false-positive-controls": "controls",
        CONTROL_SUITE_ID: "controls",
        f"{CONTROL_SUITE_ID}:{CONTROL_SUITE_VERSION}": "controls",
    }
    if normalized not in aliases:
        raise ValueError(f"Unknown benchmark suite: {suite!r}")
    return aliases[normalized]


def _suite_key_from_report(report: Mapping[str, Any]) -> str:
    suite_id = str(report.get("suite_id") or SUITE_ID)
    suite_version = str(report.get("suite_version") or SUITE_VERSION)
    return _suite_key(f"{suite_id}:{suite_version}")


def _score_case_results(case_results: list[dict[str, Any]]) -> dict[str, Any]:
    labels = _label_values()
    confusion = _confusion_matrix(case_results, labels)
    per_class = _per_class_metrics(confusion, labels)
    detection = _binary_detection_metrics(case_results)
    exact_correct = sum(1 for item in case_results if item["type_correct"])
    contradiction_cases = [item for item in case_results if item["expected"] != ContradictionType.NONE.value]
    contradiction_correct = sum(1 for item in contradiction_cases if item["type_correct"])
    contradiction_labels = [label.value for label in ContradictionType if label != ContradictionType.NONE]
    contradiction_macro_f1 = _mean(
        per_class[label]["f1"]
        for label in contradiction_labels
        if per_class[label]["support"] > 0
    )
    coverage_index = _coverage_index(per_class, contradiction_labels)
    type_accuracy = exact_correct / max(len(case_results), 1)
    contradiction_type_accuracy = contradiction_correct / max(len(contradiction_cases), 1)
    overall_score = round(
        100
        * (
            0.45 * contradiction_macro_f1
            + 0.25 * type_accuracy
            + 0.20 * detection["f1"]
            + 0.10 * coverage_index
        ),
        2,
    )
    return {
        "overall_score": overall_score,
        "metrics": {
            "type_accuracy": round(type_accuracy, 6),
            "contradiction_type_accuracy": round(contradiction_type_accuracy, 6),
            "contradiction_macro_f1": round(contradiction_macro_f1, 6),
            "coverage_index": round(coverage_index, 6),
            "calibration": _binary_confidence_calibration(case_results),
            "detection": detection,
            "per_class": per_class,
            "slices": _slice_metrics(case_results),
        },
        "confusion_matrix": confusion,
        "failures": [item for item in case_results if not item["type_correct"]],
    }


def _explanation_audit(case_results: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    case_count = len(case_results)
    rationale_count = sum(1 for item in case_results if _has_rationale(item))
    evidence_count = sum(1 for item in case_results if _has_evidence(item))
    explanation_ready_count = sum(1 for item in case_results if _has_rationale(item) and _has_evidence(item))
    correct_items = [item for item in case_results if item.get("type_correct") is True]
    correct_explanation_ready_count = sum(
        1 for item in correct_items if _has_rationale(item) and _has_evidence(item)
    )
    return {
        "case_count": case_count,
        "rationale_count": rationale_count,
        "evidence_count": evidence_count,
        "explanation_ready_count": explanation_ready_count,
        "rationale_coverage": round(rationale_count / max(case_count, 1), 6),
        "evidence_coverage": round(evidence_count / max(case_count, 1), 6),
        "explanation_ready_rate": round(explanation_ready_count / max(case_count, 1), 6),
        "correct_explanation_ready_rate": round(
            correct_explanation_ready_count / max(len(correct_items), 1),
            6,
        ),
    }


def _has_rationale(item: Mapping[str, Any]) -> bool:
    return bool(_normalize_optional_text(item.get("rationale")))


def _has_evidence(item: Mapping[str, Any]) -> bool:
    try:
        return bool(_normalize_evidence(item.get("evidence", [])))
    except ValueError:
        return False


def _label_values() -> list[str]:
    return [label.value for label in ContradictionType]


def _expect_equal(report: Mapping[str, Any], key: str, expected: Any, errors: list[str]) -> None:
    actual = report.get(key)
    if actual != expected:
        errors.append(f"{key} mismatch: expected {expected!r}, got {actual!r}")


def _is_contradiction(label: ContradictionType | str) -> bool:
    value = label.value if isinstance(label, ContradictionType) else label
    return value != ContradictionType.NONE.value


def _confusion_matrix(case_results: Iterable[Mapping[str, Any]], labels: Sequence[str]) -> dict[str, dict[str, int]]:
    matrix = {expected: {predicted: 0 for predicted in labels} for expected in labels}
    for item in case_results:
        matrix[str(item["expected"])][str(item["predicted"])] += 1
    return matrix


def _per_class_metrics(confusion: Mapping[str, Mapping[str, int]], labels: Sequence[str]) -> dict[str, dict[str, float]]:
    metrics = {}
    for label in labels:
        true_positive = confusion[label][label]
        false_positive = sum(confusion[other][label] for other in labels if other != label)
        false_negative = sum(count for predicted, count in confusion[label].items() if predicted != label)
        support = sum(confusion[label].values())
        precision = true_positive / max(true_positive + false_positive, 1)
        recall = true_positive / max(true_positive + false_negative, 1)
        f1 = 2 * precision * recall / max(precision + recall, 1e-9)
        metrics[label] = {
            "precision": round(precision, 6),
            "recall": round(recall, 6),
            "f1": round(f1, 6),
            "support": support,
        }
    return metrics


def _binary_detection_metrics(case_results: Iterable[Mapping[str, Any]]) -> dict[str, float | int]:
    true_positive = false_positive = false_negative = true_negative = 0
    for item in case_results:
        expected = _is_contradiction(str(item["expected"]))
        predicted = _is_contradiction(str(item["predicted"]))
        if expected and predicted:
            true_positive += 1
        elif not expected and predicted:
            false_positive += 1
        elif expected and not predicted:
            false_negative += 1
        else:
            true_negative += 1
    precision = true_positive / max(true_positive + false_positive, 1)
    recall = true_positive / max(true_positive + false_negative, 1)
    f1 = 2 * precision * recall / max(precision + recall, 1e-9)
    accuracy = (true_positive + true_negative) / max(
        true_positive + false_positive + false_negative + true_negative,
        1,
    )
    return {
        "precision": round(precision, 6),
        "recall": round(recall, 6),
        "f1": round(f1, 6),
        "accuracy": round(accuracy, 6),
        "true_positive": true_positive,
        "false_positive": false_positive,
        "false_negative": false_negative,
        "true_negative": true_negative,
    }


def _binary_confidence_calibration(
    case_results: Sequence[Mapping[str, Any]],
    bin_count: int = 10,
) -> dict[str, Any]:
    if not case_results:
        return {
            "bin_count": bin_count,
            "brier_score": 0.0,
            "expected_calibration_error": 0.0,
            "mean_confidence": 0.0,
            "positive_rate": 0.0,
            "bins": [],
        }

    pairs = [
        (
            float(item.get("detector_score", 0.0)),
            1.0 if _is_contradiction(str(item["expected"])) else 0.0,
        )
        for item in case_results
    ]
    total = len(pairs)
    brier_score = _mean((confidence - target) ** 2 for confidence, target in pairs)
    bins = []
    expected_calibration_error = 0.0
    for index in range(bin_count):
        lower = index / bin_count
        upper = (index + 1) / bin_count
        if index == bin_count - 1:
            bucket = [(confidence, target) for confidence, target in pairs if lower <= confidence <= upper]
        else:
            bucket = [(confidence, target) for confidence, target in pairs if lower <= confidence < upper]
        if bucket:
            mean_confidence = _mean(confidence for confidence, _target in bucket)
            empirical_rate = _mean(target for _confidence, target in bucket)
            expected_calibration_error += (len(bucket) / total) * abs(mean_confidence - empirical_rate)
        else:
            mean_confidence = 0.0
            empirical_rate = 0.0
        bins.append(
            {
                "lower": round(lower, 6),
                "upper": round(upper, 6),
                "case_count": len(bucket),
                "mean_confidence": round(mean_confidence, 6),
                "empirical_positive_rate": round(empirical_rate, 6),
            }
        )

    return {
        "bin_count": bin_count,
        "brier_score": round(brier_score, 6),
        "expected_calibration_error": round(expected_calibration_error, 6),
        "mean_confidence": round(_mean(confidence for confidence, _target in pairs), 6),
        "positive_rate": round(_mean(target for _confidence, target in pairs), 6),
        "bins": bins,
    }


def _slice_metrics(case_results: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, dict[str, Any]]]:
    return {
        "domain": _grouped_slice_metrics(case_results, "domain"),
        "difficulty": _grouped_slice_metrics(case_results, "difficulty"),
        "capability": _grouped_slice_metrics(case_results, "capability"),
        "tag": _tag_slice_metrics(case_results),
    }


def _grouped_slice_metrics(
    case_results: Sequence[Mapping[str, Any]],
    field: str,
) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for item in case_results:
        groups.setdefault(str(item[field]), []).append(item)
    return {name: _slice_summary(groups[name]) for name in sorted(groups)}


def _tag_slice_metrics(case_results: Sequence[Mapping[str, Any]]) -> dict[str, dict[str, Any]]:
    groups: dict[str, list[Mapping[str, Any]]] = {}
    for item in case_results:
        for tag in item.get("tags", []):
            groups.setdefault(str(tag), []).append(item)
    return {name: _slice_summary(groups[name]) for name in sorted(groups)}


def _slice_summary(items: Sequence[Mapping[str, Any]]) -> dict[str, Any]:
    case_count = len(items)
    exact_correct = sum(1 for item in items if item["type_correct"])
    contradiction_cases = [item for item in items if item["expected"] != ContradictionType.NONE.value]
    contradiction_correct = sum(1 for item in contradiction_cases if item["type_correct"])
    detection = _binary_detection_metrics(items)
    return {
        "case_count": case_count,
        "contradiction_case_count": len(contradiction_cases),
        "type_accuracy": round(exact_correct / max(case_count, 1), 6),
        "contradiction_type_accuracy": round(contradiction_correct / max(len(contradiction_cases), 1), 6),
        "detection_f1": detection["f1"],
        "failure_count": sum(1 for item in items if not item["type_correct"]),
    }


def _coverage_index(per_class: Mapping[str, Mapping[str, float]], contradiction_labels: Sequence[str]) -> float:
    covered = sum(1 for label in contradiction_labels if per_class[label]["support"] > 0 and per_class[label]["recall"] > 0)
    return covered / max(len(contradiction_labels), 1)


def _mean(values: Iterable[float]) -> float:
    values = list(values)
    return sum(values) / max(len(values), 1)


__all__ = [
    "BenchmarkCase",
    "ADVERSARIAL_SUITE_ID",
    "ADVERSARIAL_SUITE_VERSION",
    "CONTROL_SUITE_ID",
    "CONTROL_SUITE_VERSION",
    "DEFAULT_SUITE",
    "MULTIHOP_SUITE_ID",
    "MULTIHOP_SUITE_VERSION",
    "PREDICTION_SCHEMA",
    "REPORT_SCHEMA",
    "STANDARD_SUITE_V0_1_0_VERSION",
    "SUITE_ID",
    "SUITE_MANIFEST_SCHEMA",
    "SUITE_VERSION",
    "VALIDATION_SCHEMA",
    "build_adversarial_suite",
    "build_control_suite",
    "build_multihop_suite",
    "build_prediction_template",
    "build_suite",
    "build_suite_hash",
    "build_suite_manifest",
    "build_suite_profile",
    "build_standard_suite",
    "build_standard_suite_v0_1_0",
    "build_standard_suite_v0_1_1",
    "evaluate_prediction_file",
    "evaluate_prediction_records",
    "evaluate_standard_suite",
    "load_benchmark_report",
    "load_prediction_records",
    "suite_case_hash",
    "validate_benchmark_report",
    "write_benchmark_report",
    "write_prediction_template",
    "write_suite_manifest",
]
