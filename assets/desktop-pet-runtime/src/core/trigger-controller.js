'use strict';

const PRIORITY = Object.freeze({ idle: 0, ambient: 1, sleep: 2, pointer: 3, click: 4, drag: 5, release: 6 });

class TriggerController {
  constructor(model, options = {}) {
    this.model = model;
    this.random = options.random || Math.random;
    this.now = options.now || (() => Date.now());
    this.activityLevel = model.profiles[options.activityLevel] ? options.activityLevel : 'balanced';
    this.reducedMotion = Boolean(options.reducedMotion);
    this.paused = false;
    this.current = null;
    this.queue = [];
    this.sleeping = false;
    this.lastInteractionAt = this.now();
    this.lastSleepAt = this.now();
    this.lastStarted = Object.create(null);
    this.lastAmbient = null;
    this.quietUntil = 0;
    this.nextIdleAt = this.scheduleIdle(this.now());
    this.nextAmbientAt = this.scheduleAmbient(this.now());
  }

  profile() { return this.model.profiles[this.reducedMotion ? 'quiet' : this.activityLevel]; }
  cadence() { return this.model.schemaVersion === 3 ? this.model.cadence : null; }
  cadenceLevel() { return this.reducedMotion ? 'quiet' : this.activityLevel; }
  cadenceMultiplier() { return this.cadence()?.profileMultipliers?.[this.cadenceLevel()] || 1; }
  scheduleRange(from, range) {
    const multiplier = this.cadenceMultiplier();
    const low = range[0] * multiplier;
    const high = range[1] * multiplier;
    return from + low + this.random() * (high - low);
  }
  scheduleAmbient(from) { return this.scheduleRange(from, this.cadence()?.ambientIntervalMs || this.profile().interval); }
  scheduleIdle(from) { return this.scheduleRange(from, this.cadence()?.idleIntervalMs || [5000, 9000]); }
  setActivityLevel(level) { if (!this.model.profiles[level]) throw new Error(`Unsupported activity level: ${level}`); this.activityLevel = level; this.nextAmbientAt = this.scheduleAmbient(this.now()); this.nextIdleAt = this.scheduleIdle(this.now()); }
  setReducedMotion(enabled) { this.reducedMotion = Boolean(enabled); this.nextAmbientAt = this.scheduleAmbient(this.now()); this.nextIdleAt = this.scheduleIdle(this.now()); }
  setPaused(paused) { this.paused = Boolean(paused); if (this.paused) this.cancelCurrent(); }
  cancelCurrent() { this.current = null; this.queue = []; this.sleeping = false; }

  command(behavior, source, extra = {}) { return { type: 'start', behavior, source, ...extra }; }

  begin(behavior, source, at = this.now(), extra = {}) {
    this.current = { behavior, source, priority: PRIORITY[source] ?? 0, startedAt: at };
    if (source === 'sleep' && this.model.behaviors[behavior].phases.some((phase) => phase.completeOn === 'wake-requested')) this.sleeping = true;
    if (source === 'ambient') { this.lastAmbient = behavior; this.lastStarted[behavior] = at; }
    return this.command(behavior, source, extra);
  }

  queueAfterWake(behavior, source) {
    this.queue = [{ behavior, source }];
    return { type: 'signal', event: 'wake-requested' };
  }

  interact(kind, options = {}, at = this.now()) {
    if (this.paused) return { type: 'none' };
    const behavior = kind === 'release' && !options.moved ? this.model.bindings.click : this.model.bindings[kind];
    const source = kind === 'release' && !options.moved ? 'click' : kind;
    if (source !== 'pointer' || this.model.schemaVersion !== 3 || this.model.cadence?.pointerResetsSleep) this.lastInteractionAt = at;
    if (!behavior) return { type: 'none' };
    if (this.sleeping && ['click', 'drag', 'release'].includes(source)) return this.queueAfterWake(behavior, source);
    if (kind === 'release' && this.current?.source === 'drag') {
      this.queue = [{ behavior, source }];
      return { type: 'signal', event: 'pointer-released' };
    }
    if (source === 'pointer' && (this.current || this.sleeping || this.reducedMotion)) return { type: 'none' };
    if (this.current && (PRIORITY[source] ?? 0) < this.current.priority) return { type: 'none' };
    return this.begin(behavior, source, at, { replace: Boolean(this.current) });
  }

  markSleeping() { this.sleeping = true; }

  complete(behavior, at = this.now()) {
    if (this.current?.behavior !== behavior) return { type: 'none' };
    const source = this.current.source;
    this.current = null;
    if (source === 'sleep') { this.sleeping = false; this.lastSleepAt = at; }
    if (this.queue.length) {
      const next = this.queue.shift();
      return this.begin(next.behavior, next.source, at);
    }
    if (source === 'idle') {
      this.nextIdleAt = this.scheduleIdle(at);
      return { type: 'base' };
    }
    this.quietUntil = Math.max(this.quietUntil, at + (this.cadence()?.postEpisodeQuietMs ?? 4000));
    this.nextAmbientAt = Math.max(this.scheduleAmbient(at), this.quietUntil);
    this.nextIdleAt = this.scheduleIdle(at);
    return { type: 'base' };
  }

  eligibleAmbient(item, at, { allowRepeat = false } = {}) {
    if (!allowRepeat && item.behavior === this.lastAmbient) return false;
    if (this.reducedMotion && this.model.behaviors[item.behavior].phases.some((phase) => ['walk', 'cursor-approach', 'cursor-return'].includes(phase.motion))) return false;
    const cooldown = item.cooldownMs * this.cadenceMultiplier();
    return at - (this.lastStarted[item.behavior] ?? -Infinity) >= cooldown;
  }

  chooseAmbient(at = this.now()) {
    const choices = this.model.bindings.ambient.filter((item) => this.eligibleAmbient(item, at));
    if (!choices.length) {
      const repeatable = this.model.bindings.ambient.filter((item) => this.eligibleAmbient(item, at, { allowRepeat: true }));
      if (repeatable.length) return this.pickAmbient(repeatable);
      return null;
    }
    return this.pickAmbient(choices);
  }

  pickAmbient(choices) {
    if (!choices.length) return null;
    const weightKey = this.activityLevel;
    const weights = choices.map((item) => item[weightKey] ?? item.weight ?? 1);
    let roll = this.random() * weights.reduce((sum, value) => sum + value, 0);
    for (let index = 0; index < choices.length; index += 1) { roll -= weights[index]; if (roll < 0) return choices[index].behavior; }
    return choices.at(-1).behavior;
  }

  tick(at = this.now()) {
    if (this.paused || this.current || this.sleeping || at < this.quietUntil) return { type: 'none' };
    const sleep = this.model.bindings.sleep;
    if (at - this.lastInteractionAt >= sleep.afterMs && at - this.lastSleepAt >= sleep.afterMs) return this.begin(sleep.behavior, 'sleep', at);
    if (at >= this.nextAmbientAt) {
      const behavior = this.chooseAmbient(at);
      if (behavior) return this.begin(behavior, 'ambient', at);
      this.nextAmbientAt = this.scheduleAmbient(at);
    }
    if (at >= this.nextIdleAt) { this.nextIdleAt = this.scheduleIdle(at); return this.begin(this.model.bindings.idle, 'idle', at); }
    return { type: 'none' };
  }
}

if (typeof module !== 'undefined' && module.exports) module.exports = { PRIORITY, TriggerController };
if (typeof window !== 'undefined') { window.TriggerController = TriggerController; window.TriggerPriority = PRIORITY; }
