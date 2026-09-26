import cv2,json,numpy as np
from PIL import Image,ImageDraw
ss=json.load(open('public/button-motion.json'))['samples'];cs=json.load(open('public/cursor-track.json'))['samples'];cap=cv2.VideoCapture('reference/source.mp4');W,H=656,216

def frame(i):
 cap.set(1,i);ok,f=cap.read();q=np.array(ss[i]['quad'],np.float32);q[:,0]*=2876/720;q[:,1]*=4
 M=cv2.getPerspectiveTransform(q,np.array([[0,0],[W,0],[W,H],[0,H]],np.float32));return cv2.warpPerspective(f,M,(W,H)),M
base,mat=frame(561);p=np.array([cs[561]['x']*2876/720,cs[561]['y']*4,1]);p=mat@p;p=p[:2]/p[2];y,x=np.mgrid[:H,:W];rad=np.hypot(x-p[0],y-p[1])/2;valid=(x>5)&(x<W-5)&(y>8)&(y<H-8)&~((x>205)&(x<450)&(y>83)&(y<132))&(rad>20)
rows=[]
for i in range(562,596,2):
 im,_=frame(i);delta=im[:,:,2].astype(float)-base[:,:,2].astype(float);bs=np.arange(20,340,8);means=[np.median(delta[valid&(rad>=r)&(rad<r+8)]) if np.any(valid&(rad>=r)&(rad<r+8)) else 0 for r in bs];ri=int(np.argmax(means));rows.append((i/60,bs[ri]+4,means[ri],means))
print([(round(t,3),int(r),round(v,1)) for t,r,v,m in rows])
im=Image.new('RGB',(850,500),'white');d=ImageDraw.Draw(im)
for k,(t,r,v,m) in enumerate(rows):
 for n,z in enumerate(m):
  b=int(np.clip(z/80,0,1)*255);d.rectangle([100+n*18,35+k*24,118+n*18,59+k*24],fill=(255-b,255-b,255))
 d.text((4,39+k*24),f'{t:.3f}s',fill='black')
d.text((100,4),'Positive red-channel brightening vs radius from click (20..332 logical px)',fill='black');im.save('evidence/button-wave-propagation.png')
for t,r,v,m in rows:
 if abs(t-9.5)<.001 or abs(t-9.6)<.001:
  inds=np.where(np.array(m)>=v/2)[0];print('FWHM radial',t,bs[inds[0]],bs[inds[-1]]+8,'width',bs[inds[-1]]+8-bs[inds[0]])
