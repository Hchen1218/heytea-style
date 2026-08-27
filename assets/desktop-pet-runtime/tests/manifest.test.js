'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { ManifestError, REQUIRED_ACTIONS, validateManifest } = require('../src/core/manifest');
const { compileRuntimeModel } = require('../src/core/runtime-model');

function validManifest() {
  return {
    schemaVersion: 2,
    id: 'tea-cup',
    displayName: 'Tea Cup',
    canvas: { width: 256, height: 256 },
    anchor: { x: 128, y: 230 },
    defaultScale: 0.6,
    palette: ['#E8C84E', '#111111'],
    hitbox: { alphaThreshold: 24, bounds: { x: 20, y: 12, width: 216, height: 230 } },
    actions: Object.fromEntries(REQUIRED_ACTIONS.map((name) => [name, {
      file: `animations/${name}.webp`,
      frames: 4,
      fps: 6,
      loop: ['idle', 'walk', 'rest', 'drag'].includes(name),
      mirrorable: name === 'walk',
    }])),
  };
}

function validV3Manifest() {
  const names = ['awake-story', 'explore-walk', 'sleep-cycle', 'affection-click', 'cursor-encounter', 'held', 'drop-recover', 'fruit-hiccup'];
  const behaviors = Object.fromEntries(names.map((name) => [name, { phases: [{
    id: 'play', file: `animations/${name}.webp`, frames: 4, fps: 3,
    playback: 'once', completeOn: 'animation-finished', mirrorable: false,
  }] }]));
  behaviors['explore-walk'].phases[0] = { id: 'move', file: 'animations/explore-walk.webp', frames: 4, fps: 3, playback: 'loop', completeOn: 'motion-finished', motion: 'walk', mirrorable: true };
  behaviors['sleep-cycle'].phases[0] = { id: 'sleep', file: 'animations/sleep-cycle.webp', frames: 4, durationsMs: [300, 500, 500, 300], playback: 'loop', completeOn: 'wake-requested', mirrorable: false };
  behaviors.held.phases[0] = { id: 'held', file: 'animations/held.webp', frames: 4, fps: 3, playback: 'loop', completeOn: 'pointer-released', mirrorable: false };
  behaviors['drop-recover'].phases[0] = { id: 'fall', file: 'animations/drop-recover.webp', frames: 4, fps: 3, playback: 'loop', completeOn: 'floor-impact', motion: 'fall', mirrorable: false };
  return {
    schemaVersion: 3, characterMode: 'flavor-monster', id: 'fruit-monster', displayName: 'Fruit Monster',
    canvas: { width: 384, height: 384 }, anchor: { x: 192, y: 344 }, defaultScale: 0.6,
    palette: ['#F4BFC0', '#C8D85A', '#FFB62E'],
    hitbox: { alphaThreshold: 24, bounds: { x: 20, y: 12, width: 344, height: 350 } },
    bindings: {
      idle: 'awake-story', ambient: [{ behavior: 'explore-walk', weight: 2, cooldownMs: 90000 }, { behavior: 'fruit-hiccup', weight: 1, cooldownMs: 25000 }],
      sleep: { behavior: 'sleep-cycle', afterMs: 480000, wakeAfterMs: [60000, 180000] },
      click: 'affection-click', pointer: 'cursor-encounter', drag: 'held', release: 'drop-recover',
    },
    behaviors,
  };
}

function validCadence() {
  return {
    idleIntervalMs: [24000, 36000],
    ambientIntervalMs: [15000, 25000],
    postEpisodeQuietMs: 6000,
    pointerDwellMs: 2000,
    pointerCooldownMs: 60000,
    dragThresholdPx: 8,
    pointerResetsSleep: false,
    profileMultipliers: { quiet: 1.3, balanced: 1, lively: 0.8 },
  };
}

test('accepts the public v2 manifest', () => {
  assert.equal(validateManifest(validManifest()).id, 'tea-cup');
});

test('accepts recognized fall and touch extensions', () => {
  const manifest = validManifest();
  for (const name of ['fall', 'touch']) manifest.actions[name] = { file: `animations/${name}.webp`, frames: 4, fps: 3, loop: name === 'fall', mirrorable: name === 'touch' };
  assert.equal(validateManifest(manifest).id, 'tea-cup');
});

test('rejects missing states', () => {
  const manifest = validManifest();
  delete manifest.actions.signature;
  assert.throws(() => validateManifest(manifest), ManifestError);
});

