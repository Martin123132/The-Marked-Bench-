import json
from pathlib import Path
import shutil
from contextlib import redirect_stdout
from io import StringIO
import unittest

from marked_bench.benchmark_leaderboard import LEADERBOARD_SCHEMA, build_leaderboard, report_sha256
from marked_bench.benchmark_adoption import (
    ADOPTION_PACKET_SCHEMA,
    build_adoption_packet,
    load_adoption_packet,
    validate_adoption_packet,
)
from marked_bench.benchmark_claim import (
    RESULT_CLAIM_SCHEMA,
    build_result_claim,
    load_result_claim,
    validate_result_claim,
)
from marked_bench.benchmark_change_control import (
    CHANGE_CONTROL_SCHEMA,
    build_change_control,
    load_change_control,
    validate_change_control,
)
from marked_bench.benchmark_release import RELEASE_MANIFEST_SCHEMA, build_release_manifest, file_sha256
from marked_bench.benchmark_registry import REGISTRY_SCHEMA, build_benchmark_registry
from marked_bench.benchmark_review import (
    REVIEW_SCHEMA,
    RUBRIC_DIMENSIONS,
    build_submission_review,
    load_submission_review,
    validate_submission_review,
    write_submission_review,
)
from marked_bench.benchmark_result_card import (
    RESULT_CARD_SCHEMA,
    build_result_card,
    load_result_card,
    validate_result_card,
)
from marked_bench.benchmark_submission import (
    SUBMISSION_BUNDLE_SCHEMA,
    SUBMISSION_SCHEMA,
    build_leaderboard_submission,
    build_submission_bundle,
    load_submission_bundle,
    validate_submission_bundle,
    validate_leaderboard_submission,
    write_leaderboard_submission,
    write_submission_bundle,
)
from marked_bench.benchmark_technical_note import build_technical_note
from marked_bench.schema_validation import validate_json_file, validate_json_schema
from marked_bench.contradiction.benchmark_suite import (
    ADVERSARIAL_SUITE_ID,
    CONTROL_SUITE_ID,
    MULTIHOP_SUITE_ID,
    PREDICTION_SCHEMA,
    REPORT_SCHEMA,
    SUITE_ID,
    build_adversarial_suite,
    build_control_suite,
    build_multihop_suite,
    build_prediction_template,
    build_suite_hash,
    build_suite_manifest,
    build_suite_profile,
    build_standard_suite,
    evaluate_prediction_file,
    evaluate_prediction_records,
    evaluate_standard_suite,
    load_prediction_records,
    suite_case_hash,
    validate_benchmark_report,
    write_benchmark_report,
)
from marked_bench.contradiction.engine import Claim, ContradictionType
from marked_bench.benchmark_cli import main as benchmark_main
from marked_bench.benchmark_conformance import (
    CONFORMANCE_REPORT_SCHEMA,
    build_conformance_report,
    load_conformance_report,
    validate_conformance_report,
)
from marked_bench.benchmark_evidence import (
    EVIDENCE_LEDGER_SCHEMA,
    build_evidence_ledger,
    load_evidence_ledger,
    validate_evidence_ledger,
)
from marked_bench.benchmark_implementation import (
    IMPLEMENTATION_KIT_SCHEMA,
    build_implementation_kit,
    load_implementation_kit,
    validate_implementation_kit,
)
from marked_bench.benchmark_standard_profile import (
    STANDARD_PROFILE_SCHEMA,
    build_standard_profile,
    load_standard_profile,
    validate_standard_profile,
)
from marked_bench.benchmark_scoring_compatibility import (
    SCORING_COMPATIBILITY_SCHEMA,
    build_scoring_compatibility_profile,
    load_scoring_compatibility_profile,
    validate_scoring_compatibility_profile,
)
from marked_bench.benchmark_scoring_spec import (
    SCORING_SPEC_SCHEMA,
    build_scoring_spec,
    build_scoring_spec_markdown,
    load_scoring_spec,
    validate_scoring_spec,
)
from marked_bench.benchmark_publication import (
    PUBLICATION_PACKET_SCHEMA,
    build_publication_packet,
    create_publication_packet,
    load_publication_packet,
    validate_publication_packet,
)
from marked_bench.examples.external_submission_demo import run_demo as run_external_submission_demo


