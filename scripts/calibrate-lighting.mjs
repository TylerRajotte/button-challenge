import {launchBrowser} from './browser.mjs';
import fs from 'node:fs';
const browser=await launchBrowser();const page=await browser.newPage({viewport:{width:720,height:540},deviceScaleFactor:2});
await page.goto('http://127.0.0.1:5173/?clean');await page.waitForFunction(()=>window.__buttonRenderer);
const swatches=await page.evaluate(()=>{
  const {renderer,scene,camera,uniforms}=window.__buttonRenderer,gl=renderer.getContext();
  const values=[];
  for(const value of [0,.5,1]){uniforms.uCalibration.value=value;renderer.render(scene,camera);const pixels=new Uint8Array(4);gl.readPixels(160,150,1,1,gl.RGBA,gl.UNSIGNED_BYTE,pixels);values.push(Array.from(pixels).slice(0,3));}
  return values;
});
const linear=v=>(v/=255)<=.04045?v/12.92:((v+.055)/1.055)**2.4;
const floor=swatches[0].map(linear),gain=swatches[1].map((v,i)=>(linear(v)-floor[i])/.5);
const calibration={method:'Black and 50% linear-grey swatches rendered with the actual PBR material and scene lights; output converted from sRGB to linear before fitting.',swatches,linearFloor:floor,linearGain:gain};
fs.writeFileSync('public/lighting-calibration.json',JSON.stringify(calibration,null,2)+'\n');console.log(calibration);await browser.close();
