'use strict';

const { app, BrowserWindow, dialog, ipcMain, Menu, nativeImage, screen, shell, Tray } = require('electron');
const AdmZip = require('adm-zip');
const crypto = require('node:crypto');
const fs = require('node:fs');
const path = require('node:path');
const { pathToFileURL } = require('node:url');
const { inspectSchemaVersion, validateManifest } = require('./core/manifest');
const { parseCommandLine } = require('./core/command-line');
const { createCommandQueue } = require('./core/command-queue');
const { planWalk } = require('./core/walk-planner');
const { fallY, planCursorChase, planFall } = require('./core/motion-planner');

// Keeps local QA and screenshots isolated from a user's real imported pets.
// Production launches do not set this variable and continue using Electron's
// normal per-user application-data directory.
if (process.env.DESKTOP_PET_USER_DATA_DIR) {
  app.setPath('userData', path.resolve(process.env.DESKTOP_PET_USER_DATA_DIR));
}

const MAX_ARCHIVE_BYTES = 80 * 1024 * 1024;
const MAX_FILE_BYTES = 24 * 1024 * 1024;
const SCALE_OPTIONS = [0.5, 0.6, 0.75, 1, 1.25, 1.5];
const DEFAULT_SETTINGS = Object.freeze({
  settingsVersion: 2,
  activePetId: null,
  scale: 0.6,
  activityLevel: 'balanced',
  cursorAwareness: true,
  paused: false,
  visible: true,
  alwaysOnTop: true,
  launchAtLogin: false,
  position: null,
});

let petWindow;
let tray;
let settings;
let quitting = false;
let saveTimer;
let walkTimer;
let fallTimer;
let cursorMotionTimer;
let cursorChaseOrigin = null;
let cursorTimer;
let cursorEnteredAt = 0;
let cursorFired = false;
let lastCursorResponseAt = 0;

function isChinese() {
  return app.getLocale().toLowerCase().startsWith('zh');
}

function t(zh, en) {
  return isChinese() ? zh : en;
}

function settingsPath() {
  return path.join(app.getPath('userData'), 'settings.json');
}

function petsPath() {
  return path.join(app.getPath('userData'), 'pets');
}

function legacyPetsPath() { return path.join(app.getPath('userData'), 'legacy-pets'); }

function loadSettings() {
  try {
    const parsed = JSON.parse(fs.readFileSync(settingsPath(), 'utf8'));
    const migrated = { ...DEFAULT_SETTINGS, ...parsed, settingsVersion: 2 };
    if (!parsed.settingsVersion) migrated.scale = 0.6;
    if (!['quiet','balanced','lively'].includes(migrated.activityLevel)) migrated.activityLevel='balanced';
    migrated.cursorAwareness = migrated.cursorAwareness !== false;
    return migrated;
  } catch {
    return { ...DEFAULT_SETTINGS };
  }
}

function saveSettings() {
  fs.mkdirSync(app.getPath('userData'), { recursive: true });
  const temp = `${settingsPath()}.tmp`;
  fs.writeFileSync(temp, JSON.stringify(settings, null, 2));
  fs.renameSync(temp, settingsPath());
}

function scheduleSave() {
  clearTimeout(saveTimer);
  saveTimer = setTimeout(() => saveSettings(), 750);
}

function listPets() {
  fs.mkdirSync(petsPath(), { recursive: true });
  const pets = [];
  for (const entry of fs.readdirSync(petsPath(), { withFileTypes: true })) {
    if (!entry.isDirectory() || entry.name.startsWith('.')) continue;
    try {
      const root = path.join(petsPath(), entry.name);
      const manifest = validateManifest(JSON.parse(fs.readFileSync(path.join(root, 'pet.json'), 'utf8')));
      if (manifest.id === entry.name) pets.push({ id: manifest.id, name: manifest.displayName, root, manifest });
    } catch {
      // Invalid imported folders stay isolated and never appear in the menu.
    }
  }
  return pets.sort((a, b) => a.name.localeCompare(b.name));
}