class BenchmarkSuiteTests(unittest.TestCase):
    def test_standard_suite_has_stable_public_shape(self) -> None:
        cases = build_standard_suite()
        ids = [case.id for case in cases]

        self.assertGreaterEqual(len(cases), 15)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(case.id.startswith("marked-") for case in cases))
        self.assertTrue(any(case.expected == ContradictionType.NONE for case in cases))
        self.assertEqual(
            {
                ContradictionType.DIRECT_NEGATION,
                ContradictionType.PROPERTY_MISMATCH,
                ContradictionType.DEFINITIONAL_VIOLATION,
                ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
                ContradictionType.TEMPORAL_CONFLICT,
            },
            {case.expected for case in cases if case.expected != ContradictionType.NONE},
        )

    def test_adversarial_suite_has_stable_public_shape(self) -> None:
        cases = build_adversarial_suite()
        ids = [case.id for case in cases]

        self.assertGreaterEqual(len(cases), 15)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(case.id.startswith("marked-adv-") for case in cases))
        self.assertTrue(any(case.expected == ContradictionType.NONE for case in cases))
        self.assertEqual(
            {
                ContradictionType.DIRECT_NEGATION,
                ContradictionType.PROPERTY_MISMATCH,
                ContradictionType.DEFINITIONAL_VIOLATION,
                ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
                ContradictionType.TEMPORAL_CONFLICT,
            },
            {case.expected for case in cases if case.expected != ContradictionType.NONE},
        )

    def test_multihop_suite_has_stable_public_shape(self) -> None:
        cases = build_multihop_suite()
        ids = [case.id for case in cases]

        self.assertGreaterEqual(len(cases), 15)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(case.id.startswith("marked-hop-") for case in cases))
        self.assertTrue(any(case.expected == ContradictionType.NONE for case in cases))
        self.assertTrue(all("multihop" in case.tags for case in cases))
        self.assertEqual(
            {
                ContradictionType.DIRECT_NEGATION,
                ContradictionType.PROPERTY_MISMATCH,
                ContradictionType.DEFINITIONAL_VIOLATION,
                ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
                ContradictionType.TEMPORAL_CONFLICT,
            },
            {case.expected for case in cases if case.expected != ContradictionType.NONE},
        )

    def test_control_suite_has_stable_public_shape(self) -> None:
        cases = build_control_suite()
        ids = [case.id for case in cases]

        self.assertGreaterEqual(len(cases), 15)
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(all(case.id.startswith("marked-ctrl-") for case in cases))
        self.assertGreater(
            sum(1 for case in cases if case.expected == ContradictionType.NONE),
            sum(1 for case in cases if case.expected != ContradictionType.NONE),
        )
        self.assertTrue(all("control-track" in case.tags for case in cases))
        self.assertEqual(
            {
                ContradictionType.DIRECT_NEGATION,
                ContradictionType.PROPERTY_MISMATCH,
                ContradictionType.DEFINITIONAL_VIOLATION,
                ContradictionType.UNIVERSAL_COUNTEREXAMPLE,
                ContradictionType.TEMPORAL_CONFLICT,
            },
            {case.expected for case in cases if case.expected != ContradictionType.NONE},
        )

    def test_checked_in_suite_manifest_matches_code(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "suites" / "marked_bench_contradiction_standard_v0_1_0.json"

        manifest = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(manifest, build_suite_manifest())
        self.assertEqual(manifest["suite_hash"], build_suite_hash())
        self.assertEqual(manifest["profile"], build_suite_profile())
        self.assertEqual(manifest["profile"]["case_count"], len(build_standard_suite()))
        self.assertEqual(manifest["profile"]["label_counts"]["none"], 6)
        self.assertTrue(manifest["profile"]["quality_gates"]["requires_all_contradiction_labels"])

    def test_checked_in_adversarial_suite_manifest_matches_code(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "suites" / "marked_bench_contradiction_adversarial_v0_2_0.json"

        manifest = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(manifest, build_suite_manifest(suite="contradiction-adversarial"))
        self.assertEqual(manifest["suite_id"], ADVERSARIAL_SUITE_ID)
        self.assertEqual(manifest["suite_hash"], build_suite_hash(suite="contradiction-adversarial"))
        self.assertEqual(manifest["profile"], build_suite_profile(suite="contradiction-adversarial"))

    def test_checked_in_multihop_suite_manifest_matches_code(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "suites" / "marked_bench_contradiction_multihop_v0_3_0.json"

        manifest = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(manifest, build_suite_manifest(suite="contradiction-multihop"))
        self.assertEqual(manifest["suite_id"], MULTIHOP_SUITE_ID)
        self.assertEqual(manifest["suite_hash"], build_suite_hash(suite="contradiction-multihop"))
        self.assertEqual(manifest["profile"], build_suite_profile(suite="contradiction-multihop"))

    def test_checked_in_control_suite_manifest_matches_code(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "suites" / "marked_bench_contradiction_controls_v0_4_0.json"

        manifest = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(manifest, build_suite_manifest(suite="contradiction-controls"))
        self.assertEqual(manifest["suite_id"], CONTROL_SUITE_ID)
        self.assertEqual(manifest["suite_hash"], build_suite_hash(suite="contradiction-controls"))
        self.assertEqual(manifest["profile"], build_suite_profile(suite="contradiction-controls"))

    def test_checked_in_benchmark_registry_matches_code(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "benchmark_registry.json"

        registry = json.loads(path.read_text(encoding="utf-8"))

        self.assertEqual(registry, build_benchmark_registry())
        self.assertEqual(registry["schema"], REGISTRY_SCHEMA)
        self.assertEqual(
            [track["name"] for track in registry["tracks"]],
            [
                "contradiction",
                "contradiction-adversarial",
                "contradiction-multihop",
                "contradiction-controls",
            ],
        )
        self.assertEqual(registry["default_track"], "contradiction-multihop")
        self.assertIn("profile", registry["tracks"][0])
        self.assertEqual(registry["tracks"][0]["profile"], build_suite_profile())

    def test_public_json_schemas_cover_current_default_track(self) -> None:
        root = Path(__file__).resolve().parent.parent
        prediction_schema = json.loads(
            (root / "schemas" / "contradiction_predictions.schema.json").read_text(encoding="utf-8-sig")
        )
        report_schema = json.loads(
            (root / "schemas" / "contradiction_benchmark_report.schema.json").read_text(encoding="utf-8-sig")
        )
        suite_schema = json.loads(
            (root / "schemas" / "contradiction_suite_manifest.schema.json").read_text(encoding="utf-8-sig")
        )

        self.assertEqual(
            prediction_schema["oneOf"][1]["properties"]["schema"]["const"],
            PREDICTION_SCHEMA,
        )
        self.assertIn(MULTIHOP_SUITE_ID, prediction_schema["oneOf"][1]["properties"]["suite_id"]["enum"])
        self.assertIn(CONTROL_SUITE_ID, prediction_schema["oneOf"][1]["properties"]["suite_id"]["enum"])
        self.assertIn("0.3.0", prediction_schema["oneOf"][1]["properties"]["suite_version"]["enum"])
        self.assertIn("0.4.0", prediction_schema["oneOf"][1]["properties"]["suite_version"]["enum"])
        self.assertIn("rationale", prediction_schema["$defs"]["prediction"]["properties"])
        self.assertIn("evidence", prediction_schema["$defs"]["prediction"]["properties"])
        self.assertEqual(report_schema["properties"]["schema"]["const"], REPORT_SCHEMA)
        self.assertIn(MULTIHOP_SUITE_ID, report_schema["properties"]["suite_id"]["enum"])
        self.assertIn(CONTROL_SUITE_ID, report_schema["properties"]["suite_id"]["enum"])
        self.assertIn("0.3.0", report_schema["properties"]["suite_version"]["enum"])
        self.assertIn("0.4.0", report_schema["properties"]["suite_version"]["enum"])
        self.assertIn("explanation_audit", report_schema["required"])
        self.assertIn("rationale", report_schema["$defs"]["case_result"]["required"])
        self.assertIn("evidence", report_schema["$defs"]["case_result"]["required"])
        self.assertIn(MULTIHOP_SUITE_ID, suite_schema["properties"]["suite_id"]["enum"])
        self.assertIn(CONTROL_SUITE_ID, suite_schema["properties"]["suite_id"]["enum"])
        self.assertIn("0.3.0", suite_schema["properties"]["suite_version"]["enum"])
        self.assertIn("0.4.0", suite_schema["properties"]["suite_version"]["enum"])

    def test_public_json_artifacts_conform_to_public_schemas(self) -> None:
        root = Path(__file__).resolve().parent.parent
        checked_pairs = [
            ("benchmark_registry.json", "schemas/benchmark_registry.schema.json"),
            ("releases/marked_bench_release_v0_4_8.json", "schemas/release_manifest.schema.json"),
            ("conformance/marked_bench_conformance_v0_4_8.json", "schemas/conformance_report.schema.json"),
            ("adoption/marked_bench_adoption_packet_v0_4_8.json", "schemas/adoption_packet.schema.json"),
            ("adoption/third_party_evidence_ledger_v0_4_8.json", "schemas/third_party_evidence_ledger.schema.json"),
            ("adoption/marked_bench_implementation_kit_v0_4_8.json", "schemas/implementation_kit.schema.json"),
            ("standard/marked_bench_standard_profile_v0_4_8.json", "schemas/standard_profile.schema.json"),
            ("standard/marked_bench_change_control_v0_4_8.json", "schemas/change_control.schema.json"),
            ("standard/marked_bench_scoring_compatibility_v0_4_8.json", "schemas/scoring_compatibility.schema.json"),
            ("standard/marked_bench_scoring_spec_v0_4_8.json", "schemas/scoring_spec.schema.json"),
            ("suites/marked_bench_contradiction_standard_v0_1_0.json", "schemas/contradiction_suite_manifest.schema.json"),
            ("suites/marked_bench_contradiction_adversarial_v0_2_0.json", "schemas/contradiction_suite_manifest.schema.json"),
            ("suites/marked_bench_contradiction_multihop_v0_3_0.json", "schemas/contradiction_suite_manifest.schema.json"),
            ("suites/marked_bench_contradiction_controls_v0_4_0.json", "schemas/contradiction_suite_manifest.schema.json"),
            ("baselines/contradiction_engine_multihop_v0_3_0.json", "schemas/contradiction_benchmark_report.schema.json"),
            ("baselines/contradiction_engine_controls_v0_4_0.json", "schemas/contradiction_benchmark_report.schema.json"),
            ("leaderboard/leaderboard_multihop_v0_3_0.json", "schemas/leaderboard.schema.json"),
            ("leaderboard/leaderboard_controls_v0_4_0.json", "schemas/leaderboard.schema.json"),
            ("submissions/example_external_jsonl/example_external_result_card.json", "schemas/result_card.schema.json"),
            ("submissions/example_publication_packet/publication_packet.json", "schemas/publication_packet.schema.json"),
            ("submissions/example_publication_packet/result_claim.json", "schemas/result_claim.schema.json"),
        ]

        for artifact_path, schema_path in checked_pairs:
            with self.subTest(artifact=artifact_path):
                errors = validate_json_file(root / artifact_path, root / schema_path)
                self.assertEqual(errors, [])

        prediction_schema = json.loads(
            (root / "schemas" / "contradiction_predictions.schema.json").read_text(encoding="utf-8-sig")
        )
        template = build_prediction_template(suite="contradiction-multihop")
        self.assertEqual(
            validate_json_schema(
                template,
                prediction_schema,
                schema_path=root / "schemas" / "contradiction_predictions.schema.json",
            ),
            [],
        )

    def test_schema_validator_rejects_invalid_public_artifact_shape(self) -> None:
        root = Path(__file__).resolve().parent.parent
        schema = json.loads(
            (root / "schemas" / "contradiction_benchmark_report.schema.json").read_text(encoding="utf-8-sig")
        )
        report = evaluate_standard_suite(system_name="SchemaTamper")
        report.pop("case_results")

        errors = validate_json_schema(
            report,
            schema,
            schema_path=root / "schemas" / "contradiction_benchmark_report.schema.json",
        )

        self.assertTrue(any("missing required property 'case_results'" in error for error in errors))

    def test_public_registry_advertises_submission_review_schema(self) -> None:
        registry = build_benchmark_registry()

        self.assertEqual(registry["schema_ids"]["submission_review"], REVIEW_SCHEMA)
        self.assertEqual(registry["schemas"]["submission_review"], "schemas/submission_review.schema.json")
        self.assertEqual(registry["schema_ids"]["publication_packet"], PUBLICATION_PACKET_SCHEMA)
        self.assertEqual(registry["schemas"]["publication_packet"], "schemas/publication_packet.schema.json")
        self.assertEqual(registry["schema_ids"]["result_claim"], RESULT_CLAIM_SCHEMA)
        self.assertEqual(registry["schemas"]["result_claim"], "schemas/result_claim.schema.json")
        self.assertEqual(registry["schema_ids"]["implementation_kit"], IMPLEMENTATION_KIT_SCHEMA)
        self.assertEqual(registry["schemas"]["implementation_kit"], "schemas/implementation_kit.schema.json")
        self.assertEqual(registry["schema_ids"]["standard_profile"], STANDARD_PROFILE_SCHEMA)
        self.assertEqual(registry["schemas"]["standard_profile"], "schemas/standard_profile.schema.json")
        self.assertEqual(registry["schema_ids"]["change_control"], CHANGE_CONTROL_SCHEMA)
        self.assertEqual(registry["schemas"]["change_control"], "schemas/change_control.schema.json")
        self.assertEqual(registry["schema_ids"]["scoring_compatibility"], SCORING_COMPATIBILITY_SCHEMA)
        self.assertEqual(registry["schemas"]["scoring_compatibility"], "schemas/scoring_compatibility.schema.json")
        self.assertEqual(registry["schema_ids"]["scoring_spec"], SCORING_SPEC_SCHEMA)
        self.assertEqual(registry["schemas"]["scoring_spec"], "schemas/scoring_spec.schema.json")
        self.assertEqual(registry["schema_ids"]["result_card"], RESULT_CARD_SCHEMA)
        self.assertEqual(registry["schemas"]["result_card"], "schemas/result_card.schema.json")
        self.assertEqual(registry["schema_ids"]["adoption_packet"], ADOPTION_PACKET_SCHEMA)
        self.assertEqual(registry["schemas"]["adoption_packet"], "schemas/adoption_packet.schema.json")
        self.assertEqual(registry["schema_ids"]["third_party_evidence_ledger"], EVIDENCE_LEDGER_SCHEMA)
        self.assertEqual(
            registry["schemas"]["third_party_evidence_ledger"],
            "schemas/third_party_evidence_ledger.schema.json",
        )

    def test_checked_in_release_manifest_matches_current_artifacts(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "releases" / "marked_bench_release_v0_4_8.json"

        manifest = json.loads(path.read_text(encoding="utf-8"))
        artifact_paths = {entry["path"] for entry in manifest["artifacts"]}

        self.assertEqual(manifest, build_release_manifest(root))
        self.assertEqual(manifest["schema"], RELEASE_MANIFEST_SCHEMA)
        self.assertEqual(manifest["registry_sha256"], file_sha256(root / "benchmark_registry.json"))
        self.assertGreater(manifest["artifact_count"], 20)
        self.assertIn("submissions/example_external_jsonl/predictions.jsonl", artifact_paths)
        self.assertIn("submissions/example_external_jsonl/example_external_submission_review.json", artifact_paths)
        self.assertIn("conformance/marked_bench_conformance_v0_4_8.json", artifact_paths)
        self.assertIn("standard/marked_bench_standard_profile_v0_4_8.json", artifact_paths)
        self.assertIn("standard/marked_bench_change_control_v0_4_8.json", artifact_paths)
        self.assertIn("standard/marked_bench_scoring_compatibility_v0_4_8.json", artifact_paths)
        self.assertIn("standard/marked_bench_scoring_spec_v0_4_8.json", artifact_paths)
        self.assertIn("adoption/marked_bench_adoption_packet_v0_4_8.json", artifact_paths)
        self.assertIn("adoption/third_party_evidence_ledger_v0_4_8.json", artifact_paths)
        self.assertIn("adoption/marked_bench_implementation_kit_v0_4_8.json", artifact_paths)
        self.assertIn("adoption/implementation_kit/github_actions_validate_result.yml", artifact_paths)
        self.assertIn("suites/marked_bench_contradiction_controls_v0_4_0.json", artifact_paths)
        self.assertIn("leaderboard/leaderboard_controls_v0_4_0.json", artifact_paths)
        self.assertIn("docs/ANNOUNCEMENT_PACKAGE.md", artifact_paths)
        self.assertIn("docs/SCORING_SPEC.md", artifact_paths)
        self.assertIn("docs/THIRD_PARTY_EVIDENCE.md", artifact_paths)
        self.assertIn("schemas/publication_packet.schema.json", artifact_paths)
        self.assertIn("schemas/result_claim.schema.json", artifact_paths)
        self.assertIn("schemas/implementation_kit.schema.json", artifact_paths)
        self.assertIn("schemas/standard_profile.schema.json", artifact_paths)
        self.assertIn("schemas/change_control.schema.json", artifact_paths)
        self.assertIn("schemas/scoring_compatibility.schema.json", artifact_paths)
        self.assertIn("schemas/scoring_spec.schema.json", artifact_paths)
        self.assertIn("schemas/adoption_packet.schema.json", artifact_paths)
        self.assertIn("schemas/third_party_evidence_ledger.schema.json", artifact_paths)
        self.assertIn("submissions/example_external_jsonl/example_external_result_card.json", artifact_paths)
        self.assertIn("submissions/example_publication_packet/publication_packet.json", artifact_paths)
        self.assertIn("submissions/example_publication_packet/result_claim.json", artifact_paths)

    def test_checked_in_conformance_report_matches_current_evidence(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "conformance" / "marked_bench_conformance_v0_4_8.json"

        report = load_conformance_report(path)
        validation = validate_conformance_report(report, root=root)

        self.assertEqual(report, build_conformance_report(root))
        self.assertEqual(report["schema"], CONFORMANCE_REPORT_SCHEMA)
        self.assertTrue(report["passed"], report["failures"])
        self.assertIn("checked_publication_packets_valid", [check["name"] for check in report["checks"]])
        self.assertIn("checked_result_claims_valid", [check["name"] for check in report["checks"]])
        self.assertIn("adoption_packet_valid", [check["name"] for check in report["checks"]])
        self.assertIn("third_party_evidence_ledger_valid", [check["name"] for check in report["checks"]])
        self.assertIn("implementation_kit_valid", [check["name"] for check in report["checks"]])
        self.assertIn("standard_profile_valid", [check["name"] for check in report["checks"]])
        self.assertIn("change_control_valid", [check["name"] for check in report["checks"]])
        self.assertIn("scoring_compatibility_valid", [check["name"] for check in report["checks"]])
        self.assertIn("scoring_spec_valid", [check["name"] for check in report["checks"]])
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_in_adoption_packet_matches_current_evidence(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "adoption" / "marked_bench_adoption_packet_v0_4_8.json"

        packet = load_adoption_packet(path)
        validation = validate_adoption_packet(packet, root=root)

        self.assertEqual(packet, build_adoption_packet(root))
        self.assertEqual(packet["schema"], ADOPTION_PACKET_SCHEMA)
        self.assertEqual(packet["default_track"], "contradiction-multihop")
        self.assertTrue(packet["standard_claims"]["public_result_card_required"])
        self.assertTrue(packet["standard_claims"]["public_result_claim_required"])
        self.assertTrue(packet["standard_claims"]["implementation_kit_required"])
        self.assertTrue(packet["standard_claims"]["standard_profile_required"])
        self.assertTrue(packet["standard_claims"]["change_control_required"])
        self.assertTrue(packet["standard_claims"]["scoring_compatibility_required"])
        self.assertTrue(packet["standard_claims"]["scoring_spec_required"])
        self.assertTrue(packet["standard_claims"]["third_party_evidence_ledger_required"])
        self.assertIn("checked_publication_packet", [item["name"] for item in packet["required_public_artifacts"]])
        self.assertIn("checked_result_claim", [item["name"] for item in packet["required_public_artifacts"]])
        self.assertIn("implementation_kit", [item["name"] for item in packet["required_public_artifacts"]])
        self.assertIn("standard_profile", [item["name"] for item in packet["required_public_artifacts"]])
        self.assertIn("change_control", [item["name"] for item in packet["required_public_artifacts"]])
        self.assertIn("scoring_compatibility", [item["name"] for item in packet["required_public_artifacts"]])
        self.assertIn("scoring_spec", [item["name"] for item in packet["required_public_artifacts"]])
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_in_evidence_ledger_matches_current_evidence(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "adoption" / "third_party_evidence_ledger_v0_4_8.json"

        ledger = load_evidence_ledger(path)
        validation = validate_evidence_ledger(ledger, root=root)

        self.assertEqual(ledger, build_evidence_ledger())
        self.assertEqual(ledger["schema"], EVIDENCE_LEDGER_SCHEMA)
        self.assertEqual(ledger["entry_count"], 0)
        self.assertEqual(ledger["status"], "awaiting-third-party-evidence")
        self.assertTrue(validation["valid"], validation["errors"])

    def test_evidence_ledger_validates_bundle_review_and_claim_evidence(self) -> None:
        root = Path(__file__).resolve().parent.parent
        packet_dir = Path("submissions/example_publication_packet")
        card = load_result_card(root / packet_dir / "result_card.json")
        entry = {
            "evidence_id": "example-publication-packet",
            "submitted_at": "2026-05-31",
            "submitter": card["submitter"],
            "system_name": card["system_name"],
            "system_version": card["system_version"],
            "suite_id": card["suite_id"],
            "suite_version": card["suite_version"],
            "suite_hash": card["suite_hash"],
            "result_card_path": (packet_dir / "result_card.json").as_posix(),
            "result_card_sha256": file_sha256(root / packet_dir / "result_card.json"),
            "submission_bundle_path": (packet_dir / "submission_bundle.json").as_posix(),
            "submission_bundle_sha256": file_sha256(root / packet_dir / "submission_bundle.json"),
            "review_path": (packet_dir / "submission_review.json").as_posix(),
            "review_sha256": file_sha256(root / packet_dir / "submission_review.json"),
            "review_decision": "needs_review",
            "result_claim_path": (packet_dir / "result_claim.json").as_posix(),
            "result_claim_sha256": file_sha256(root / packet_dir / "result_claim.json"),
            "verification_status": "pending",
            "adoption_claim": False,
            "evidence_url": None,
            "notes": "Checked packet used to exercise third-party evidence validation.",
        }

        ledger = build_evidence_ledger(entries=[entry])
        validation = validate_evidence_ledger(ledger, root=root)

        self.assertTrue(validation["valid"], validation["errors"])
        self.assertEqual(validation["summary"]["entry_count"], 1)
        self.assertEqual(validation["summary"]["verified_entry_count"], 0)

        tampered_entry = dict(entry)
        tampered_entry.pop("submission_bundle_path")
        tampered_ledger = build_evidence_ledger(entries=[tampered_entry])
        tampered_validation = validate_evidence_ledger(tampered_ledger, root=root)

        self.assertFalse(tampered_validation["valid"])
        self.assertTrue(
            any("submission_bundle_path is required" in error for error in tampered_validation["errors"]),
            tampered_validation["errors"],
        )

    def test_checked_in_implementation_kit_matches_current_release(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "adoption" / "marked_bench_implementation_kit_v0_4_8.json"

        kit = load_implementation_kit(path)
        validation = validate_implementation_kit(kit, root=root)

        self.assertEqual(kit, build_implementation_kit(root))
        self.assertEqual(kit["schema"], IMPLEMENTATION_KIT_SCHEMA)
        self.assertEqual(kit["default_track"], "contradiction-multihop")
        self.assertIn("github_actions_template", [item["name"] for item in kit["kit_files"]])
        self.assertIn("validate_result_claim", [item["name"] for item in kit["external_ci_commands"]])
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_in_standard_profile_matches_current_release(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "standard" / "marked_bench_standard_profile_v0_4_8.json"

        profile = load_standard_profile(path)
        validation = validate_standard_profile(profile, root=root)

        self.assertEqual(profile, build_standard_profile(root))
        self.assertEqual(profile["schema"], STANDARD_PROFILE_SCHEMA)
        self.assertEqual(profile["requirement_summary"]["unsatisfied"], 0)
        self.assertIn("release_conformance", [item["id"] for item in profile["standard_requirements"]])
        self.assertIn("scoring_compatibility_vectors", [item["id"] for item in profile["standard_requirements"]])
        self.assertIn("scoring_spec", [item["id"] for item in profile["standard_requirements"]])
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_in_change_control_matches_current_release(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "standard" / "marked_bench_change_control_v0_4_8.json"

        profile = load_change_control(path)
        validation = validate_change_control(profile, root=root)

        self.assertEqual(profile, build_change_control(root))
        self.assertEqual(profile["schema"], CHANGE_CONTROL_SCHEMA)
        self.assertIn("suite_case_change", [item["id"] for item in profile["change_types"]])
        self.assertIn("scoring_change", [item["id"] for item in profile["change_types"]])
        self.assertTrue(profile["compatibility_rules"]["released_case_meaning_is_immutable"])
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_in_scoring_compatibility_profile_matches_current_release(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "standard" / "marked_bench_scoring_compatibility_v0_4_8.json"

        profile = load_scoring_compatibility_profile(path)
        validation = validate_scoring_compatibility_profile(profile, root=root)
        vector_names = {vector["name"] for vector in profile["vectors"]}
        perfect_vectors = [vector for vector in profile["vectors"] if vector["name"] == "perfect"]

        self.assertEqual(profile, build_scoring_compatibility_profile(root))
        self.assertEqual(profile["schema"], SCORING_COMPATIBILITY_SCHEMA)
        self.assertEqual(profile["vector_count"], 12)
        self.assertEqual(vector_names, {"perfect", "always_none", "rotated_labels"})
        self.assertTrue(all(vector["expected_summary"]["overall_score"] == 100.0 for vector in perfect_vectors))
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_in_scoring_spec_matches_current_release(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "standard" / "marked_bench_scoring_spec_v0_4_8.json"
        doc_path = root / "docs" / "SCORING_SPEC.md"

        spec = load_scoring_spec(path)
        validation = validate_scoring_spec(spec, root=root)

        self.assertEqual(spec, build_scoring_spec(root))
        self.assertEqual(spec["schema"], SCORING_SPEC_SCHEMA)
        self.assertEqual(spec["metric_definitions"]["overall_score"].startswith("round(100 *"), True)
        self.assertEqual(spec["calibration_contract"]["bin_count"], 10)
        self.assertIn("suite_hash", spec["report_contract"]["comparability_key"])
        self.assertEqual(doc_path.read_text(encoding="utf-8"), build_scoring_spec_markdown(root))
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_external_submission_packet_validates(self) -> None:
        root = Path(__file__).resolve().parent.parent
        packet_dir = root / "submissions" / "example_external_jsonl"
        report_path = packet_dir / "example_external_report.json"

        report = json.loads(report_path.read_text(encoding="utf-8"))
        scored_report = evaluate_prediction_file(
            packet_dir / "predictions.jsonl",
            system_name="ExampleExternalJsonl",
            suite="contradiction-multihop",
        )
        bundle = load_submission_bundle(packet_dir / "example_external_submission_bundle.json")
        review = load_submission_review(packet_dir / "example_external_submission_review.json")

        self.assertTrue(validate_benchmark_report(report)["valid"])
        self.assertEqual(report["suite_id"], MULTIHOP_SUITE_ID)
        self.assertEqual(report["overall_score"], scored_report["overall_score"])
        self.assertTrue(validate_submission_bundle(bundle, base_dir=packet_dir)["valid"])
        self.assertTrue(validate_submission_review(review, base_dir=packet_dir)["valid"])

    def test_checked_external_result_card_validates(self) -> None:
        root = Path(__file__).resolve().parent.parent
        packet_dir = root / "submissions" / "example_external_jsonl"
        path = packet_dir / "example_external_result_card.json"

        card = load_result_card(path)
        validation = validate_result_card(card, base_dir=packet_dir)

        self.assertEqual(
            card,
            build_result_card(
                "example_external_report.json",
                bundle_path="example_external_submission_bundle.json",
                review_path="example_external_submission_review.json",
                base_dir=packet_dir,
                notes="Checked example result card for the external JSONL workflow.",
            ),
        )
        self.assertEqual(card["schema"], RESULT_CARD_SCHEMA)
        self.assertTrue(card["publication"]["ready_for_leaderboard_review"])
        self.assertFalse(card["publication"]["accepted"])
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_publication_packet_validates(self) -> None:
        root = Path(__file__).resolve().parent.parent
        packet_dir = root / "submissions" / "example_publication_packet"
        path = packet_dir / "publication_packet.json"

        packet = load_publication_packet(path)
        validation = validate_publication_packet(packet, base_dir=packet_dir)

        self.assertEqual(packet, build_publication_packet(packet_dir, notes=packet["notes"]))
        self.assertEqual(packet["schema"], PUBLICATION_PACKET_SCHEMA)
        self.assertEqual(packet["suite_id"], MULTIHOP_SUITE_ID)
        self.assertTrue(packet["ready_for_publication"])
        self.assertTrue(validation["valid"], validation["errors"])
        self.assertIn("result_card", {entry["role"] for entry in packet["files"]})

    def test_checked_result_claim_validates(self) -> None:
        root = Path(__file__).resolve().parent.parent
        packet_dir = root / "submissions" / "example_publication_packet"
        path = packet_dir / "result_claim.json"

        claim = load_result_claim(path)
        validation = validate_result_claim(claim, base_dir=packet_dir)

        self.assertEqual(
            claim,
            build_result_claim(
                "publication_packet.json",
                base_dir=packet_dir,
                notes="Checked example result claim for the publication packet workflow.",
            ),
        )
        self.assertEqual(claim["schema"], RESULT_CLAIM_SCHEMA)
        self.assertEqual(claim["suite_id"], MULTIHOP_SUITE_ID)
        self.assertIn("not a safety certification", claim["claim"]["text"])
        self.assertTrue(validation["valid"], validation["errors"])

    def test_checked_in_technical_note_matches_generated_evidence(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "docs" / "TECHNICAL_NOTE.md"

        note = path.read_text(encoding="utf-8")

        self.assertEqual(note, build_technical_note(root))
        self.assertIn("## Public Tracks", note)
        self.assertIn("marked-bench-contradiction-adversarial", note)
        self.assertIn("marked-bench-contradiction-multihop", note)
        self.assertIn("marked-bench-contradiction-controls", note)
        self.assertIn("## Baseline Evidence", note)

    def test_default_engine_report_is_json_serializable(self) -> None:
        report = evaluate_standard_suite()

        self.assertEqual(report["schema"], REPORT_SCHEMA)
        self.assertEqual(report["suite_id"], SUITE_ID)
        self.assertEqual(report["suite_hash"], suite_case_hash(build_standard_suite()))
        self.assertEqual(report["case_count"], len(build_standard_suite()))
        self.assertGreaterEqual(report["overall_score"], 85.0)
        self.assertIn("confusion_matrix", report)
        self.assertIn("per_class", report["metrics"])
        self.assertIn("calibration", report["metrics"])
        self.assertIn("brier_score", report["metrics"]["calibration"])
        self.assertEqual(report["metrics"]["calibration"]["bin_count"], 10)
        self.assertEqual(len(report["metrics"]["calibration"]["bins"]), 10)
        self.assertIn("slices", report["metrics"])
        self.assertIn("difficulty", report["metrics"]["slices"])
        self.assertIn("easy", report["metrics"]["slices"]["difficulty"])
        self.assertIn("tag", report["metrics"]["slices"])
        self.assertIn("negation", report["metrics"]["slices"]["tag"])
        json.dumps(report)

    def test_default_engine_does_not_solve_adversarial_suite(self) -> None:
        report = evaluate_standard_suite(suite="contradiction-adversarial")

        self.assertEqual(report["suite_id"], ADVERSARIAL_SUITE_ID)
        self.assertLess(report["overall_score"], 80.0)
        self.assertGreater(report["overall_score"], 25.0)
        self.assertGreater(len(report["failures"]), 0)
        self.assertTrue(validate_benchmark_report(report)["valid"])

    def test_default_engine_does_not_solve_multihop_suite(self) -> None:
        report = evaluate_standard_suite(suite="contradiction-multihop")

        self.assertEqual(report["suite_id"], MULTIHOP_SUITE_ID)
        self.assertLess(report["overall_score"], 70.0)
        self.assertGreater(len(report["failures"]), 0)
        self.assertTrue(validate_benchmark_report(report)["valid"])

    def test_default_engine_handles_control_suite_without_false_positive_controls(self) -> None:
        report = evaluate_standard_suite(suite="contradiction-controls")

        self.assertEqual(report["suite_id"], CONTROL_SUITE_ID)
        self.assertGreaterEqual(report["overall_score"], 90.0)
        control_results = [item for item in report["case_results"] if "control" in item["tags"]]
        self.assertTrue(control_results)
        self.assertTrue(all(item["predicted"] == ContradictionType.NONE.value for item in control_results))
        self.assertTrue(validate_benchmark_report(report)["valid"])

    def test_report_validator_rejects_tampered_scores(self) -> None:
        report = evaluate_standard_suite()
        validation = validate_benchmark_report(report)
        tampered = dict(report)
        tampered["overall_score"] = 1000

        tampered_validation = validate_benchmark_report(tampered)

        self.assertTrue(validation["valid"])
        self.assertFalse(tampered_validation["valid"])
        self.assertTrue(any("overall_score mismatch" in error for error in tampered_validation["errors"]))

    def test_report_validator_rejects_tampered_suite_hash(self) -> None:
        report = evaluate_standard_suite()
        tampered = dict(report)
        tampered["suite_hash"] = "0" * 64

        validation = validate_benchmark_report(tampered)

        self.assertFalse(validation["valid"])
        self.assertTrue(any("suite_hash mismatch" in error for error in validation["errors"]))

    def test_report_validator_rejects_modified_suite_case(self) -> None:
        report = evaluate_standard_suite()
        tampered = dict(report)
        tampered_cases = [dict(case) for case in report["suite_cases"]]
        tampered_cases[0]["expected"] = "none"
        tampered["suite_cases"] = tampered_cases

        validation = validate_benchmark_report(tampered)

        self.assertFalse(validation["valid"])
        self.assertTrue(any("suite case was modified" in error for error in validation["errors"]))

    def test_report_validator_rejects_tampered_slice_metrics(self) -> None:
        report = evaluate_standard_suite()
        tampered = dict(report)
        tampered_metrics = json.loads(json.dumps(report["metrics"]))
        tampered_metrics["slices"]["difficulty"]["easy"]["type_accuracy"] = 0.0
        tampered["metrics"] = tampered_metrics

        validation = validate_benchmark_report(tampered)

        self.assertFalse(validation["valid"])
        self.assertTrue(any("metrics mismatch" in error for error in validation["errors"]))

    def test_report_validator_rejects_tampered_calibration_metrics(self) -> None:
        report = evaluate_standard_suite()
        tampered = dict(report)
        tampered_metrics = json.loads(json.dumps(report["metrics"]))
        tampered_metrics["calibration"]["brier_score"] = 1.0
        tampered["metrics"] = tampered_metrics

        validation = validate_benchmark_report(tampered)

        self.assertFalse(validation["valid"])
        self.assertTrue(any("metrics mismatch" in error for error in validation["errors"]))

    def test_report_validator_rejects_invalid_detector_score(self) -> None:
        report = evaluate_standard_suite()
        tampered = dict(report)
        tampered_results = [dict(item) for item in report["case_results"]]
        tampered_results[0]["detector_score"] = 1.5
        tampered["case_results"] = tampered_results

        validation = validate_benchmark_report(tampered)

        self.assertFalse(validation["valid"])
        self.assertTrue(any("detector_score must be between 0 and 1" in error for error in validation["errors"]))

    def test_report_validator_rejects_tampered_case_tags(self) -> None:
        report = evaluate_standard_suite()
        tampered = dict(report)
        tampered_results = [dict(item) for item in report["case_results"]]
        tampered_results[0]["tags"] = ["changed"]
        tampered["case_results"] = tampered_results

        validation = validate_benchmark_report(tampered)

        self.assertFalse(validation["valid"])
        self.assertTrue(any("tags do not match canonical suite" in error for error in validation["errors"]))

    def test_custom_detector_can_be_scored(self) -> None:
        def empty_detector(_claim: Claim):
            return None

        report = evaluate_standard_suite(empty_detector, system_name="empty")

        self.assertEqual(report["system_name"], "empty")
        self.assertLess(report["overall_score"], 50.0)
        self.assertGreater(len(report["failures"]), 0)

    def test_external_prediction_records_score_into_valid_report(self) -> None:
        cases = build_adversarial_suite()
        predictions = [
            {
                "case_id": case.id,
                "predicted": case.expected.value,
                "detector_score": 1.0,
                "detector_note": "exact label",
            }
            for case in cases
        ]

        report = evaluate_prediction_records(
            predictions,
            system_name="ExternalPerfect",
            suite="contradiction-adversarial",
        )

        self.assertEqual(report["system_name"], "ExternalPerfect")
        self.assertEqual(report["overall_score"], 100.0)
        self.assertEqual(report["failures"], [])
        self.assertTrue(validate_benchmark_report(report)["valid"])

    def test_external_prediction_records_preserve_explanation_evidence(self) -> None:
        cases = build_adversarial_suite()
        predictions = [
            {
                "case_id": case.id,
                "predicted": case.expected.value,
                "detector_score": 1.0,
                "rationale": f"Matches expected label for {case.id}.",
                "evidence": [case.premise, case.query],
            }
            for case in cases
        ]

        report = evaluate_prediction_records(
            predictions,
            system_name="ExternalExplained",
            suite="contradiction-adversarial",
        )

        self.assertEqual(report["overall_score"], 100.0)
        self.assertEqual(report["case_results"][0]["rationale"], f"Matches expected label for {cases[0].id}.")
        self.assertEqual(report["case_results"][0]["evidence"], [cases[0].premise, cases[0].query])
        self.assertEqual(report["explanation_audit"]["rationale_count"], len(cases))
        self.assertEqual(report["explanation_audit"]["evidence_count"], len(cases))
        self.assertEqual(report["explanation_audit"]["explanation_ready_rate"], 1.0)
        self.assertTrue(validate_benchmark_report(report)["valid"])

    def test_external_prediction_records_require_full_canonical_coverage(self) -> None:
        cases = build_standard_suite()
        incomplete = [{"case_id": cases[0].id, "predicted": cases[0].expected.value}]
        invalid_label = [{"case_id": case.id, "predicted": case.expected.value} for case in cases]
        invalid_label[0]["predicted"] = "almost_correct"

        with self.assertRaisesRegex(ValueError, "missing predictions"):
            evaluate_prediction_records(incomplete, system_name="Incomplete")
        with self.assertRaisesRegex(ValueError, "invalid predicted label"):
            evaluate_prediction_records(invalid_label, system_name="InvalidLabel")

    def test_external_prediction_records_reject_invalid_detector_score(self) -> None:
        cases = build_standard_suite()
        predictions = [{"case_id": case.id, "predicted": case.expected.value} for case in cases]
        predictions[0]["detector_score"] = -0.1

        with self.assertRaisesRegex(ValueError, "detector_score must be between 0 and 1"):
            evaluate_prediction_records(predictions, system_name="InvalidScore")

    def test_prediction_template_and_json_submission_round_trip(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "predictions.json"
        cases = build_adversarial_suite()
        predictions = [{"case_id": case.id, "predicted": case.expected.value} for case in cases]

        try:
            template = build_prediction_template(suite="contradiction-adversarial")
            template["predictions"] = predictions
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(template), encoding="utf-8")

            loaded = load_prediction_records(path)
            report = evaluate_prediction_file(path, system_name="JsonSubmitter", suite="contradiction-adversarial")

            self.assertEqual(template["schema"], PREDICTION_SCHEMA)
            self.assertEqual(len(loaded), len(cases))
            self.assertEqual(report["overall_score"], 100.0)
            self.assertTrue(validate_benchmark_report(report)["valid"])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_leaderboard_submission_validates_report_hash_and_metadata(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="SubmissionSystem"), report_path)
            submission = build_leaderboard_submission(
                report_path,
                system_version="1.0.0",
                submitter="Marked Bench Test",
                notes="submission validation test",
                disclosures={
                    "system_description": "symbolic baseline",
                    "model": "none",
                    "prompting": "none",
                    "preprocessing": "none",
                    "retrieval": "none",
                    "postprocessing": "none",
                    "training_data": "none",
                    "runtime": "python unittest",
                },
            )
            validation = validate_leaderboard_submission(submission)

            self.assertEqual(submission["schema"], SUBMISSION_SCHEMA)
            self.assertEqual(submission["report_sha256"], report_sha256(report_path))
            self.assertEqual(submission["suite_hash"], build_suite_hash())
            self.assertEqual(submission["system_name"], "SubmissionSystem")
            self.assertTrue(validation["valid"], validation["errors"])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_leaderboard_submission_rejects_hash_mismatch(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="SubmissionSystem"), report_path)
            submission = build_leaderboard_submission(
                report_path,
                system_version="1.0.0",
                submitter="Marked Bench Test",
            )
            submission["report_sha256"] = "0" * 64

            validation = validate_leaderboard_submission(submission)

            self.assertFalse(validation["valid"])
            self.assertTrue(any("report_sha256 mismatch" in error for error in validation["errors"]))
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_submission_bundle_validates_review_packet(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"
        submission_path = output_root / "submission.json"
        bundle_path = output_root / "bundle.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="BundleSystem"), report_path)
            submission = build_leaderboard_submission(
                "report.json",
                system_version="1.0.0",
                submitter="Marked Bench Test",
                base_dir=output_root,
                disclosures={
                    "system_description": "symbolic baseline",
                    "model": "none",
                    "prompting": "none",
                    "preprocessing": "none",
                    "retrieval": "none",
                    "postprocessing": "none",
                    "training_data": "none",
                    "runtime": "python unittest",
                },
            )
            write_leaderboard_submission(submission, submission_path)

            bundle = build_submission_bundle("submission.json", base_dir=output_root)
            write_submission_bundle(bundle, bundle_path)
            validation = validate_submission_bundle(bundle, base_dir=output_root)

            self.assertEqual(bundle["schema"], SUBMISSION_BUNDLE_SCHEMA)
            self.assertEqual(bundle["system_name"], "BundleSystem")
            self.assertEqual(bundle["report_path"], "report.json")
            self.assertTrue(validation["valid"], validation["errors"])
            self.assertTrue(validation["summary"]["ready_for_leaderboard_review"])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_submission_bundle_rejects_hash_mismatch(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"
        submission_path = output_root / "submission.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="BundleSystem"), report_path)
            submission = build_leaderboard_submission(
                "report.json",
                system_version="1.0.0",
                submitter="Marked Bench Test",
                base_dir=output_root,
            )
            write_leaderboard_submission(submission, submission_path)
            bundle = build_submission_bundle("submission.json", base_dir=output_root)
            bundle["files"][0]["sha256"] = "0" * 64

            validation = validate_submission_bundle(bundle, base_dir=output_root)

            self.assertFalse(validation["valid"])
            self.assertTrue(any("sha256 mismatch" in error for error in validation["errors"]))
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_submission_review_template_validates_pending_rubric(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"
        submission_path = output_root / "submission.json"
        bundle_path = output_root / "bundle.json"
        review_path = output_root / "review.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="ReviewSystem"), report_path)
            submission = build_leaderboard_submission(
                "report.json",
                system_version="1.0.0",
                submitter="Marked Bench Test",
                base_dir=output_root,
                disclosures={
                    "system_description": "symbolic baseline",
                    "model": "none",
                    "prompting": "none",
                    "preprocessing": "none",
                    "retrieval": "none",
                    "postprocessing": "none",
                    "training_data": "none",
                    "runtime": "python unittest",
                },
            )
            write_leaderboard_submission(submission, submission_path)
            bundle = build_submission_bundle("submission.json", base_dir=output_root)
            write_submission_bundle(bundle, bundle_path)

            review = build_submission_review(
                "bundle.json",
                reviewer="reviewer-a",
                base_dir=output_root,
            )
            write_submission_review(review, review_path)
            validation = validate_submission_review(review, base_dir=output_root)

            self.assertEqual(review["schema"], REVIEW_SCHEMA)
            self.assertEqual(review["system_name"], "ReviewSystem")
            self.assertEqual(set(review["rubric"]), set(RUBRIC_DIMENSIONS))
            self.assertFalse(review["summary"]["ready_for_decision"])
            self.assertTrue(validation["valid"], validation["errors"])
            self.assertFalse(validation["summary"]["ready_for_decision"])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_submission_review_accept_requires_complete_accept_level_rubric(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"
        submission_path = output_root / "submission.json"
        bundle_path = output_root / "bundle.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="AcceptedReviewSystem"), report_path)
            submission = build_leaderboard_submission(
                "report.json",
                system_version="1.0.0",
                submitter="Marked Bench Test",
                base_dir=output_root,
                disclosures={
                    "system_description": "symbolic baseline",
                    "model": "none",
                    "prompting": "none",
                    "preprocessing": "none",
                    "retrieval": "none",
                    "postprocessing": "none",
                    "training_data": "none",
                    "runtime": "python unittest",
                },
            )
            write_leaderboard_submission(submission, submission_path)
            write_submission_bundle(build_submission_bundle("submission.json", base_dir=output_root), bundle_path)
            review = build_submission_review(
                "bundle.json",
                reviewer="reviewer-a",
                decision="accept",
                base_dir=output_root,
            )
            for item in review["rubric"].values():
                item["score"] = 2
            review["summary"] = {
                "completed_dimensions": len(RUBRIC_DIMENSIONS),
                "dimension_count": len(RUBRIC_DIMENSIONS),
                "rubric_total": 2 * len(RUBRIC_DIMENSIONS),
                "rubric_max": 2 * len(RUBRIC_DIMENSIONS),
                "accept_recommendation_minimum": 9,
                "ready_for_decision": True,
                "recommendation": "accept",
            }

            validation = validate_submission_review(review, base_dir=output_root)

            self.assertTrue(validation["valid"], validation["errors"])
            self.assertTrue(validation["summary"]["ready_for_decision"])
            self.assertEqual(validation["summary"]["recommendation"], "accept")
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_submission_review_rejects_bundle_hash_mismatch(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"
        submission_path = output_root / "submission.json"
        bundle_path = output_root / "bundle.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="ReviewSystem"), report_path)
            submission = build_leaderboard_submission(
                "report.json",
                system_version="1.0.0",
                submitter="Marked Bench Test",
                base_dir=output_root,
            )
            write_leaderboard_submission(submission, submission_path)
            write_submission_bundle(build_submission_bundle("submission.json", base_dir=output_root), bundle_path)
            review = build_submission_review("bundle.json", base_dir=output_root)
            review["bundle_sha256"] = "0" * 64

            validation = validate_submission_review(review, base_dir=output_root)

            self.assertFalse(validation["valid"])
            self.assertTrue(any("bundle_sha256 mismatch" in error for error in validation["errors"]))
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_report_writer_creates_parent_directories(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "nested" / "report.json"
        report = evaluate_standard_suite()

        try:
            write_benchmark_report(report, path)

            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["suite_id"], SUITE_ID)
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_writes_requested_report_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "cli-report.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--report", str(path)])

            loaded = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(loaded["suite_id"], SUITE_ID)
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_validates_report_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "cli-report.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--report", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-report", str(path)])

            self.assertIn("Validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_creates_and_validates_submission_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "cli-report.json"
        submission_path = output_root / "submission.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--system-name", "CliSubmissionSystem", "--report", str(report_path)])
            with redirect_stdout(StringIO()) as create_output:
                benchmark_main(
                    [
                        "--create-submission",
                        str(submission_path),
                        "--submission-report",
                        str(report_path),
                        "--system-version",
                        "2026.05",
                        "--submitter",
                        "Marked Bench Test",
                        "--submission-notes",
                        "created by CLI test",
                        "--disclosure",
                        "system_description=symbolic baseline",
                    ]
                )
            with redirect_stdout(StringIO()) as validate_output:
                benchmark_main(["--validate-submission", str(submission_path)])

            submission = json.loads(submission_path.read_text(encoding="utf-8"))
            self.assertEqual(submission["system_name"], "CliSubmissionSystem")
            self.assertEqual(submission["schema"], SUBMISSION_SCHEMA)
            self.assertIn("Submission:", create_output.getvalue())
            self.assertIn("Submission validation: pass", validate_output.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_creates_and_validates_submission_bundle_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "cli-report.json"
        submission_path = output_root / "submission.json"
        bundle_path = output_root / "submission-bundle.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--system-name", "CliBundleSystem", "--report", str(report_path)])
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--create-submission",
                        str(submission_path),
                        "--submission-report",
                        str(report_path),
                        "--system-version",
                        "2026.05",
                        "--submitter",
                        "Marked Bench Test",
                        "--disclosure",
                        "system_description=symbolic baseline",
                    ]
                )
            with redirect_stdout(StringIO()) as create_output:
                benchmark_main(
                    [
                        "--create-submission-bundle",
                        str(bundle_path),
                        "--bundle-submission",
                        str(submission_path),
                    ]
                )
            with redirect_stdout(StringIO()) as validate_output:
                benchmark_main(["--validate-submission-bundle", str(bundle_path)])

            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            self.assertEqual(bundle["schema"], SUBMISSION_BUNDLE_SCHEMA)
            self.assertEqual(bundle["system_name"], "CliBundleSystem")
            self.assertIn("Submission bundle:", create_output.getvalue())
            self.assertIn("Submission bundle validation: pass", validate_output.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_creates_and_validates_submission_review_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "cli-report.json"
        submission_path = output_root / "submission.json"
        bundle_path = output_root / "submission-bundle.json"
        review_path = output_root / "submission-review.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--system-name", "CliReviewSystem", "--report", str(report_path)])
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--create-submission",
                        str(submission_path),
                        "--submission-report",
                        str(report_path),
                        "--system-version",
                        "2026.05",
                        "--submitter",
                        "Marked Bench Test",
                        "--disclosure",
                        "system_description=symbolic baseline",
                    ]
                )
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--create-submission-bundle",
                        str(bundle_path),
                        "--bundle-submission",
                        str(submission_path),
                    ]
                )
            with redirect_stdout(StringIO()) as create_output:
                benchmark_main(
                    [
                        "--create-submission-review",
                        str(review_path),
                        "--review-bundle",
                        str(bundle_path),
                        "--reviewer",
                        "reviewer-a",
                    ]
                )
            with redirect_stdout(StringIO()) as validate_output:
                benchmark_main(["--validate-submission-review", str(review_path)])

            review = json.loads(review_path.read_text(encoding="utf-8"))
            self.assertEqual(review["schema"], REVIEW_SCHEMA)
            self.assertEqual(review["system_name"], "CliReviewSystem")
            self.assertIn("Submission review:", create_output.getvalue())
            self.assertIn("Submission review validation: pass", validate_output.getvalue())
            self.assertIn("Ready for decision: False", validate_output.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_external_submission_demo_writes_valid_bundle(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output" / "external-demo"

        try:
            summary = run_external_submission_demo(output_root)
            bundle_path = Path(summary["bundle_path"])
            bundle = json.loads(bundle_path.read_text(encoding="utf-8"))
            validation = validate_submission_bundle(bundle, base_dir=output_root)

            self.assertTrue(summary["bundle_valid"])
            self.assertEqual(summary["system_name"], "ExampleExternalJsonl")
            self.assertTrue(Path(summary["prediction_path"]).exists())
            self.assertTrue(Path(summary["report_path"]).exists())
            self.assertTrue(Path(summary["submission_path"]).exists())
            self.assertTrue(Path(summary["review_path"]).exists())
            self.assertTrue(summary["review_valid"])
            self.assertTrue(validation["valid"], validation["errors"])
        finally:
            shutil.rmtree(output_root.parent, ignore_errors=True)

    def test_publication_packet_builder_writes_self_contained_packet(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output" / "publication-builder"
        source_dir = output_root / "source"
        packet_dir = output_root / "packet"
        prediction_path = source_dir / "predictions.jsonl"
        report_path = source_dir / "report.json"

        try:
            source_dir.mkdir(parents=True, exist_ok=True)
            records = [
                {
                    "case_id": record["case_id"],
                    "predicted": "none",
                    "detector_score": 0.0,
                    "rationale": "Builder test predicts no contradiction.",
                    "evidence": [record["premise"], record["query"]],
                }
                for record in build_prediction_template(suite="contradiction-multihop")["predictions"]
            ]
            prediction_path.write_text(
                "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
                encoding="utf-8",
            )
            report = evaluate_prediction_file(prediction_path, system_name="PublicationBuilder", suite="contradiction-multihop")
            write_benchmark_report(report, report_path)

            packet = create_publication_packet(
                packet_dir,
                report_path,
                prediction_path=prediction_path,
                system_version="builder-1",
                submitter="Marked Bench Test",
                packet_notes="builder packet",
            )
            loaded = load_publication_packet(packet_dir / "publication_packet.json")
            validation = validate_publication_packet(loaded, base_dir=packet_dir)
            claim = build_result_claim(
                "publication_packet.json",
                base_dir=packet_dir,
                notes="builder result claim",
            )

            self.assertEqual(packet, loaded)
            self.assertEqual(packet, build_publication_packet(packet_dir, notes="builder packet"))
            self.assertEqual(claim["schema"], RESULT_CLAIM_SCHEMA)
            self.assertIn("PublicationBuilder builder-1 scored", claim["claim"]["text"])
            self.assertEqual(packet["schema"], PUBLICATION_PACKET_SCHEMA)
            self.assertEqual(packet["system_name"], "PublicationBuilder")
            self.assertTrue(packet["ready_for_publication"])
            self.assertTrue((packet_dir / "report.json").exists())
            self.assertTrue((packet_dir / "predictions.jsonl").exists())
            self.assertTrue(validation["valid"], validation["errors"])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_writes_always_none_baseline_report(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "always-none.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--detector",
                        "always-none",
                        "--system-name",
                        "AlwaysNoneDetector",
                        "--report",
                        str(path),
                    ]
                )

            report = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(report["system_name"], "AlwaysNoneDetector")
            self.assertLess(report["overall_score"], 50.0)
            self.assertTrue(validate_benchmark_report(report)["valid"])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_suite_manifest_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "suite.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-suite", str(path)])

            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest, build_suite_manifest())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_adversarial_suite_manifest_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "adversarial-suite.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--suite", "contradiction-adversarial", "--export-suite", str(path)])

            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest, build_suite_manifest(suite="contradiction-adversarial"))
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_multihop_suite_manifest_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "multihop-suite.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--suite", "contradiction-multihop", "--export-suite", str(path)])

            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest, build_suite_manifest(suite="contradiction-multihop"))
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_control_suite_manifest_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "control-suite.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--suite", "contradiction-controls", "--export-suite", str(path)])

            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest, build_suite_manifest(suite="contradiction-controls"))
            self.assertEqual(manifest["suite_id"], CONTROL_SUITE_ID)
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_benchmark_registry_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "benchmark-registry.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-registry", str(path)])

            registry = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(registry, build_benchmark_registry())
            self.assertEqual(registry["schema"], REGISTRY_SCHEMA)
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_release_manifest_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "release-manifest.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-release-manifest", str(path)])

            manifest = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(manifest, build_release_manifest(Path(__file__).resolve().parent.parent))
            self.assertEqual(manifest["schema"], RELEASE_MANIFEST_SCHEMA)
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_conformance_report_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "conformance-report.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-conformance-report", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-conformance-report", str(path)])

            report = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(report, build_conformance_report(Path(__file__).resolve().parent.parent))
            self.assertEqual(report["schema"], CONFORMANCE_REPORT_SCHEMA)
            self.assertIn("Conformance validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_adoption_packet_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "adoption-packet.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-adoption-packet", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-adoption-packet", str(path)])

            packet = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(packet, build_adoption_packet(Path(__file__).resolve().parent.parent))
            self.assertEqual(packet["schema"], ADOPTION_PACKET_SCHEMA)
            self.assertIn("Adoption packet validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_evidence_ledger_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "evidence-ledger.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-evidence-ledger", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-evidence-ledger", str(path)])

            ledger = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(ledger, build_evidence_ledger())
            self.assertEqual(ledger["schema"], EVIDENCE_LEDGER_SCHEMA)
            self.assertIn("Evidence ledger validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_implementation_kit_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "implementation-kit.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-implementation-kit", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-implementation-kit", str(path)])

            kit = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(kit, build_implementation_kit(Path(__file__).resolve().parent.parent))
            self.assertEqual(kit["schema"], IMPLEMENTATION_KIT_SCHEMA)
            self.assertIn("Implementation kit validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_standard_profile_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "standard-profile.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-standard-profile", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-standard-profile", str(path)])

            profile = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(profile, build_standard_profile(Path(__file__).resolve().parent.parent))
            self.assertEqual(profile["schema"], STANDARD_PROFILE_SCHEMA)
            self.assertIn("Standard profile validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_change_control_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "change-control.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-change-control", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-change-control", str(path)])

            profile = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(profile, build_change_control(Path(__file__).resolve().parent.parent))
            self.assertEqual(profile["schema"], CHANGE_CONTROL_SCHEMA)
            self.assertIn("Change-control validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_scoring_compatibility_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "scoring-compatibility.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-scoring-compatibility", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-scoring-compatibility", str(path)])

            profile = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(profile, build_scoring_compatibility_profile(Path(__file__).resolve().parent.parent))
            self.assertEqual(profile["schema"], SCORING_COMPATIBILITY_SCHEMA)
            self.assertIn("Scoring compatibility validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_and_validates_scoring_spec_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "scoring-spec.json"
        doc_path = output_root / "SCORING_SPEC.md"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-scoring-spec", str(path)])
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(["--validate-scoring-spec", str(path)])
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-scoring-spec-doc", str(doc_path)])

            spec = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(spec, build_scoring_spec(Path(__file__).resolve().parent.parent))
            self.assertEqual(spec["schema"], SCORING_SPEC_SCHEMA)
            self.assertEqual(
                doc_path.read_text(encoding="utf-8"),
                build_scoring_spec_markdown(Path(__file__).resolve().parent.parent),
            )
            self.assertIn("Scoring spec validation: pass", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_creates_and_validates_result_card_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "report.json"
        submission_path = output_root / "submission.json"
        bundle_path = output_root / "bundle.json"
        review_path = output_root / "review.json"
        card_path = output_root / "result-card.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--system-name", "CliResultCardSystem", "--report", str(report_path)])
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--create-submission",
                        str(submission_path),
                        "--submission-report",
                        str(report_path),
                        "--system-version",
                        "1.0.0",
                        "--submitter",
                        "Marked Bench Test",
                    ]
                )
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--create-submission-bundle",
                        str(bundle_path),
                        "--bundle-submission",
                        str(submission_path),
                    ]
                )
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--create-submission-review",
                        str(review_path),
                        "--review-bundle",
                        str(bundle_path),
                        "--reviewer",
                        "reviewer",
                    ]
                )
            with redirect_stdout(StringIO()) as create_output:
                benchmark_main(
                    [
                        "--create-result-card",
                        str(card_path),
                        "--result-report",
                        "report.json",
                        "--result-bundle",
                        "bundle.json",
                        "--result-review",
                        "review.json",
                    ]
                )
            with redirect_stdout(StringIO()) as validate_output:
                benchmark_main(["--validate-result-card", str(card_path)])

            card = json.loads(card_path.read_text(encoding="utf-8"))
            self.assertEqual(card["schema"], RESULT_CARD_SCHEMA)
            self.assertEqual(card["system_name"], "CliResultCardSystem")
            self.assertIn("Result card:", create_output.getvalue())
            self.assertIn("Result card validation: pass", validate_output.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_creates_and_validates_publication_packet_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        report_path = output_root / "publication-report.json"
        packet_dir = output_root / "publication-packet"
        packet_path = packet_dir / "publication_packet.json"
        claim_path = packet_dir / "result_claim.json"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--system-name", "CliPublicationPacketSystem", "--report", str(report_path)])
            with redirect_stdout(StringIO()) as create_output:
                benchmark_main(
                    [
                        "--create-publication-packet",
                        str(packet_dir),
                        "--publication-report",
                        str(report_path),
                        "--system-version",
                        "1.0.0",
                        "--submitter",
                        "Marked Bench Test",
                        "--publication-notes",
                        "CLI publication packet test",
                    ]
                )
            with redirect_stdout(StringIO()) as validate_output:
                benchmark_main(["--validate-publication-packet", str(packet_path)])
            with redirect_stdout(StringIO()) as create_claim_output:
                benchmark_main(
                    [
                        "--create-result-claim",
                        str(claim_path),
                        "--claim-publication-packet",
                        "publication_packet.json",
                        "--claim-notes",
                        "CLI result claim test",
                    ]
                )
            with redirect_stdout(StringIO()) as validate_claim_output:
                benchmark_main(["--validate-result-claim", str(claim_path)])

            packet = json.loads(packet_path.read_text(encoding="utf-8"))
            claim = json.loads(claim_path.read_text(encoding="utf-8"))
            self.assertEqual(packet["schema"], PUBLICATION_PACKET_SCHEMA)
            self.assertEqual(packet["system_name"], "CliPublicationPacketSystem")
            self.assertTrue(packet["ready_for_publication"])
            self.assertEqual(claim["schema"], RESULT_CLAIM_SCHEMA)
            self.assertIn("CliPublicationPacketSystem", claim["claim"]["text"])
            self.assertIn("Publication packet:", create_output.getvalue())
            self.assertIn("Publication packet validation: pass", validate_output.getvalue())
            self.assertIn("Result claim:", create_claim_output.getvalue())
            self.assertIn("Result claim validation: pass", validate_claim_output.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_technical_note_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "technical-note.md"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(["--export-technical-note", str(path)])

            self.assertEqual(path.read_text(encoding="utf-8"), build_technical_note(Path(__file__).resolve().parent.parent))
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_prediction_template_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "predictions.jsonl"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--suite",
                        "contradiction-adversarial",
                        "--export-prediction-template",
                        str(path),
                    ]
                )

            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), len(build_adversarial_suite()))
            self.assertIn("case_id", records[0])
            self.assertIn("predicted", records[0])
            self.assertNotIn("expected", records[0])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_multihop_prediction_template_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "multihop-predictions.jsonl"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--suite",
                        "contradiction-multihop",
                        "--export-prediction-template",
                        str(path),
                    ]
                )

            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), len(build_multihop_suite()))
            self.assertTrue(records[0]["case_id"].startswith("marked-hop-"))
            self.assertNotIn("expected", records[0])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_exports_control_prediction_template_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        path = output_root / "controls-predictions.jsonl"

        try:
            with redirect_stdout(StringIO()):
                benchmark_main(
                    [
                        "--suite",
                        "contradiction-controls",
                        "--export-prediction-template",
                        str(path),
                    ]
                )

            records = [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]
            self.assertEqual(len(records), len(build_control_suite()))
            self.assertTrue(records[0]["case_id"].startswith("marked-ctrl-"))
            self.assertNotIn("expected", records[0])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_scores_prediction_jsonl_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        prediction_path = output_root / "predictions.jsonl"
        report_path = output_root / "prediction-report.json"
        cases = build_adversarial_suite()
        records = [{"case_id": case.id, "predicted": case.expected.value} for case in cases]

        try:
            prediction_path.parent.mkdir(parents=True, exist_ok=True)
            prediction_path.write_text(
                "\n".join(json.dumps(record, sort_keys=True) for record in records) + "\n",
                encoding="utf-8",
            )
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(
                    [
                        "--suite",
                        "contradiction-adversarial",
                        "--score-predictions",
                        str(prediction_path),
                        "--system-name",
                        "ExternalJsonl",
                        "--report",
                        str(report_path),
                    ]
                )

            report = json.loads(report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["system_name"], "ExternalJsonl")
            self.assertEqual(report["overall_score"], 100.0)
            self.assertIn("Overall score: 100.00", captured.getvalue())
            self.assertTrue(validate_benchmark_report(report)["valid"])
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_leaderboard_ranks_valid_reports_and_rejects_invalid(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        strong_path = output_root / "strong.json"
        weak_path = output_root / "weak.json"
        invalid_path = output_root / "invalid.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="Strong"), strong_path)
            write_benchmark_report(evaluate_standard_suite(lambda _claim: None, system_name="Weak"), weak_path)
            invalid = evaluate_standard_suite(system_name="Invalid")
            invalid["overall_score"] = 1_000
            write_benchmark_report(invalid, invalid_path)

            leaderboard = build_leaderboard([weak_path, strong_path, invalid_path])

            self.assertEqual(leaderboard["schema"], LEADERBOARD_SCHEMA)
            self.assertEqual(leaderboard["entry_count"], 2)
            self.assertEqual(leaderboard["rejected_count"], 1)
            self.assertEqual(leaderboard["entries"][0]["system_name"], "Strong")
            self.assertEqual(leaderboard["entries"][0]["rank"], 1)
            self.assertEqual(leaderboard["entries"][1]["system_name"], "Weak")
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_cli_builds_leaderboard_inside_repo(self) -> None:
        output_root = Path(__file__).resolve().parent.parent / ".test-output"
        strong_path = output_root / "strong.json"
        weak_path = output_root / "weak.json"
        leaderboard_path = output_root / "leaderboard.json"

        try:
            write_benchmark_report(evaluate_standard_suite(system_name="Strong"), strong_path)
            write_benchmark_report(evaluate_standard_suite(lambda _claim: None, system_name="Weak"), weak_path)
            with redirect_stdout(StringIO()) as captured:
                benchmark_main(
                    [
                        "--build-leaderboard",
                        str(weak_path),
                        str(strong_path),
                        "--leaderboard-output",
                        str(leaderboard_path),
                    ]
                )

            leaderboard = json.loads(leaderboard_path.read_text(encoding="utf-8"))
            self.assertEqual(leaderboard["entries"][0]["system_name"], "Strong")
            self.assertIn("Leaderboard entries: 2", captured.getvalue())
        finally:
            shutil.rmtree(output_root, ignore_errors=True)

    def test_checked_in_baseline_report_validates(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "baselines" / "contradiction_engine_v0_1_0.json"

        report = json.loads(path.read_text(encoding="utf-8"))
        validation = validate_benchmark_report(report)

        self.assertTrue(validation["valid"], validation["errors"])
        self.assertEqual(report["overall_score"], 100.0)

    def test_checked_in_weak_baseline_report_validates(self) -> None:
        root = Path(__file__).resolve().parent.parent
        path = root / "baselines" / "always_none_v0_1_0.json"

        report = json.loads(path.read_text(encoding="utf-8"))
        validation = validate_benchmark_report(report)

        self.assertTrue(validation["valid"], validation["errors"])
        self.assertEqual(report["system_name"], "AlwaysNoneDetector")
        self.assertEqual(report["overall_score"], 8.82)

    def test_checked_in_adversarial_baseline_reports_validate(self) -> None:
        root = Path(__file__).resolve().parent.parent
        strong_path = root / "baselines" / "contradiction_engine_adversarial_v0_2_0.json"
        weak_path = root / "baselines" / "always_none_adversarial_v0_2_0.json"

        strong = json.loads(strong_path.read_text(encoding="utf-8"))
        weak = json.loads(weak_path.read_text(encoding="utf-8"))

        self.assertTrue(validate_benchmark_report(strong)["valid"])
        self.assertTrue(validate_benchmark_report(weak)["valid"])
        self.assertEqual(strong["suite_id"], ADVERSARIAL_SUITE_ID)
        self.assertEqual(strong["overall_score"], 52.37)
        self.assertEqual(weak["overall_score"], 8.82)

    def test_checked_in_multihop_baseline_reports_validate(self) -> None:
        root = Path(__file__).resolve().parent.parent
        strong_path = root / "baselines" / "contradiction_engine_multihop_v0_3_0.json"
        weak_path = root / "baselines" / "always_none_multihop_v0_3_0.json"

        strong = json.loads(strong_path.read_text(encoding="utf-8"))
        weak = json.loads(weak_path.read_text(encoding="utf-8"))

        self.assertTrue(validate_benchmark_report(strong)["valid"])
        self.assertTrue(validate_benchmark_report(weak)["valid"])
        self.assertEqual(strong["suite_id"], MULTIHOP_SUITE_ID)
        self.assertLess(strong["overall_score"], 70.0)
        self.assertEqual(weak["system_name"], "AlwaysNoneDetector")

    def test_checked_in_control_baseline_reports_validate(self) -> None:
        root = Path(__file__).resolve().parent.parent
        strong_path = root / "baselines" / "contradiction_engine_controls_v0_4_0.json"
        weak_path = root / "baselines" / "always_none_controls_v0_4_0.json"

        strong = json.loads(strong_path.read_text(encoding="utf-8"))
        weak = json.loads(weak_path.read_text(encoding="utf-8"))

        self.assertTrue(validate_benchmark_report(strong)["valid"])
        self.assertTrue(validate_benchmark_report(weak)["valid"])
        self.assertEqual(strong["suite_id"], CONTROL_SUITE_ID)
        self.assertGreaterEqual(strong["overall_score"], 90.0)
        self.assertEqual(weak["system_name"], "AlwaysNoneDetector")
        self.assertLess(weak["overall_score"], 40.0)

    def test_checked_in_leaderboard_matches_baseline_reports(self) -> None:
        root = Path(__file__).resolve().parent.parent
        weak_path = root / "baselines" / "always_none_v0_1_0.json"
        strong_path = root / "baselines" / "contradiction_engine_v0_1_0.json"
        leaderboard_path = root / "leaderboard" / "leaderboard_v0_1_0.json"

        leaderboard = json.loads(leaderboard_path.read_text(encoding="utf-8"))

        self.assertEqual(leaderboard["schema"], LEADERBOARD_SCHEMA)
        self.assertEqual(leaderboard["entry_count"], 2)
        self.assertEqual(leaderboard["rejected_count"], 0)
        self.assertEqual(leaderboard["entries"][0]["system_name"], "ContradictionEngine")
        self.assertEqual(leaderboard["entries"][0]["rank"], 1)
        self.assertEqual(leaderboard["entries"][0]["report_sha256"], report_sha256(strong_path))
        self.assertEqual(leaderboard["entries"][1]["system_name"], "AlwaysNoneDetector")
        self.assertEqual(leaderboard["entries"][1]["rank"], 2)
        self.assertEqual(leaderboard["entries"][1]["report_sha256"], report_sha256(weak_path))

    def test_checked_in_adversarial_leaderboard_matches_baseline_reports(self) -> None:
        root = Path(__file__).resolve().parent.parent
        weak_path = root / "baselines" / "always_none_adversarial_v0_2_0.json"
        strong_path = root / "baselines" / "contradiction_engine_adversarial_v0_2_0.json"
        leaderboard_path = root / "leaderboard" / "leaderboard_adversarial_v0_2_0.json"

        leaderboard = json.loads(leaderboard_path.read_text(encoding="utf-8"))

        self.assertEqual(leaderboard["schema"], LEADERBOARD_SCHEMA)
        self.assertEqual(leaderboard["entry_count"], 2)
        self.assertEqual(leaderboard["rejected_count"], 0)
        self.assertEqual(leaderboard["entries"][0]["system_name"], "ContradictionEngine")
        self.assertEqual(leaderboard["entries"][0]["rank"], 1)
        self.assertEqual(leaderboard["entries"][0]["overall_score"], 52.37)
        self.assertEqual(leaderboard["entries"][0]["report_sha256"], report_sha256(strong_path))
        self.assertEqual(leaderboard["entries"][1]["system_name"], "AlwaysNoneDetector")
        self.assertEqual(leaderboard["entries"][1]["rank"], 2)
        self.assertEqual(leaderboard["entries"][1]["report_sha256"], report_sha256(weak_path))

    def test_checked_in_multihop_leaderboard_matches_baseline_reports(self) -> None:
        root = Path(__file__).resolve().parent.parent
        weak_path = root / "baselines" / "always_none_multihop_v0_3_0.json"
        strong_path = root / "baselines" / "contradiction_engine_multihop_v0_3_0.json"
        leaderboard_path = root / "leaderboard" / "leaderboard_multihop_v0_3_0.json"

        leaderboard = json.loads(leaderboard_path.read_text(encoding="utf-8"))

        self.assertEqual(leaderboard["schema"], LEADERBOARD_SCHEMA)
        self.assertEqual(leaderboard["entry_count"], 2)
        self.assertEqual(leaderboard["rejected_count"], 0)
        self.assertEqual(leaderboard["entries"][0]["system_name"], "ContradictionEngine")
        self.assertEqual(leaderboard["entries"][0]["rank"], 1)
        self.assertEqual(leaderboard["entries"][0]["suite_id"], MULTIHOP_SUITE_ID)
        self.assertEqual(leaderboard["entries"][0]["report_sha256"], report_sha256(strong_path))
        self.assertEqual(leaderboard["entries"][1]["system_name"], "AlwaysNoneDetector")
        self.assertEqual(leaderboard["entries"][1]["rank"], 2)
        self.assertEqual(leaderboard["entries"][1]["report_sha256"], report_sha256(weak_path))

    def test_checked_in_control_leaderboard_matches_baseline_reports(self) -> None:
        root = Path(__file__).resolve().parent.parent
        weak_path = root / "baselines" / "always_none_controls_v0_4_0.json"
        strong_path = root / "baselines" / "contradiction_engine_controls_v0_4_0.json"
        leaderboard_path = root / "leaderboard" / "leaderboard_controls_v0_4_0.json"

        leaderboard = json.loads(leaderboard_path.read_text(encoding="utf-8"))

        self.assertEqual(leaderboard["schema"], LEADERBOARD_SCHEMA)
        self.assertEqual(leaderboard["entry_count"], 2)
        self.assertEqual(leaderboard["rejected_count"], 0)
        self.assertEqual(leaderboard["entries"][0]["system_name"], "ContradictionEngine")
        self.assertEqual(leaderboard["entries"][0]["rank"], 1)
        self.assertEqual(leaderboard["entries"][0]["suite_id"], CONTROL_SUITE_ID)
        self.assertEqual(leaderboard["entries"][0]["report_sha256"], report_sha256(strong_path))
        self.assertEqual(leaderboard["entries"][1]["system_name"], "AlwaysNoneDetector")
        self.assertEqual(leaderboard["entries"][1]["rank"], 2)
        self.assertEqual(leaderboard["entries"][1]["report_sha256"], report_sha256(weak_path))


if __name__ == "__main__":
    unittest.main()
