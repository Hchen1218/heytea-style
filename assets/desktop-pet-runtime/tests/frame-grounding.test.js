'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { groundingOffsets } = require('../src/core/frame-grounding');

test('grounding offsets align every visible frame to the floor anchor', () => {
  assert.deepEqual(groundingOffsets([
    { bottom: 346 },
    { bottom: 322 },
    { bottom: 344 },
    null,
  ], 344), [-2, 22, 0, 0]);
});

test('grounding offsets round fractional translations and ignore invalid boxes', () => {
  assert.deepEqual(groundingOffsets([{ bottom: 343.6 }, { bottom: Number.NaN }], 344), [0, 0]);
});
