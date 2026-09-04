'use strict';

const assert = require('node:assert/strict');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const test = require('node:test');
const asar = require('@electron/asar');
const { listedAsarPath, validatePackagedApp } = require('../scripts/after-pack');
const expectedMetadata = require('../package.json');

async function fixture({ includeMain = true, packagedVersion = expectedMetadata.version, corrupt = false } = {}) {
  const root = fs.mkdtempSync(path.join(os.tmpdir(), 'doodle-runtime-pack-'));
  const project = path.join(root, 'project');
  const appOutDir = path.join(root, 'dist', 'mac-arm64');
  const resources = path.join(appOutDir, 'Doodle Desktop Pet.app', 'Contents', 'Resources');
  const source = path.join(root, 'source');
  fs.mkdirSync(project, { recursive: true });
  fs.mkdirSync(resources, { recursive: true });
  fs.mkdirSync(source, { recursive: true });
  const expected = { name: expectedMetadata.name, version: expectedMetadata.version, main: 'src/main.js' };
  fs.writeFileSync(path.join(project, 'package.json'), JSON.stringify(expected));
  fs.writeFileSync(path.join(source, 'package.json'), JSON.stringify({ ...expected, version: packagedVersion }));
  if (includeMain) {
    fs.mkdirSync(path.join(source, 'src'));
    fs.writeFileSync(path.join(source, 'src', 'main.js'), "'use strict';\n");
  }
  const archive = path.join(resources, 'app.asar');
  if (corrupt) fs.writeFileSync(archive, 'not-an-asar');
  else await asar.createPackage(source, archive);
  fs.writeFileSync(path.join(resources, 'default_app.asar'), 'fallback');
  const context = {
    electronPlatformName: 'darwin',
    appOutDir,
    packager: { projectDir: project, appInfo: { productFilename: 'Doodle Desktop Pet' } },
  };
  return { context, resources };
}

test('validates app.asar and removes the Electron fallback archive', async (t) => {
  const { context, resources } = await fixture();
  t.after(() => fs.rmSync(path.dirname(context.packager.projectDir), { recursive: true, force: true }));
  const result = validatePackagedApp(context);
  assert.equal(result.version, expectedMetadata.version);
  assert.equal(fs.existsSync(path.join(resources, 'default_app.asar')), false);
});

test('rejects a corrupt app.asar without removing the fallback archive', async (t) => {
  const { context, resources } = await fixture({ corrupt: true });
  t.after(() => fs.rmSync(path.dirname(context.packager.projectDir), { recursive: true, force: true }));
  assert.throws(() => validatePackagedApp(context), /RUNTIME_BUILD_VALIDATION_FAILED/);
  assert.equal(fs.existsSync(path.join(resources, 'default_app.asar')), true);
});

test('normalizes asar listing paths to posix with a leading slash', () => {
  assert.equal(listedAsarPath('package.json'), '/package.json');
  assert.equal(listedAsarPath('\\package.json'), '/package.json');
  assert.equal(listedAsarPath('/package.json'), '/package.json');
  assert.equal(listedAsarPath('src\\main.js'), '/src/main.js');
});

test('accepts Windows-style asar listings that omit the leading slash', async (t) => {
  const { context } = await fixture();
  t.after(() => fs.rmSync(path.dirname(context.packager.projectDir), { recursive: true, force: true }));
  const asarApi = {
    listPackage: () => ['package.json', 'src\\main.js'],
    extractFile: (archive, file) => asar.extractFile(archive, file),
  };
  const result = validatePackagedApp(context, asarApi);
  assert.equal(result.version, expectedMetadata.version);
});

test('rejects a missing entry or mismatched version', async (t) => {
  const missing = await fixture({ includeMain: false });
  const mismatch = await fixture({ packagedVersion: '3.1.0' });
  t.after(() => {
    fs.rmSync(path.dirname(missing.context.packager.projectDir), { recursive: true, force: true });
    fs.rmSync(path.dirname(mismatch.context.packager.projectDir), { recursive: true, force: true });
  });
  assert.throws(() => validatePackagedApp(missing.context), /entry is missing/);
  assert.throws(() => validatePackagedApp(mismatch.context), /version does not match/);
});