function listLegacyPets() {
  const found = [];
  for (const base of [petsPath(), legacyPetsPath()]) {
    fs.mkdirSync(base, { recursive: true });
    for (const entry of fs.readdirSync(base, { withFileTypes: true })) {
      if (!entry.isDirectory() || entry.name.startsWith('.')) continue;
      try {
        const root = path.join(base, entry.name);
        const manifest = JSON.parse(fs.readFileSync(path.join(root, 'pet.json'), 'utf8'));
        if (inspectSchemaVersion(manifest) === 1 && manifest.id === entry.name) found.push({ id: manifest.id, name: manifest.displayName || manifest.id, root });
      } catch { /* keep unreadable folders isolated */ }
    }
  }
  return found.sort((a,b)=>a.name.localeCompare(b.name));
}

function activePet() {
  return listPets().find((pet) => pet.id === settings.activePetId) || null;
}

function petPayload() {
  const pet = activePet();
  if (!pet) return { fallback: true, paused: settings.paused, scale: settings.scale, activityLevel: settings.activityLevel, cursorAwareness: settings.cursorAwareness };
  const actionUrls = {};
  for (const [name, action] of Object.entries(pet.manifest.actions)) {
    actionUrls[name] = pathToFileURL(path.join(pet.root, action.file)).href;
  }
  return {
    fallback: false,
    manifest: pet.manifest,
    actionUrls,
    paused: settings.paused,
    scale: settings.scale,
    activityLevel: settings.activityLevel,
    cursorAwareness: settings.cursorAwareness,
  };
}

function currentCanvas() {
  const pet = activePet();
  return pet ? pet.manifest.canvas : { width: 256, height: 256 };
}

function currentAnchor() {
  const pet = activePet();
  return pet ? pet.manifest.anchor : { x: 128, y: 224 };
}

function windowSize() {
  const canvas = currentCanvas();
  return {
    width: Math.round(canvas.width * settings.scale),
    height: Math.round(canvas.height * settings.scale),
  };
}

function floorPosition(display, x) {
  const size = windowSize();
  const anchor = currentAnchor();
  return {
    x: Math.round(Math.min(Math.max(x, display.workArea.x - size.width * 0.25), display.workArea.x + display.workArea.width - size.width * 0.75)),
    y: Math.round(display.workArea.y + display.workArea.height - anchor.y * settings.scale),
  };
}

function resetPosition() {
  if (!petWindow) return;
  const display = screen.getPrimaryDisplay();
  const size = windowSize();
  const target = floorPosition(display, display.workArea.x + display.workArea.width - size.width - 28);
  settings.position = target;
  petWindow.setBounds({ ...target, ...size });
  saveSettings();
}

function restoreBounds() {
  const size = windowSize();
  const candidate = settings.position || { x: 0, y: 0 };
  const display = screen.getDisplayNearestPoint(candidate);
  const target = settings.position ? floorPosition(display, candidate.x) : floorPosition(display, display.workArea.x + display.workArea.width - size.width - 28);
  settings.position = target;
  petWindow.setBounds({ ...target, ...size });
}

function moveWindow({ x, y, dx = 0, dragging = false }) {
  if (!petWindow) return { hitEdge: false };
  const bounds = petWindow.getBounds();
  const requestedX = Number.isFinite(x) ? x : bounds.x + dx;
  const point = { x: Math.round(requestedX + bounds.width / 2), y: Math.round((Number.isFinite(y) ? y : bounds.y) + bounds.height / 2) };
  const display = screen.getDisplayNearestPoint(point);
  const size = windowSize();
  const minX = display.workArea.x - size.width * 0.25;
  const maxX = display.workArea.x + display.workArea.width - size.width * 0.75;
  const clampedX = Math.round(Math.min(Math.max(requestedX, minX), maxX));
  const target = floorPosition(display, clampedX);
  if (dragging && Number.isFinite(y)) {
    const minY = display.workArea.y - size.height * 0.25;
    const maxY = display.workArea.y + display.workArea.height - size.height * 0.5;
    target.y = Math.round(Math.min(Math.max(y, minY), maxY));
  }
  petWindow.setPosition(target.x, target.y, false);
  settings.position = target;
  scheduleSave();
  return { hitEdge: clampedX !== Math.round(requestedX), position: target };
}

function stopWalk(notify = false) {
  if (walkTimer) clearInterval(walkTimer);
  walkTimer = null;
  if (notify && petWindow && !petWindow.isDestroyed()) petWindow.webContents.send('pet:walk-finished');
}

