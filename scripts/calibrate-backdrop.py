import json
import numpy as np
from PIL import Image
from scipy.ndimage import gaussian_filter1d
from scipy.optimize import minimize
im=np.asarray(Image.open('evidence/replay/source-0.png').convert('RGB'),float)
y,x=np.mgrid[:540,:720]; mask=np.ones((540,720),bool)
mask[195:365,175:545]=False;mask[305:345,550:590]=False
xx=x[mask]-360; yy=y[mask]; rgb=im[mask]
def fit(params,final=False):
 aspect,cy=params;r=np.sqrt((xx/aspect)**2+(yy-cy)**2);indices=np.minimum((r/3).astype(int),159)
 count=np.bincount(indices,minlength=160);profile=np.zeros((160,3))
 valid=count>0
 for c in range(3):
  raw=np.bincount(indices,weights=rgb[:,c],minlength=160)/np.maximum(count,1)
  profile[:,c]=np.interp(np.arange(160),np.flatnonzero(valid),raw[valid]);profile[:,c]=gaussian_filter1d(profile[:,c],2)
 prediction=np.stack([np.interp(r/3,np.arange(160)+.5,profile[:,c]) for c in range(3)],1)
 error=np.sqrt(((prediction-rgb)**2).mean())
 return (error,profile) if final else error
res=minimize(fit,[1.45,267],method='Nelder-Mead',options={'maxiter':100,'xatol':.01})
err,profile=fit(res.x,True);aspect,cy=res.x;radius=360
stops=[]
for r in range(0,361,6):
 color=[float(np.interp(r/3,np.arange(160)+.5,profile[:,c])) for c in range(3)]
 stops.append('rgb('+','.join(f'{a:.2f}' for a in color)+f') {r/radius*100:.3f}%')
css=f'radial-gradient(ellipse {radius*aspect:.3f}px {radius}px at 50% {cy+50:.3f}px, '+','.join(stops)+')'
open('src/backdrop.css','w').write('/* Fitted native CSS gradient; source background, masked to exclude the button and its contact shadow. */\n.halo {background:'+css+';}\n')
json.dump({'aspect':aspect,'centerY':cy,'maskedRGB_RMSE':err,'method':'Smooth elliptical CSS gradient fitted to background-only samples; button, shadow, cursor excluded.'},open('evidence/backdrop-calibration.json','w'),indent=2)
print(res.x,err)
