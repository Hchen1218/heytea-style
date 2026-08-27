'use strict';

class GestureState {
  constructor(thresholdPx = 8) {
    this.thresholdPx = thresholdPx;
    this.state = 'idle';
    this.start = null;
  }

  press(point) {
    if (this.state !== 'idle') return { type: 'none' };
    this.state = 'pending';
    this.start = { x: point.x, y: point.y };
    return { type: 'pressed' };
  }

  move(point) {
    if (this.state === 'dragging') return { type: 'drag-move' };
    if (this.state !== 'pending' || !this.start) return { type: 'none' };
    const distance = Math.hypot(point.x - this.start.x, point.y - this.start.y);
    if (distance < this.thresholdPx) return { type: 'pending' };
    this.state = 'dragging';
    return { type: 'drag-start' };
  }

  release() {
    if (this.state === 'pending') {
      this.reset();
      return { type: 'click' };
    }
    if (this.state === 'dragging') {
      this.reset();
      return { type: 'drag-release', moved: true };
    }
    return { type: 'none' };
  }

  cancel() {
    const wasDragging = this.state === 'dragging';
    this.reset();
    return wasDragging ? { type: 'drag-release', moved: true } : { type: 'cancel' };
  }

  reset() {
    this.state = 'idle';
    this.start = null;
  }
}

if (typeof module !== 'undefined' && module.exports) module.exports = { GestureState };
if (typeof window !== 'undefined') window.GestureState = GestureState;
