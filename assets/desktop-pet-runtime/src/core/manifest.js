'use strict';

const path = require('node:path');

const REQUIRED_ACTIONS = Object.freeze(['idle', 'walk', 'rest', 'happy', 'drag', 'land', 'wave', 'signature', 'curious', 'stretch', 'tiptoe', 'play']);
const OPTIONAL_ACTIONS = Object.freeze(['fall', 'touch']);
const ALLOWED_ACTIONS = Object.freeze([...REQUIRED_ACTIONS, ...OPTIONAL_ACTIONS]);
const LEGACY_ACTIONS = Object.freeze(REQUIRED_ACTIONS.slice(0, 8));
const REQUIRED_BINDINGS = Object.freeze(['idle', 'sleep', 'click', 'pointer', 'drag', 'release', 'ambient']);
const COMPLETION_EVENTS = Object.freeze(['animation-finished', 'motion-finished', 'floor-impact', 'pointer-released', 'wake-requested', 'timeout']);
const MOTION_TYPES = Object.freeze(['walk', 'fall', 'cursor-approach', 'cursor-return']);

class ManifestError extends Error {}

function assert(condition, message) { if (!condition) throw new ManifestError(message); }
function between(value, min, max) { return Number.isInteger(value) && value >= min && value <= max; }

function validateRelativeAssetPath(value, label) {
  assert(typeof value === 'string' && value.length > 0, `${label} must be a non-empty string`);
  const normalized = value.replaceAll('\\', '/');
  assert(!path.posix.isAbsolute(normalized), `${label} must be relative`);
  assert(normalized.split('/').every((part) => part && part !== '.' && part !== '..' && !part.includes(':')), `${label} is unsafe`);
  assert(['.png', '.webp'].includes(path.posix.extname(normalized).toLowerCase()), `${label} must be PNG or WebP`);
  return normalized;
}

function inspectSchemaVersion(manifest) { return Number.isInteger(manifest?.schemaVersion) ? manifest.schemaVersion : null; }

