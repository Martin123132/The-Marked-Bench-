from __future__ import annotations

"""Check that public licensing notices stay aligned with company policy."""

from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent

REQUIRED_FRAGMENTS = {
    Path("LICENSE"): (
        "PolyForm Noncommercial License 1.0.0",
        "TWO HANDS NETWORK LTD",
    ),
    Path("COMMERCIAL-LICENSE.md"): (
        "TWO HANDS NETWORK LTD",
        "Chief Operating Officer (COO)",
        "commercial license",
    ),
    Path("NOTICE.md"): (
        "source-available software, not open-source software",
        "TWO HANDS NETWORK LTD",
        "Chief Operating Officer (COO)",
    ),
    Path("README.md"): (
        "PolyForm Noncommercial License 1.0.0",
        "Chief Operating Officer (COO) of TWO HANDS NETWORK LTD",
    ),
    Path("CITATION.cff"): (
        "PolyForm-Noncommercial-1.0.0",
    ),
}

FORBIDDEN_FRAGMENTS = {
    Path("README.md"): (
        "The Marked Bench Non-Commercial License",
    ),
    Path("CITATION.cff"): (
        "LicenseRef-The-Marked-Bench-Non-Commercial",
    ),
}


def main() -> int:
    errors: list[str] = []
    for path, fragments in REQUIRED_FRAGMENTS.items():
        text = _read_text(path, errors)
        for fragment in fragments:
            if not _contains_fragment(text, fragment):
                errors.append(f"{path}: missing required licensing text {fragment!r}")

    for path, fragments in FORBIDDEN_FRAGMENTS.items():
        text = _read_text(path, errors)
        for fragment in fragments:
            if _contains_fragment(text, fragment):
                errors.append(f"{path}: still contains stale licensing text {fragment!r}")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print("License notice checks passed.")
    return 0


def _read_text(path: Path, errors: list[str]) -> str:
    try:
        return (ROOT / path).read_text(encoding="utf-8")
    except OSError as exc:
        errors.append(f"{path}: could not read file: {exc}")
        return ""


def _contains_fragment(text: str, fragment: str) -> bool:
    return " ".join(fragment.split()) in " ".join(text.split())


if __name__ == "__main__":
    raise SystemExit(main())
