'use strict';

function floorBottom(display, floorMode = 'work-area') {
  const area = floorMode === 'display-edge' ? display?.bounds : display?.workArea;
  if (!area || !Number.isFinite(area.y) || !Number.isFinite(area.height)) return 0;
  return area.y + area.height;
}

if (typeof module !== 'undefined' && module.exports) module.exports = { floorBottom };
