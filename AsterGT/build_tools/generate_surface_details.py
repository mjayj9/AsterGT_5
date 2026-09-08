from pathlib import Path
import numpy as np
from PIL import Image,ImageDraw,ImageFilter
r=Path('outputs/AsterGT/assets');rng=np.random.default_rng(514)
n=1024
noise=np.zeros((n,n))
for side,weight in [(8,.4),(32,.3),(128,.18),(512,.12)]:
 a=Image.fromarray((rng.random((side,side))*255).astype('uint8')).resize((n,n),Image.Resampling.BICUBIC)
 noise+=np.asarray(a)/255*weight
fine=rng.normal(0,.035,(n,n));h=np.clip(noise+fine,0,1)
for kind in ['asphalt','ground']:
 if kind=='asphalt':
  val=.29+(h-.5)*.22;colors=np.stack([val*.97,val,val*1.015],-1)
  speckles=rng.random((n,n));colors[speckles>.995]+=.10
 else:
  base=np.array([.31,.34,.23]);colors=base+(h[:,:,None]-.5)*np.array([.25,.26,.19]);colors+=fine[:,:,None]*.6
 Image.fromarray((np.clip(colors,0,1)*255).astype('uint8')).save(r/(kind+'.png'))
 dx=np.roll(h,1,1)-np.roll(h,-1,1);dy=np.roll(h,1,0)-np.roll(h,-1,0);normal=np.stack([dx*.8,dy*.8,np.ones_like(h)],-1);normal/=np.linalg.norm(normal,axis=2)[:,:,None]
 Image.fromarray(((normal*.5+.5)*255).astype('uint8')).save(r/(kind+'_normal.png'))
for typ in ['leaf','needle']:
 im=Image.new('RGBA',(256,256),(0,0,0,0));dr=ImageDraw.Draw(im)
 for k in range(135 if typ=='leaf' else 260):
  x,y=rng.uniform(14,242,2)
  if ((x-128)/120)**2+((y-128)/118)**2>1:continue
  green=int(rng.uniform(68,132));color=(int(green*.58),green,int(green*.40),255)
  if typ=='leaf':
   w=int(rng.uniform(7,19));hh=int(rng.uniform(5,13));dr.ellipse((x-w,y-hh,x+w,y+hh),fill=color);dr.line((x-w,y,x+w,y),fill=(int(green*.65),int(green*.86),int(green*.4),255),width=1)
  else:
   angle=rng.uniform(0,6.28);dr.line((x,y,x+np.cos(angle)*25,y+np.sin(angle)*25),fill=color,width=2)
 im.save(r/(typ+'_cluster.png'))
print('Generated detailed road/ground normals and foliage textures')