function stopFall() { if (fallTimer) clearInterval(fallTimer); fallTimer = null; }
function stopCursorMotion() { if (cursorMotionTimer) clearInterval(cursorMotionTimer); cursorMotionTimer = null; }
function stopPhysicalMotion() { stopWalk(false); stopFall(); stopCursorMotion(); cursorChaseOrigin = null; }

function beginWalk() {
  stopFall();
  stopCursorMotion();
  stopWalk(false);
  if (!petWindow || settings.paused) return null;
  const bounds = petWindow.getBounds();
  const display = screen.getDisplayNearestPoint({ x: bounds.x + bounds.width / 2, y: bounds.y + bounds.height / 2 });
  const size = windowSize();
  const minX = display.workArea.x - size.width * 0.25;
  const maxX = display.workArea.x + display.workArea.width - size.width * 0.75;
  const plan = planWalk({ currentX: bounds.x, minX, maxX, workAreaWidth: display.workArea.width });
  if (!plan) return null;
  const startedAt = Date.now();
  walkTimer = setInterval(() => {
    const elapsed = (Date.now() - startedAt) / 1000;
    const travelled = Math.min(plan.distance, elapsed * plan.speed);
    const nextX = bounds.x + plan.direction * travelled;
    moveWindow({ x: nextX });
    if (travelled >= plan.distance) stopWalk(true);
  }, 50);
  return plan;
}

function beginFall() {
  stopWalk(false); stopCursorMotion(); stopFall();
  if (!petWindow) return null;
  const bounds = petWindow.getBounds();
  const display = screen.getDisplayNearestPoint({ x: bounds.x + bounds.width / 2, y: bounds.y + bounds.height / 2 });
  const target = floorPosition(display, bounds.x);
  const plan = planFall({ startY: bounds.y, floorY: target.y });
  if (!plan) {
    petWindow.setPosition(target.x, target.y, false);
    petWindow.webContents.send('pet:fall-finished');
    return null;
  }
  const startedAt = Date.now();
  fallTimer = setInterval(() => {
    const y = fallY(plan, Date.now() - startedAt);
    petWindow.setPosition(target.x, y, false);
    if (y >= plan.floorY) {
      stopFall();
      settings.position = target;
      scheduleSave();
      petWindow.webContents.send('pet:fall-finished');
    }
  }, 50);
  return plan;
}

function horizontalBounds(bounds) {
  const display = screen.getDisplayNearestPoint({ x: bounds.x + bounds.width / 2, y: bounds.y + bounds.height / 2 });
  const size = windowSize();
  return {
    minX: display.workArea.x - size.width * 0.25,
    maxX: display.workArea.x + display.workArea.width - size.width * 0.75,
  };
}

function animateHorizontal(fromX, toX, speed, finishedEvent) {
  stopCursorMotion();
  const direction = toX < fromX ? -1 : 1;
  const distance = Math.abs(toX - fromX);
  const startedAt = Date.now();
  cursorMotionTimer = setInterval(() => {
    const travelled = Math.min(distance, (Date.now() - startedAt) / 1000 * speed);
    moveWindow({ x: fromX + direction * travelled });
    if (travelled >= distance) {
      stopCursorMotion();
      petWindow.webContents.send(finishedEvent, { direction });
    }
  }, 50);
}

function beginCursorChase(point) {
  stopWalk(false); stopFall(); stopCursorMotion();
  if (!petWindow || settings.paused) return null;
  const bounds = petWindow.getBounds();
  const limits = horizontalBounds(bounds);
  const plan = planCursorChase({ currentX: bounds.x, cursorX: point.x, windowWidth: bounds.width, ...limits });
  if (!plan) return null;
  cursorChaseOrigin = plan.originX;
  animateHorizontal(plan.originX, plan.targetX, plan.speed, 'pet:cursor-chase-arrived');
  return plan;
}

function returnCursorChase() {
  if (!petWindow || cursorChaseOrigin === null) return null;
  const fromX = petWindow.getBounds().x;
  const targetX = cursorChaseOrigin;
  const direction = targetX < fromX ? -1 : 1;
  animateHorizontal(fromX, targetX, 42, 'pet:cursor-chase-returned');
  cursorChaseOrigin = null;
  return { direction, targetX };
}

