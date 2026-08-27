'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { floorBottom } = require('../src/core/floor-policy');

const display = {
  bounds: { x: 0, y: 0, width: 1440, height: 900 },
  workArea: { x: 0, y: 25, width: 1440, height: 841 },
};

test('work-area floor keeps legacy pets above the Dock/taskbar', () => {
  assert.equal(floorBottom(display), 866);
  assert.equal(floorBottom(display, 'work-area'), 866);
});

test('display-edge floor removes the reserved-area floating gap', () => {
  assert.equal(floorBottom(display, 'display-edge'), 900);
});
