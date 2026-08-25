'use strict';
const test=require('node:test');const assert=require('node:assert/strict');const {planWalk}=require('../src/core/walk-planner');
test('plans one monotonic local walk in the allowed range',()=>{const p=planWalk({currentX:500,minX:0,maxX:1200,workAreaWidth:1000,random:()=>.5});assert.equal(p.direction,1);assert.ok(p.distance>=80&&p.distance<=240);assert.ok(p.speed>=30&&p.speed<=36);assert.equal(p.targetX,500+p.distance);});
test('chooses away from a nearby boundary',()=>{const p=planWalk({currentX:30,minX:0,maxX:1000,workAreaWidth:1000,random:()=>0});assert.equal(p.direction,1);});
