"""Native-frame source-only cell trajectories through all four click pulses."""
from pathlib import Path
import cv2,json,numpy as np
root=Path(__file__).resolve().parents[1];j=json.loads((root/'public/material-calibration.json').read_text());track=json.loads((root/'public/cursor-track.json').read_text())['samples'];cap=cv2.VideoCapture(str(root/'reference/source.mp4'));cap.set(cv2.CAP_PROP_POS_FRAMES,0);_,f=cap.read();f0=cv2.cvtColor(f,cv2.COLOR_BGR2RGB);g0=cv2.cvtColor(f0,cv2.COLOR_RGB2GRAY);mask=np.zeros(g0.shape,np.uint8);mask[885:1270,825:2050]=255;mask[1010:1150,1150:1740]=0;pts=cv2.goodFeaturesToTrack(g0,600,.02,16,mask=mask);ox,oy=j['lattice']['originNativePx'];px,py=j['lattice']['pitchNativePx'];yy,xx=np.mgrid[0:13,0:40];cx=ox+(xx+.5)*px;cy=oy+(yy+.5)*py;valid=np.array(j['idleCenterObserved']);records=[]
for clickFrame in [408,562,637,776]:
 for rel in list(range(-3,20))+list(range(20,47,2)):
  idx=clickFrame+rel;t=idx/60;cap.set(cv2.CAP_PROP_POS_FRAMES,idx);ok,f=cap.read();f=cv2.cvtColor(f,cv2.COLOR_BGR2RGB);g=cv2.cvtColor(f,cv2.COLOR_RGB2GRAY);q,st,err=cv2.calcOpticalFlowPyrLK(g0,g,pts,None,winSize=(31,31),maxLevel=4,criteria=(cv2.TERM_CRITERIA_EPS|cv2.TERM_CRITERIA_COUNT,40,.001));good=(st[:,0]>0)&(err[:,0]<40);h,inl=cv2.findHomography(q[good],pts[good],cv2.RANSAC,2.5);e=np.linalg.norm(cv2.perspectiveTransform(q[good],h)-pts[good],axis=2).flatten();e=float(np.median(e[inl[:,0]>0]));a=cv2.warpPerspective(f,h,(2876,2160));colors=np.empty((13,40,3))
  for r in range(13):
   for c in range(40):
    sx=int(round(cx[r,c]));sy=int(round(cy[r,c]));colors[r,c]=np.median(a[sy-8:sy+9,sx-8:sx+9].reshape(-1,3),axis=0)
  s=track[idx];cursor=cv2.perspectiveTransform(np.array([[[s['x']*2876/720,s['y']*4]]],np.float32),h)[0,0];s=track[clickFrame];origin=cv2.perspectiveTransform(np.array([[[s['x']*2876/720,s['y']*4]]],np.float32),h)[0,0];v=valid&(np.hypot(cx-cursor[0],cy-cursor[1])>95)
  records.append({'frame':idx,'t':t,'clickFrame':clickFrame,'age':rel/60,'alignmentErrorNativePx':e,'sourceToIdleHomography':h.tolist(),'cursorAlignedNative':cursor.tolist(),'clickOriginAlignedNative':origin.tolist(),'centerRGB':colors.tolist(),'valid':v.tolist()})
  if len(records)%20==0:print('extracted',len(records),'frame',idx,'err',e,flush=True)
(root/'reference/analysis/dense-click-material.json').write_text(json.dumps(records,separators=(',',':'))+'\n')
print('DONE',len(records),flush=True)
