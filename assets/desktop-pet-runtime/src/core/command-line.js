'use strict';

function parseCommandLine(argv) {
  const result = { quit: false, show: false, openPet: null };
  for (let index = 0; index < argv.length; index += 1) {
    const value = argv[index];
    if (value === '--quit') result.quit = true;
    else if (value === '--show') result.show = true;
    else if (value === '--open-pet' && typeof argv[index + 1] === 'string') {
      result.openPet = argv[index + 1];
      index += 1;
    }
  }
  return result;
}

function forwardedCommandLine(commandLine, additionalData) {
  if (Array.isArray(additionalData?.argv)) return additionalData.argv;
  return Array.isArray(commandLine) ? commandLine : [];
}

module.exports = { forwardedCommandLine, parseCommandLine };
