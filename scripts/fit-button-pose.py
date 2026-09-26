import json,numpy as np
from scipy.optimize import least_squares
from pathlib import Path
b=json.load(open('public/button-motion.json'))['samples'];c=json.load(open('public/cursor-track.json'))['samples'];ids=[i for i in range(100,1110,2) if b[i]['width']>324 and not any(abs(i-x)<30 for x in[411,568,645,782])];target=np.array([b[i]['quad'] for i in ids]);cursor=np.array([[c[i]['x'],c[i]['y']] for i in ids]);baseW=319.215;baseH=105.478;corners=np.array([[-baseW/2,-baseH/2],[baseW/2,-baseH/2],[baseW/2,baseH/2],[-baseW/2,baseH/2]])
# CSS transform convention: perspective * rotateX * rotateY * scale.
def project(p):
 cx,cy,ax,ay,f,scale=p
 tx=-(cursor[:,1]-270)/54*np.pi/180*ax;ty=(cursor[:,0]-360)/160*np.pi/180*ay
 X=corners[:,0][None,:]*scale;Y=corners[:,1][None,:]*scale
 x=np.cos(ty[:,None])*X;z=-np.sin(ty[:,None])*X
 y=np.cos(tx[:,None])*Y-np.sin(tx[:,None])*z
 z2=np.sin(tx[:,None])*Y+np.cos(tx[:,None])*z
 return np.stack([cx+x*f/(f-z2),cy+y*f/(f-z2)],axis=-1)
def residual(p):return (project(p)-target).ravel()
r=least_squares(residual,[360.1,269.76,9,9,860,1.03],bounds=([358,268,3,3,200,.99],[362,272,20,20,3000,1.07]),loss='soft_l1',f_scale=.5)
p=r.x;errors=project(p)-target
out={'model':'CSS perspective(f) rotateX(-normalizedY*angleX) rotateY(normalizedX*angleY) scale(hoverScale); transformations apply right to left; no rotateZ','normalization':{'xCenter':360,'xRadius':160,'yCenter':270,'yRadius':54},'baseWidth':baseW,'baseHeight':baseH,'centerX':float(p[0]),'centerY':float(p[1]),'angleXDegrees':float(p[2]),'angleYDegrees':float(p[3]),'perspective':float(p[4]),'hoverScale':float(p[5]),'fitFrames':len(ids),'coordinateRMSE':float(np.sqrt(np.mean(errors**2))),'cornerDistanceRMSE':float(np.sqrt(np.mean(np.sum(errors**2,axis=-1)))),'maxCornerDistance':float(np.sqrt(np.sum(errors**2,axis=-1)).max()),'note':'Least-squares fit to measured ideal blue-silhouette corner quads; cursor normalized to source logical canvas. Compression windows excluded. Rounded edges, threshold, and video cursor blur limit subpixel accuracy.'}
Path('public/button-pose-model.json').write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2))
# Compare hand-round parameters.
e=project([360.1,269.76,9,9,860,1.03])-target;print('requested guess RMSE',np.sqrt(np.mean(e**2)))
