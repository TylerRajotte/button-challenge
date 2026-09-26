"""Measure source button material: numeric tile palette, lattice, seam profiles, dynamics.
No implementation screenshot is read. All colors are decoded source-video sRGB.
"""
from pathlib import Path
import cv2,json,numpy as np
ROOT=Path(__file__).resolve().parents[1]
OUT=ROOT/'reference/analysis'; OUT.mkdir(exist_ok=True)
cap=cv2.VideoCapture(str(ROOT/'reference/source.mp4'))
def frame(t):
 cap.set(cv2.CAP_PROP_POS_MSEC,t*1000); ok,bgr=cap.read()
 if not ok: raise ValueError(t)
 return cv2.cvtColor(bgr,cv2.COLOR_BGR2RGB)
f0=frame(0)
def peaks(a,offset):
 d=a-np.convolve(a,np.ones(11)/11,'same')
 p=np.array([i for i in range(6,len(a)-6) if d[i]==min(d[i-5:i+6]) and d[i]<-1])+offset
 return p
xp=peaks(f0[895:1010,850:2010].mean(axis=(0,2)),850)
yp=peaks(f0[890:1270,900:1100].mean(axis=(1,2)),890)
px,ox=np.polyfit(np.arange(len(xp))+2,xp,1)
py,oy=np.polyfit(np.arange(len(yp))+1,yp,1)
print('grid',ox,oy,px,py,flush=True)
# Register every selected frame to first-frame coordinates from stable grid corners.
g0=cv2.cvtColor(f0,cv2.COLOR_RGB2GRAY)
mask=np.zeros(g0.shape,np.uint8);mask[885:1270,825:2050]=255;mask[1010:1150,1150:1740]=0
pts=cv2.goodFeaturesToTrack(g0,600,.02,16,mask=mask)

def align(f):
 if np.array_equal(f,f0):return f,np.eye(3),0.
 g=cv2.cvtColor(f,cv2.COLOR_RGB2GRAY)
 p,st,err=cv2.calcOpticalFlowPyrLK(g0,g,pts,None,winSize=(31,31),maxLevel=4,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,.001))
 good=(st[:,0]>0)&(err[:,0]<35)
 h,inl=cv2.findHomography(p[good],pts[good],cv2.RANSAC,2.5)
 if h is None: return f,np.eye(3),999
 pred=cv2.perspectiveTransform(p[good],h)
 residual=np.linalg.norm(pred-pts[good],axis=2).flatten()
 return cv2.warpPerspective(f,h,(f.shape[1],f.shape[0])),h,float(np.median(residual[inl[:,0]>0]))

def sample(f):
 colors=[];valid=[]
 for row in range(13):
  cr=[]; vr=[]
  for col in range(40):
   x=int(round(ox+(col+.5)*px));y=int(round(oy+(row+.5)*py))
   a=f[y-8:y+9,x-8:x+9].reshape(-1,3)
   # White label, cursor, and clipped button corners are explicitly unobserved.
   good=(a[:,2].astype(float)-a[:,0]>70)&(a[:,0]<180)
   vr.append(bool(good.mean()>.9))
   cr.append(np.median(a[good],axis=0).tolist() if good.sum()>50 else [np.nan]*3)
  colors.append(cr);valid.append(vr)
 return np.array(colors),np.array(valid)
base,valid=sample(f0)
# Also reject strongly contaminated shadow/label regions, while retaining visible blue snippets.
valid[4:8,11:29]=False
# Fit quadratic smooth illumination and impute unobserved cells with the row's residual median.
yy,xx=np.mgrid[0:13,0:40];x=(xx-19.5)/20;y=(yy-6)/6
X=np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
coef=np.linalg.lstsq(X[valid],base[valid],rcond=None)[0];smooth=X@coef
palette=base.copy();palette[~valid]=smooth[~valid]
resid=base-smooth
# Full-center medians are slightly less anti-aliased than individual pixels; direct measured palette retained.
rows=[]
for r in range(13):rows.append({'row':r,'meanRGB':np.round(np.mean(base[r][valid[r]],axis=0),2).tolist(),'residualStdRGB':np.round(np.std(resid[r][valid[r]],axis=0),2).tolist()})
times=np.unique(np.r_[np.arange(0,19.71,1/6),[.5,1,1.2,1.4,1.5,2,3,6,8,12,18,19,19.5,19.7]])
track=json.loads((ROOT/'public/cursor-track.json').read_text())['samples']
records=[];aligned={0:f0}
for k,t in enumerate(times):
 f=frame(float(t));a,h,e=align(f); colors,v=sample(a)
 s=track[min(round(t*60),len(track)-1)]
 cursor=cv2.perspectiveTransform(np.array([[[s['x']*2876/720,s['y']*4]]],np.float32),h)[0,0]
 # Exclude all label locations and cursor cells from dynamic material fits.
 v &= valid
 dist=np.hypot(ox+(xx+.5)*px-cursor[0],oy+(yy+.5)*py-cursor[1]);v &= dist>75
 records.append({'t':round(float(t),6),'alignmentMedianErrorPx':round(e,4),'sourceToIdleHomography':h.tolist(),'cursorAlignedNative':cursor.tolist(),'centerRGB':np.nan_to_num(colors,nan=-1).round(2).tolist(),'valid':v.tolist()})
 if float(t) in [0,.5,1,1.5,2,3,6,8,12,18,19,19.5,19.7]:aligned[float(t)]=a
 if k%20==0:print('frame',k,len(times),'error',e,flush=True)
