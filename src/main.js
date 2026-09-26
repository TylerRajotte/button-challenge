import {asset,sourcePost} from './urls.js';
import * as THREE from 'three';
import './style.css';
import './backdrop.css';
import {createReplay} from './replay.js';
import {clickCompression} from './click-animation.js';
import {createSurfaceMaterial} from './surface-material.js';

const stage = document.querySelector('#stage');
const button = document.querySelector('#ripple-button');
// Keep native text outside every transformed/composited surface.
document.body.append(button);
const label=button.querySelector('span');
const wrap = document.querySelector('.button-wrap');
const shadow = document.querySelector('.contact-shadow');
const reduceMotion = matchMedia('(prefers-reduced-motion: reduce)').matches;
const pointer = new THREE.Vector2(0, 0);
const smoothPointer = new THREE.Vector2(0, 0);
const materialPointer=new THREE.Vector2();
const uniforms = {
  uTime: { value: 0 }, uPointer: { value: materialPointer }, uHover: { value: 0 },
  uClicks: { value: Array.from({length:4},()=>new THREE.Vector4(0,0,-100,0)) },
};
let hovering = false, pressing = false, hover = 0, press = 0;
let renderer, scene, camera, mesh, surfaceGroup, lastTime = 0, frozenTime = null;
let scale = 1;
let clickIndex=0;
const clickProfiles=[2,2,2,2];
uniforms.uClickProfiles={value:clickProfiles};
let replayController=null;
let stageRect=null;
function positionNativeButton(size=1){
  const r=stageRect??stage.getBoundingClientRect(), unit=scale*size;
  const snap=value=>Math.round(value*devicePixelRatio)/devicePixelRatio;
  button.style.left=`${snap(r.left+360*scale-160*unit)}px`;
  button.style.top=`${snap(r.top+270*scale-52*unit)}px`;
  button.style.width=`${snap(320*unit)}px`;
  button.style.height=`${snap(104*unit)}px`;
  button.style.borderRadius=`${32*unit}px`;
  label.style.fontSize=`${24*unit}px`;
  label.style.letterSpacing=`${-.05*unit}px`;
}
function resize() {
  const viewport = stage.parentElement;
  scale = document.body.classList.contains('compare')
    ? viewport.clientWidth / 720 : Math.min(innerWidth / 720, innerHeight / 540);
  stage.style.setProperty('--stage-scale', scale);
  renderer?.setPixelRatio(Math.min(Math.max(2,devicePixelRatio * scale),4));
  renderer?.setSize(370, 156, false);
  stageRect=stage.getBoundingClientRect();positionNativeButton();
}

// A continuous squircle boundary gives the soft corners in the source film.
function roundedShape(w, h, r) {
  const s = new THREE.Shape(), x = -w/2, y = -h/2, k=.78;
  s.moveTo(x+r,y);s.lineTo(x+w-r,y);
  s.bezierCurveTo(x+w-r+k*r,y,x+w,y+r-k*r,x+w,y+r);
  s.lineTo(x+w,y+h-r);s.bezierCurveTo(x+w,y+h-r+k*r,x+w-r+k*r,y+h,x+w-r,y+h);
  s.lineTo(x+r,y+h);s.bezierCurveTo(x+r-k*r,y+h,x,y+h-r+k*r,x,y+h-r);
  s.lineTo(x,y+r);s.bezierCurveTo(x,y+r-k*r,x+r-k*r,y,x+r,y);
  return s;
}

