'use strict';

const { contextBridge, ipcRenderer } = require('electron');

contextBridge.exposeInMainWorld('petAPI', {
  getActivePet: () => ipcRenderer.invoke('pet:get-active'),
  setIgnoreMouse: (ignore) => ipcRenderer.send('pet:set-ignore-mouse', Boolean(ignore)),
  moveWindow: (payload) => ipcRenderer.invoke('pet:move-window', payload),
  beginWalk: () => ipcRenderer.invoke('pet:begin-walk'),
  beginFall: () => ipcRenderer.invoke('pet:begin-fall'),
  beginCursorChase: (point) => ipcRenderer.invoke('pet:begin-cursor-chase', point),
  returnCursorChase: () => ipcRenderer.invoke('pet:return-cursor-chase'),
  stopWalk: () => ipcRenderer.send('pet:stop-walk'),
  persistPosition: () => ipcRenderer.send('pet:persist-position'),
  showContextMenu: () => ipcRenderer.invoke('pet:show-context-menu'),
  onPetChanged: (callback) => {
    const listener = (_event, payload) => callback(payload);
    ipcRenderer.on('pet:changed', listener);
    return () => ipcRenderer.removeListener('pet:changed', listener);
  },
  onWalkFinished: (callback) => { const listener=()=>callback(); ipcRenderer.on('pet:walk-finished',listener); return()=>ipcRenderer.removeListener('pet:walk-finished',listener); },
  onFallFinished: (callback) => { const listener=()=>callback(); ipcRenderer.on('pet:fall-finished',listener); return()=>ipcRenderer.removeListener('pet:fall-finished',listener); },
  onCursorNear: (callback) => { const listener=(_event,point)=>callback(point); ipcRenderer.on('pet:cursor-near',listener); return()=>ipcRenderer.removeListener('pet:cursor-near',listener); },
  onCursorChaseArrived: (callback) => { const listener=(_event,payload)=>callback(payload); ipcRenderer.on('pet:cursor-chase-arrived',listener); return()=>ipcRenderer.removeListener('pet:cursor-chase-arrived',listener); },
  onCursorChaseReturned: (callback) => { const listener=(_event,payload)=>callback(payload); ipcRenderer.on('pet:cursor-chase-returned',listener); return()=>ipcRenderer.removeListener('pet:cursor-chase-returned',listener); },
});