# Seam crosssections averaged in cells free from label and rounded mask. Subtract linear inter-center ramp.
profiles=[]
for t in [0,2,3,6,12,19.5]:
 a=aligned[t]
 for orientation in ['vertical','horizontal']:
  cuts=[]; ids=[]
  for r in range(1,12):
   for c in range(2,38):
    if not valid[r,c] or not valid[r,c-1] or not valid[max(0,r-1),c]:continue
    if orientation=='vertical':
     sx=ox+c*px;sy=oy+(r+.5)*py
     cut=np.array([a[int(round(sy))-4:int(round(sy))+5,int(round(sx+d))].mean(axis=0) for d in range(-12,13)])
    else:
     sx=ox+(c+.5)*px;sy=oy+r*py
     cut=np.array([a[int(round(sy+d)),int(round(sx))-4:int(round(sx))+5].mean(axis=0) for d in range(-12,13)])
    cuts.append(cut);ids.append([r,c])
  cuts=np.array(cuts)
  profiles.append({'t':t,'orientation':orientation,'offsetNativePx':list(range(-12,13)),'meanRGB':cuts.mean(axis=0).round(3).tolist(),'medianRGB':np.median(cuts,axis=0).round(3).tolist(),'sampleCount':len(cuts)})
# Individual near-hover patch crosssections, using frame2 cursor around col34,row5.
patches=[]
for t in [0,2,3,6,19.5]:
 a=aligned[t]
 for r,c in [(2,33),(3,35),(8,34),(2,6),(9,6),(9,20)]:
  sx=ox+c*px;sy=oy+(r+.5)*py
  cut=[a[int(round(sy))-4:int(round(sy))+5,int(round(sx+d))].mean(axis=0).round(2).tolist() for d in range(-16,17)]
  patches.append({'t':t,'row':r,'seamColumn':c,'offsetNativePx':list(range(-16,17)),'RGB':cut})
cal={'source':'reference/source.mp4','method':'Native decoded sRGB, cell center 17x17 median; label/corner cells imputed with quadratic spatial illumination. Numeric material values only; not an image texture.','sourceSize':[2876,2160],'lattice':{'originNativePx':[ox,oy],'pitchNativePx':[px,py],'origin720':[ox*720/2876,oy/4],'pitch720':[px*720/2876,py/4],'columns':40,'rows':13,'xSeamPeaksNative':xp.tolist(),'ySeamPeaksNative':yp.tolist()},'idleCenterRGB':palette.round(2).tolist(),'idleCenterRGBMeasured':np.nan_to_num(base,nan=-1).round(2).tolist(),'idleCenterObserved':valid.tolist(),'idleSmoothPolynomialCoefficients':coef.tolist(),'idleRowStatistics':rows,'seamProfiles':profiles,'localSeamProfiles':patches}
(ROOT/'public/material-calibration.json').write_text(json.dumps(cal,separators=(',',':'))+'\n')
(OUT/'material-dynamics.json').write_text(json.dumps(records,separators=(',',':'))+'\n')
# Concise machine-computed report data.
print('valid',valid.sum(),'color mean',base[valid].mean(0),'residualstd',resid[valid].std(0),flush=True)
for rec in records:
 if rec['t'] in [0,.5,1,1.5,2,3,6,12,19.5]:
  cur=np.array(rec['centerRGB']); v=np.array(rec['valid']);delta=cur-base
  print('time',rec['t'],'delta percentiles',np.percentile(delta[v], [10,50,90],axis=0),'error',rec['alignmentMedianErrorPx'],flush=True)
