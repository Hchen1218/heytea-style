'use strict';
const path = require('node:path');
const REQUIRED_ACTIONS = Object.freeze(['idle','walk','rest','happy','drag','land','wave','signature','curious','stretch','tiptoe','play']);
const OPTIONAL_ACTIONS = Object.freeze(['fall','touch']);
const ALLOWED_ACTIONS = Object.freeze([...REQUIRED_ACTIONS, ...OPTIONAL_ACTIONS]);
const LEGACY_ACTIONS = Object.freeze(REQUIRED_ACTIONS.slice(0, 8));
class ManifestError extends Error {}
function assert(condition, message) { if (!condition) throw new ManifestError(message); }
function between(value,min,max){return Number.isInteger(value)&&value>=min&&value<=max;}
function validateRelativeAssetPath(value,label){assert(typeof value==='string'&&value.length>0,`${label} must be a non-empty string`);const normalized=value.replaceAll('\\','/');assert(!path.posix.isAbsolute(normalized),`${label} must be relative`);assert(normalized.split('/').every((part)=>part&&part!=='.'&&part!=='..'&&!part.includes(':')),`${label} is unsafe`);assert(['.png','.webp'].includes(path.posix.extname(normalized).toLowerCase()),`${label} must be PNG or WebP`);return normalized;}
function inspectSchemaVersion(manifest){return Number.isInteger(manifest?.schemaVersion)?manifest.schemaVersion:null;}
function validateManifest(manifest){
  assert(manifest&&typeof manifest==='object'&&!Array.isArray(manifest),'manifest must be an object');
  assert(manifest.schemaVersion===2,'schemaVersion must be exactly 2');
  assert(/^[a-z0-9]+(?:-[a-z0-9]+)*$/.test(manifest.id),'id must use lowercase letters, digits, and hyphens');
  assert(typeof manifest.displayName==='string'&&manifest.displayName.trim(),'displayName is required');
  const {canvas,anchor,hitbox}=manifest;
  assert(canvas&&between(canvas.width,32,1024)&&between(canvas.height,32,1024),'canvas dimensions must be 32-1024');
  assert(anchor&&between(anchor.x,0,canvas.width-1)&&between(anchor.y,0,canvas.height-1),'anchor is outside the canvas');
  assert(typeof manifest.defaultScale==='number'&&manifest.defaultScale>=0.5&&manifest.defaultScale<=2,'defaultScale must be 0.5-2');
  assert(Array.isArray(manifest.palette)&&manifest.palette.length>=1&&manifest.palette.length<=3&&manifest.palette.every((c)=>/^#[0-9a-f]{6}$/i.test(c)),'palette must have 1-3 #RRGGBB colors');
  assert(hitbox&&between(hitbox.alphaThreshold,1,254)&&hitbox.bounds,'hitbox is invalid');const b=hitbox.bounds;
  assert(between(b.x,0,canvas.width-1)&&between(b.y,0,canvas.height-1)&&between(b.width,1,canvas.width)&&between(b.height,1,canvas.height)&&b.x+b.width<=canvas.width&&b.y+b.height<=canvas.height,'hitbox.bounds leaves the canvas');
  assert(manifest.actions&&typeof manifest.actions==='object'&&!Array.isArray(manifest.actions),'actions is required');
  const names=Object.keys(manifest.actions);assert(REQUIRED_ACTIONS.every((n)=>names.includes(n)),'all twelve schema-v2 actions are required');assert(names.every((n)=>ALLOWED_ACTIONS.includes(n)),`unsupported action: ${names.find((n)=>!ALLOWED_ACTIONS.includes(n))}`);
  for(const name of names){const a=manifest.actions[name];assert(a&&typeof a==='object',`actions.${name} must be an object`);a.file=validateRelativeAssetPath(a.file,`actions.${name}.file`);assert(between(a.frames,1,24),`actions.${name}.frames must be 1-24`);assert(between(a.fps,1,30),`actions.${name}.fps must be 1-30`);assert(typeof a.loop==='boolean'&&typeof a.mirrorable==='boolean',`actions.${name} flags must be boolean`);}
  assert(manifest.actions.walk.mirrorable===true,'walk must be mirrorable');return manifest;
}
module.exports={ManifestError,REQUIRED_ACTIONS,OPTIONAL_ACTIONS,ALLOWED_ACTIONS,LEGACY_ACTIONS,inspectSchemaVersion,validateManifest,validateRelativeAssetPath};
