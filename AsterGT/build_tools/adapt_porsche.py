from pathlib import Path
import json,struct,math,copy,hashlib,argparse,zipfile
ROOT=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--source',required=True,help='Original .glb or user ZIP');options=parser.parse_args();source=Path(options.source)
if source.suffix.lower()=='.zip':
 with zipfile.ZipFile(source) as archive:data=archive.read('source/porsche_992_gt3_r.glb')
else:data=source.read_bytes()
n=struct.unpack_from('<I',data,12)[0];g=json.loads(data[20:20+n]);off=20+n;binary=data[off+8:off+8+struct.unpack_from('<I',data,off)[0]]
def ident():return [[float(i==j) for j in range(4)] for i in range(4)]
def mat(n):
 if 'matrix' in n:return [[n['matrix'][c*4+r] for c in range(4)] for r in range(4)]
 m=ident();q=n.get('rotation',[0,0,0,1]);x,y,z,w=q;s=n.get('scale',[1,1,1]);t=n.get('translation',[0,0,0])
 rot=[[1-2*(y*y+z*z),2*(x*y-z*w),2*(x*z+y*w)],[2*(x*y+z*w),1-2*(x*x+z*z),2*(y*z-x*w)],[2*(x*z-y*w),2*(y*z+x*w),1-2*(x*x+y*y)]]
 for r in range(3):
  for c in range(3):m[r][c]=rot[r][c]*s[c]
  m[r][3]=t[r]
 return m
def mul(a,b):return [[sum(a[r][k]*b[k][c] for k in range(4)) for c in range(4)] for r in range(4)]
def point(a,v):return [sum(a[r][c]*v[c] for c in range(3))+a[r][3] for r in range(3)]
def flatten(a):return [a[r][c] for c in range(4) for r in range(4)]
world={};ancestors={}
def walk(i,parent,path):
 no=g['nodes'][i];world[i]=mul(parent,mat(no));ancestors[i]=path+[no.get('name','')]
 for child in no.get('children',[]):walk(child,world[i],ancestors[i])
for i in g['scenes'][g.get('scene',0)]['nodes']:walk(i,ident(),[])
normal=ident();normal[0][0]=-100;normal[1][1]=100;normal[2][2]=-100;normal[1][3]=-.69
trans={i:mul(normal,m) for i,m in world.items()}
def bounds(i):
 pts=[]
 for primitive in g['meshes'][g['nodes'][i]['mesh']]['primitives']:
  a=g['accessors'][primitive['attributes']['POSITION']]
  for k in range(8):pts.append(point(trans[i],[a['max' if k&(1<<j) else 'min'][j] for j in range(3)]))
 return [[min(v[j] for v in pts) for j in range(3)],[max(v[j] for v in pts) for j in range(3)]]
centers={};radii={}
for tag in ['LF','RF','LR','RR']:
 idx=next(i for i,n in enumerate(g['nodes']) if n.get('name','').startswith('GEO_TIRE_'+tag+'_') and 'mesh' in n);lo,hi=bounds(idx);centers[tag]=[(a+b)/2 for a,b in zip(lo,hi)];radii[tag]=(hi[1]-lo[1])/2
mid=sum(c[2] for c in centers.values())/4
for i in trans:trans[i][2][3]-=mid
for c in centers.values():c[2]-=mid
idx=next(i for i,n in enumerate(g['nodes']) if 'STEER_PLASTIC_0' in n.get('name','') and 'mesh' in n);lo,hi=bounds(idx);steer=[(a+b)/2 for a,b in zip(lo,hi)]
nodes=[{'name':'Porsche992GT3R','children':[1],'extras':{'author':'MattDoesBlender','license':'CC-BY-NC-SA-4.0','changes':'Meter scale, wheel and steering pivots, separated calipers, redundant blur rims disabled, PBR parameter correction. Original mesh buffers and textures preserved.'}},{'name':'Body','children':[]}]
groups={'Body':1};pivots={'Body':[0,0,0]}
for tag in centers:
 for prefix in ['Wheel_','Caliper_']:
  name=prefix+tag;groups[name]=len(nodes);pivots[name]=centers[tag];nodes[0]['children'].append(len(nodes));nodes.append({'name':name,'translation':centers[tag],'children':[]})
