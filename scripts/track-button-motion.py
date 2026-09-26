#!/usr/bin/env python3
"""Measure source blue rounded-rectangle geometry at native video frame cadence."""
import cv2,json,numpy as np
from pathlib import Path

def intersect(h,v):
 # horizontal edge y=h[0]*x+h[1]; vertical edge x=v[0]*y+v[1]
 x=(v[0]*h[1]+v[1])/(1-v[0]*h[0]);return np.array([x,h[0]*x+h[1]])
cap=cv2.VideoCapture('reference/source.mp4');fps=cap.get(5);out=[];i=0
while True:
 ok,f=cap.read()
 if not ok:break
 # Half resolution retains quarter-logical-pixel edge positions.
 f=cv2.resize(f,(1438,1080),interpolation=cv2.INTER_AREA)
 b,g,r=cv2.split(f);mask=((b.astype(float)-r)>70)&(b>120)&(g<200)
 mask[:380]=False;mask[735:]=False;mask[:,:320]=False;mask[:,1160:]=False
 n,labels,stats,centroids=cv2.connectedComponentsWithStats(mask.astype('uint8'))
 ind=1+np.argmax(stats[1:,4]);m=labels==ind;ys,xs=np.where(m);x0,x1=xs.min(),xs.max();y0,y1=ys.min(),ys.max();w=x1-x0;h=y1-y0
 xx=np.arange(round(x0+w*.18),round(x1-w*.18));yt=np.array([np.flatnonzero(m[:,x])[0] for x in xx]);yb=np.array([np.flatnonzero(m[:,x])[-1] for x in xx]);top=np.polyfit(xx,yt,1);bottom=np.polyfit(xx,yb,1)
 yy=np.arange(round(y0+h*.3),round(y1-h*.3));xl=np.array([np.flatnonzero(m[y,:])[0] for y in yy]);xr=np.array([np.flatnonzero(m[y,:])[-1] for y in yy]);left=np.polyfit(yy,xl,1);right=np.polyfit(yy,xr,1)
 q=np.array([intersect(top,left),intersect(top,right),intersect(bottom,right),intersect(bottom,left)]);q[:,0]*=720/1438;q[:,1]/=2
 widths=[np.linalg.norm(q[1]-q[0]),np.linalg.norm(q[2]-q[3])];heights=[np.linalg.norm(q[3]-q[0]),np.linalg.norm(q[2]-q[1])];c=q.mean(axis=0)
 rot=np.degrees(np.arctan2(*(q[1]-q[0])[::-1]));botrot=np.degrees(np.arctan2(*(q[2]-q[3])[::-1]))
 sample={'t':round(i/fps,6),'cx':round(c[0],3),'cy':round(c[1],3),'width':round(np.mean(widths),3),'height':round(np.mean(heights),3),'rotation':round((rot+botrot)/2,4),'topWidth':round(widths[0],3),'bottomWidth':round(widths[1],3),'leftHeight':round(heights[0],3),'rightHeight':round(heights[1],3),'quad':np.round(q,3).tolist(),'maskArea':round(len(xs)*720/1438/2,3)}
 out.append(sample);i+=1
cap.release()
data={'source':'reference/source.mp4','fps':fps,'duration':len(out)/fps,'coordinateWidth':720,'coordinateHeight':540,'quadOrder':['topLeft','topRight','bottomRight','bottomLeft'],'method':'Blue silhouette segmentation; linear fit of central straight edge segments; intersections are unrounded ideal corner locations. Rotation in clockwise degrees.','samples':out}
Path('public/button-motion.json').write_text(json.dumps(data,separators=(',',':'))+'\n')
print(len(out))
for k in ['cx','cy','width','height','rotation']:print(k,min(x[k] for x in out),max(x[k] for x in out))
for i in range(0,len(out),30):print({k:out[i][k] for k in ['t','cx','cy','width','height','rotation']})