function cursorCooldownMs() { return { quiet: 60000, balanced: 30000, lively: 18000 }[settings.activityLevel] || 30000; }
function pollCursor() {
  if (!petWindow || petWindow.isDestroyed() || !settings.visible || settings.paused || !settings.cursorAwareness) { cursorEnteredAt=0; cursorFired=false; return; }
  const point=screen.getCursorScreenPoint(); const b=petWindow.getBounds(); const pad=96;
  const near=point.x>=b.x-pad&&point.x<=b.x+b.width+pad&&point.y>=b.y-pad&&point.y<=b.y+b.height+pad;
  if(!near){cursorEnteredAt=0;cursorFired=false;return;}
  if(!cursorEnteredAt)cursorEnteredAt=Date.now();
  if(!cursorFired&&Date.now()-cursorEnteredAt>=1500&&Date.now()-lastCursorResponseAt>=cursorCooldownMs()){
    cursorFired=true;lastCursorResponseAt=Date.now();petWindow.webContents.send('pet:cursor-near', point);
  }
}

function persistPosition() {
  if (!petWindow) return;
  settings.position = petWindow.getPosition().reduce((result, value, index) => {
    result[index === 0 ? 'x' : 'y'] = value;
    return result;
  }, {});
  saveSettings();
}

function trayImage() {
  const svg = `<svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 32 32"><path fill="#111" d="M8 7c5-4 12-3 15 2 3 4 2 12-2 16-5 4-13 2-16-3C3 17 4 10 8 7Z"/><circle fill="#fff" cx="12" cy="15" r="2"/><circle fill="#fff" cx="20" cy="15" r="2"/><path stroke="#fff" stroke-width="2" stroke-linecap="round" d="M13 21c2 1 4 1 6-1"/></svg>`;
  return nativeImage.createFromDataURL(`data:image/svg+xml;base64,${Buffer.from(svg).toString('base64')}`);
}

function notifyRenderer() {
  if (!petWindow || petWindow.isDestroyed()) return;
  stopPhysicalMotion();
  petWindow.webContents.send('pet:changed', petPayload());
  restoreBounds();
}

function setPetVisible(visible) {
  settings.visible = Boolean(visible);
  settings.visible ? petWindow?.showInactive() : petWindow?.hide();
  saveSettings();
  updateTrayMenu();
}

function quitRuntime() {
  quitting = true;
  app.quit();
}

function sizeMenuItems() {
  return SCALE_OPTIONS.map((scale) => ({
    label: `${Math.round(scale * 100)}%`, type: 'radio', checked: settings.scale === scale,
    click: () => { settings.scale = scale; saveSettings(); notifyRenderer(); updateTrayMenu(); },
  }));
}

function activityMenuItems() {
  return [['quiet',t('安静','Quiet')],['balanced',t('均衡','Balanced')],['lively',t('活泼','Lively')]].map(([value,label])=>({
    label, type:'radio', checked:settings.activityLevel===value,
    click:()=>{settings.activityLevel=value;saveSettings();notifyRenderer();updateTrayMenu();},
  }));
}

function petChoiceMenuItems() {
  const pets = listPets();
  return pets.length ? pets.map((pet) => ({
    label: pet.name, type: 'radio', checked: pet.id === settings.activePetId,
    click: () => { settings.activePetId = pet.id; saveSettings(); notifyRenderer(); updateTrayMenu(); },
  })) : [{ label: t('尚未导入', 'No imported pets'), enabled: false }];
}

function showPetContextMenu() {
  const menu = Menu.buildFromTemplate([
    { label: t('暂停活动', 'Pause activity'), type: 'checkbox', checked: settings.paused,
      click: (item) => { settings.paused = item.checked; saveSettings(); notifyRenderer(); updateTrayMenu(); } },
    { label: t('活跃度', 'Activity'), submenu: activityMenuItems() },
    { label: t('尺寸', 'Size'), submenu: sizeMenuItems() },
    { label: t('切换角色', 'Choose pet'), submenu: petChoiceMenuItems() },
    { label: t('鼠标靠近回应', 'Cursor awareness'), type: 'checkbox', checked: settings.cursorAwareness,
      click: (item) => { settings.cursorAwareness = item.checked; saveSettings(); notifyRenderer(); updateTrayMenu(); } },
    { type: 'separator' },
    { label: t('隐藏桌宠', 'Hide pet'), click: () => setPetVisible(false) },
    { label: t('退出桌宠', 'Quit pet'), click: quitRuntime },
  ]);
  return new Promise((resolve) => menu.popup({ window: petWindow, callback: resolve }));
}

