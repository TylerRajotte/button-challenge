from pathlib import Path
from PIL import Image,ImageDraw
import json,numpy as np
folder=Path('evidence/click-replay'); metrics=[]
for start in [408,562,637,776]:
 frames=[start+d for d in [-3,0,3,6,9,12,18,24,30,39]]
 sheet=Image.new('RGB',(1000,10*180),'#f4f6fa');draw=ImageDraw.Draw(sheet)
 for i,n in enumerate(frames):
  a=Image.open(folder/f'source-{n:04d}.png').convert('RGB');b=Image.open(folder/f'implementation-{n:04d}.png').convert('RGB')
  for j,im in enumerate([a,b]):
   crop=im.crop((170,197,550,343)).resize((494,164));sheet.paste(crop,(j*500,i*180+16))
  draw.text((8,i*180+2),f'Source {n/60:.3f}s',fill='#18365a');draw.text((508,i*180+2),f'Recreation {n/60:.3f}s',fill='#18365a')
  ar=np.asarray(a,dtype=float)[222:317,210:510];br=np.asarray(b,dtype=float)[222:317,210:510];mask=np.ones(ar.shape[:2],bool);mask[34:62,85:216]=False
  metrics.append({'frame':n,'time':n/60,'faceMAE':float(abs(ar-br)[mask].mean()),'signedRGBDelta':(br-ar)[mask].mean(0).round(3).tolist()})
 sheet.save(folder/f'comparison-{start}.jpg',quality=95)
(folder/'pixel-metrics.json').write_text(json.dumps(metrics,indent=2))
print('Mean click-face MAE:',np.mean([r['faceMAE'] for r in metrics]))
