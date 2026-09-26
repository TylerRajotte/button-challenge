import json,cv2,numpy as np
from PIL import Image,ImageDraw
j=json.load(open('public/button-motion.json'));ss=j['samples'];w,h=1400,840;im=Image.new('RGB',(w,h),'white');d=ImageDraw.Draw(im)
for row,(key,color) in enumerate([('width','#174bb3'),('height','#7722a0'),('cx','#00805c'),('cy','#b35512'),('rotation','#a83030')]):
 vals=[s[key] for s in ss];low=min(vals);high=max(vals);lo=40+row*155;d.text((12,lo),f'{key}: {low:.3f} .. {high:.3f}',fill='black');d.line([(65,lo+125),(1370,lo+125)],fill='#aaa')
 pts=[(65+s['t']/19.7167*1300,lo+115-(s[key]-low)/(high-low)*95) for s in ss];d.line(pts,fill=color,width=2)
 for t in range(20):x=65+t/19.7167*1300;d.line([(x,lo+20),(x,lo+125)],fill='#dddddd');d.text((x,lo+127),str(t),fill='black')
 d.line(pts,fill=color,width=2)
im.save('evidence/button-motion-curves.png')
cap=cv2.VideoCapture('reference/source.mp4');times=[6.65,6.75,6.8,6.85,6.9,7.0,7.1,7.2,8.8,9,9.1,9.2,9.3,9.4,9.5,9.6,9.7,9.8,10.35,10.45,10.55,10.65,10.75,10.85,10.95,11.05,12.65,12.75,12.85,12.95,13.05,13.15,13.25,13.35]
thumbW,thumbH=540,220;sheet=Image.new('RGB',(thumbW*4,thumbH*((len(times)+3)//4)),'#eee');d=ImageDraw.Draw(sheet)
for k,t in enumerate(times):
 i=round(t*60);cap.set(1,i);ok,f=cap.read();crop=f[790:1400,680:2220];im=Image.fromarray(cv2.cvtColor(crop,cv2.COLOR_BGR2RGB));im.thumbnail((thumbW,thumbH-20));xy=(k%4*thumbW,k//4*thumbH);sheet.paste(im,xy);s=ss[i];d.text((xy[0]+3,xy[1]+thumbH-18),f'{t:.2f}s  W{s["width"]:.2f} H{s["height"]:.2f} R{s["rotation"]:.2f}',fill='black')
sheet.save('evidence/button-press-sequences.jpg',quality=95)
