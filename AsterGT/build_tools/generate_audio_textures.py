from pathlib import Path
import math, random, wave, struct
from PIL import Image
p=Path(__file__).resolve().parents[1]
def write(name,s):f=p/name;f.parent.mkdir(parents=True,exist_ok=True);f.write_text(s.strip()+'\n',encoding='utf-8')
random.seed(26)
for typ in ['asphalt','ground','paint_normal']:
 im=Image.new('RGB',(256,256));px=im.load()
 for y in range(256):
  for x in range(256):
   n=random.random()
   if typ=='asphalt':v=int(99+n*30);px[x,y]=(v,v+1,v+2)
   elif typ=='ground':v=int(86+n*56);px[x,y]=(v,int(v*.98),int(v*.83))
   else:px[x,y]=(128+random.randint(-2,2),128+random.randint(-2,2),255)
 im.save(p/'assets'/f'{typ}.png')
for name,rpm in [('idle',850),('low',1800),('mid',3600),('high',6500),('wind',0),('tire',0),('rain',0),('impact',0),('shift',0),('horn',0)]:
 rate=22050;n=rate*2 if rpm or name in ['wind','tire','rain','horn'] else rate//3
 freq=round(rpm/60*4*2)/2
 samples=[];smooth=0
 for i in range(n):
  t=i/rate;noise=random.uniform(-1,1);smooth=smooth*.91+noise*.09
  if rpm:
   v=sum(math.sin(2*math.pi*freq*k*t+math.sin(2*math.pi*13*t)*.025)/(k**1.3) for k in range(1,9))*.28
   v+=math.sin(2*math.pi*(freq/2)*t)*.1
  elif name=='wind':v=smooth*.7
  elif name=='rain':v=noise*.12+smooth*.4
  elif name=='tire':v=noise*.22+math.sin(2*math.pi*1100*t+noise*.4)*.10
  elif name=='horn':v=(math.sin(2*math.pi*420*t)+math.sin(2*math.pi*510*t))*.2
  elif name=='impact':v=(smooth+math.sin(2*math.pi*65*t)*.7)*math.exp(-t*22)
  else:v=noise*math.exp(-t*75)*.7+math.sin(2*math.pi*80*t)*math.exp(-t*22)*.25
  samples.append(int(max(-.95,min(.95,v))*32767))
 with wave.open(str(p/'assets'/f'{name}.wav'),'wb') as w:w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(struct.pack('<'+'h'*n,*samples))

import shutil
shutil.copy(p/'assets/wind.wav',p/'assets/roll.wav')
