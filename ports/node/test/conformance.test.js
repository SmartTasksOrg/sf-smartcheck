'use strict';
// npm test -> runs the shared conformance vectors through the Node port and
// asserts they match the Python-generated expected.json.
const fs = require('fs'), path = require('path'), assert = require('assert');
const { check } = require('../lib/check.js');
const C = path.join(__dirname, '..', '..', 'conformance');
const vectors = JSON.parse(fs.readFileSync(path.join(C, 'vectors.json'), 'utf8'));
const expected = JSON.parse(fs.readFileSync(path.join(C, 'expected.json'), 'utf8')).results;

let n = 0;
for (const c of vectors.cases) {
  const got = check(c.answer, c.sources || '');
  const exp = expected.find(e => e.name === c.name);
  assert.strictEqual(got.passed, exp.passed, `${c.name}: passed`);
  assert.strictEqual(Number(got.citation_coverage), Number(exp.citation_coverage), `${c.name}: coverage`);
  assert.strictEqual(got.issues.length, exp.issues.length, `${c.name}: issue count`);
  got.issues.forEach((is, i) => assert.strictEqual(is.type, exp.issues[i].type, `${c.name}: issue ${i}`));
  n++;
}
console.log(`ok - ${n} conformance cases pass`);
