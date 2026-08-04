#!/usr/bin/env node
'use strict';
const fs = require('fs');
const path = require('path');
const { check } = require('../lib/check.js');

const argv = process.argv.slice(2);
if (argv[0] === '--answer') {
  const ans = argv[1] || '';
  const si = argv.indexOf('--sources');
  const src = si !== -1 ? (argv[si + 1] || '') : '';
  process.stdout.write(JSON.stringify(check(ans, src)) + '\n');
  process.exit(0);
}
const vpath = argv[0] || path.join(__dirname, '..', '..', 'conformance', 'vectors.json');
const v = JSON.parse(fs.readFileSync(vpath, 'utf8'));
const results = v.cases.map(c => Object.assign({ name: c.name }, check(c.answer, c.sources || '')));
process.stdout.write(JSON.stringify({ policy_version: v.policy_version, results }, null, 2) + '\n');