function validateCommon(manifest) {
  assert(manifest && typeof manifest === 'object' && !Array.isArray(manifest), 'manifest must be an object');
  assert(/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(manifest.id), 'id must use lowercase letters, digits, and hyphens');
  assert(typeof manifest.displayName === 'string' && manifest.displayName.trim(), 'displayName is required');
  const { canvas, anchor, hitbox } = manifest;
  assert(canvas && between(canvas.width, 32, 1024) && between(canvas.height, 32, 1024), 'canvas dimensions must be 32-1024');
  assert(anchor && between(anchor.x, 0, canvas.width - 1) && between(anchor.y, 0, canvas.height - 1), 'anchor is outside the canvas');
  assert(typeof manifest.defaultScale === 'number' && manifest.defaultScale >= 0.5 && manifest.defaultScale <= 2, 'defaultScale must be 0.5-2');
  if (manifest.floorMode !== undefined) assert(['work-area', 'display-edge'].includes(manifest.floorMode), 'floorMode must be work-area or display-edge');
  assert(Array.isArray(manifest.palette) && manifest.palette.length >= 1 && manifest.palette.length <= 3 && manifest.palette.every((color) => /^#[0-9a-f]{6}$/i.test(color)), 'palette must have 1-3 #RRGGBB colors');
  assert(hitbox && between(hitbox.alphaThreshold, 1, 254) && hitbox.bounds, 'hitbox is invalid');
  const bounds = hitbox.bounds;
  assert(between(bounds.x, 0, canvas.width - 1) && between(bounds.y, 0, canvas.height - 1) && between(bounds.width, 1, canvas.width) && between(bounds.height, 1, canvas.height) && bounds.x + bounds.width <= canvas.width && bounds.y + bounds.height <= canvas.height, 'hitbox.bounds leaves the canvas');
}

function validateV2(manifest) {
  assert(manifest.actions && typeof manifest.actions === 'object' && !Array.isArray(manifest.actions), 'actions is required');
  const names = Object.keys(manifest.actions);
  assert(REQUIRED_ACTIONS.every((name) => names.includes(name)), 'all twelve schema-v2 actions are required');
  assert(names.every((name) => ALLOWED_ACTIONS.includes(name)), `unsupported action: ${names.find((name) => !ALLOWED_ACTIONS.includes(name))}`);
  for (const name of names) {
    const action = manifest.actions[name];
    assert(action && typeof action === 'object', `actions.${name} must be an object`);
    action.file = validateRelativeAssetPath(action.file, `actions.${name}.file`);
    assert(between(action.frames, 1, 24), `actions.${name}.frames must be 1-24`);
    assert(between(action.fps, 1, 30), `actions.${name}.fps must be 1-30`);
    assert(typeof action.loop === 'boolean' && typeof action.mirrorable === 'boolean', `actions.${name} flags must be boolean`);
  }
  assert(manifest.actions.walk.mirrorable === true, 'walk must be mirrorable');
}

function validatePhase(behaviorName, phase, index) {
  const label = `behaviors.${behaviorName}.phases[${index}]`;
  assert(phase && typeof phase === 'object' && !Array.isArray(phase), `${label} must be an object`);
  assert(/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(phase.id), `${label}.id is invalid`);
  phase.file = validateRelativeAssetPath(phase.file, `${label}.file`);
  assert(between(phase.frames, 1, 24), `${label}.frames must be 1-24`);
  const hasFps = phase.fps !== undefined;
  const hasDurations = phase.durationsMs !== undefined;
  assert(hasFps !== hasDurations, `${label} must declare exactly one of fps or durationsMs`);
  if (hasFps) assert(between(phase.fps, 1, 30), `${label}.fps must be 1-30`);
  if (hasDurations) {
    assert(Array.isArray(phase.durationsMs) && phase.durationsMs.length === phase.frames, `${label}.durationsMs must match frames`);
    assert(phase.durationsMs.every((duration) => between(duration, 34, 10000)), `${label}.durationsMs values must be 34-10000`);
  }
  assert(['once', 'loop'].includes(phase.playback), `${label}.playback must be once or loop`);
  assert(COMPLETION_EVENTS.includes(phase.completeOn), `${label}.completeOn is unsupported`);
  assert(typeof phase.mirrorable === 'boolean', `${label}.mirrorable must be boolean`);
  if (phase.grounding !== undefined) assert(['floor', 'free'].includes(phase.grounding), `${label}.grounding must be floor or free`);
  if (phase.playback === 'loop') assert(phase.completeOn !== 'animation-finished', `${label} loop must have an external exit event`);
  if (phase.motion !== undefined) assert(MOTION_TYPES.includes(phase.motion), `${label}.motion is unsupported`);
  if (phase.completeOn === 'timeout') assert(between(phase.timeoutMs, 100, 24 * 60 * 60 * 1000), `${label}.timeoutMs is required for timeout`);
  if (phase.completeOn === 'motion-finished') assert(['walk', 'cursor-approach', 'cursor-return'].includes(phase.motion), `${label} motion-finished requires walk or cursor motion`);
  if (phase.completeOn === 'floor-impact') assert(phase.motion === 'fall', `${label} floor-impact requires fall motion`);
}

function validateRange(value, label, min = 1000, max = 24 * 60 * 60 * 1000) {
  assert(Array.isArray(value) && value.length === 2 && value.every((item) => between(item, min, max)) && value[0] <= value[1], `${label} is invalid`);
}

function validateCadence(cadence) {
  if (cadence === undefined) return;
  assert(cadence && typeof cadence === 'object' && !Array.isArray(cadence), 'cadence must be an object');
  validateRange(cadence.idleIntervalMs, 'cadence.idleIntervalMs');
  validateRange(cadence.ambientIntervalMs, 'cadence.ambientIntervalMs');
  assert(between(cadence.postEpisodeQuietMs, 0, 24 * 60 * 60 * 1000), 'cadence.postEpisodeQuietMs is invalid');
  assert(between(cadence.pointerDwellMs, 250, 60 * 1000), 'cadence.pointerDwellMs is invalid');
  assert(between(cadence.pointerCooldownMs, 0, 24 * 60 * 60 * 1000), 'cadence.pointerCooldownMs is invalid');
  assert(between(cadence.dragThresholdPx, 1, 64), 'cadence.dragThresholdPx is invalid');
  assert(typeof cadence.pointerResetsSleep === 'boolean', 'cadence.pointerResetsSleep must be boolean');
  const multipliers = cadence.profileMultipliers;
  assert(multipliers && typeof multipliers === 'object' && !Array.isArray(multipliers), 'cadence.profileMultipliers is required');
  for (const level of ['quiet', 'balanced', 'lively']) {
    assert(typeof multipliers[level] === 'number' && multipliers[level] >= 0.25 && multipliers[level] <= 4, `cadence.profileMultipliers.${level} is invalid`);
  }
}

function validateV3(manifest) {
  assert(manifest.characterMode === 'flavor-monster', 'schema v3 characterMode must be flavor-monster');
  validateCadence(manifest.cadence);
  assert(manifest.behaviors && typeof manifest.behaviors === 'object' && !Array.isArray(manifest.behaviors), 'behaviors is required');
  const behaviorNames = Object.keys(manifest.behaviors);
  assert(behaviorNames.length >= 6 && behaviorNames.length <= 10, 'schema v3 requires 6-10 behaviors');
  assert(behaviorNames.every((name) => /^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(name)), 'behavior names must use lowercase letters, digits, and hyphens');
  for (const name of behaviorNames) {
    const behavior = manifest.behaviors[name];
    assert(behavior && typeof behavior === 'object' && !Array.isArray(behavior), `behaviors.${name} must be an object`);
    assert(Array.isArray(behavior.phases) && behavior.phases.length >= 1 && behavior.phases.length <= 12, `behaviors.${name}.phases must contain 1-12 phases`);
    const ids = behavior.phases.map((phase) => phase?.id);
    assert(new Set(ids).size === ids.length, `behaviors.${name} phase ids must be unique`);
    behavior.phases.forEach((phase, index) => validatePhase(name, phase, index));
  }

  const bindings = manifest.bindings;
  assert(bindings && typeof bindings === 'object' && !Array.isArray(bindings), 'bindings is required');
  assert(REQUIRED_BINDINGS.every((name) => Object.hasOwn(bindings, name)), 'all schema-v3 bindings are required');
  const direct = ['idle', 'click', 'pointer', 'drag', 'release'];
  for (const name of direct) assert(typeof bindings[name] === 'string' && behaviorNames.includes(bindings[name]), `bindings.${name} must reference a behavior`);
  assert(bindings.sleep && typeof bindings.sleep === 'object' && behaviorNames.includes(bindings.sleep.behavior), 'bindings.sleep.behavior must reference a behavior');
  assert(between(bindings.sleep.afterMs, 1000, 24 * 60 * 60 * 1000), 'bindings.sleep.afterMs is invalid');
  assert(Array.isArray(bindings.sleep.wakeAfterMs) && bindings.sleep.wakeAfterMs.length === 2 && bindings.sleep.wakeAfterMs.every((value) => between(value, 1000, 24 * 60 * 60 * 1000)) && bindings.sleep.wakeAfterMs[0] <= bindings.sleep.wakeAfterMs[1], 'bindings.sleep.wakeAfterMs is invalid');
  assert(Array.isArray(bindings.ambient) && bindings.ambient.length >= 1, 'bindings.ambient must not be empty');
  for (const [index, item] of bindings.ambient.entries()) {
    assert(item && typeof item === 'object' && behaviorNames.includes(item.behavior), `bindings.ambient[${index}].behavior must reference a behavior`);
    assert(between(item.weight, 1, 100), `bindings.ambient[${index}].weight must be 1-100`);
    assert(between(item.cooldownMs, 0, 24 * 60 * 60 * 1000), `bindings.ambient[${index}].cooldownMs is invalid`);
  }
  const reachable = new Set([...direct.map((name) => bindings[name]), bindings.sleep.behavior, ...bindings.ambient.map((item) => item.behavior)]);
  const unreachable = behaviorNames.filter((name) => !reachable.has(name));
  assert(unreachable.length === 0, `unbound behaviors: ${unreachable.join(', ')}`);
}

function validateManifest(manifest) {
  validateCommon(manifest);
  if (manifest.schemaVersion === 2) validateV2(manifest);
  else if (manifest.schemaVersion === 3) validateV3(manifest);
  else throw new ManifestError('schemaVersion must be 2 or 3');
  return manifest;
}

module.exports = { ALLOWED_ACTIONS, COMPLETION_EVENTS, LEGACY_ACTIONS, MOTION_TYPES, ManifestError, OPTIONAL_ACTIONS, REQUIRED_ACTIONS, REQUIRED_BINDINGS, inspectSchemaVersion, validateManifest, validateRelativeAssetPath };