try {
  renderer = new THREE.WebGLRenderer({ canvas: document.querySelector('#surface'), alpha:true, antialias:true });
  renderer.setClearColor(0x000000, 0);
  renderer.outputColorSpace=THREE.SRGBColorSpace;
  renderer.toneMapping=THREE.NoToneMapping;
  scene=new THREE.Scene();
  camera=new THREE.PerspectiveCamera(THREE.MathUtils.radToDeg(2*Math.atan(78/900)),370/156,.1,2000);
  camera.position.set(0,0,900);
  surfaceGroup=new THREE.Group();scene.add(surfaceGroup);
  scene.add(new THREE.AmbientLight(0xffffff, 1.55));
  const key=new THREE.DirectionalLight(0xffffff, 1.45);key.position.set(-100,220,400);surfaceGroup.add(key);
  const fill=new THREE.DirectionalLight(0x9cbcff,.28);fill.position.set(200,-50,250);surfaceGroup.add(fill);
  const material=await createSurfaceMaterial(uniforms);
  const geometry=new THREE.ExtrudeGeometry(roundedShape(316,101.5,31),{depth:.5,bevelEnabled:true,bevelSegments:5,steps:1,bevelSize:2,bevelThickness:.25,curveSegments:24});
  mesh=new THREE.Mesh(geometry,material);mesh.position.z=-.75;surfaceGroup.add(mesh);
  window.__buttonRenderer={renderer,scene,camera,material,uniforms,surfaceGroup};
} catch(error) {
  document.documentElement.classList.add('no-webgl');
  document.querySelector('#fallback').hidden=false;
  document.querySelector('#fallback').textContent='WebGL is unavailable. Showing the simplified button.';
  console.error(error);
}

function toSurfacePoint(x,y,amount=hover,unit=1+amount*.03){
  const ax=-y/54*amount*Math.PI/20,ay=x/160*amount*Math.PI/20;
  const cx=Math.cos(ax),sx=Math.sin(ax),cy=Math.cos(ay),sy=Math.sin(ay),f=900;
  const a=unit*(cy-x*cx*sy/f),b=unit*x*sx/f;
  const c=unit*(sx*sy-y*cx*sy/f),d=unit*(cx+y*sx/f),det=a*d-b*c;
  return new THREE.Vector2((x*d-b*y)/det,-(a*y-c*x)/det);
}
function move(clientX,clientY){
  const r=stage.getBoundingClientRect();
  pointer.set((clientX-r.left)/scale-360,270-(clientY-r.top)/scale);
}
button.addEventListener('pointerenter',e=>{replayController?.stop();hovering=true;move(e.clientX,e.clientY);});
button.addEventListener('pointermove',e=>move(e.clientX,e.clientY));
button.addEventListener('pointerleave',()=>{hovering=false;pressing=false;});
button.addEventListener('pointerdown',e=>{pressing=true;hovering=true;move(e.clientX,e.clientY);button.setPointerCapture(e.pointerId);});
button.addEventListener('pointerup',e=>{pressing=false;if(e.pointerType!=='mouse')hovering=false;});
button.addEventListener('pointercancel',()=>{pressing=false;hovering=false;});
button.addEventListener('click',()=>{if(!reduceMotion){const q=toSurfacePoint(pointer.x,-pointer.y);uniforms.uClicks.value[clickIndex].set(q.x,q.y,uniforms.uTime.value,1);clickProfiles[clickIndex]=2;clickIndex=(clickIndex+1)%4;}pressing=false;button.dispatchEvent(new CustomEvent('activate',{bubbles:true}));});
button.addEventListener('keydown',e=>{if(e.key===' '||e.key==='Enter'){replayController?.stop();pressing=true;hovering=true;pointer.set(0,0);}});
button.addEventListener('keyup',()=>{pressing=false;});
button.addEventListener('blur',()=>{hovering=false;pressing=false;});