function updateTrayMenu() {
  const pets = listPets();
  const legacyPets = listLegacyPets();
  const template = [
    {
      label: settings.visible ? t('隐藏桌宠', 'Hide pet') : t('显示桌宠', 'Show pet'),
      click: () => {
        settings.visible = !settings.visible;
        settings.visible ? petWindow.showInactive() : petWindow.hide();
        saveSettings();
        updateTrayMenu();
      },
    },
    {
      label: t('导入角色包…', 'Import pet pack…'),
      click: importPetPack,
    },
    {
      label: t('切换角色', 'Choose pet'),
      submenu: petChoiceMenuItems(),
    },
    {
      label: t('需要升级的角色', 'Pets needing upgrade'),
      submenu: legacyPets.length
        ? [
            ...legacyPets.map((pet)=>({label:`${pet.name} (v1)`,enabled:false})),
            {type:'separator'},
            {label:t('打开角色目录','Open pet folder'),click:()=>shell.openPath(legacyPetsPath())},
          ]
        : [{label:t('没有待升级角色','No pets need upgrade'),enabled:false}],
    },
    {
      label: t('尺寸', 'Size'),
      submenu: sizeMenuItems(),
    },
    {
      label: t('暂停活动', 'Pause activity'),
      type: 'checkbox',
      checked: settings.paused,
      click: (item) => {
        settings.paused = item.checked;
        saveSettings();
        notifyRenderer();
      },
    },
    {
      label: t('活跃度', 'Activity'),
      submenu: activityMenuItems(),
    },
    {
      label: t('鼠标靠近回应', 'Cursor awareness'),
      type: 'checkbox', checked: settings.cursorAwareness,
      click: (item)=>{settings.cursorAwareness=item.checked;saveSettings();notifyRenderer();},
    },
    {
      label: t('始终置顶', 'Always on top'),
      type: 'checkbox',
      checked: settings.alwaysOnTop,
      click: (item) => {
        settings.alwaysOnTop = item.checked;
        petWindow.setAlwaysOnTop(item.checked, 'floating');
        saveSettings();
      },
    },
    {
      label: t('开机启动', 'Launch at login'),
      type: 'checkbox',
      checked: settings.launchAtLogin,
      click: (item) => {
        settings.launchAtLogin = item.checked;
        app.setLoginItemSettings({ openAtLogin: item.checked });
        saveSettings();
      },
    },
    { label: t('回到右下角', 'Reset to bottom right'), click: resetPosition },
    { type: 'separator' },
    {
      label: t('退出', 'Quit'),
      click: quitRuntime,
    },
  ];
  tray.setContextMenu(Menu.buildFromTemplate(template));
  tray.setToolTip(t('涂鸦桌宠', 'Doodle Desktop Pet'));
}

async function handleCommandLine(argv) {
  const command = parseCommandLine(argv);
  if (command.quit) { quitRuntime(); return; }
  if (command.openPet) await installPetPack(command.openPet, { interactive: false });
  if (command.show || command.openPet) setPetVisible(true);
}

const commandQueue = createCommandQueue(handleCommandLine);

function validateZipEntryName(name) {
  const normalized = name.replaceAll('\\', '/');
  const parts = normalized.split('/').filter(Boolean);
  if (!parts.length || normalized.startsWith('/') || parts.some((part) => part === '.' || part === '..' || part.includes(':'))) {
    throw new Error(t(`压缩包包含不安全路径：${name}`, `Unsafe ZIP path: ${name}`));
  }
  return parts;
}

async function importPetPack() {
  const selection = await dialog.showOpenDialog({
    title: t('导入桌宠角色包', 'Import desktop pet pack'),
    properties: ['openFile'],
    filters: [{ name: 'Desktop pet pack', extensions: ['zip'] }],
  });
  if (selection.canceled || !selection.filePaths[0]) return;

  return installPetPack(selection.filePaths[0], { interactive: true });
}

