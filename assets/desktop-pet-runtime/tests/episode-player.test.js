'use strict';

const test = require('node:test');
const assert = require('node:assert/strict');
const { EpisodePlayer } = require('../src/core/episode-player');

const model = { behaviors: {
  sleep: { id: 'sleep', phases: [
    { id: 'enter', clip: 'a', playback: 'once', completeOn: 'animation-finished' },
    { id: 'loop', clip: 'b', playback: 'loop', completeOn: 'wake-requested' },
    { id: 'exit', clip: 'c', playback: 'once', completeOn: 'animation-finished' },
  ] },
  fall: { id: 'fall', phases: [
    { id: 'air', clip: 'd', playback: 'loop', completeOn: 'floor-impact', motion: 'fall' },
    { id: 'impact', clip: 'e', playback: 'once', completeOn: 'animation-finished' },
  ] },
  timed: { id: 'timed', phases: [{ id: 'hold', clip: 'f', playback: 'loop', completeOn: 'timeout', timeoutRangeMs: [100, 100] }] },
} };

test('sleep advances enter to persistent loop and exits only on wake request', () => {
  const player = new EpisodePlayer(model, { now: () => 0 });
  assert.equal(player.start('sleep').phase.id, 'enter');
  assert.equal(player.signal('animation-finished').phase.id, 'loop');
  assert.equal(player.signal('animation-finished').status, 'ignored');
  assert.equal(player.signal('wake-requested').phase.id, 'exit');
  assert.equal(player.signal('animation-finished').status, 'completed');
});

test('floor impact advances fall into impact animation', () => {
  const player = new EpisodePlayer(model);
  player.start('fall');
  assert.equal(player.signal('motion-finished').status, 'ignored');
  assert.equal(player.signal('floor-impact').phase.id, 'impact');
});

test('timeout phases finish at their deadline', () => {
  let now = 0;
  const player = new EpisodePlayer(model, { now: () => now, random: () => 0 });
  player.start('timed');
  now = 99; assert.equal(player.tick().status, 'waiting');
  now = 100; assert.equal(player.tick().status, 'completed');
});
