'use strict';

function clamp(value, minimum, maximum) { return Math.min(Math.max(value, minimum), maximum); }

function planWalk({ currentX, minX, maxX, workAreaWidth, random = Math.random }) {
  const roomLeft = Math.max(0, currentX - minX);
  const roomRight = Math.max(0, maxX - currentX);
  let direction = random() < 0.5 ? -1 : 1;
  if ((direction < 0 ? roomLeft : roomRight) < 80) direction *= -1;
  const room = direction < 0 ? roomLeft : roomRight;
  if (room < 40) return null;
  const wanted = clamp(workAreaWidth * (0.08 + random() * 0.12), 80, 240);
  const distance = Math.min(wanted, room);
  const speed = 30 + random() * 6;
  return { direction, distance, speed, targetX: currentX + direction * distance };
}

module.exports = { clamp, planWalk };