async function installPetPack(filePath, { interactive = false } = {}) {
  const staging = path.join(petsPath(), `.import-${crypto.randomUUID()}`);
  fs.mkdirSync(staging, { recursive: true });
  let replacedBackup = null;
  let destination = null;
  try {
    const resolvedPack = path.resolve(filePath);
    if (path.extname(resolvedPack).toLowerCase() !== '.zip' || !fs.statSync(resolvedPack).isFile()) {
      throw new Error(t('启动器指定的角色包不存在或不是 ZIP', 'The launcher pet pack is missing or is not a ZIP'));
    }
    const zip = new AdmZip(resolvedPack);
    const entries = zip.getEntries();
    if (!entries.length) throw new Error(t('角色包为空', 'The pet pack is empty'));
    let total = 0;
    const roots = new Set();
    for (const entry of entries) {
      const parts = validateZipEntryName(entry.entryName);
      roots.add(parts[0]);
      const size = Number(entry.header.size || 0);
      if (size > MAX_FILE_BYTES) throw new Error(t('角色包中有文件超过 24 MB', 'A pack file exceeds 24 MB'));
      total += size;
      if (total > MAX_ARCHIVE_BYTES) throw new Error(t('角色包解压后超过 80 MB', 'The expanded pack exceeds 80 MB'));
      if (entry.isDirectory) continue;
      const destination = path.join(staging, ...parts);
      const resolved = path.resolve(destination);
      if (!resolved.startsWith(`${path.resolve(staging)}${path.sep}`)) throw new Error(t('角色包路径越界', 'Pack path escapes its root'));
      fs.mkdirSync(path.dirname(resolved), { recursive: true });
      fs.writeFileSync(resolved, entry.getData(), { flag: 'wx' });
    }
    if (roots.size !== 1) throw new Error(t('角色包必须只有一个顶层目录', 'The pack must have one top-level directory'));
    const rootName = [...roots][0];
    const sourceRoot = path.join(staging, rootName);
    const rawManifest = JSON.parse(fs.readFileSync(path.join(sourceRoot, 'pet.json'), 'utf8'));
    if (inspectSchemaVersion(rawManifest) === 1) {
      if (rawManifest.id !== rootName) throw new Error(t('顶层目录必须与角色 id 相同', 'Top-level directory must match the pet id'));
      const legacyDestination = path.join(legacyPetsPath(), rawManifest.id);
      fs.mkdirSync(legacyPetsPath(), { recursive: true });
      if (fs.existsSync(legacyDestination)) {
        const suffix = new Date().toISOString().replace(/[:.]/g, '-');
        fs.renameSync(sourceRoot, `${legacyDestination}-${suffix}`);
      } else fs.renameSync(sourceRoot, legacyDestination);
      await dialog.showMessageBox({
        type:'info', buttons:[t('知道了','OK')],
        message:t(`“${rawManifest.displayName || rawManifest.id}”是 v1 八动作角色包，已完整保留但不会运行。请交给桌宠 Skill 补画四个动作并重新确认。`,`“${rawManifest.displayName || rawManifest.id}” is a v1 eight-action pack. It was preserved but will not run. Use the desktop-pet Skill to add four actions and review it.`),
      });
      updateTrayMenu(); return;
    }
    const manifest = validateManifest(rawManifest);
    if (manifest.id !== rootName) throw new Error(t('顶层目录必须与角色 id 相同', 'Top-level directory must match the pet id'));
    if (!fs.existsSync(path.join(sourceRoot, 'preview.png'))) throw new Error(t('缺少 preview.png', 'preview.png is missing'));
    for (const action of Object.values(manifest.actions)) {
      if (!fs.statSync(path.join(sourceRoot, action.file)).isFile()) throw new Error(t('缺少动作素材', 'An animation file is missing'));
    }

    destination = path.join(petsPath(), manifest.id);
    if (fs.existsSync(destination)) {
      if (interactive) {
        const answer = await dialog.showMessageBox({
          type: 'question',
          buttons: [t('替换', 'Replace'), t('取消', 'Cancel')],
          defaultId: 1,
          cancelId: 1,
          message: t(`角色“${manifest.displayName}”已存在，是否替换？`, `“${manifest.displayName}” already exists. Replace it?`),
        });
        if (answer.response !== 0) return null;
      }
      replacedBackup = path.join(petsPath(), `.backup-${manifest.id}-${crypto.randomUUID()}`);
      fs.renameSync(destination, replacedBackup);
    }
    fs.renameSync(sourceRoot, destination);
    if (replacedBackup) fs.rmSync(replacedBackup, { recursive: true, force: true });
    settings.activePetId = manifest.id;
    settings.scale = manifest.defaultScale;
    settings.visible = true;
    saveSettings();
    notifyRenderer();
    petWindow?.showInactive();
    updateTrayMenu();
    return manifest;
  } catch (error) {
    if (replacedBackup && destination && fs.existsSync(replacedBackup) && !fs.existsSync(destination)) {
      fs.renameSync(replacedBackup, destination);
    }
    dialog.showErrorBox(t('无法导入角色包', 'Could not import pet pack'), error.message);
    return null;
  } finally {
    fs.rmSync(staging, { recursive: true, force: true });
  }
}

