import {asset} from './urls.js';
/** Playback of cursor measurements from the source film, in its 720 × 540 space. */
export async function createReplay({stage, apply, release}) {
  const response=await fetch(asset('cursor-track.json'));
  if(!response.ok) return null;
  const data=await response.json();
  const samples=data.samples;
  const clickData=await fetch(asset('source-clicks.json')).then(r=>r.json());
  if(!Array.isArray(samples)||!samples.length)return null;
  const duration=data.duration ?? data.durationSeconds ?? 19.716667;
  const cursor=document.createElement('div');cursor.className='virtual-cursor replay-cursor';cursor.hidden=true;
  cursor.innerHTML='<svg viewBox="0 0 22 24" width="16" height="18"><path d="M2 2 L7 20 L11 12 L20 8 Z" fill="white" stroke="#202327" stroke-width="1.35" stroke-linejoin="round"/></svg>';
  document.body.append(cursor);
  const video=document.querySelector('.comparison video');
  let active=false,playing=false,time=0,start=0;
  let control,readout;
  const touchCursor=document.querySelector('.virtual-cursor:not(.replay-cursor)');
  if(!video){
    const nav=document.createElement('nav');nav.className='demo-controls';nav.setAttribute('aria-label','Reference playback');
    nav.innerHTML='<button type="button" id="replay-motion">Replay source motion</button><a href="./?compare">Compare source</a><output aria-live="off"></output>';
    if(new URLSearchParams(location.search).has('clean'))nav.hidden=true;
    document.body.append(nav);control=nav.querySelector('button');readout=nav.querySelector('output');
    control.onclick=()=>{if(playing)stop();else play();};
  }else{
    control=document.querySelector('#play-reference');
    control.textContent='Play both';
    video.onplay=()=>{active=true;playing=true;cursor.hidden=false;control.textContent='Pause both';};
    video.onpause=()=>{playing=false;control.textContent='Play both';};
    video.addEventListener('seeked',()=>{active=true;time=video.currentTime;render(time,true);});
    video.addEventListener('ended',()=>{playing=false;control.textContent='Replay both';});
  }
  function interpolate(t){
    let lo=0,hi=samples.length-1;
    while(lo<hi){const mid=Math.ceil((lo+hi)/2);if(samples[mid].t<=t)lo=mid;else hi=mid-1;}
    const a=samples[lo],b=samples[Math.min(lo+1,samples.length-1)];
    const mix=b.t===a.t?0:Math.max(0,Math.min(1,(t-a.t)/(b.t-a.t)));
    return {x:a.x+(b.x-a.x)*mix,y:a.y+(b.y-a.y)*mix,cursorScale:(a.cursorScale??1)+((b.cursorScale??1)-(a.cursorScale??1))*mix};
  }
  function render(t,instant=false){
    const p=interpolate(t);
    cursor.hidden=false;if(touchCursor)touchCursor.hidden=true;
    const rect=stage.getBoundingClientRect(),scale=rect.width/720;
    cursor.style.transformOrigin='0 0';cursor.style.transform=`translate(${rect.left+(p.x-1.45*p.cursorScale)*scale}px,${rect.top+(p.y-1.5*p.cursorScale)*scale}px) scale(${p.cursorScale*scale})`;
    const clicks=clickData.events.filter(e=>t>=e.t&&t-e.t<1.25).map(e=>({...interpolate(e.t),t:e.t,strength:e.strength??1,profile:e.profile??2}));
    apply({...p,time:t,clicks,instant});
    if(readout)readout.value=`${t.toFixed(1)} / ${duration.toFixed(1)} s`;
  }
  function play(){active=true;playing=true;time=0;start=performance.now()/1000;cursor.hidden=false;if(control)control.textContent='Stop replay';render(0,true);}
  function stop(){active=false;playing=false;cursor.hidden=true;if(touchCursor)touchCursor.hidden=document.querySelector('.touchpad')?.hidden??true;if(video)video.pause();else control.textContent='Replay source motion';if(readout)readout.value='';release();}
  return {
    update(now){if(!active)return;if(video)time=video.currentTime;else if(playing)time=(now-start)%duration;render(time);},
    play,stop,
    seek(t){active=true;playing=false;time=Math.max(0,Math.min(duration,t));if(video)video.currentTime=time;render(time,true);},
    get state(){return {active,playing,time,duration,samples:samples.length};},
    pointAt:interpolate,
  };
}
