'use strict';

const canvas = document.getElementById('pet');
const context = canvas.getContext('2d', { alpha: true, willReadFrequently: true });
const runtimeAPI = window.petAPI || {
  getActivePet: async () => ({ fallback: true, paused: false, scale: 0.6, activityLevel: 'balanced' }),
  setIgnoreMouse: () => {}, moveWindow: async () => ({}), beginWalk: async () => null,
  beginFall: async () => null, beginCursorChase: async () => null, returnCursorChase: async () => null,
  stopWalk: () => {}, persistPosition: () => {}, showContextMenu: async () => {},
  onPetChanged: () => () => {}, onWalkFinished: () => () => {}, onFallFinished: () => () => {},
  onCursorNear: () => () => {}, onCursorChaseArrived: () => () => {}, onCursorChaseReturned: () => () => {},
};
if (!window.petAPI) document.body.dataset.runtime = 'standalone';

const fallbackManifest = {
  canvas: { width: 256, height: 256 }, anchor: { x: 128, y: 224 },
  hitbox: { alphaThreshold: 24, bounds: { x: 42, y: 28, width: 172, height: 205 } },
};
const fallbackModel = {
  schemaVersion: 0, base: { clip: 'fallback', frame: 0 },
  clips: { fallback: { id: 'fallback', frames: 4, fps: 6, mirrorable: false } },
  behaviors: { fallback: { id: 'fallback', phases: [{ id: 'play', clip: 'fallback', playback: 'once', completeOn: 'animation-finished' }] } },
  bindings: { idle: 'fallback', click: 'fallback', pointer: 'fallback', drag: 'fallback', release: 'fallback', sleep: { behavior: 'fallback', afterMs: 480000, wakeAfterMs: [60000, 180000] }, ambient: [{ behavior: 'fallback', weight: 1, cooldownMs: 30000 }] },
  profiles: { quiet: { interval: [20000, 35000] }, balanced: { interval: [8000, 15000] }, lively: { interval: [5000, 9000] } },
};

const motionQuery = matchMedia('(prefers-reduced-motion: reduce)');
let payload, manifest, model, images = {}, groundingByClip = {}, player, controller, gesture;
let tickTimer, frameTimer, wakeTimer, displayedClip, frameIndex = 0, direction = 1;
let ignoreMouse = true, dragging = false, pointerPressing = false, dragMoved = false, dragStart, pointerOffset, cursorPoint;
const pendingSignals = new Set();

function loadImage(url) { return new Promise((resolve, reject) => { const image = new Image(); image.onload = () => resolve(image); image.onerror = () => reject(new Error(`Could not load ${url}`)); image.src = url; }); }
function clearTimers() { clearTimeout(tickTimer); clearTimeout(frameTimer); clearTimeout(wakeTimer); runtimeAPI.stopWalk(); dragging = false; pointerPressing = false; groundingByClip = {}; gesture?.reset(); }
function computeGroundingOffsets(image, frames) {
  const width = manifest.canvas.width;
  const height = manifest.canvas.height;
  const probe = document.createElement('canvas');
  probe.width = width; probe.height = height;
  const probeContext = probe.getContext('2d', { alpha: true, willReadFrequently: true });
  const boxes = [];
  for (let frame = 0; frame < frames; frame += 1) {
    probeContext.clearRect(0, 0, width, height);
    probeContext.drawImage(image, frame * width, 0, width, height, 0, 0, width, height);
    const pixels = probeContext.getImageData(0, 0, width, height).data;
    let bottom = 0;
    for (let y = height - 1; y >= 0 && !bottom; y -= 1) {
      for (let x = 0; x < width; x += 1) {
        if (pixels[(y * width + x) * 4 + 3] > 0) { bottom = y + 1; break; }
      }
    }
    boxes.push(bottom ? { bottom } : null);
  }
  return window.groundingOffsets(boxes, manifest.anchor.y);
}
function buildGroundingOffsets() {
  groundingByClip = {};
  if (payload.fallback || model.schemaVersion !== 3) return;
  for (const [clipId, clip] of Object.entries(model.clips)) {
    if (clip.grounding !== 'floor' || !images[clipId]) continue;
    try { groundingByClip[clipId] = computeGroundingOffsets(images[clipId], clip.frames); } catch { groundingByClip[clipId] = []; }
  }
}
function drawFallback(frame) { context.save(); context.lineWidth = 6; context.lineCap = 'round'; context.strokeStyle = '#111'; context.fillStyle = '#e8c84e'; context.beginPath(); context.moveTo(78, 70); context.lineTo(91, 210); context.quadraticCurveTo(128, 220, 165, 210); context.lineTo(178, 70); context.closePath(); context.fill(); context.stroke(); context.beginPath(); context.arc(112, 135, 4, 0, Math.PI * 2); context.arc(143, 136, 4, 0, Math.PI * 2); context.fillStyle = '#111'; context.fill(); const kick = frame % 2 ? 8 : -8; context.beginPath(); context.moveTo(108, 211); context.lineTo(104 - kick, 231); context.moveTo(148, 211); context.lineTo(152 + kick, 231); context.stroke(); context.restore(); }
function render(clipId = displayedClip, frame = frameIndex) { const clip = model.clips[clipId] || model.clips[model.base.clip]; context.clearRect(0, 0, canvas.width, canvas.height); context.save(); const grounding = groundingByClip[clipId]?.[frame] || 0; if (grounding) context.translate(0, grounding); if (direction < 0 && clip.mirrorable) { context.translate(canvas.width, 0); context.scale(-1, 1); } if (payload.fallback) drawFallback(frame); else context.drawImage(images[clipId], frame * manifest.canvas.width, 0, manifest.canvas.width, manifest.canvas.height, 0, 0, manifest.canvas.width, manifest.canvas.height); context.restore(); }
function showBase() { displayedClip = model.base.clip; frameIndex = model.base.frame || 0; render(); }
function frameDelay(clip, index) { return clip.durationsMs ? clip.durationsMs[index] : 1000 / clip.fps; }