function draw(t){
  replayController?.update(t/1000);
  const dt=Math.min((t-lastTime)/1000,.05);lastTime=t;
  if(frozenTime===null&&!reduceMotion)uniforms.uTime.value=t/1000;
  hover=THREE.MathUtils.damp(hover,hovering?1:0,hovering?9:12,dt);
  if(Math.abs(hover-(hovering?1:0))<.0005)hover=hovering?1:0;
  press=THREE.MathUtils.damp(press,pressing?1:0,18,dt);
  if(Math.abs(press-(pressing?1:0))<.0005)press=pressing?1:0;
  smoothPointer.copy(pointer);
  uniforms.uHover.value=hover;
  const rx=reduceMotion?0:smoothPointer.y/54*hover*9;
  const ry=reduceMotion?0:smoothPointer.x/160*hover*9;
  const impulse=reduceMotion?0:Math.max(...uniforms.uClicks.value.map((c,i)=>clickCompression(uniforms.uTime.value-c.z,clickProfiles[i])));
  const size=(1+(reduceMotion?0:hover*.03))*(1-impulse)-press*.008;
  wrap.style.transform='none';
  surfaceGroup?.rotation.set(-THREE.MathUtils.degToRad(rx),THREE.MathUtils.degToRad(ry),0);
  surfaceGroup?.scale.setScalar(size);
  materialPointer.copy(toSurfacePoint(pointer.x,-pointer.y,hover,size));
  shadow.style.transform=`perspective(900px) rotateX(${rx}deg) rotateY(${ry}deg) scale(${size})`;
  positionNativeButton(size);
  renderer?.render(scene,camera);
  requestAnimationFrame(draw);
}
resize();addEventListener('resize',resize);addEventListener('scroll',()=>{stageRect=stage.getBoundingClientRect();positionNativeButton();},true);requestAnimationFrame(draw);
// Deterministic visual review hook; never samples or displays the reference in the rendered button.
window.buttonReview={
  set({x=0,y=0,active=false,time=1,down=false}={}){frozenTime=time;uniforms.uTime.value=time;pointer.set(x,y);smoothPointer.copy(pointer);hovering=active;hover=active?1:0;pressing=down;press=down?1:0;uniforms.uClicks.value.forEach(v=>v.z=-100);},
  resume(){frozenTime=null;},
  get state(){return {hovering,pressing,hover,pointer:pointer.toArray(),webgl:!!renderer,reducedMotion:reduceMotion};}
};

if(new URLSearchParams(location.search).has('compare')){
  document.body.classList.add('compare');
  document.querySelector('#app').innerHTML=`<section class="comparison"><header><h1>Pixel ripple button — comparison</h1><a href="./">Open interactive button</a></header><div class="compare-grid"><figure class="compare-panel"><figcaption>Raul Dronca · source video</figcaption><div class="compare-viewport"><video src="${asset('reference/source.mp4')}" muted playsinline preload="auto"></video></div></figure><figure class="compare-panel"><figcaption>Live WebGL recreation · move your pointer over the button</figcaption><div id="live-viewport" class="compare-viewport"></div></figure></div><div class="compare-controls"><button id="play-reference">Play source</button><input aria-label="Source video timeline" id="timeline" type="range" min="0" max="19.7" step=".0167" value="0"><output id="timestamp">0.00 s</output><a href="${asset('reference/contact-sheet.jpg')}" target="_blank">Extracted frames</a></div></section>`;
  document.querySelector('#live-viewport').append(stage);
  const video=document.querySelector('video'), slider=document.querySelector('#timeline');
  document.querySelector('#play-reference').onclick=()=>{if(video.paused)video.play();else video.pause();};
  video.onplay=()=>document.querySelector('#play-reference').textContent='Pause source';
  video.onpause=()=>document.querySelector('#play-reference').textContent='Play source';
  video.ontimeupdate=()=>{slider.value=video.currentTime;document.querySelector('#timestamp').value=`${video.currentTime.toFixed(2)} s`;};
  slider.oninput=()=>{video.pause();video.currentTime=+slider.value;};
  new ResizeObserver(resize).observe(document.querySelector('#live-viewport'));resize();
}

