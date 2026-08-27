'use strict';

const DEFAULT_PROFILES = Object.freeze({
  quiet: { interval: [20000, 35000], cursorCooldown: 60000 },
  balanced: { interval: [8000, 15000], cursorCooldown: 30000 },
  lively: { interval: [5000, 9000], cursorCooldown: 18000 },
});

const DEFAULT_V3_CADENCE = Object.freeze({
  idleIntervalMs: [24000, 36000],
  ambientIntervalMs: [15000, 25000],
  postEpisodeQuietMs: 6000,
  pointerDwellMs: 2000,
  pointerCooldownMs: 60000,
  dragThresholdPx: 8,
  pointerResetsSleep: false,
  profileMultipliers: { quiet: 1.3, balanced: 1, lively: 0.8 },
});

const V2_AMBIENT = Object.freeze({
  curious: { quiet: 24, balanced: 22, lively: 19, cooldownMs: 18000 },
  stretch: { quiet: 19, balanced: 16, lively: 14, cooldownMs: 24000 },
  tiptoe: { quiet: 16, balanced: 14, lively: 13, cooldownMs: 18000 },
  play: { quiet: 18, balanced: 16, lively: 17, cooldownMs: 24000 },
  signature: { quiet: 10, balanced: 12, lively: 12, cooldownMs: 25000 },
  wave: { quiet: 8, balanced: 10, lively: 10, cooldownMs: 30000 },
  walk: { quiet: 5, balanced: 10, lively: 15, cooldownMs: 90000 },
});

function phase(id, clip, playback, completeOn, extra = {}) { return { id, clip, playback, completeOn, ...extra }; }

function compileV2(manifest) {
  const clips = Object.fromEntries(Object.entries(manifest.actions).map(([name, action]) => [name, { id: name, file: action.file, frames: action.frames, fps: action.fps, mirrorable: action.mirrorable }]));
  const behaviors = {};
  for (const name of ['idle', 'happy', 'land', 'wave', 'signature', 'curious', 'stretch', 'tiptoe', 'play']) {
    behaviors[name] = { id: name, phases: [phase('play', name, 'once', 'animation-finished')] };
  }
  behaviors.walk = { id: 'walk', phases: [phase('move', 'walk', 'loop', 'motion-finished', { motion: 'walk' })] };
  behaviors.rest = { id: 'rest', phases: [phase('sleep', 'rest', 'loop', 'timeout', { timeoutRangeMs: [20000, 45000] })] };
  behaviors.drag = { id: 'drag', phases: [phase('held', 'drag', 'loop', 'pointer-released')] };
  behaviors['v2-release'] = { id: 'v2-release', phases: [
    phase('fall', manifest.actions.fall ? 'fall' : 'drag', 'loop', 'floor-impact', { motion: 'fall' }),
    phase('land', 'land', 'once', 'animation-finished'),
  ] };
  behaviors['v2-pointer'] = { id: 'v2-pointer', phases: [
    phase('approach', 'walk', 'loop', 'motion-finished', { motion: 'cursor-approach' }),
    phase('touch', manifest.actions.touch ? 'touch' : 'wave', 'once', 'animation-finished'),
    phase('return', 'walk', 'loop', 'motion-finished', { motion: 'cursor-return' }),
  ] };
  return {
    schemaVersion: 2,
    base: { clip: 'idle', frame: 0 }, clips, behaviors,
    bindings: {
      idle: 'idle', click: 'happy', pointer: 'v2-pointer', drag: 'drag', release: 'v2-release',
      sleep: { behavior: 'rest', afterMs: 8 * 60 * 1000, wakeAfterMs: [20000, 45000] },
      ambient: Object.entries(V2_AMBIENT).map(([behavior, policy]) => ({ behavior, ...policy })),
    },
    profiles: DEFAULT_PROFILES,
    cadence: null,
  };
}

function compileV3(manifest) {
  const clips = {};
  const behaviors = {};
  for (const [behaviorName, behavior] of Object.entries(manifest.behaviors)) {
    const phases = behavior.phases.map((source) => {
      const clipId = `${behaviorName}:${source.id}`;
      clips[clipId] = { id: clipId, file: source.file, frames: source.frames, ...(source.fps ? { fps: source.fps } : { durationsMs: [...source.durationsMs] }), mirrorable: source.mirrorable, grounding: source.grounding || 'free' };
      return { id: source.id, clip: clipId, playback: source.playback, completeOn: source.completeOn, ...(source.motion ? { motion: source.motion } : {}), ...(source.timeoutMs ? { timeoutRangeMs: [source.timeoutMs, source.timeoutMs] } : {}) };
    });
    behaviors[behaviorName] = { id: behaviorName, phases };
  }
  const idleBehavior = behaviors[manifest.bindings.idle];
  return {
    schemaVersion: 3,
    base: { clip: idleBehavior.phases[0].clip, frame: 0 },
    clips,
    behaviors,
    bindings: JSON.parse(JSON.stringify(manifest.bindings)),
    profiles: DEFAULT_PROFILES,
    cadence: { ...DEFAULT_V3_CADENCE, ...(manifest.cadence || {}), profileMultipliers: { ...DEFAULT_V3_CADENCE.profileMultipliers, ...(manifest.cadence?.profileMultipliers || {}) } },
  };
}

function compileRuntimeModel(manifest) {
  if (manifest.schemaVersion === 2) return compileV2(manifest);
  if (manifest.schemaVersion === 3) return compileV3(manifest);
  throw new Error(`Unsupported schema version: ${manifest.schemaVersion}`);
}

module.exports = { DEFAULT_PROFILES, DEFAULT_V3_CADENCE, V2_AMBIENT, compileRuntimeModel };
