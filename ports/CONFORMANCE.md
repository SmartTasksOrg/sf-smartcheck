# SmartCheck port conformance contract

The Python core (`src/sf_smartcheck/core.py`) is the source of truth. A port is
correct **iff** it produces the same `Verdict` as the reference for every case
in `conformance/vectors.json`.

A `Verdict` is: `passed` (bool), `issues` (ordered list of `{type, confidence, span}`),
`citation_coverage` (float). Numbers are compared by value; issue **order** matters
(rules fire in the order: unsourced-number, contradiction, hedged, seeded).

## Add a case
1. Add `{name, answer, sources}` to `conformance/vectors.json`.
2. `python conformance/gen_expected.py` to refresh `expected.json`.
3. `./conformance/run.sh` — all installed ports must stay green.

## CI
Wire `conformance/run.sh` into each language's CI job; it exits non-zero on any
mismatch. Runtimes that aren't installed are reported as SKIP, not failure.
