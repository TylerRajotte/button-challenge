"""Measure cursor response of seam floors separately from tile faces."""
from pathlib import Path
import json,cv2,numpy as np
root=Path(__file__).resolve().parents[1];p=root/'public/material-calibration.json';j=json.loads(p.read_text());rs=json.loads((root/'reference/analysis/material-dynamics.json').read_text());cap=cv2.VideoCapture(str(root/'reference/source.mp4'));ox,oy=j['lattice']['originNativePx'];px,py=j['lattice']['pitchNativePx'];y,x=np.mgrid[0:13,0:40];cx=ox+(x+.5)*px;cy=oy+(y+.5)*py;valid=np.array(j['idleSeamFloorObserved']);base=np.array(j['idleSeamFloorRGB']);sigma=j['hoverResponseFit']['sigmaNativePx'];clicks=[6.8,9.366667,10.616667,12.933333]
# Both axes are retained to audit directional differences.

def measure(f):
 vertical=np.zeros((13,40,3));horizontal=vertical.copy()
 for r in range(13):
  for c in range(40):
   vv=[];hh=[]
   for k in [0,1]:
    xx=int(round(ox+(c+k)*px));yy=int(round(oy+(r+.5)*py));vv.append(f[yy-4:yy+5,xx-2:xx+3].mean(axis=0).min(axis=0))
    xx=int(round(ox+(c+.5)*px));yy=int(round(oy+(r+k)*py));hh.append(f[yy-2:yy+3,xx-4:xx+5].mean(axis=1).min(axis=0))
   vertical[r,c]=np.mean(vv,axis=0);horizontal[r,c]=np.mean(hh,axis=0)
 return vertical,horizontal

def profiles(f,orientation):
 cuts=[]
 for r in range(1,12):
  for c in range(2,38):
   if not valid[r,c] or not valid[r,c-1] or not valid[r-1,c]:continue
   if orientation=='vertical':
    sx=ox+c*px;sy=oy+(r+.5)*py
    cut=np.array([f[int(round(sy))-4:int(round(sy))+5,int(round(sx+d))].mean(axis=0) for d in range(-8,9)])
   else:
    sx=ox+(c+.5)*px;sy=oy+r*py
    cut=np.array([f[int(round(sy+d)),int(round(sx))-4:int(round(sx))+5].mean(axis=0) for d in range(-8,9)])
   cuts.append(cut)
 return np.array(cuts).mean(0)
cap.set(cv2.CAP_PROP_POS_MSEC,0);ok,f=cap.read();f=cv2.cvtColor(f,cv2.COLOR_BGR2RGB);v0,h0=measure(f);idleAxes=[v0,h0]
records=[r for r in rs if (1.8<=r['t']<=18.4 and not any(c<=r['t']<=c+.65 for c in clicks)) or r['t'] in [0,1,19.5]]
values=[];masks=[];gs=[];times=[];pf=[]
for i,r in enumerate(records):
 cap.set(cv2.CAP_PROP_POS_MSEC,r['t']*1000);ok,f=cap.read();f=cv2.cvtColor(f,cv2.COLOR_BGR2RGB);f=cv2.warpPerspective(f,np.array(r['sourceToIdleHomography']),(2876,2160));vv,hh=measure(f);values.append([vv,hh]);d=np.hypot(cx-r['cursorAlignedNative'][0],cy-r['cursorAlignedNative'][1]);masks.append(valid&np.array(r['valid'])&(d>100));gs.append(np.exp(-d*d/(2*sigma*sigma)));times.append(r['t'])
 if r['t'] in [0,1,2,3,6,12,18,19.5]:
  pf.append({'t':r['t'],'vertical':profiles(f,'vertical').round(3).tolist(),'horizontal':profiles(f,'horizontal').round(3).tolist()})
 if i%20==0:print('sample',i,len(records),flush=True)
