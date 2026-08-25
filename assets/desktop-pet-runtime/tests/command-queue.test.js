'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { createCommandQueue } = require('../src/core/command-queue');

test('holds early launcher commands until the runtime is ready', async () => {
  const handled = [];
  const queue = createCommandQueue(async (argv) => handled.push(argv));

  await queue.dispatch(['runner', '--open-pet', '/tmp/tea.zip']);
  assert.deepEqual(handled, []);

  await queue.markReady();
  assert.deepEqual(handled, [['runner', '--open-pet', '/tmp/tea.zip']]);
});

test('runs ready commands sequentially', async () => {
  const handled = [];
  const queue = createCommandQueue(async (argv) => {
    await Promise.resolve();
    handled.push(argv.at(-1));
  });

  await queue.markReady();
  await Promise.all([
    queue.dispatch(['runner', '--show']),
    queue.dispatch(['runner', '--quit']),
  ]);
  assert.deepEqual(handled, ['--show', '--quit']);
});
