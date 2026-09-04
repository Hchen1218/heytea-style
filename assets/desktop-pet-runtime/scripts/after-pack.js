'use strict';

const fs = require('node:fs');
const path = require('node:path');
const asar = require('@electron/asar');

function fail(message) {
  throw new Error(`RUNTIME_BUILD_VALIDATION_FAILED: ${message}`);
}

function listedAsarPath(file) {
  return `/${String(file).replaceAll('\\', '/').replace(/^\/+/, '')}`;
}

function resourcesDirectory(context) {
  if (context.electronPlatformName === 'darwin') {
    return path.join(
      context.appOutDir,
      `${context.packager.appInfo.productFilename}.app`,
      'Contents',
      'Resources',
    );
  }
  return path.join(context.appOutDir, 'resources');
}

function validatePackagedApp(context, asarApi = asar) {
  const resources = resourcesDirectory(context);
  const archive = path.join(resources, 'app.asar');
  let stat;
  try {
    stat = fs.statSync(archive);
  } catch (error) {
    fail(`app.asar is missing: ${error.message}`);
  }
  if (!stat.isFile() || stat.size === 0) fail('app.asar is empty or not a regular file');

  let files;
  let packagedMetadata;
  try {
    files = new Set(asarApi.listPackage(archive).map(listedAsarPath));
    packagedMetadata = JSON.parse(asarApi.extractFile(archive, 'package.json').toString('utf8'));
  } catch (error) {
    fail(`app.asar is invalid: ${error.message}`);
  }

  const expectedMetadata = JSON.parse(
    fs.readFileSync(path.join(context.packager.projectDir, 'package.json'), 'utf8'),
  );
  const main = expectedMetadata.main;
  if (!files.has('/package.json')) fail('package.json is missing from app.asar');
  if (typeof main !== 'string' || !files.has(`/${main.replace(/^\/+/, '')}`)) {
    fail(`application entry is missing from app.asar: ${main || '<unset>'}`);
  }
  if (packagedMetadata.name !== expectedMetadata.name) fail('packaged application name does not match source metadata');
  if (packagedMetadata.version !== expectedMetadata.version) fail('packaged application version does not match source metadata');
  if (packagedMetadata.main !== expectedMetadata.main) fail('packaged application entry does not match source metadata');

  const defaultApp = path.join(resources, 'default_app.asar');
  if (fs.existsSync(defaultApp)) fs.rmSync(defaultApp);
  return { archive, main, version: packagedMetadata.version, defaultAppRemoved: !fs.existsSync(defaultApp) };
}

async function afterPack(context) {
  const result = validatePackagedApp(context);
  console.log(`  • verified packaged runtime  appAsar=${result.archive} entry=${result.main} version=${result.version}`);
}

exports.default = afterPack;
exports.listedAsarPath = listedAsarPath;
exports.resourcesDirectory = resourcesDirectory;
exports.validatePackagedApp = validatePackagedApp;
