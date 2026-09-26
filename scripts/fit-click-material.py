"""Source-only projected least-squares fit of traveling click light and per-tile gain."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import minimize
root=Path(__file__).resolve().parents[1];p=root/'public/material-calibration.json';j=json.loads(p.read_text());rs=json.loads((root/'reference/analysis/dense-click-material.json').read_text());ox,oy=j['lattice']['originNativePx'];px,py=j['lattice']['pitchNativePx'];yy,xx=np.mgrid[0:13,0:40];cx=ox+(xx+.5)*px;cy=oy+(yy+.5)*py;idle=np.array(j['idleCenterRGB']);ha=np.array(j['hoverResponseFit']['baseDeltaRGB']);hb=np.array(j['hoverResponseFit']['radialDeltaRGB']);sig=j['hoverResponseFit']['sigmaNativePx'];colors=np.array([r['centerRGB'] for r in rs]);masks=np.array([r['valid'] for r in rs]);ages=np.array([r['age'] for r in rs])[:,None,None];dist=[];hover=[]
for r in rs:
 cursor=r['cursorAlignedNative'];origin=r['clickOriginAlignedNative'];g=np.exp(-((cx-cursor[0])**2+(cy-cursor[1])**2)/(2*sig*sig));hover.append(idle+ha+hb*g[...,None]);dist.append(np.hypot(cx-origin[0],cy-origin[1])/4)
hover=np.array(hover);dist=np.array(dist);res=colors-hover;baseline=np.zeros_like(res)
for click in [408,562,637,776]:
 v=np.array([r['clickFrame']==click and r['age']<0 for r in rs]);correction=res[v].mean(0)
 for i,r in enumerate(rs):
  if r['clickFrame']==click:baseline[i]=correction
# Remove local pre-click prediction bias for identification; report errors both ways.
delta=res-baseline;mask=masks&(ages>=0);observed=np.array(j['idleCenterObserved']);flatmask=mask.reshape(-1);dy=delta[...,0]
# parameters: radius at age0, speed, sigmaAhead, widthBehind, powerBehind, ageDecay, growthSeconds
bounds=[(-35,35),(500,950),(3,35),(10,150),(.5,3),(0,4),(.001,.15)]

def weight(p):
 r0,v,front,back,power,decay,growth=p;offset=dist-(r0+v*ages)
 w=np.where(offset>=0,np.exp(-offset.clip(0)**2/(2*front*front)),np.exp(-((-offset).clip(0)/back)**power))
 return w*np.exp(-ages.clip(0)*decay)*(1-np.exp(-ages.clip(0)/growth))*(ages>=0)
def project(w,values):
 den=np.maximum((mask*w*w).sum(0),1e-9)
 gain=(mask*w*values).sum(0)/den
 pred=w*gain
 return gain,pred

def obj(p):
 w=weight(p);gain,pred=project(w,dy);e=(pred-dy)[mask];return np.mean(e*e)
solutions=[]
for seed in [[16,720,15,65,1,.55,.02],[0,720,10,60,1,1,.05],[-10,760,12,90,1,1,.03]]:
 opt=minimize(obj,seed,method='L-BFGS-B',bounds=bounds,options={'maxiter':250,'ftol':1e-10});solutions.append(opt);print('FIT',opt.fun,opt.x,opt.success,flush=True)
best=min(solutions,key=lambda o:o.fun);pars=best.x;w=weight(pars);gains=[];preds=[]
for channel in range(3):
 gain,pred=project(w,delta[...,channel]);gains.append(gain);preds.append(pred)
gains=np.stack(gains,-1);pred=np.stack(preds,-1);errors=(pred-delta)[mask];print('RMS corrected',np.sqrt((errors*errors).mean(0)),'MAE',np.abs(errors).mean(0),flush=True);print('gain mean/std',gains[observed].mean(0),gains[observed].std(0),flush=True)
# Compare old formula in identical source-centered material coordinates.
offset=dist-(16+720*ages);oldband=np.where(offset>=0,np.exp(-offset.clip(0)**2/(2*15**2)),np.exp(offset.clip(max=0)/65));oldpred=hb[None]*.8*oldband[...,None]*np.exp(-ages.clip(0)*.55)[...,None]*(ages>=0)[...,None];olderr=(oldpred-res)[mask]
print('OLD RMS',np.sqrt((olderr*olderr).mean(0)),'MAE',np.abs(olderr).mean(0),flush=True)
# Gain relationship with normal hover gains.
for c in range(3):print('gain channel',c,'correlation with hover',np.corrcoef(gains[observed,c],hb[observed,c])[0,1],'ratio',np.dot(gains[observed,c],hb[observed,c])/np.dot(hb[observed,c],hb[observed,c]),flush=True)
# Impute obscured cells using measured relationship to hover response.
for c in range(3):
 coeff=np.linalg.lstsq(np.c_[np.ones(observed.sum()),hb[observed,c]],gains[observed,c],rcond=None)[0];gains[~observed,c]=coeff[0]+coeff[1]*hb[~observed,c]
# Time-binned observed excess amplitude, and proposed vs optimized errors.
rows=[]
for age in np.unique(ages):
 if age<0:continue
 ix=(ages[:,0,0]==age);v=mask[ix];target=res[ix];optp=pred[ix]+baseline[ix];oldp=oldpred[ix];vv=v&(w[ix]>.35)
 rows.append({'age':round(float(age),6),'sourceMaxMeanRGB':target[vv].mean(0).round(3).tolist() if vv.sum() else None,'optimizedMAE_RGB':np.abs((optp-target)[v]).mean(0).round(3).tolist(),'oldMAE_RGB':np.abs((oldp-target)[v]).mean(0).round(3).tolist(),'meanEnvelope':float(np.exp(-age*pars[5])*(1-np.exp(-age/pars[6])))})
fit={'sourceOnly':True,'method':'Native148frame trajectories, firstframe grid registered separately for every frame; ordinary cursor glow subtracted and tiny pre-click residual removed separately per event/cell. Per-cell RGB pulse gains solved by least squares for each candidate front shape.','formula':'offset=distance720Px-(initialRadius720Px+speed720PxPerSecond*age); band=offset>=0?exp(-offset^2/(2*aheadSigma720Px^2)):exp(-((-offset)/behindWidth720Px)^behindPower); envelope=(1-exp(-age/growthSeconds))*exp(-age*decayPerSecond); excessRGB=pulseGainRGB*band*envelope; age>=0','initialRadius720Px':pars[0],'speed720PxPerSecond':pars[1],'aheadSigma720Px':pars[2],'behindWidth720Px':pars[3],'behindPower':pars[4],'decayPerSecond':pars[5],'growthSeconds':pars[6],'pulseGainRGB':gains.round(3).tolist(),'observed':observed.tolist(),'fitRMSE_RGB':np.sqrt((errors*errors).mean(0)).round(4).tolist(),'fitMAE_RGB':np.abs(errors).mean(0).round(4).tolist(),'oldFormulaRMSE_RGB':np.sqrt((olderr*olderr).mean(0)).round(4).tolist(),'oldFormulaMAE_RGB':np.abs(olderr).mean(0).round(4).tolist(),'ageStatistics':rows}
j['clickResponseFit']=fit;p.write_text(json.dumps(j,separators=(',',':'))+'\n');(root/'reference/analysis/click-response-fit.json').write_text(json.dumps(fit,indent=2)+'\n')
