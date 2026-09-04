'use strict';

const fs = require('node:fs');
const path = require('node:path');
const { spawnSync } = require('node:child_process');
const expectedVersion = require('../package.json').version;
const SELF_TEST_PREFIX = 'SELF_TEST_RESULT:';

function findExecutable(root = path.resolve(__dirname, '..', 'dist')) {
  if (process.platform === 'darwin') {
    for (const directory of fs.readdirSync(root, { withFileTypes: true })) {
      if (!directory.isDirectory() || !directory.name.startsWith('mac')) continue;
      const app = path.join(root, directory.name, 'Doodle Desktop Pet.app', 'Contents');
      const plist = path.join(app, 'Info.plist');
      if (fs.existsSync(plist)) return path.join(app, 'MacOS', 'Doodle Desktop Pet');
    }
  } else if (process.platform === 'win32') {
    for (const directory of ['win-unpacked', 'win-arm64-unpacked', 'win-ia32-unpacked']) {
      const executable = path.join(root, directory, 'Doodle Desktop Pet.exe');
      if (fs.existsSync(executable)) return executable;
    }
  }
  throw new Error(`packaged runtime executable was not found under ${root}`);
}

function parseSelfTestOutput(stdout) {
  const line = String(stdout || '')
    .split(/\r?\n/)
    .map((item) => item.trim())
    .filter(Boolean)
    .findLast((item) => item.startsWith(SELF_TEST_PREFIX));
  if (!line) throw new Error('self-test response was not found');
  return JSON.parse(line.slice(SELF_TEST_PREFIX.length) || '{}');
}

function runPackagedSelfTest(executable = findExecutable()) {
  const result = spawnSync(executable, ['--self-test'], { encoding: 'utf8', timeout: 15000 });
  if (result.error) throw result.error;
  if (result.status !== 0) throw new Error(`self-test exited ${result.status}: ${(result.stderr || result.stdout).trim()}`);
  const payload = parseSelfTestOutput(result.stdout);
  if (payload.ok !== true || payload.product !== 'Doodle Desktop Pet') throw new Error(`invalid self-test response: ${JSON.stringify(payload)}`);
  if (payload.version !== expectedVersion) throw new Error(`self-test version ${payload.version} does not match ${expectedVersion}`);
  return payload;
}

if (require.main === module) console.log(JSON.stringify(runPackagedSelfTest()));

module.exports = { findExecutable, parseSelfTestOutput, runPackagedSelfTest };
