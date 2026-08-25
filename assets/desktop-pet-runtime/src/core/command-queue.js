'use strict';

function createCommandQueue(handler) {
  let ready = false;
  let pending = [];
  let tail = Promise.resolve();

  function dispatch(argv) {
    const commandLine = [...argv];
    if (!ready) {
      pending.push(commandLine);
      return Promise.resolve();
    }
    tail = tail.catch(() => {}).then(() => handler(commandLine));
    return tail;
  }

  async function markReady() {
    ready = true;
    const queued = pending;
    pending = [];
    for (const commandLine of queued) await dispatch(commandLine);
  }

  return { dispatch, markReady };
}

module.exports = { createCommandQueue };
