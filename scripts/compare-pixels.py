"""Compare timestamp-matched renders: explicit color and structure metrics, not whole-white-page scores."""
from pathlib import Path
import json
import numpy as np
from PIL import Image
root=Path(__file__).resolve().parents[1]
regions={'upper_face':[230,225,490,247], 'lower_face':[230,287,490,309], 'left_face':[210,241,290,297], 'right_face':[432,241,510,297], 'halo_top':[260,120,460,200], 'halo_left':[100,200,175,340], 'shadow':[230,326,490,352]}
results=[]
for time in [0,2,4,8,12,16,19]:
 source=root/f'evidence/replay/source-{time}.png'; impl=root/f'evidence/replay/implementation-{time}.png'
 if not source.exists() or not impl.exists():continue
 a=np.asarray(Image.open(source).convert('RGB'),dtype=float);b=np.asarray(Image.open(impl).convert('RGB'),dtype=float)
 row={'time':time,'regions':{}}
 for name,(x,y,X,Y) in regions.items():
  aa=a[y:Y,x:X];bb=b[y:Y,x:X]
  row['regions'][name]={'sourceRGB':aa.mean((0,1)).round(3).tolist(),'implementationRGB':bb.mean((0,1)).round(3).tolist(),'signedRGBDelta':(bb-aa).mean((0,1)).round(3).tolist(),'pixelMAE':round(float(abs(bb-aa).mean()),3),'RMSE':round(float(np.sqrt(((bb-aa)**2).mean())),3)}
 results.append(row)
out=root/'evidence/pixel-comparison.json';out.write_text(json.dumps(results,indent=2))
lines=['# Pixel comparisons','', 'Matched timestamps at 720 × 540; values are 8-bit sRGB. Face regions exclude text. These unregistered regional scores include geometry and random-tile differences; they do not certify perceptual identity.','', '| Time | Region | Source RGB | Recreation RGB | Signed RGB delta | Pixel MAE |','|---|---|---|---|---|---|']
for result in results:
 for name,r in result['regions'].items():lines.append(f"| {result['time']} | {name} | {r['sourceRGB']} | {r['implementationRGB']} | {r['signedRGBDelta']} | {r['pixelMAE']} |")
(root/'evidence/pixel-comparison.md').write_text('\n'.join(lines)+'\n')
print(json.dumps({'report':str(out),'meanFaceMAE':round(np.mean([r['regions'][k]['pixelMAE'] for r in results for k in ['upper_face','lower_face','left_face','right_face']]),3)},indent=2))
