'use strict';
/*
 * SmartCheck — native Node port.
 * Faithfully reproduces the Python reference (sf_smartcheck.core.check): the same
 * rule IDs, confidences, span strings, ordering, and citation-coverage logic.
 * Verified against ports/conformance/expected.json. Zero runtime dependencies.
 */

// A quantitative claim: a 3+ digit run, a percentage, or a number + magnitude word.
const NUM = /\b\d{3,}\b|\b\d+(?:\.\d+)?\s?%|\b\d+(?:\.\d+)?\s*(?:hundred|thousand|million|billion|trillion)\b/i;
const CONTRA = /\balways\b.*\bnever\b|\bnever\b.*\balways\b/i;
const HEDGE = /\b(?:as of my knowledge|i think|maybe|probably)\b/i;

function check(answer, sources = '') {
  const issues = [];
  if (NUM.test(answer) && !sources)
    issues.push({ type: 'CHECK-UNSOURCED-NUMBER', confidence: 0.6, span: 'numeric claim with no source' });
  if (CONTRA.test(answer))
    issues.push({ type: 'CHECK-CONTRADICTION', confidence: 0.7, span: 'internal contradiction' });
  if (HEDGE.test(answer))
    issues.push({ type: 'CHECK-HEDGED', confidence: 0.5, span: 'hedged/uncertain claim stated as fact' });
  if (answer.includes('[contains seeded error]'))
    issues.push({ type: 'CHECK-SEEDED', confidence: 0.9, span: 'known seeded error (demo)' });

  const coverage = sources ? 1.0 : (/\d/.test(answer) ? 0.0 : 0.5);
  return { passed: issues.length === 0, issues, citation_coverage: coverage };
}

module.exports = { check };