test('rejects traversal paths', () => {
  const manifest = validManifest();
  manifest.actions.idle.file = '../idle.webp';
  assert.throws(() => validateManifest(manifest), ManifestError);
});

test('requires a mirrorable walk action', () => {
  const manifest = validManifest();
  manifest.actions.walk.mirrorable = false;
  assert.throws(() => validateManifest(manifest), /walk must be mirrorable/);
});

test('accepts schema v3 with eight reachable behaviors', () => {
  const manifest = validV3Manifest();
  manifest.cadence = validCadence();
  assert.equal(validateManifest(manifest).schemaVersion, 3);
  const model = compileRuntimeModel(manifest);
  assert.equal(model.bindings.sleep.behavior, 'sleep-cycle');
  assert.equal(Object.keys(model.behaviors).length, 8);
  assert.deepEqual(model.clips['sleep-cycle:sleep'].durationsMs, [300, 500, 500, 300]);
  assert.deepEqual(model.cadence.idleIntervalMs, [24000, 36000]);
});

test('v3 rejects malformed cadence policy', () => {
  const missing = validV3Manifest();
  missing.cadence = { ...validCadence(), idleIntervalMs: [36000, 24000] };
  assert.throws(() => validateManifest(missing), /cadence.idleIntervalMs is invalid/);
  const negative = validV3Manifest();
  negative.cadence = { ...validCadence(), dragThresholdPx: 0 };
  assert.throws(() => validateManifest(negative), /cadence.dragThresholdPx is invalid/);
  const multiplier = validV3Manifest();
  multiplier.cadence = { ...validCadence(), profileMultipliers: { quiet: 1.3, balanced: 0, lively: 0.8 } };
  assert.throws(() => validateManifest(multiplier), /cadence.profileMultipliers.balanced is invalid/);
});

test('v2 compiles to the same episode model without changing the manifest', () => {
  const manifest = validManifest();
  const model = compileRuntimeModel(validateManifest(manifest));
  assert.equal(model.schemaVersion, 2);
  assert.equal(model.bindings.click, 'happy');
  assert.deepEqual(model.behaviors['v2-release'].phases.map((phase) => phase.id), ['fall', 'land']);
  assert.equal(manifest.schemaVersion, 2);
});

test('v3 rejects unbound behaviors and non-terminating loops', () => {
  const unbound = validV3Manifest();
  unbound.bindings.ambient = [{ behavior: 'explore-walk', weight: 2, cooldownMs: 90000 }];
  assert.throws(() => validateManifest(unbound), /unbound behaviors/);
  const badLoop = validV3Manifest();
  badLoop.behaviors['sleep-cycle'].phases[0].completeOn = 'animation-finished';
  assert.throws(() => validateManifest(badLoop), /external exit event/);
});

test('v3 rejects invalid phase timing and unsafe paths', () => {
  const timing = validV3Manifest();
  timing.behaviors['awake-story'].phases[0].durationsMs = [100];
  assert.throws(() => validateManifest(timing), /exactly one of fps or durationsMs/);
  const traversal = validV3Manifest();
  traversal.behaviors['awake-story'].phases[0].file = '../awake.webp';
  assert.throws(() => validateManifest(traversal), /unsafe/);
});

test('v3 accepts floor/free grounding metadata and rejects unknown modes', () => {
  const manifest = validV3Manifest();
  manifest.behaviors['awake-story'].phases[0].grounding = 'floor';
  manifest.behaviors.held.phases[0].grounding = 'free';
  assert.equal(validateManifest(manifest).schemaVersion, 3);
  const model = compileRuntimeModel(manifest);
  assert.equal(model.clips['awake-story:play'].grounding, 'floor');
  assert.equal(model.clips['held:held'].grounding, 'free');
  const invalid = validV3Manifest();
  invalid.behaviors['awake-story'].phases[0].grounding = 'floating';
  assert.throws(() => validateManifest(invalid), /grounding must be floor or free/);
});

test('floorMode selects a valid physical floor boundary', () => {
  const manifest = validV3Manifest();
  manifest.floorMode = 'display-edge';
  assert.equal(validateManifest(manifest).floorMode, 'display-edge');
  manifest.floorMode = 'floating';
  assert.throws(() => validateManifest(manifest), /floorMode must be work-area or display-edge/);
});