// An indirect pointer preserves mouse-style hovering on iPad and other touch screens.
if(!new URLSearchParams(location.search).has('clean')) {
  const cursor=document.createElement('div');cursor.className='virtual-cursor';cursor.hidden=true;
  cursor.innerHTML='<svg viewBox="0 0 22 24" width="22" height="24"><path d="M2 2 L7 20 L11 12 L20 8 Z" fill="white" stroke="#202327" stroke-width="1.35" stroke-linejoin="round"/></svg>';
  document.body.append(cursor);
  const toggle=document.createElement('button');toggle.className='touchpad-toggle';toggle.textContent='Use touchpad';toggle.setAttribute('aria-expanded','false');document.body.append(toggle);
  const pad=document.createElement('section');pad.id='virtual-touchpad';toggle.setAttribute('aria-controls',pad.id);pad.className='touchpad';pad.hidden=true;pad.setAttribute('aria-label','Virtual mouse touchpad');
  pad.innerHTML='<header><span>Virtual touchpad</span><button type="button" aria-label="Close touchpad">Close</button></header><div class="touchpad-surface" tabindex="0" role="application" aria-label="Move cursor. Drag to move, tap to click, or use arrow keys."><span>Slide to move · tap to click</span></div><footer><small>Cursor stays in place when you lift.</small><button type="button" id="virtual-click">Click</button></footer>';
  document.body.append(pad);
  let virtualX=360,virtualY=270,drag=null;
  function virtualMove(){
    const r=stage.getBoundingClientRect();
    cursor.style.transform=`translate(${r.left+virtualX*scale}px,${r.top+virtualY*scale}px) scale(${scale})`;
    const x=virtualX-360,y=270-virtualY;
    const inside=Math.abs(x)<160&&Math.abs(y)<52;
    hovering=inside;pointer.set(x,y);
  }
  function openPad(open){if(open)replayController?.stop();pad.hidden=!open;toggle.hidden=open;cursor.hidden=!open;toggle.setAttribute('aria-expanded',String(open));if(open)virtualMove();else hovering=false;}
  function virtualClick(){replayController?.stop();virtualMove();if(Math.abs(virtualX-360)<160&&Math.abs(virtualY-270)<52){pressing=true;button.click();setTimeout(()=>pressing=false,130);}}
  toggle.onclick=()=>openPad(true);pad.querySelector('header button').onclick=()=>openPad(false);
  pad.querySelector('#virtual-click').onclick=virtualClick;
  const surface=pad.querySelector('.touchpad-surface');
  surface.onpointerdown=e=>{replayController?.stop();e.preventDefault();surface.setPointerCapture(e.pointerId);drag={x:e.clientX,y:e.clientY,startX:e.clientX,startY:e.clientY,time:performance.now(),distance:0};surface.classList.add('is-dragging');};
  surface.onpointermove=e=>{if(!drag)return;const dx=e.clientX-drag.x,dy=e.clientY-drag.y;drag.distance+=Math.hypot(dx,dy);virtualX=THREE.MathUtils.clamp(virtualX+dx*1.5,145,575);virtualY=THREE.MathUtils.clamp(virtualY+dy*1.5,165,375);drag.x=e.clientX;drag.y=e.clientY;virtualMove();};
  surface.onpointerup=()=>{if(drag&&drag.distance<7&&performance.now()-drag.time<450)virtualClick();drag=null;surface.classList.remove('is-dragging');};
  surface.onpointercancel=()=>{drag=null;surface.classList.remove('is-dragging');pressing=false;};
  surface.onkeydown=e=>{const offsets={ArrowLeft:[-5,0],ArrowRight:[5,0],ArrowUp:[0,-5],ArrowDown:[0,5]};if(offsets[e.key]){replayController?.stop();e.preventDefault();virtualX+=offsets[e.key][0];virtualY+=offsets[e.key][1];virtualMove();}else if(e.key===' '||e.key==='Enter'){e.preventDefault();virtualClick();}};
  // Opt in on every device; opening the page never covers the demo with controls.
  addEventListener('resize',()=>{if(!pad.hidden&&!replayController?.state.active)virtualMove();});
  addEventListener('scroll',()=>{if(!pad.hidden&&!replayController?.state.active)virtualMove();},true);
}

createReplay({stage,
  apply({x,y,time,clicks,instant}){
    frozenTime=time;uniforms.uTime.value=reduceMotion?0:time;pointer.set(x-360,270-y);
    hovering=Math.abs(pointer.x)<165&&Math.abs(pointer.y)<56;pressing=false;
    if(instant){hover=hovering?1:0;smoothPointer.copy(pointer);}
    uniforms.uClicks.value.forEach((v,i)=>{const c=clicks?.[i];if(c&&!reduceMotion){const q=toSurfacePoint(c.x-360,c.y-270,1);v.set(q.x,q.y,c.t,c.strength);clickProfiles[i]=c.profile??2;}else v.set(0,0,-100,0);});
  },
  release(){frozenTime=null;hovering=false;uniforms.uClicks.value.forEach(v=>v.z=-100);}
}).then(controller=>{replayController=controller;window.sourceReplay=controller;}).catch(error=>console.warn('Source motion replay unavailable:',error));

if(!new URLSearchParams(location.search).has('clean')){
  const links=document.createElement('nav');links.className='site-links';links.setAttribute('aria-label','About this recreation');
  links.innerHTML=`<a href="${asset('transcript.html')}">Read the transcript</a><a href="${sourcePost}" target="_blank" rel="noopener noreferrer">Original post on X ↗</a>`;
  document.body.append(links);
}
