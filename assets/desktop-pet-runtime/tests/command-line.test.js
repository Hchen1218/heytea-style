'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { parseCommandLine } = require('../src/core/command-line');

test('parses a delivery-folder open command', () => {
  assert.deepEqual(parseCommandLine(['runner', '--open-pet', '/tmp/tea.zip']), {
    quit: false, show: false, openPet: '/tmp/tea.zip',
  });
});

test('parses show and graceful quit commands', () => {
  assert.equal(parseCommandLine(['runner', '--show']).show, true);
  assert.equal(parseCommandLine(['runner', '--quit']).quit, true);
});

test('ignores an incomplete open command', () => {
  assert.equal(parseCommandLine(['runner', '--open-pet']).openPet, null);
});
