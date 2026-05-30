"""Run The Marked Bench contradiction standard and write a JSON report."""

from pathlib import Path

from marked_bench.contradiction.benchmark_suite import evaluate_standard_suite, write_benchmark_report


def main() -> None:
    report = evaluate_standard_suite()
    output_path = Path("artifacts") / "marked_bench_contradiction_benchmark_report.json"
    write_benchmark_report(report, output_path)

    print(f"Suite: {report['suite_id']} v{report['suite_version']}")
    print(f"Cases: {report['case_count']}")
    print(f"Overall score: {report['overall_score']:.2f}")
    print(f"Type accuracy: {report['metrics']['type_accuracy']:.2f}")
    print(f"Detection F1: {report['metrics']['detection']['f1']:.2f}")
    print(f"Report: {output_path}")


if __name__ == "__main__":
    main()
