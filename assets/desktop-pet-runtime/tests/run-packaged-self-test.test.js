'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const { parseSelfTestOutput } = require('../scripts/run-packaged-self-test');

test('parses SELF_TEST_RESULT when Chromium writes trailing stdout', () => {
  const payload = parseSelfTestOutput([
    'gpu process started',
    'SELF_TEST_RESULT:{"ok":true,"product":"Doodle Desktop Pet","version":"3.1.1"}',
    '[1234:0904] Chromium leftover',
    '',
  ].join('\n'));
  assert.deepEqual(payload, { ok: true, product: 'Doodle Desktop Pet', version: '3.1.1' });
});

test('rejects stdout that never contains the self-test prefix', () => {
  assert.throws(() => parseSelfTestOutput('{"ok":true}\n[gpu] leftover\n'), /self-test response was not found/);
});
