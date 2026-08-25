'use strict';

const { clamp } = require('./walk-planner');

function planFall({ startY, floorY }) {
  const distance = Math.max(0, floorY - startY);
  if (distance < 8) return null;
  const duration = clamp(320 + Math.sqrt(distance) * 38, 420, 1250);
  return { startY, floorY, distance, duration };
}

function fallY(plan, elapsedMs) {
  const progress = clamp(elapsedMs / plan.duration, 0, 1);
  return Math.round(plan.startY + plan.distance * progress * progress);
}

function planCursorChase({ currentX, cursorX, windowWidth, minX, maxX }) {
  const centerX = currentX + windowWidth / 2;
  const delta = cursorX - centerX;
  if (Math.abs(delta) < 10) return null;
  const direction = delta < 0 ? -1 : 1;
  const distance = Math.min(80, Math.max(28, Math.abs(delta) - windowWidth * 0.22));
  const targetX = Math.round(clamp(currentX + direction * distance, minX, maxX));
  const actualDistance = Math.abs(targetX - currentX);
  if (actualDistance < 8) return null;
  return { originX: currentX, targetX, distance: actualDistance, direction, speed: 42 };
}

module.exports = { fallY, planCursorChase, planFall };
