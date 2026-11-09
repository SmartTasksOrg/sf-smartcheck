"""SmartCheck CLI.

    sf-smartcheck --demo
    sf-smartcheck ANSWER [--sources FILE ...] [--json]

ANSWER is a file path, or `-` to read standard input. Exit code 0 when the
answer passes, 1 when anything is flagged.
"""
import argparse
import json
import os
import sys
from dataclasses import asdict

from . import core
from ._version import __version__

BANNER = f"\n🦔 SmartCheck {__version__}  ·  IAIso §2 · Verification"
FOOTER = "\nBacked by IAIso §2 · Verification · part of the Smart* family · https://smarttasks.cloud\n"


def _demo_dir():
    return os.path.join(os.path.dirname(__file__), "..", "..", "demo")


def _read(path: str) -> str:
    return sys.stdin.read() if path == "-" else open(path, encoding="utf-8").read()


def main(argv=None):
    argv = argv if argv is not None else sys.argv[1:]
    if "--version" in argv:
        print(f"SmartCheck {__version__}"); return 0
    if not argv or "--demo" in argv:
        print(BANNER); print(core_demo()); print(FOOTER); return 0

    ap = argparse.ArgumentParser(prog="sf-smartcheck")
    ap.add_argument("answer", help="file with the AI output to check, or - for stdin")
    ap.add_argument("--sources", nargs="*", default=[], help="source files the answer should rest on")
    ap.add_argument("--threshold", type=float, default=core.SUPPORT_THRESHOLD)
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)

    sources = "\n".join(_read(p) for p in a.sources)
    v = core.check(_read(a.answer), sources, threshold=a.threshold)
    if a.json:
        print(json.dumps(asdict(v), indent=2, ensure_ascii=False))
    else:
        print(f"{'PASS' if v.passed else 'FLAG'}  citation coverage {v.citation_coverage:.0%}")
        for i in v.issues:
            print(f"  ✗ {i.type} (conf {i.confidence}): {i.span}")
    return 0 if v.passed else 1


def core_demo() -> str:
    return _DEMO()


def _DEMO():
    source = "Q3 report: revenue grew 3.4% to 1,200 million yuan. Churn was flat."
    cases = [
        ("Revenue grew 340 last quarter.", ""),
        ("It always works and never fails.", ""),
        ("Revenue grew 3.4% to 1,200 million yuan.", source),
        ("Revenue grew 4.3% to 1,200 million yuan.", source),
        ("The board approved a new dividend.", source),
    ]
    out = []
    for answer, src in cases:
        v = core.check(answer, src)
        label = "with source" if src else "no source"
        out.append(f"{'PASS' if v.passed else 'FLAG'}  “{answer[:48]}”  ({label})")
        for i in v.issues:
            out.append(f"    ✗ {i.type} (conf {i.confidence})")
    return "\n".join(out)


if __name__ == "__main__":
    sys.exit(main())
