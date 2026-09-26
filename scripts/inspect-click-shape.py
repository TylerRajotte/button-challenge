from pathlib import Path
import json,numpy as np
from scipy.optimize import least_squares
__file__=str(Path(__file__).parent/'fit-click-material.py');exec(Path(__file__).read_text().split('solutions=[]')[0])
rows=[]
for age in np.unique(ages):
 if not 0<age<=.5:continue
 ix=abs(ages[:,0,0]-age)<1e-5;v=mask[ix]&(hb[...,0]>25);d=dist[ix][v];target=(delta[...,0][ix]/np.maximum(hb[...,0],10))[v]
 def fun(p):
  radius,amp,front,back=p;off=d-radius;pred=amp*np.where(off>=0,np.exp(-off.clip(0)**2/(2*front*front)),np.exp(-((-off).clip(0)/back)**1.3));return pred-target
 opt=least_squares(fun,[16+720*age,1,10+30*age,15+100*age],bounds=([max(0,720*age-40),0,2,2],[720*age+50,3,100,200]));r,a,f,b=opt.x;rows.append({'age':float(age),'radius':r,'gainRelativeToHoverRadial':a,'aheadSigma':f,'behindWidth':b,'RMSE':float(np.sqrt(np.mean(opt.fun**2)))})
 print(round(float(age),4),np.round(opt.x,3),'rmse',round(float(np.sqrt(np.mean(opt.fun**2))),3),flush=True)
(root/'reference/analysis/click-independent-age-shape.json').write_text(json.dumps(rows,indent=2)+'\n')
