'use strict';

const assert = require('node:assert/strict');
const test = require('node:test');
const { GestureState } = require('../src/core/gesture-state');

test('a stationary press resolves to one click on release', () => {
  const gesture = new GestureState(8);
  assert.equal(gesture.press({ x: 100, y: 100 }).type, 'pressed');
  assert.equal(gesture.move({ x: 105, y: 103 }).type, 'pending');
  assert.deepEqual(gesture.release(), { type: 'click' });
  assert.equal(gesture.state, 'idle');
});

test('movement at the threshold starts drag exactly once', () => {
  const gesture = new GestureState(8);
  gesture.press({ x: 100, y: 100 });
  assert.equal(gesture.move({ x: 106, y: 106 }).type, 'drag-start');
  assert.equal(gesture.move({ x: 120, y: 105 }).type, 'drag-move');
  assert.deepEqual(gesture.release(), { type: 'drag-release', moved: true });
});

test('legacy five-pixel threshold distinguishes a click from a moved drag', () => {
  const click = new GestureState(5);
  click.press({ x: 100, y: 100 });
  assert.equal(click.move({ x: 103, y: 103 }).type, 'pending');
  assert.deepEqual(click.release(), { type: 'click' });

  const drag = new GestureState(5);
  drag.press({ x: 100, y: 100 });
  assert.equal(drag.move({ x: 105, y: 100 }).type, 'drag-start');
  assert.deepEqual(drag.release(), { type: 'drag-release', moved: true });
});

test('cancelled pending press produces no click or drag', () => {
  const gesture = new GestureState(8);
  gesture.press({ x: 40, y: 40 });
  assert.deepEqual(gesture.cancel(), { type: 'cancel' });
  assert.equal(gesture.state, 'idle');
});

test('cancelled drag uses the same release path as a moved drag', () => {
  const gesture = new GestureState(8);
  gesture.press({ x: 40, y: 40 });
  gesture.move({ x: 50, y: 40 });
  assert.deepEqual(gesture.cancel(), { type: 'drag-release', moved: true });
});

test('a second press cannot overlap an active gesture', () => {
  const gesture = new GestureState(8);
  gesture.press({ x: 40, y: 40 });
  assert.deepEqual(gesture.press({ x: 80, y: 80 }), { type: 'none' });
});
