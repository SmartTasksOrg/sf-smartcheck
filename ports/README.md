# SmartCheck — language ports

Native re-implementations of SmartCheck's core (`check(answer, sources) → Verdict`)
in Go, Node, Java, and PHP, so the same governance gate runs in any stack — CI,
pre-commit, a Java service, a PHP app — with **no Python runtime**.

Every port is held to one contract: it must reproduce the **Python reference**
(`src/sf_smartcheck/core.py`) exactly — same rule IDs, confidences, span strings,
ordering, and citation-coverage — for every case in `conformance/vectors.json`.

## Rules (identical across all ports)
- `CHECK-UNSOURCED-NUMBER` (0.6) — a quantitative claim (3+ digit run, a percentage,
  or a number + magnitude word) with no `sources`.
- `CHECK-CONTRADICTION` (0.7) — `always … never` / `never … always`.
- `CHECK-HEDGED` (0.5) — hedging stated as fact (`i think`, `maybe`, `probably`, …).
- `CHECK-SEEDED` (0.9) — the demo marker `[contains seeded error]`.
- `citation_coverage` = 1.0 with sources, else 0.0 if the answer contains a digit, else 0.5.

## Verify
```bash
cd conformance && ./run.sh
```
Runs each port whose runtime is installed and diffs its output against the
Python-generated `expected.json`. Regenerate the reference after changing rules:
```bash
python gen_expected.py
```

## Contract files
- `conformance/vectors.json` — shared inputs.
- `conformance/expected.json` — Python reference output (source of truth).
- `conformance/compare.py` — float-normalising comparator.

Each port also supports a one-shot mode, e.g. `node node/bin/cli.js --answer "grew 340%"`.
