import {launchBrowser} from './browser.mjs';
import fs from 'node:fs';
import assert from 'node:assert/strict';
const dir='evidence/live-click/direct';fs.mkdirSync(dir,{recursive:true});
const browser=await launchBrowser();const page=await browser.newPage({viewport:{width:720,height:540},deviceScaleFactor:1});
await page.goto('http://127.0.0.1:5173/?clean');await page.waitForFunction(()=>window.sourceReplay);
await page.mouse.move(485,301);await page.waitForTimeout(1500);
// Read the actual rendered WebGL canvas immediately after each normal live frame.
// No frozen timeline, simulated clock, or reconstructed pixels are used here.
await page.evaluate(()=>{
  const {renderer}=window.__buttonRenderer,render=renderer.render.bind(renderer);
  window.liveFrames=[];let clicked=null;
  document.querySelector('#ripple-button').addEventListener('click',e=>{clicked=performance.now();window.trustedClick=e.isTrusted;},{once:true});
  renderer.render=function(...args){
    render(...args);const age=clicked===null?-1:(performance.now()-clicked)/1000;
    if((clicked===null&&window.liveFrames.length===0)||(age>=0&&age<.75)){
      window.liveFrames.push({age,scale:window.__buttonRenderer.surfaceGroup.scale.x,fontSize:parseFloat(getComputedStyle(document.querySelector('#ripple-button span')).fontSize),png:renderer.domElement.toDataURL('image/png')});
    }
    if(age>=.75)renderer.render=render;
  };
});
await page.waitForTimeout(100);await page.mouse.click(485,301);await page.waitForTimeout(1000);
const result=await page.evaluate(()=>({trusted:window.trustedClick,frames:window.liveFrames}));
for(const [i,f] of result.frames.entries()){fs.writeFileSync(`${dir}/frame-${String(i).padStart(3,'0')}.png`,Buffer.from(f.png.split(',')[1],'base64'));delete f.png;}
fs.writeFileSync(`${dir}/measurements.json`,JSON.stringify(result,null,2));
assert.ok(result.trusted);assert.ok(result.frames.filter(f=>f.age>=0&&f.age<.2).length>=5,'Need at least five genuine early live frames');assert.ok(Math.min(...result.frames.map(f=>f.scale))<.985);
console.log({trusted:result.trusted,frames:result.frames.length,earlyFrames:result.frames.filter(f=>f.age>=0&&f.age<.2).length,minimumScale:Math.min(...result.frames.map(f=>f.scale))});await browser.close();
