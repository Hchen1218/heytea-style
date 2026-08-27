'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const { forwardedCommandLine, parseCommandLine } = require('../src/core/command-line');

test('parseCommandLine reads launcher actions', () => {
  assert.deepEqual(parseCommandLine(['runtime', '--open-pet', '/tmp/pet.zip']), {
    quit: false,
    show: false,
    openPet: '/tmp/pet.zip',
  });
});

test('forwardedCommandLine prefers the explicit single-instance payload', () => {
  const fallback = ['runtime'];
  const payload = ['runtime', '--open-pet', '/tmp/pet.zip'];
  assert.deepEqual(forwardedCommandLine(fallback, { argv: payload }), payload);
});

test('forwardedCommandLine falls back to Electron commandLine', () => {
  const fallback = ['runtime', '--quit'];
  assert.deepEqual(forwardedCommandLine(fallback, null), fallback);
});