vals=np.array(values);masks=np.array(masks);gs=np.array(gs);times=np.array(times);fitmask=masks.copy();fitmask[(times<1.8)|(times>18.4)]=False;n=np.maximum(fitmask.sum(0),1);sg=(fitmask*gs).sum(0);sgg=(fitmask*gs*gs).sum(0);den=np.maximum(n*sgg-sg*sg,1e-8)
X=np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
fits=[]
for axis in range(2):
 delta=vals[:,axis]-idleAxes[axis];sy=(fitmask[...,None]*delta).sum(0);sgy=(fitmask[...,None]*gs[...,None]*delta).sum(0);b=(n[...,None]*sgy-sg[...,None]*sy)/den[...,None];a=(sy-b*sg[...,None])/n[...,None];pred=idleAxes[axis]+a+gs[...,None]*b;error=(pred-vals[:,axis])[fitmask];mae=np.abs(error).mean(0);rmse=np.sqrt((error*error).mean(0));
 for z in [a,b]:z[~valid]=(X@np.linalg.lstsq(X[valid],z[valid],rcond=None)[0])[~valid]
 idle=idleAxes[axis].copy();idle[~valid]=(X@np.linalg.lstsq(X[valid],idle[valid],rcond=None)[0])[~valid]
 fits.append({'orientation':['vertical','horizontal'][axis],'idleFloorRGB':idle.round(3).tolist(),'baseDeltaRGB':a.round(3).tolist(),'radialDeltaRGB':b.round(3).tolist(),'fitMAE_RGB':mae.round(4).tolist(),'fitRMSE_RGB':rmse.round(4).tolist(),'meanBaseDeltaRGB':a[valid].mean(0).round(4).tolist(),'meanRadialDeltaRGB':b[valid].mean(0).round(4).tolist()})
 print('AXIS',axis,'MAE',mae,'RMSE',rmse,'MEANBASE',a[valid].mean(0),'MEANRAD',b[valid].mean(0),flush=True)
# Combined floor uses mean directionalfloor. This differs slightly from prior median4edge palette.
a=(np.array(fits[0]['baseDeltaRGB'])+np.array(fits[1]['baseDeltaRGB']))/2;b=(np.array(fits[0]['radialDeltaRGB'])+np.array(fits[1]['radialDeltaRGB']))/2;idle=(np.array(fits[0]['idleFloorRGB'])+np.array(fits[1]['idleFloorRGB']))/2
pred=idle+a+gs[...,None]*b;actual=vals.mean(axis=1);error=(pred-actual)[fitmask];mae=np.abs(error).mean(0);rmse=np.sqrt((error*error).mean(0))
fit={'method':'Average of left/right/top/bottom seam minima; each edge min over5px across seam after averaging9px along seam. Source frames transformed to firstframe via homography. RGBs are decoded sRGB0..255, not linear light.','formula':'idleFloorRGB + hoverAmount*(baseDeltaRGB + radialDeltaRGB*exp(-distanceNativePx^2/(2*sigmaNativePx^2)))','sigmaNativePx':sigma,'sigma720Px':sigma/4,'idleFloorRGB':idle.round(3).tolist(),'baseDeltaRGB':a.round(3).tolist(),'radialDeltaRGB':b.round(3).tolist(),'observed':valid.tolist(),'fitMAE_RGB':mae.round(4).tolist(),'fitRMSE_RGB':rmse.round(4).tolist(),'meanBaseDeltaRGB':a[valid].mean(0).round(4).tolist(),'meanRadialDeltaRGB':b[valid].mean(0).round(4).tolist(),'directionalFits':fits,'seamOffsetNativePx':list(range(-8,9)),'stateProfiles':pf}
j['hoverSeamResponseFit']=fit;p.write_text(json.dumps(j,separators=(',',':'))+'\n');(root/'reference/analysis/seam-dynamics.json').write_text(json.dumps({'times':times.tolist(),'values':vals.round(3).tolist(),'valid':masks.tolist(),'gaussianWeight':gs.round(6).tolist()},separators=(',',':'))+'\n');print('COMBINED MAE',mae,'RMSE',rmse,flush=True)
