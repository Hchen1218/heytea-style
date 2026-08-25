'use strict';

const INTERACTION_STATES = new Set(['happy', 'drag', 'fall', 'land', 'cursorChase', 'touch', 'cursorReturn']);
const AMBIENT_STATES = ['curious', 'stretch', 'tiptoe', 'play', 'signature', 'wave', 'walk'];
const PROFILES = Object.freeze({
  quiet: { interval: [20000, 35000], cursorCooldown: 60000, weights: { curious: 24, stretch: 19, tiptoe: 16, play: 18, signature: 10, wave: 8, walk: 5 } },
  balanced: { interval: [8000, 15000], cursorCooldown: 30000, weights: { curious: 22, stretch: 16, tiptoe: 14, play: 16, signature: 12, wave: 10, walk: 10 } },
  lively: { interval: [5000, 9000], cursorCooldown: 18000, weights: { curious: 19, stretch: 14, tiptoe: 13, play: 17, signature: 12, wave: 10, walk: 15 } },
});
const COOLDOWNS = Object.freeze({ curious: 18000, stretch: 24000, tiptoe: 18000, play: 24000, signature: 25000, wave: 30000, walk: 90000 });
const DURATIONS = Object.freeze({ curious: 1800, stretch: 2200, tiptoe: 1700, play: 2600, signature: 2300, wave: 1800, walk: 10000, happy: 1400, land: 1000, touch: 1800 });
const PHYSICAL_STATES = new Set(['walk', 'drag', 'fall', 'cursorChase', 'cursorReturn']);

function actionCycleMs(action) {
  if (!action || !Number.isInteger(action.frames) || !Number.isInteger(action.fps) || action.frames < 1 || action.fps < 1) return 0;
  return action.frames / action.fps * 1000;
}

function shouldLoopAction(state, action) {
  return state === 'rest' || PHYSICAL_STATES.has(state) || Boolean(action?.loop);
}

class BehaviorController {
  constructor(options = {}) {
    this.random = options.random || Math.random;
    this.now = options.now || (() => Date.now());
    this.sleepAfterMs = options.sleepAfterMs || 8 * 60 * 1000;
    this.quietAfterMs = options.quietAfterMs ?? 4000;
    this.activityLevel = PROFILES[options.activityLevel] ? options.activityLevel : 'balanced';
    this.reducedMotion = Boolean(options.reducedMotion);
    this.actionTimings = options.actionTimings || {};
    this.state = 'idle'; this.direction = 1; this.paused = false; this.episode = null;
    this.lastInteractionAt = this.now(); this.lastRestAt = this.now(); this.lastAmbient = null;
    this.lastStarted = Object.create(null); this.quietUntil = 0;
    this.nextAmbientAt = this.scheduleAmbient(this.now());
  }
  profile() { return PROFILES[this.reducedMotion ? 'quiet' : this.activityLevel]; }
  scheduleAmbient(from) { const [lo, hi] = this.profile().interval; return from + lo + this.random() * (hi - lo); }
  setActivityLevel(level) { if (!PROFILES[level]) throw new Error(`Unsupported activity level: ${level}`); this.activityLevel = level; this.nextAmbientAt = this.scheduleAmbient(this.now()); }
  setReducedMotion(enabled) { this.reducedMotion = Boolean(enabled); if (this.reducedMotion && this.state === 'walk') this.finishEpisode(this.now()); this.nextAmbientAt = this.scheduleAmbient(this.now()); }
  setPaused(paused) { this.paused = Boolean(paused); if (this.paused) this.finishEpisode(this.now(), false); }
  setDirection(direction) { this.direction = direction < 0 ? -1 : 1; }
  startEpisode(action, durationMs = DURATIONS[action] || 1800, source = 'ambient', at = this.now()) {
    const minimumDuration = actionCycleMs(this.actionTimings[action]);
    const effectiveDuration = durationMs > 0 ? Math.max(durationMs, minimumDuration) : 0;
    this.state = action; this.episode = { action, source, startedAt: at, endsAt: effectiveDuration > 0 ? at + effectiveDuration : 0 };
    if (AMBIENT_STATES.includes(action)) { this.lastAmbient = action; this.lastStarted[action] = at; }
    return this.state;
  }
  finishEpisode(at = this.now(), enforceQuiet = true) { this.state = 'idle'; this.episode = null; if (enforceQuiet) this.quietUntil = Math.max(this.quietUntil, at + this.quietAfterMs); this.nextAmbientAt = Math.max(this.scheduleAmbient(at), this.quietUntil); return this.state; }
  interact(state) { if (!INTERACTION_STATES.has(state)) throw new Error(`Unsupported interaction state: ${state}`); const at = this.now(); this.lastInteractionAt = at; const external = new Set(['drag','fall','cursorChase','cursorReturn']); return this.startEpisode(state, external.has(state) ? 0 : DURATIONS[state], 'interaction', at); }
  releaseDrag() { return this.state === 'drag' ? this.interact('land') : this.state; }
  animationFinished(state) { return state !== this.state || ['drag','fall','cursorChase','cursorReturn'].includes(state) ? this.state : this.finishEpisode(this.now()); }
  eligible(action, at) { if (action === this.lastAmbient || (action === 'walk' && this.reducedMotion)) return false; return at - (this.lastStarted[action] ?? -Infinity) >= COOLDOWNS[action]; }
  chooseAmbient(at = this.now()) { const choices = Object.entries(this.profile().weights).filter(([name]) => this.eligible(name, at)); if (!choices.length) return null; const total = choices.reduce((s, [,w]) => s+w, 0); let roll=this.random()*total; for(const [name,w] of choices){roll-=w;if(roll<0)return name;} return choices.at(-1)[0]; }
  proximity(at = this.now()) { if (this.paused || this.state !== 'idle' || at < this.quietUntil) return this.state; const choices=['curious','tiptoe','wave'].filter((name)=>this.eligible(name,at)); if(!choices.length)return this.state; const action=choices[Math.min(choices.length-1,Math.floor(this.random()*choices.length))]; return this.startEpisode(action,DURATIONS[action],'cursor',at); }
  tick(at = this.now()) {
    if (this.paused || ['drag','fall','cursorChase','cursorReturn'].includes(this.state)) return this.state;
    if (this.episode?.endsAt && at >= this.episode.endsAt) { const ended=this.episode.action; this.finishEpisode(at); if(ended==='rest') this.lastRestAt=at; }
    if (this.state !== 'idle') return this.state;
    if (at-this.lastInteractionAt>=this.sleepAfterMs && at-this.lastRestAt>=this.sleepAfterMs) { this.lastRestAt=at; return this.startEpisode('rest',20000+this.random()*25000,'sleep',at); }
    if (at < this.quietUntil || at < this.nextAmbientAt) return this.state;
    const action=this.chooseAmbient(at); if(!action){this.nextAmbientAt=this.scheduleAmbient(at);return this.state;} return this.startEpisode(action,DURATIONS[action],'ambient',at);
  }
}

if (typeof module !== 'undefined' && module.exports) module.exports = { actionCycleMs, AMBIENT_STATES, BehaviorController, COOLDOWNS, PROFILES, shouldLoopAction };
if (typeof window !== 'undefined') { window.BehaviorController = BehaviorController; window.shouldLoopAction = shouldLoopAction; }