groups['Steering']=len(nodes);pivots['Steering']=steer;nodes[0]['children'].append(len(nodes));nodes.append({'name':'Steering','translation':steer,'children':[]})
skipped=[];kept=[]
for i,nod in enumerate(g['nodes']):
 if 'mesh' not in nod:continue
 path=ancestors[i]
 if any('RIM_BLUR' in a or 'GEO_RIM_STATIC' in a for a in path):skipped.append(nod['name']);continue
 group='Body'
 for tag in centers:
  if 'WHEEL_'+tag in path or 'DISC_'+tag in path:group='Wheel_'+tag
  if 'SUSP_'+tag in path:group='Caliper_'+tag
 if 'STEER_HR' in path:group='Steering'
 m=copy.deepcopy(trans[i])
 for j in range(3):m[j][3]-=pivots[group][j]
 nodes[groups[group]]['children'].append(len(nodes));nodes.append({'name':nod['name'],'mesh':nod['mesh'],'matrix':flatten(m)});kept.append(i)
for material in g['materials']:
 name=material.get('name','').lower();p=material.setdefault('pbrMetallicRoughness',{})
 if 'carpaint' in name:p.update(metallicFactor=.55,roughnessFactor=.24)
 elif 'rim' in name or 'disc' in name:p.update(metallicFactor=.85,roughnessFactor=.3)
 elif 'carbon' in name:p.update(metallicFactor=.12,roughnessFactor=.38,baseColorFactor=[.09,.105,.12,1])
 elif 'tyre' in name:p.update(metallicFactor=0,roughnessFactor=.84)
 elif any(key in name for key in ['foam','alcantara','plastic','borrachas']) and 'baseColorTexture' not in p:p.update(metallicFactor=0,roughnessFactor=.92,baseColorFactor=[.035,.042,.045,1])
 elif any(key in name for key in ['electronics','mechanics','grid']) and 'baseColorTexture' not in p:p.update(metallicFactor=.25,roughnessFactor=.47,baseColorFactor=[.08,.09,.10,1])
 elif 'metal_parts' in name and 'baseColorTexture' not in p:p.update(metallicFactor=.75,roughnessFactor=.36,baseColorFactor=[.25,.26,.27,1])
 elif 'window' in name or 'windshield' in name:p.update(metallicFactor=.05,roughnessFactor=.09)
 elif 'glass' in name:p['roughnessFactor']=.10
 elif 'occlusion' in name:p['baseColorFactor']=[.035,.045,.05,1]
 material['doubleSided']=True
original_asset=copy.deepcopy(g['asset']);g['asset']['generator']='ASTER glTF pivot adapter; original '+g['asset'].get('generator','');g['nodes']=nodes;g['scenes']=[{'name':'Porsche992GT3R','nodes':[0]}];g['scene']=0
js=json.dumps(g,separators=(',',':')).encode();js+=b' '*((-len(js))%4);binary+=b'\x00'*((-len(binary))%4)
result=struct.pack('<4sII',b'glTF',2,12+8+len(js)+8+len(binary))+struct.pack('<I4s',len(js),b'JSON')+js+struct.pack('<I4s',len(binary),b'BIN\x00')+binary
out=ROOT/'assets/porsche_992_gt3_r.glb';out.write_bytes(result)
report={'source':original_asset,'source_sha256':hashlib.sha256(data).hexdigest(),'scale':100,'length_m':4.7678327,'width_m':2.049064,'centers':centers,'radii':radii,'wheelbase':abs(centers['LF'][2]-centers['LR'][2]),'steering_center':steer,'skipped_meshes':skipped,'kept_mesh_count':len(kept),'geometry_buffer_sha256':hashlib.sha256(binary).hexdigest(),'source_geometry_unchanged':True}
(ROOT/'assets/porsche_rig.json').write_text(json.dumps(report,indent=2),encoding='utf-8')
print(json.dumps(report,indent=2))
