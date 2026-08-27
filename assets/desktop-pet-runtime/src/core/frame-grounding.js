'use strict';

/**
 * Return the vertical translation needed to put each visible frame on the
 * manifest floor anchor. `box` uses the Canvas/PIL convention where bottom
 * is exclusive, so a frame whose last visible row is `anchorY - 1` needs a
 * translation of +1.
 */
function groundingOffsets(frameBoxes, anchorY) {
  if (!Array.isArray(frameBoxes) || !Number.isFinite(anchorY)) return [];
  return frameBoxes.map((box) => {
    if (!box || !Number.isFinite(box.bottom)) return 0;
    return Math.round(anchorY - box.bottom);
  });
}

if (typeof module !== 'undefined' && module.exports) module.exports = { groundingOffsets };
if (typeof window !== 'undefined') window.groundingOffsets = groundingOffsets;
