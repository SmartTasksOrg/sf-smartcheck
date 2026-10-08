#!/usr/bin/env python3
"""Regenerate expected.json from the Python reference (the source of truth).

Run from anywhere; it adds the package src to the path automatically:
    python gen_expected.py
Every language port must reproduce this file byte-for-byte (after JSON canonicalisation).
"""
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.abspath(os.path.join(HERE, "..", "..", "src"))
sys.path.insert(0, SRC)

from sf_smartcheck.core import check  # noqa: E402


def verdict_to_dict(name, v):
    return {
        "name": name,
        "passed": v.passed,
        "issues": [{"type": i.type, "confidence": i.confidence, "span": i.span} for i in v.issues],
        "citation_coverage": v.citation_coverage,
    }


def main():
    vectors = json.load(open(os.path.join(HERE, "vectors.json"), encoding="utf-8"))
    out = {"policy_version": vectors.get("policy_version"),
           "results": [verdict_to_dict(c["name"], check(c["answer"], c.get("sources", "")))
                       for c in vectors["cases"]]}
    with open(os.path.join(HERE, "expected.json"), "w", encoding="utf-8") as f:
        json.dump(out, f, indent=2, sort_keys=True)
        f.write("\n")
    print(f"wrote expected.json ({len(out['results'])} cases)")


if __name__ == "__main__":
    main()
