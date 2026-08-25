'use strict';
const test = require('node:test');
const assert = require('node:assert/strict');
const { fallY, planCursorChase, planFall } = require('../src/core/motion-planner');

test('fall advances monotonically and ends exactly on the floor', () => {
  const plan = planFall({ startY: 20, floorY: 320 });
  const samples = [0, .25, .5, .75, 1].map((ratio) => fallY(plan, plan.duration * ratio));
  assert.deepEqual([...samples].sort((a,b)=>a-b), samples);
  assert.equal(samples.at(-1), 320);
});

test('near-floor release skips fall', () => assert.equal(planFall({ startY: 315, floorY: 320 }), null));

test('cursor chase is short, directed, bounded, and remembers origin', () => {
  const plan = planCursorChase({ currentX: 400, cursorX: 700, windowWidth: 154, minX: 0, maxX: 1000 });
  assert.equal(plan.originX, 400);
  assert.equal(plan.direction, 1);
  assert.ok(plan.distance >= 28 && plan.distance <= 80);
  assert.equal(plan.targetX, 480);
});
