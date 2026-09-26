"""Measure absolute blue seam floors independently of bright tile interiors."""
import json,cv2,numpy as np
from pathlib import Path
root=Path(__file__).resolve().parents[1];p=root/'public/material-calibration.json';j=json.loads(p.read_text());cap=cv2.VideoCapture(str(root/'reference/source.mp4'));ok,f=cap.read();f=cv2.cvtColor(f,cv2.COLOR_BGR2RGB);ox,oy=j['lattice']['originNativePx'];px,py=j['lattice']['pitchNativePx'];valid=np.array(j['idleCenterObserved']);floors=np.zeros((13,40,3));y,x=np.mgrid[0:13,0:40];X=np.stack([np.ones_like(x),x,y,x*x,x*y,y*y],-1)
for r in range(13):
 for c in range(40):
  vals=[]
  for k in [0,1]:
   xx=int(round(ox+(c+k)*px));yy=int(round(oy+(r+.5)*py));vals.append(f[yy-4:yy+5,xx-2:xx+3].mean(axis=0).min(axis=0))
   xx=int(round(ox+(c+.5)*px));yy=int(round(oy+(r+k)*py));vals.append(f[yy-2:yy+3,xx-4:xx+5].mean(axis=1).min(axis=0))
  floors[r,c]=np.median(vals,axis=0)
# Outer edge cells' perimeter includes background; mark inferred for seam only.
v=valid.copy();v[[0,-1],:]=False;v[:,[0,-1]]=False
smooth=X@np.linalg.lstsq(X[v],floors[v],rcond=None)[0];floors[~v]=smooth[~v]
j['idleSeamFloorRGB']=floors.round(3).tolist();j['idleSeamFloorObserved']=v.tolist();j['seamFloorMethod']='Median of four cell-edge blue seam floor RGB values; each edge minimum over +/-2 native px after 9 px along-edge averaging. Outer-edge, label and corner values are quadratically imputed.'
p.write_text(json.dumps(j,separators=(',',':'))+'\n')
print('Seam floor palette measured',v.sum(),'mean',floors[v].mean(0))
