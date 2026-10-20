from __future__ import annotations

from dataclasses import replace
from pathlib import Path
import tempfile
import subprocess
import sys
import unittest

from marked_bench.contradiction.engine import Claim, ContradictionType as Kind
from marked_bench.contradiction.multihop_reference import MultiHopReference, build_reference_report
from marked_bench.contradiction.benchmark_suite import validate_benchmark_report
from scripts.check_multihop_reference import audit_reference, build_evidence


class MultiHopReferenceTests(unittest.TestCase):
    def setUp(self):
        self.reference = MultiHopReference()

    def label(self, premise, query):
        proof = self.reference.explain(Claim("arbitrary", premise, query))
        return proof.type if proof else Kind.NONE

    def test_long_membership_chain_and_broken_link(self):
        premise = "Crate Zed belongs to shipment Red. Shipment Red belongs to bin Indigo. Bin Indigo has mass 20 kg."
        query = "Crate Zed has mass 21 kg."
        self.assertEqual(self.label(premise, query), Kind.PROPERTY_MISMATCH)
        self.assertEqual(self.label(premise.replace("Shipment Red belongs to bin Indigo. ", ""), query), Kind.NONE)
        proof = self.reference.explain(Claim("x", premise, query))
        self.assertEqual(len(proof.premises), 3)

    def test_cycle_terminates_and_order_is_irrelevant(self):
        premise = "Crate Zed belongs to bin Indigo. Bin Indigo belongs to crate Zed. Bin Indigo has mass 20 kg."
        query = "Crate Zed has mass 21 kg."
        self.assertEqual(self.label(premise, query), Kind.PROPERTY_MISMATCH)
        reversed_premise = "Bin Indigo has mass 20 kg. Bin Indigo belongs to crate Zed. Crate Zed belongs to bin Indigo."
        self.assertEqual(self.label(reversed_premise, query), Kind.PROPERTY_MISMATCH)

    def test_units_are_converted_not_compared_as_strings(self):
        premise = "Crate Zed belongs to bin Indigo. Bin Indigo has mass 0.45359237 kg."
        self.assertEqual(self.label(premise, "Crate Zed has mass 1 lb."), Kind.NONE)
        self.assertEqual(self.label(premise, "Crate Zed has mass 1 kg."), Kind.PROPERTY_MISMATCH)

    def test_conflicting_quantities_abstain(self):
        premise = "Crate Zed belongs to bin Indigo. Bin Indigo has mass 20 kg. Bin Indigo has mass 21 kg."
        self.assertEqual(self.label(premise, "Crate Zed has mass 21 kg."), Kind.NONE)

    def test_maximum_context_uses_linked_entity_not_other_numbers(self):
        premise = "Model Willow was evaluated under context profile Cedar. Context profile Cedar has a maximum context window of 2,048 tokens."
        self.assertEqual(self.label(premise, "The Willow evaluation used a 4,096 token maximum context window under profile Cedar."), Kind.PROPERTY_MISMATCH)
        self.assertEqual(self.label(premise, "The Other evaluation used a 4,096 token maximum context window under profile Cedar."), Kind.NONE)

    def test_definitional_membership_and_scope(self):
        premise = "A locked archive is defined as a record that cannot be edited after approval. Dataset Pine is classified as a locked archive."
        self.assertEqual(self.label(premise, "Pine was edited after approval."), Kind.DEFINITIONAL_VIOLATION)
        self.assertEqual(self.label(premise, "Pine was edited before approval."), Kind.NONE)
        self.assertEqual(self.label(premise, "Pine was not edited after approval."), Kind.NONE)

    def test_minimum_boundaries_and_subject_identity(self):
        rule = "Panel approval requires at least four independent reviewers. "
        for count, expected in ((3, Kind.DEFINITIONAL_VIOLATION), (4, Kind.NONE), (5, Kind.NONE)):
            with self.subTest(count=count):
                self.assertEqual(self.label(rule + f"Release West had exactly {count} independent reviewers.", "Release West satisfied panel approval."), expected)
        self.assertEqual(self.label(rule + "Release East had exactly two independent reviewers.", "Release West satisfied panel approval."), Kind.NONE)

    def test_universal_membership_and_nonuniversal_controls(self):
        premise = "Every critical deployment must complete safety review before operation. System Birch is a critical deployment."
        query = "System Birch entered operation without safety review."
        self.assertEqual(self.label(premise, query), Kind.UNIVERSAL_COUNTEREXAMPLE)
        self.assertEqual(self.label(premise.replace("Every", "Most"), query), Kind.NONE)
        self.assertEqual(self.label(premise.replace("System Birch is a critical deployment.", "System Ash is a critical deployment."), query), Kind.NONE)

    def test_collection_membership_is_required(self):
        premise = "All records in collection Elm are immutable after publication. Record N8 belongs to collection Elm."
        query = "Record N8 was edited after publication."
        self.assertEqual(self.label(premise, query), Kind.UNIVERSAL_COUNTEREXAMPLE)
        self.assertEqual(self.label(premise.replace("collection Elm.", "collection Other."), query), Kind.NONE)

    def test_temporal_interval_boundaries(self):
        for year, expected in ((2017, Kind.NONE), (2018, Kind.TEMPORAL_CONFLICT), (2020, Kind.TEMPORAL_CONFLICT), (2021, Kind.NONE)):
            with self.subTest(year=year):
                premise = f"Fleet Amber used manual approval for all launches from 2018 through 2020. System Oak launched under Fleet Amber in {year}."
                self.assertEqual(self.label(premise, "System Oak used automated approval at launch."), expected)

    def test_replacement_date_boundary_and_later_reversal(self):
        replacement = "API v8 replaced API v7 as the current endpoint on 2024-04-01. "
        for day, expected in (("2024-03-31", Kind.NONE), ("2024-04-01", Kind.TEMPORAL_CONFLICT), ("2025-01-01", Kind.TEMPORAL_CONFLICT)):
            with self.subTest(day=day):
                self.assertEqual(self.label(replacement + f"Request North was processed on {day}.", "Request North used API v7 as the current endpoint."), expected)
        reversal = "API v7 replaced API v8 as the current endpoint on 2024-05-01. "
        self.assertEqual(self.label(replacement + reversal + "Request North was processed on 2024-06-01.", "Request North used API v7 as the current endpoint."), Kind.NONE)

    def test_invalid_dates_and_unsupported_polarity_abstain(self):
        self.assertEqual(self.label("API v8 replaced API v7 as the current endpoint on 2024-99-99. Request North was processed on 2025-01-01.", "Request North used API v7 as the current endpoint."), Kind.NONE)
        self.assertEqual(self.label("Policy Ivory permits downloads. Service Birch inherits policy Ivory from platform Oak.", "Service Birch forbids downloads."), Kind.NONE)

    def test_ids_and_metadata_do_not_select_rules(self):
        claim = Claim("none", "Crate A7 belongs to bin B8. Bin B8 has mass 20 kg.", "Crate A7 has mass 21 kg.")
        altered = replace(claim, id="direct-negation-answer", domain="negation", metadata={"expected": "direct_negation"})
        self.assertEqual(self.reference.explain(claim), self.reference.explain(altered))
        self.assertEqual(self.reference.detect(altered).claim_id, altered.id)

    def test_public_report_validates_and_is_deterministic(self):
        report = build_reference_report()
        self.assertEqual(report, build_reference_report())
        validation = validate_benchmark_report(report)
        self.assertTrue(validation["valid"], validation["errors"])
        self.assertEqual(report["suite_hash"], "07a2bb9c0e8356d1cdab98b5b1b35a3c8bd29beff695816dfb151dbb5f6d0d1f")
        for row in report["case_results"]:
            if row["predicted"] != "none":
                self.assertGreaterEqual(len(row["evidence"]), 2)

    def test_public_invariance_and_ablation_checks(self):
        audit = audit_reference()
        self.assertEqual(audit["invariance_checks"], 90)
        self.assertGreaterEqual(audit["required_fact_ablations"], 12)
        report, document = build_evidence()
        self.assertGreater(report["overall_score"], 45.93)
        self.assertIn("not a held-out evaluation split", document)

    def test_packaged_module_entry_point(self):
        with tempfile.TemporaryDirectory(prefix="marked-bench-reference-test-") as temporary:
            result = subprocess.run(
                [sys.executable, "-m", "marked_bench.contradiction.multihop_reference", "--report", str(Path(temporary) / "report.json")],
                cwd=Path(__file__).resolve().parents[1], capture_output=True, text=True, timeout=30,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("MultiHopReference:", result.stdout)


if __name__ == "__main__":
    unittest.main()
