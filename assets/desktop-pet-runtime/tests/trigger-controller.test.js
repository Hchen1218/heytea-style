'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { TriggerController } = require('../src/core/trigger-controller');

function model() {
  const behaviors = Object.fromEntries(['idle', 'walk', 'hiccup', 'sleep', 'click', 'pointer', 'drag', 'release'].map((name) => [name, { id: name, phases: [{ motion: name === 'walk' ? 'walk' : undefined, completeOn: name === 'sleep' ? 'wake-requested' : 'animation-finished' }] }]));
  return {
    behaviors,
    profiles: { quiet: { interval: [20000, 35000] }, balanced: { interval: [8000, 15000] }, lively: { interval: [5000, 9000] } },
    bindings: {
      idle: 'idle', ambient: [{ behavior: 'walk', weight: 2, cooldownMs: 90000 }, { behavior: 'hiccup', weight: 1, cooldownMs: 25000 }],
      sleep: { behavior: 'sleep', afterMs: 1000, wakeAfterMs: [60000, 180000] }, click: 'click', pointer: 'pointer', drag: 'drag', release: 'release',
    },
  };
}

function v3Model() {
  const runtimeModel = model();
  runtimeModel.schemaVersion = 3;
  runtimeModel.cadence = {
    idleIntervalMs: [24000, 36000],
    ambientIntervalMs: [15000, 25000],
    postEpisodeQuietMs: 6000,
    pointerDwellMs: 2000,
    pointerCooldownMs: 60000,
    dragThresholdPx: 8,
    pointerResetsSleep: false,
    profileMultipliers: { quiet: 1.3, balanced: 1, lively: 0.8 },
  };
  return runtimeModel;
}

test('sleep blocks ambient and queues click behind wake', () => {
  let now = 0;
  const controller = new TriggerController(model(), { now: () => now, random: () => 0 });
  now = 1001;
  assert.equal(controller.tick().behavior, 'sleep');
  assert.equal(controller.sleeping, true);
  assert.deepEqual(controller.interact('click'), { type: 'signal', event: 'wake-requested' });
  assert.equal(controller.complete('sleep').behavior, 'click');
});

test('legacy timeout sleep remains directly interruptible', () => {
  let now = 0;
  const runtimeModel = model();
  runtimeModel.behaviors.sleep.phases[0].completeOn = 'timeout';
  const controller = new TriggerController(runtimeModel, { now: () => now, random: () => 0 });
  now = 1001;
  controller.tick();
  assert.equal(controller.sleeping, false);
  assert.equal(controller.interact('click').behavior, 'click');
});

test('drag release signals the held loop then starts the release behavior', () => {
  const controller = new TriggerController(model(), { random: () => 0 });
  assert.equal(controller.interact('drag').behavior, 'drag');
  assert.deepEqual(controller.interact('release', { moved: true }), { type: 'signal', event: 'pointer-released' });
  assert.equal(controller.complete('drag').behavior, 'release');
});

test('an unmoved legacy release resolves to click instead of fall recovery', () => {
  const controller = new TriggerController(model(), { random: () => 0 });
  assert.equal(controller.interact('drag').behavior, 'drag');
  assert.deepEqual(controller.interact('release', { moved: false }), { type: 'signal', event: 'pointer-released' });
  assert.equal(controller.complete('drag').behavior, 'click');
});

test('reduced motion blocks autonomous locomotion and pointer chase', () => {
  let now = 100000;
  const controller = new TriggerController(model(), { now: () => now, random: () => 0, reducedMotion: true });
  assert.equal(controller.interact('pointer').type, 'none');
  assert.equal(controller.eligibleAmbient(controller.model.bindings.ambient[0], now), false);
  assert.equal(controller.eligibleAmbient(controller.model.bindings.ambient[1], now), true);
});

test('ambient cooldown and non-repetition are data driven', () => {
  let now = 200000;
  const controller = new TriggerController(model(), { now: () => now, random: () => 0 });
  controller.lastStarted.walk = now - 89999;
  assert.equal(controller.eligibleAmbient(controller.model.bindings.ambient[0], now), false);
  controller.lastAmbient = 'hiccup';
  assert.equal(controller.eligibleAmbient(controller.model.bindings.ambient[1], now), false);
});

test('v3 cadence scales idle and ambient cooldowns by activity level', () => {
  let now = 0;
  const controller = new TriggerController(v3Model(), { now: () => now, random: () => 0 });
  assert.equal(controller.nextIdleAt, 24000);
  assert.equal(controller.nextAmbientAt, 15000);
  controller.setActivityLevel('lively');
  assert.equal(controller.nextIdleAt, 19200);
  assert.equal(controller.nextAmbientAt, 12000);
  controller.setActivityLevel('quiet');
  assert.equal(controller.nextIdleAt, 31200);
  assert.equal(controller.nextAmbientAt, 19500);
});

test('v3 pointer proximity does not reset the sleep clock but click does', () => {
  let now = 0;
  const controller = new TriggerController(v3Model(), { now: () => now, random: () => 0 });
  now = 1000;
  controller.interact('pointer');
  assert.equal(controller.lastInteractionAt, 0);
  controller.interact('click');
  assert.equal(controller.lastInteractionAt, 1000);
});

test('v3 ambient can repeat when it is the only cooled-down candidate', () => {
  let now = 0;
  const runtimeModel = v3Model();
  runtimeModel.bindings.ambient = [{ behavior: 'hiccup', weight: 1, cooldownMs: 1000 }];
  const controller = new TriggerController(runtimeModel, { now: () => now, random: () => 0 });
  controller.lastAmbient = 'hiccup';
  controller.lastStarted.hiccup = 0;
  now = 1000;
  assert.equal(controller.chooseAmbient(), 'hiccup');
});

test('click preempts pointer but cannot preempt release recovery', () => {
  const controller = new TriggerController(model(), { random: () => 0 });
  assert.equal(controller.interact('pointer').behavior, 'pointer');
  assert.equal(controller.interact('click').behavior, 'click');
  controller.complete('click');
  assert.equal(controller.interact('release', { moved: true }).behavior, 'release');
  assert.equal(controller.interact('click').type, 'none');
});

test('completed episodes enforce a quiet interval', () => {
  let now = 0;
  const controller = new TriggerController(model(), { now: () => now, random: () => 0 });
  controller.interact('click');
  controller.complete('click', now);
  now = 3999;
  assert.equal(controller.tick().type, 'none');
  assert.equal(controller.quietUntil, 4000);
});

test('paused controller clears activity and ignores triggers', () => {
  const controller = new TriggerController(model(), { random: () => 0 });
  controller.interact('drag');
  controller.setPaused(true);
  assert.equal(controller.current, null);
  assert.equal(controller.interact('release', { moved: true }).type, 'none');
});

test('awake idle does not starve ambient behaviors in a long simulation', () => {
  let now = 0;
  let seed = 11;
  const random = () => ((seed = (seed * 48271) % 2147483647) / 2147483647);
  const runtimeModel = model();
  runtimeModel.bindings.sleep.afterMs = 99 * 60 * 1000;
  const controller = new TriggerController(runtimeModel, { now: () => now, random });
  const sources = new Set();
  for (now = 0; now <= 10 * 60 * 1000; now += 250) {
    const command = controller.tick(now);
    if (command.type === 'start') {
      sources.add(command.source);
      controller.complete(command.behavior, now + 1000);
    }
  }
  assert.ok(sources.has('idle'));
  assert.ok(sources.has('ambient'));
});
