#!/usr/bin/env python3
"""SmartCheck integration adapter — the single source of truth for every
framework wrapper in this folder. Exposes TOOL_NAME, DESCRIPTION, INPUT_SCHEMA
and run(payload)->dict, plus a CLI:  python adapter.py --file <input>
"""
import argparse
import json
import os
import sys

from smartcheck.core import check

TOOL_NAME = "smartcheck_check"
DESCRIPTION = "Flag confident-but-unsourced AI output: unsourced numbers, contradictions, hedging, seeded errors."
INPUT_SCHEMA = {
    "type": "object",
    "properties": {
        "answer": {
                "type": "string",
                "description": "The AI answer to check"
        },
        "sources": {
                "type": "string",
                "description": "Cited sources (empty = none)",
                "default": ""
        }
    },
    "required": ["answer"],
}


def _read(p):
    with open(p, encoding="utf-8", errors="ignore") as f:
        return f.read()


def run(payload):
    """Run SmartCheck on a payload dict and return a compact, JSON-safe result."""
    v = check(payload.get('answer', ''), payload.get('sources', ''))
    result = {'passed': v.passed, 'citation_coverage': v.citation_coverage,
              'issues': [{'type': i.type, 'confidence': i.confidence, 'span': i.span} for i in v.issues]}
    return result


def main(argv=None):
    ap = argparse.ArgumentParser(description=DESCRIPTION)
    ap.add_argument("--text")
    ap.add_argument("--file")
    ap.add_argument("--root")
    ap.add_argument("--sources")
    args = ap.parse_args(argv)
    payload = {'answer': _read(args.file) if args.file else (args.text or ''), 'sources': args.sources or ''}
    print(json.dumps(run(payload)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
