#!/usr/bin/env python3
"""Extract custom-arrow tip from the supplied 60fps reference video.
Dependencies: opencv-python-headless, numpy. Run from repository root.
The cursor mask is derived from a sharp, isolated arrow in source frame zero.
"""
import argparse, json, pathlib
import cv2
import numpy as np

def run(source, output):
    cap = cv2.VideoCapture(str(source))
    fps=cap.get(cv2.CAP_PROP_FPS); count=int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    width=int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); height=int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    ok,first=cap.read()
    assert ok and (width,height)==(2876,2160), 'Template coordinates are for the supplied source.'
    half=cv2.resize(first,(1438,1080),interpolation=cv2.INTER_AREA)
    gray=cv2.cvtColor(half,cv2.COLOR_BGR2GRAY)
    template=gray[629:663,1119:1155]
    outline=(template<120).astype(np.uint8)*255
    contours,_=cv2.findContours(outline,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_SIMPLE)
    mask=np.zeros_like(template);cv2.drawContours(mask,contours,-1,255,-1)
    # The visible upper-left tip is 3.5,3.5 half-resolution pixels inside the crop.
    tip=(3.5,3.5)
    cap.set(cv2.CAP_PROP_POS_FRAMES,0)
    samples=[]
    templates=[]
    for scale in [0.72,0.78,0.84,0.9,0.96,1.0,1.06,1.12]:
        size=(round(template.shape[1]*scale),round(template.shape[0]*scale))
        templates.append((scale,cv2.resize(template,size,interpolation=cv2.INTER_AREA),cv2.resize(mask,size,interpolation=cv2.INTER_NEAREST)))
    prev=(1122.5,632.5)
    for i in range(count):
        ok,frame=cap.read()
        if not ok:break
        small=cv2.resize(frame,(1438,1080),interpolation=cv2.INTER_AREA)
        g=cv2.cvtColor(small,cv2.COLOR_BGR2GRAY)
        # Motion stays below this 60fps radius. Constrain to the previous neighborhood
        # so neither changing mosaic tiles nor the white label can steal the match.
        left=max(310,round(prev[0]-80));top=max(390,round(prev[1]-80))
        right=min(1210,round(prev[0]+115));bottom=min(735,round(prev[1]+115))
        roi=g[top:bottom,left:right]
        best=None
        for scale,t,m in templates:
            result=cv2.matchTemplate(roi,t,cv2.TM_SQDIFF_NORMED,mask=m)
            err,_,p,_=cv2.minMaxLoc(result)
            if best is None or err<best[0]:best=(err,p,scale)
        err,p,scale=best
        prev=(p[0]+left+tip[0]*scale,p[1]+top+tip[1]*scale)
        x=prev[0]*720/1438;y=prev[1]/2
        samples.append({'t':round(i/fps,6),'x':round(x,3),'y':round(y,3),'confidence':round(max(0,1-err),4),'cursorScale':scale})
    cap.release()
    # Matching a sharp template to motion blur underestimates the visible arrow size.
    # Keep raw matcher scale for audit, but use shrink only while the tip is still.
    for i,sample in enumerate(samples):
        lo=samples[max(0,i-3)];hi=samples[min(len(samples)-1,i+3)]
        span=max(1,min(len(samples)-1,i+3)-max(0,i-3))
        speed=np.hypot(hi['x']-lo['x'],hi['y']-lo['y'])/span
        sample['detectionScale']=sample['cursorScale']
        sample['cursorScale']=max(0.84,sample['detectionScale']) if speed<0.4 else 1.0
        if sample['cursorScale']>=0.96:sample['cursorScale']=1.0
    data={'source':str(source),'sourceWidth':width,'sourceHeight':height,'fps':fps,'frameCount':len(samples),'duration':round(count/fps,6),'coordinateWidth':720,'coordinateHeight':540,'anchor':'upper-left visible arrow tip','cursorScaleNote':'Rendering scale: raw detectionScale is used only during stationary intervals; movement blur otherwise biases scale too low. Shrink is visual evidence, not a verified pointerdown event.','method':'Temporal, multiscale masked custom-arrow template matching; source decoded at native 60 fps, half-resolution analysis','samples':samples}
    pathlib.Path(output).parent.mkdir(parents=True,exist_ok=True)
    pathlib.Path(output).write_text(json.dumps(data,separators=(',',':'))+'\n')
    pts=np.array([[s['x'],s['y']] for s in samples]); ds=np.linalg.norm(np.diff(pts,axis=0),axis=1)
    print(json.dumps({'frames':len(samples),'minConfidence':min(s['confidence'] for s in samples),'medianConfidence':float(np.median([s['confidence'] for s in samples])),'largestStep':float(ds.max()),'stepsOver30':np.where(ds>30)[0].tolist(),'lowestConfidence':sorted(range(len(samples)),key=lambda i:samples[i]['confidence'])[:30]},indent=2))

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--source',default='reference/source.mp4');p.add_argument('--output',default='public/cursor-track.json');a=p.parse_args();run(a.source,a.output)