async function startMotion(phase) {
  let plan = null;
  if (phase.motion === 'walk') plan = await runtimeAPI.beginWalk();
  if (phase.motion === 'fall') plan = await runtimeAPI.beginFall();
  if (phase.motion === 'cursor-approach') plan = await runtimeAPI.beginCursorChase(cursorPoint);
  if (phase.motion === 'cursor-return') plan = await runtimeAPI.returnCursorChase();
  if (plan?.direction) direction = plan.direction;
  if (!plan) {
    if (phase.completeOn === 'floor-impact') signalPlayer('floor-impact');
    else if (phase.completeOn === 'motion-finished') signalPlayer('motion-finished');
  }
}

function scheduleWakeIfNeeded(phase) {
  clearTimeout(wakeTimer);
  if (phase.completeOn !== 'wake-requested') return;
  controller.markSleeping();
  const [low, high] = model.bindings.sleep.wakeAfterMs;
  wakeTimer = setTimeout(() => signalPlayer('wake-requested'), low + Math.random() * (high - low));
}

function playCurrentPhase() {
  clearTimeout(frameTimer);
  const phase = player.currentPhase();
  if (!phase) return;
  const clip = model.clips[phase.clip];
  displayedClip = phase.clip; frameIndex = 0; render(); scheduleWakeIfNeeded(phase);
  if (phase.motion) startMotion(phase);
  if (pendingSignals.delete(phase.completeOn)) { queueMicrotask(() => signalPlayer(phase.completeOn)); return; }
  const advance = () => {
    if (player.currentPhase() !== phase) return;
    frameIndex += 1;
    if (frameIndex >= clip.frames) {
      if (phase.playback === 'loop') frameIndex = 0;
      else { frameIndex = clip.frames - 1; render(); signalPlayer('animation-finished'); return; }
    }
    render(); frameTimer = setTimeout(advance, frameDelay(clip, frameIndex));
  };
  frameTimer = setTimeout(advance, frameDelay(clip, 0));
}

function runCommand(command) {
  if (!command || command.type === 'none') return;
  if (command.type === 'base') { player.cancel(); showBase(); return; }
  if (command.type === 'signal') { signalPlayer(command.event); return; }
  if (command.type === 'start') { clearTimeout(frameTimer); if (command.replace) player.cancel(); player.start(command.behavior); playCurrentPhase(); }
}

function signalPlayer(event) {
  const result = player.signal(event);
  if (result.status === 'advanced') playCurrentPhase();
  else if (result.status === 'completed') runCommand(controller.complete(result.behaviorId));
  else if (["pointer-released", "wake-requested"].includes(event)) pendingSignals.add(event);
}

function scheduleTick() {
  clearTimeout(tickTimer);
  tickTimer = setTimeout(() => {
    const result = player.tick();
    if (result.status === 'advanced') playCurrentPhase();
    else if (result.status === 'completed') runCommand(controller.complete(result.behaviorId));
    runCommand(controller.tick()); scheduleTick();
  }, 250);
}

async function applyPet(nextPayload) {
  clearTimers(); pendingSignals.clear(); payload = nextPayload; manifest = payload.fallback ? fallbackManifest : payload.manifest;
  model = payload.fallback ? fallbackModel : payload.runtimeModel; canvas.width = manifest.canvas.width; canvas.height = manifest.canvas.height;
  images = {}; if (!payload.fallback) images = Object.fromEntries(await Promise.all(Object.entries(payload.clipUrls).map(async ([name, url]) => [name, await loadImage(url)]))); buildGroundingOffsets();
  player = new window.EpisodePlayer(model); controller = new window.TriggerController(model, { activityLevel: payload.activityLevel || 'balanced', reducedMotion: motionQuery.matches }); controller.setPaused(payload.paused); gesture = new window.GestureState(model.schemaVersion === 2 ? 5 : (model.cadence?.dragThresholdPx || 8));
  direction = 1; showBase(); scheduleTick();
}

