'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { ManifestError, REQUIRED_ACTIONS, validateManifest } = require('../src/core/manifest');

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
