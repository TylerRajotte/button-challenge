import {launchBrowser} from './browser.mjs';
import assert from 'node:assert/strict';
import fs from 'node:fs';
const browser=await launchBrowser();
const page=await browser.newPage({viewport:{width:720,height:540},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:5173/?clean');await page.waitForFunction(()=>window.sourceReplay);
fs.mkdirSync('evidence/replay',{recursive:true});
for(const time of [0,2,4,8,12,16,19]){
  await page.evaluate(t=>window.sourceReplay.seek(t),time);await page.waitForTimeout(200);
  await page.screenshot({path:`evidence/replay/implementation-${time}.png`});
}
console.log('Track:',await page.evaluate(()=>window.sourceReplay.state));
await page.goto('http://127.0.0.1:5173/');await page.getByRole('button',{name:'Replay source motion',exact:true}).click();
await page.waitForFunction(()=>window.sourceReplay.state.time>1);assert.equal(await page.evaluate(()=>window.sourceReplay.state.playing),true);
await page.getByRole('button',{name:'Stop replay',exact:true}).click();assert.equal(await page.evaluate(()=>window.sourceReplay.state.active),false);
await page.setViewportSize({width:1472,height:690});await page.goto('http://127.0.0.1:5173/?compare');await page.waitForFunction(()=>window.sourceReplay);
await page.getByRole('button',{name:'Play both',exact:true}).click();await page.waitForFunction(()=>window.sourceReplay.state.time>2);await page.getByRole('button',{name:'Pause both',exact:true}).click();
await page.evaluate(()=>window.sourceReplay.seek(4));await page.waitForFunction(()=>!document.querySelector('video').seeking);await page.screenshot({path:'evidence/comparison.png'});
const result=await page.evaluate(()=>({replay:window.sourceReplay.state,videoTime:document.querySelector('video').currentTime,labelTransform:getComputedStyle(document.querySelector('#ripple-button span')).transform,buttonTransform:getComputedStyle(document.querySelector('#ripple-button')).transform,buttonParent:document.querySelector('#ripple-button').parentElement.tagName}));
assert.ok(Math.abs(result.replay.time-result.videoTime)<.05);assert.equal(result.labelTransform,'none');assert.equal(result.buttonTransform,'none');assert.equal(result.buttonParent,'BODY');assert.deepEqual(errors,[]);
console.log(JSON.stringify({synchronizedReplay:'passed',nativeText:'passed',...result,errors},null,2));await browser.close();
