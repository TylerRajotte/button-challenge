"""Check click-ring excess color after subtracting ordinary hover."""
import cv2,json,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[1];j=json.loads((root/'public/material-calibration.json').read_text());rs=json.loads((root/'reference/analysis/material-dynamics.json').read_text());track=json.loads((root/'public/cursor-track.json').read_text())['samples'];base=np.array(j['idleCenterRGB']);a=np.array(j['hoverResponseFit']['baseDeltaRGB']);b=np.array(j['hoverResponseFit']['radialDeltaRGB']);sig=j['hoverResponseFit']['sigmaNativePx'];ox,oy=j['lattice']['originNativePx'];px,py=j['lattice']['pitchNativePx'];y,x=np.mgrid[0:13,0:40];cx=ox+(x+.5)*px;cy=oy+(y+.5)*py;rows=[]
for click in [6.8,9.366667,10.616667,12.933333]:
 for r in rs:
  age=r['t']-click
  if not 0<age<.65:continue
  cur=np.array(r['centerRGB']);cursor=r['cursorAlignedNative'];g=np.exp(-((cx-cursor[0])**2+(cy-cursor[1])**2)/(2*sig*sig));res=cur-(base+a+b*g[...,None]);s=track[round(click*60)];origin=cv2.perspectiveTransform(np.array([[[s['x']*2876/720,s['y']*4]]],np.float32),np.array(r['sourceToIdleHomography']))[0,0];dist=np.hypot(cx-origin[0],cy-origin[1]);v=np.array(r['valid']);offset=dist-(64+2880*age)
  rows.extend(np.c_[offset[v]/4,res[v],np.full(v.sum(),age)].tolist())
arr=np.array(rows);summary=[]
for lo,hi in zip(range(-100,100,10),range(-90,110,10)):
 v=(arr[:,0]>=lo)&(arr[:,0]<hi)
 if v.sum():summary.append({'ringOffset720Range':[lo,hi],'meanExcessRGB':arr[v,1:4].mean(0).round(3).tolist(),'samples':int(v.sum())})
(root/'reference/analysis/click-material-profile.json').write_text(json.dumps({'assumedRingRadius720':'16 + 720*ageSeconds','summary':summary},indent=2)+'\n')
for x in summary:print(x)
