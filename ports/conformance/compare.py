#!/usr/bin/env python3
"""Compare a port's stdout JSON against expected.json (float-normalised, order-sensitive).
Usage:  <port emits JSON on stdout> | python compare.py expected.json
Exits 0 on PASS, 1 on first mismatch."""
import json
import sys


def norm(results):
    return [{
        "name": r["name"],
        "passed": bool(r["passed"]),
        "citation_coverage": round(float(r["citation_coverage"]), 6),
        "issues": [{"type": i["type"], "confidence": round(float(i["confidence"]), 6),
                    "span": i["span"]} for i in r["issues"]],
    } for r in results]


def main():
    expected = json.load(open(sys.argv[1], encoding="utf-8"))["results"]
    got = json.load(sys.stdin)["results"]
    e, g = norm(expected), norm(got)
    if e == g:
        print(f"PASS ({len(e)} cases)")
        return 0
    if len(e) != len(g):
        print(f"FAIL: case count {len(g)} != expected {len(e)}")
        return 1
    for a, b in zip(e, g):
        if a != b:
            print(f"FAIL at case '{a['name']}':")
            print("  expected:", json.dumps(a, sort_keys=True))
            print("  got:     ", json.dumps(b, sort_keys=True))
            return 1
    return 1


if __name__ == "__main__":
    sys.exit(main())
