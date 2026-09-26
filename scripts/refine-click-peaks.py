"""Peak-weighted source-only refinement, separated from overall material MAE."""
from pathlib import Path
import json,numpy as np
from scipy.optimize import minimize
__file__=str(Path(__file__).parent/'fit-click-material-local-origin.py');exec(Path(__file__).read_text().split('solutions=[]')[0])
fit=j['clickResponseFit'];pars=np.array([fit[k] for k in ['initialRadius720Px','speed720PxPerSecond','aheadSigma720Px','aheadSigmaGrowth720PxPerSecond','behindWidth720Px','behindWidthGrowth720PxPerSecond','behindPower','decayPerSecond','growthSeconds']]);gains=np.array(fit['pulseGainRGB']);baseW=weight(pars);pred=baseW[...,None]*gains;lm=np.array([.2126,.7152,.0722]);targetL=res@lm;predL=pred@lm;clicks=[408,562,637,776];clickIx=np.array([clicks.index(r['clickFrame']) for r in rs]);rows=[]
for ci,click in enumerate(clicks):
 for age in [.016667,.033333,.05,.083333,.1,.15,.2,.25,.3]:
  ix=(clickIx==ci)&(abs(ages[:,0,0]-age)<1e-5);v=mask[ix]&(baseW[ix]>.65)
  if not v.sum():continue
  tv=targetL[ix][v];pv=predL[ix][v];ratio=np.dot(tv,pv)/np.dot(pv,pv);rows.append({'clickFrame':click,'age':age,'sourceLuma':float(tv.mean()),'predictedLuma':float(pv.mean()),'leastSquaresAmplitudeRatio':float(ratio),'samples':int(v.sum())});print(rows[-1],flush=True)
# Only source-backed crest locations get extra weight, retaining context around front.
positive=(targetL>5);fitmask=mask&positive&(ages<.4)
importance=1+4*np.clip(targetL/40,0,1)**2

def smoothstep(lo,hi,x):
 v=np.clip((x-lo)/(hi-lo),0,1);return v*v*(3-2*v)
def model(q):
 offsets=q[:4];boost=q[4];widthScale=q[5]
 a=(ages+offsets[clickIx,None,None]).clip(0);r0,v,f0,fs,b0,bs,power,decay,growth=pars
 off=dist-(r0+v*a);boostWindow=smoothstep(.005,.04,a)*(1-smoothstep(.15,.27,a));sigma=(f0+fs*a)*(1+(widthScale-1)*boostWindow);behind=(b0+bs*a)*(1+(widthScale-1)*boostWindow)
 band=np.where(off>=0,np.exp(-off.clip(0)**2/(2*sigma*sigma)),np.exp(-((-off).clip(0)/behind)**power));env=1-np.exp(-a/growth);return band*env*(1+boost*boostWindow)
def objective(q):
 w=model(q);e=(w[...,None]*gains)@lm-targetL;return np.sum((e*e*importance)[fitmask])/np.sum(importance[fitmask])
for fixedOffsets in [False,True]:
 bounds=[(-.04,.04)]*4+[(0,.5),(.7,1.1)]
 if fixedOffsets:bounds[:4]=[(0,0)]*4
 opt=minimize(objective,[0,0,0,0,.2,.95],method='L-BFGS-B',bounds=bounds,options={'maxiter':250,'ftol':1e-10});print('REFINEMENT',fixedOffsets,opt.fun,opt.x,flush=True)
 if not fixedOffsets:best=opt
q=best.x;newW=model(q);newPred=newW[...,None]*gains;errors=(newPred-res)[mask];oldErrors=(pred-res)[mask];print('MAE old/new',abs(oldErrors).mean(0),abs(errors).mean(0),flush=True)
for ci,click in enumerate(clicks):
 ix=clickIx==ci;peak=mask[ix]&(targetL[ix]>25)&(ages[ix]<.3);print('CLICKCREST',click,'old/newLumaMAE',abs((predL-targetL)[ix][peak]).mean(),abs((newPred@lm-targetL)[ix][peak]).mean(),flush=True)
result={'baseModel':'clickResponseFit','method':'148 native source frames, exact ordinary-hover subtraction; luminance residuals weighted toward source crests, positive pulse samples untilage.4. Keeps geometry timeline separate.','lightAgeAdvanceSeconds':{str(c):round(float(q[i]),6) for i,c in enumerate(clicks)},'boostAmount':round(float(q[4]),6),'earlyWidthMultiplier':round(float(q[5]),6),'boostWindow':'smoothstep(.005,.04,lightAge)*(1-smoothstep(.15,.27,lightAge))','formula':'lightAge=max(0,age+lightAgeAdvanceSeconds); use lightAge for base radius,widths,onset; multiply both widths by1+(earlyWidthMultiplier-1)*boostWindow; multiply excessRGB by1+boostAmount*boostWindow.','operationalMAE_RGB':abs(errors).mean(0).round(4).tolist(),'originalOperationalMAE_RGB':abs(oldErrors).mean(0).round(4).tolist(),'crestRatios':rows};(root/'reference/analysis/click-peak-refinement.json').write_text(json.dumps(result,indent=2)+'\n')

j["clickPeakRefinement"]=result
p.write_text(json.dumps(j,separators=(",",":"))+"\n")
