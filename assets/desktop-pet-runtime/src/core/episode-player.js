'use strict';

class EpisodePlayer {
  constructor(model, options = {}) {
    this.model = model;
    this.random = options.random || Math.random;
    this.now = options.now || (() => Date.now());
    this.episode = null;
  }

  currentPhase() {
    if (!this.episode) return null;
    return this.episode.behavior.phases[this.episode.phaseIndex] || null;
  }

  timeoutFor(phase) {
    if (!phase?.timeoutRangeMs) return 0;
    const [low, high] = phase.timeoutRangeMs;
    return low + this.random() * (high - low);
  }

  start(behaviorId, at = this.now()) {
    const behavior = this.model.behaviors[behaviorId];
    if (!behavior) throw new Error(`Unknown behavior: ${behaviorId}`);
    this.episode = { behaviorId, behavior, phaseIndex: 0, startedAt: at, phaseStartedAt: at, deadline: 0 };
    this.enterPhase(at);
    return this.snapshot('started');
  }

  enterPhase(at = this.now()) {
    const phase = this.currentPhase();
    if (!phase) return null;
    this.episode.phaseStartedAt = at;
    const timeout = this.timeoutFor(phase);
    this.episode.deadline = timeout ? at + timeout : 0;
    return phase;
  }

  signal(event, at = this.now()) {
    const phase = this.currentPhase();
    if (!phase || phase.completeOn !== event) return this.snapshot('ignored');
    this.episode.phaseIndex += 1;
    if (this.episode.phaseIndex >= this.episode.behavior.phases.length) {
      const completed = this.episode.behaviorId;
      this.episode = null;
      return { status: 'completed', behaviorId: completed, phase: null };
    }
    this.enterPhase(at);
    return this.snapshot('advanced');
  }

  tick(at = this.now()) {
    if (this.episode?.deadline && at >= this.episode.deadline) return this.signal('timeout', at);
    return this.snapshot('waiting');
  }

  cancel() {
    const behaviorId = this.episode?.behaviorId || null;
    this.episode = null;
    return behaviorId;
  }

  snapshot(status = 'waiting') {
    return { status, behaviorId: this.episode?.behaviorId || null, phase: this.currentPhase() };
  }
}

if (typeof module !== 'undefined' && module.exports) module.exports = { EpisodePlayer };
if (typeof window !== 'undefined') window.EpisodePlayer = EpisodePlayer;
