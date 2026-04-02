from __future__ import annotations

import re
import sys
from pathlib import Path

IGNORE_DIRS = {
    ".git",
    ".venv",
    "__pycache__",
    ".pytest_cache",
    "data/state",
}

ALLOWLIST_FRAGMENTS = {
    "replace-with-rotated-token",
    "${x_bearer_token}",
    "your-rotated-token",
    "changeme",
    "example-token",
}

PATTERNS = [
    re.compile(r"authorization\s*[:=]\s*[\"']?bearer\s+[a-z0-9%._-]{16,}", re.IGNORECASE),
    re.compile(r"x[_-]?bearer[_-]?token\s*[:=]\s*[\"']?[a-z0-9%._-]{16,}", re.IGNORECASE),
    re.compile(r"(api[_-]?key|secret|password)\s*[:=]\s*[\"']?[^\s\"']{8,}", re.IGNORECASE),
]


def _is_ignored(path: Path) -> bool:
    return any(part in IGNORE_DIRS for part in path.parts)


def _looks_binary(payload: bytes) -> bool:
    return b"\x00" in payload


def scan_repo(root: Path) -> list[str]:
    findings: list[str] = []
    for path in root.rglob("*"):
        if not path.is_file() or _is_ignored(path):
            continue
        payload = path.read_bytes()
        if _looks_binary(payload):
            continue
        text = payload.decode("utf-8", errors="ignore")
        for pattern in PATTERNS:
            match = pattern.search(text)
            if match:
                lowered_match = match.group(0).lower()
                if any(fragment in lowered_match for fragment in ALLOWLIST_FRAGMENTS):
                    continue
                findings.append(f"{path}: {match.group(0)[:120]}")
                break
    return findings


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    root = Path(argv[0] if argv else ".").resolve()
    findings = scan_repo(root)
    if findings:
        print("Potential secrets detected:")
        for finding in findings:
            print(f" - {finding}")
        return 1
    print("No potential secrets detected.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