function createWindow() {
  const size = windowSize();
  petWindow = new BrowserWindow({
    ...size,
    show: false,
    frame: false,
    transparent: true,
    resizable: false,
    movable: false,
    minimizable: false,
    maximizable: false,
    fullscreenable: false,
    skipTaskbar: true,
    focusable: false,
    alwaysOnTop: settings.alwaysOnTop,
    hasShadow: false,
    backgroundColor: '#00000000',
    webPreferences: {
      preload: path.join(__dirname, 'preload.js'),
      contextIsolation: true,
      nodeIntegration: false,
      sandbox: true,
    },
  });
  petWindow.setAlwaysOnTop(settings.alwaysOnTop, 'floating');
  if (process.platform === 'darwin') petWindow.setVisibleOnAllWorkspaces(true, { visibleOnFullScreen: true });
  petWindow.setIgnoreMouseEvents(true, { forward: true });
  petWindow.loadFile(path.join(__dirname, 'renderer', 'index.html'));
  petWindow.once('ready-to-show', () => {
    restoreBounds();
    if (settings.visible) petWindow.showInactive();
  });
  petWindow.on('close', (event) => {
    if (!quitting) {
      event.preventDefault();
      settings.visible = false;
      petWindow.hide();
      saveSettings();
      updateTrayMenu();
    }
  });
  petWindow.on('moved', () => {
    const [x, y] = petWindow.getPosition();
    settings.position = { x, y };
    scheduleSave();
  });
}

function registerIpc() {
  ipcMain.handle('pet:get-active', () => petPayload());
  ipcMain.on('pet:set-ignore-mouse', (_event, ignore) => {
    if (petWindow && !petWindow.isDestroyed()) petWindow.setIgnoreMouseEvents(Boolean(ignore), { forward: true });
  });
  ipcMain.handle('pet:move-window', (_event, payload) => { if (payload?.dragging) stopPhysicalMotion(); return moveWindow(payload || {}); });
  ipcMain.handle('pet:begin-walk', beginWalk);
  ipcMain.handle('pet:begin-fall', beginFall);
  ipcMain.handle('pet:begin-cursor-chase', (_event, point) => beginCursorChase(point || screen.getCursorScreenPoint()));
  ipcMain.handle('pet:return-cursor-chase', returnCursorChase);
  ipcMain.on('pet:stop-walk', () => stopWalk(false));
  ipcMain.on('pet:persist-position', persistPosition);
  ipcMain.handle('pet:show-context-menu', showPetContextMenu);
}

if (!app.requestSingleInstanceLock()) {
  app.quit();
} else {
  commandQueue.dispatch(process.argv);
  app.on('second-instance', (_event, commandLine) => {
    commandQueue.dispatch(commandLine).catch((error) => console.error('Could not handle launcher command:', error));
  });

  app.whenReady().then(async () => {
    settings = loadSettings();
    fs.mkdirSync(petsPath(), { recursive: true });
    registerIpc();
    createWindow();
    tray = new Tray(trayImage());
    cursorTimer = setInterval(pollCursor, 500);
    tray.on('double-click', () => {
      settings.visible = !petWindow.isVisible();
      settings.visible ? petWindow.showInactive() : petWindow.hide();
      saveSettings();
      updateTrayMenu();
    });
    updateTrayMenu();
    await commandQueue.markReady();
  });
}

app.on('window-all-closed', () => {});
app.on('before-quit', () => {
  quitting = true;
  clearTimeout(saveTimer);
  clearInterval(cursorTimer);
  stopWalk(false);
  stopFall();
  stopCursorMotion();
  if (settings) saveSettings();
});
