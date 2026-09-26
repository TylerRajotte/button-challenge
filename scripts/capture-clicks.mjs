import {launchBrowser} from './browser.mjs';
import fs from 'node:fs';
const browser=await launchBrowser();const page=await browser.newPage({viewport:{width:720,height:540},deviceScaleFactor:1});
const errors=[];page.on('pageerror',e=>errors.push(e.message));
await page.goto('http://127.0.0.1:5173/?clean');await page.waitForFunction(()=>window.sourceReplay);
fs.mkdirSync('evidence/click-replay',{recursive:true});
const frames=[];
for(const start of [408,562,637,776])for(const delta of [-3,0,3,6,9,12,18,24,30,39])frames.push(start+delta);
for(const frame of frames){await page.evaluate(t=>window.sourceReplay.seek(t),frame/60);await page.waitForTimeout(60);await page.screenshot({path:`evidence/click-replay/implementation-${String(frame).padStart(4,'0')}.png`});}
fs.writeFileSync('evidence/click-replay/frames.json',JSON.stringify(frames));console.log({frames:frames.length,errors});await browser.close();
