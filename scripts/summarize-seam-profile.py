"""Reduce measured seam RGB cross-sections to width/asymmetry statistics."""
from pathlib import Path
import json,numpy as np
root=Path(__file__).resolve().parents[1];p=root/'public/material-calibration.json';j=json.loads(p.read_text());fit=j['hoverSeamResponseFit'];xx=np.array(fit['seamOffsetNativePx']);profiles=[]
for state in fit['stateProfiles']:
 for axis in ['vertical','horizontal']:
  a=np.array(state[axis]);baseline=a[0]+(a[-1]-a[0])*(xx[:,None]+8)/16;depth=baseline[:,0]-a[:,0];depth/=depth.max();up=np.where(depth>=.5)[0];l=up[0];r=up[-1];left=np.interp(.5,[depth[l-1],depth[l]],[xx[l-1],xx[l]]);right=np.interp(.5,[depth[r+1],depth[r]],[xx[r+1],xx[r]]);centroid=(depth.clip(0)*xx).sum()/depth.clip(0).sum()
  profiles.append({'t':state['t'],'orientation':axis,'normalizedRedDepth':depth.round(4).tolist(),'FWHM_nativePx':round(float(right-left),4),'halfDepthLeftNativePx':round(float(left),4),'halfDepthRightNativePx':round(float(right),4),'depthCentroidNativePx':round(float(centroid),4)})
fit['widthMeasurements']=profiles;j['hoverSeamResponseFit']=fit;p.write_text(json.dumps(j,separators=(',',':'))+'\n')
(root/'reference/analysis/seam-width-measurements.json').write_text(json.dumps({'offsetNativePx':xx.tolist(),'profiles':profiles},indent=2)+'\n')