function pointerCoordinates(event) { const rect = canvas.getBoundingClientRect(); return { x: Math.max(0, Math.min(canvas.width - 1, Math.floor((event.clientX - rect.left) / rect.width * canvas.width))), y: Math.max(0, Math.min(canvas.height - 1, Math.floor((event.clientY - rect.top) / rect.height * canvas.height))) }; }
function isVisiblePixel(event) { const { x, y } = pointerCoordinates(event), b = manifest.hitbox.bounds; if (x < b.x || y < b.y || x >= b.x + b.width || y >= b.y + b.height) return false; try { return context.getImageData(x, y, 1, 1).data[3] >= manifest.hitbox.alphaThreshold; } catch { return true; } }
function updateClickThrough(ignore) { if (ignoreMouse === ignore) return; ignoreMouse = ignore; runtimeAPI.setIgnoreMouse(ignore); }
canvas.addEventListener('pointermove', (event) => {
  if (model.schemaVersion === 3 && pointerPressing) {
    const gestureResult = gesture.move({ x: event.screenX, y: event.screenY });
    if (gestureResult.type === 'drag-start') {
      dragging = true; dragMoved = true;
      runCommand(controller.interact('drag'));
    }
    if (dragging) {
      const x = event.screenX - pointerOffset.x, y = event.screenY - pointerOffset.y;
      runtimeAPI.moveWindow({ x, y, dragging: true });
    }
    return;
  }
  if (dragging) {
    const gestureResult = gesture.move({ x: event.screenX, y: event.screenY });
    if (gestureResult.type === 'drag-start' || gestureResult.type === 'drag-move') dragMoved = true;
    const x = event.screenX - pointerOffset.x, y = event.screenY - pointerOffset.y;
    runtimeAPI.moveWindow({ x, y, dragging: true });
    return;
  }
  updateClickThrough(!isVisiblePixel(event));
});
canvas.addEventListener('pointerleave', () => { if (!dragging && !pointerPressing) updateClickThrough(true); });
canvas.addEventListener('pointerdown', (event) => {
  if (event.button !== 0 || !isVisiblePixel(event)) return;
  dragMoved = false; dragStart = { x: event.screenX, y: event.screenY }; pointerOffset = { x: event.screenX - window.screenX, y: event.screenY - window.screenY };
  canvas.setPointerCapture(event.pointerId); updateClickThrough(false);
  if (model.schemaVersion === 3) { pointerPressing = true; gesture.press(dragStart); return; }
  gesture.press(dragStart); dragging = true; runCommand(controller.interact('drag'));
});
function finishPointer(event) {
  if (model.schemaVersion === 3) {
    if (!pointerPressing) return;
    const result = event.type === 'pointercancel' ? gesture.cancel() : gesture.release();
    pointerPressing = false;
    if (dragging && result.type === 'drag-release') runCommand(controller.interact('release', { moved: true }));
    else if (result.type === 'click') runCommand(controller.interact('click'));
    dragging = false;
    if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId);
    if (result.type === 'drag-release') runtimeAPI.persistPosition();
    updateClickThrough(!isVisiblePixel(event));
    return;
  }
  if (!dragging) return;
  const result = event.type === 'pointercancel' ? gesture.cancel() : gesture.release();
  dragMoved = result.type === 'drag-release';
  dragging = false; if (canvas.hasPointerCapture(event.pointerId)) canvas.releasePointerCapture(event.pointerId); runCommand(controller.interact('release', { moved: dragMoved })); if (!dragMoved) runtimeAPI.persistPosition(); updateClickThrough(!isVisiblePixel(event));
}
canvas.addEventListener('pointerup', finishPointer); canvas.addEventListener('pointercancel', finishPointer);
canvas.addEventListener('contextmenu', async (event) => { event.preventDefault(); if (!isVisiblePixel(event)) return; updateClickThrough(false); try { await runtimeAPI.showContextMenu(); } finally { updateClickThrough(true); } });
runtimeAPI.onWalkFinished(() => signalPlayer('motion-finished'));
runtimeAPI.onFallFinished(() => signalPlayer('floor-impact'));
runtimeAPI.onCursorNear((point) => { cursorPoint = point; runCommand(controller.interact('pointer')); });
runtimeAPI.onCursorChaseArrived(({ direction: nextDirection }) => { direction = nextDirection; signalPlayer('motion-finished'); });
runtimeAPI.onCursorChaseReturned(() => { signalPlayer('motion-finished'); runtimeAPI.persistPosition(); });
motionQuery.addEventListener('change', (event) => { if (controller) { controller.setReducedMotion(event.matches); if (event.matches && player.currentPhase()?.motion && player.currentPhase().motion !== 'fall') { runtimeAPI.stopWalk(); player.cancel(); controller.current = null; showBase(); } } });
runtimeAPI.onPetChanged((next) => applyPet(next).catch(() => applyPet({ fallback: true, paused: false, scale: 0.6, activityLevel: 'balanced' })));
runtimeAPI.getActivePet().then(applyPet).catch(() => applyPet({ fallback: true, paused: false, scale: 0.6, activityLevel: 'balanced' }));
