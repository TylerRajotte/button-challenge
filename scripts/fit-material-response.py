"""Fit a stationary per-tile response to measured cursor-local illumination."""
import json,numpy as np,cv2
from pathlib import Path
root=Path(__file__).resolve().parents[1];path=root/'public/material-calibration.json';j=json.loads(path.read_text());rs=json.loads((root/'reference/analysis/material-dynamics.json').read_text());track=json.loads((root/'public/cursor-track.json').read_text())['samples'];base=np.array(j['idleCenterRGBMeasured']);valid=np.array(j['idleCenterObserved']);ox,oy=j['lattice']['originNativePx'];px,py=j['lattice']['pitchNativePx'];yy,xx=np.mgrid[0:13,0:40];cx=ox+(xx+.5)*px;cy=oy+(yy+.5)*py
clicks=[6.8,9.366667,10.616667,12.933333];records=[r for r in rs if 1.8<=r['t']<=18.4 and not any(c<=r['t']<=c+.65 for c in clicks)];values=np.array([r['centerRGB'] for r in records])-base;mask=np.array([r['valid'] for r in records]);n=mask.sum(0);n=np.maximum(n,1)
def fit(g):
 sg=(mask*g).sum(0);sgg=(mask*g*g).sum(0);sy=(mask[...,None]*values).sum(0);sgy=(mask[...,None]*g[...,None]*values).sum(0);den=np.maximum(n*sgg-sg*sg,1e-8)
 b=(n[...,None]*sgy-sg[...,None]*sy)/den[...,None];a=(sy-b*sg[...,None])/n[...,None];pred=a+g[...,None]*b;err=np.sqrt(np.mean(((pred-values)[mask])**2,axis=0));return err,a,b
best=None
for lag in np.arange(-.10,.201,1/60):
 ds=[]
 for r in records:
  s=track[min(max(round((r['t']-lag)*60),0),len(track)-1)];p=cv2.perspectiveTransform(np.array([[[s['x']*2876/720,s['y']*4]]],np.float32),np.array(r['sourceToIdleHomography']))[0,0];ds.append((cx-p[0])**2+(cy-p[1])**2)
 ds=np.array(ds)
 for sigma in np.arange(140,281,5):
  g=np.exp(-ds/(2*sigma*sigma));err,a,b=fit(g)
  if best is None or err[0]<best[0][0]:best=(err,sigma,lag,a,b)
err,sig,lag,a,b=best
print('BEST: RMSErgb sigmaNative lagSeconds',err,sig,lag)
# Masks identify inferred coefficients. Unknown label/corner coefficients use polynomial spatial fit.
x=(xx-19.5)/20;y=(yy-6)/6;X=np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
for z in [a,b]:
 z[~valid]=(X@np.linalg.lstsq(X[valid],z[valid],rcond=None)[0])[~valid]
print('base delta mean, std',a[valid].mean(0),a[valid].std(0));print('radial delta mean std',b[valid].mean(0),b[valid].std(0));print('b range',np.percentile(b[valid],[0,10,50,90,100],axis=0))
j['hoverResponseFit']={'formula':'RGB(t)=idleRGB + hoverAmount*(baseDeltaRGB + radialDeltaRGB*exp(-distanceNativePx^2/(2*sigmaNativePx^2))). Cursor is sampled at t-cursorLagSeconds and transformed into idle lattice coordinates. Empirical fit, not proof of original shader.','sigmaNativePx':int(sig),'sigma720Px':float(sig/4),'cursorLagSeconds':round(float(lag),6),'fitRMSE_RGB':err.round(4).tolist(),'fitTimeWindowSeconds':[1.8,18.4],'excludedClickWindows':[[c,c+.65] for c in clicks],'baseDeltaRGB':a.round(3).tolist(),'radialDeltaRGB':b.round(3).tolist(),'observed':valid.tolist()}
path.write_text(json.dumps(j,separators=(',',':'))+'\n')
