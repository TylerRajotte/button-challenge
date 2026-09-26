import cv2,json,numpy as np
from PIL import Image,ImageDraw
j=json.load(open('public/cursor-track.json'));ss=j['samples'];cap=cv2.VideoCapture('reference/source.mp4')
# Regular samples plus every unusually uncertain sample.
ids=sorted(set(list(range(0,len(ss),15))+sorted(range(len(ss)),key=lambda i:ss[i]['confidence'])[:30]))
w,h=280,135; sheet=Image.new('RGB',(w*7,h*((len(ids)+6)//7)), '#f4f4f4');d=ImageDraw.Draw(sheet)
for k,i in enumerate(ids):
 s=ss[i];cap.set(1,i);ok,f=cap.read();x=round(s['x']*2876/720);y=round(s['y']*4)
 crop=f[max(0,y-80):min(2160,y+150),max(0,x-180):min(2876,x+300)]
 cv2.circle(crop,(min(x,180),min(y,80)),9,(0,0,255),2)
 im=Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB));im.thumbnail((w,h-20));xy=(k%7*w,k//7*h);sheet.paste(im,xy);d.text((xy[0]+3,xy[1]+h-18),f'{i/60:.2f}s frame {i} conf {s["confidence"]:.2f}',fill='black')
sheet.save('evidence/cursor-tracking-contact-sheet.jpg',quality=90)
print(len(ids),sheet.size)
