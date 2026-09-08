from pathlib import Path
import urllib.request,struct,zlib
folder=Path('work/tools');folder.mkdir(parents=True,exist_ok=True)
url='https://github.com/godotengine/godot-builds/releases/download/4.6.3-stable/Godot_v4.6.3-stable_export_templates.tpz'
def request_range(start,end):
 req=urllib.request.Request(url,headers={'Range':f'bytes={start}-{end}','User-Agent':'AsterGT-build/1.0','Accept-Encoding':'identity'})
 with urllib.request.urlopen(req,timeout=60) as r:
  if r.status!=206:raise RuntimeError(f'Range download unsupported: {r.status}')
  return r.read(),r.headers.get('Content-Range','')
size=1255918323
tail,_=request_range(size-65536,size-1)
i=tail.rfind(b'PK\x05\x06');e=struct.unpack_from('<4s4H2IH',tail,i)
cd_size,cd_offset=e[5],e[6]
cd,_=request_range(cd_offset,cd_offset+cd_size-1)
j=0;found=[]
while cd[j:j+4]==b'PK\x01\x02':
 h=struct.unpack_from('<4s6H3I5H2I',cd,j)
 name=cd[j+46:j+46+h[10]].decode()
 if 'windows_release_x86_64.exe' in name:found.append((name,h))
 j+=46+h[10]+h[11]+h[12]
for name,h in found:
 header,_=request_range(h[16],h[16]+29);lh=struct.unpack('<4s5H3I2H',header);start=h[16]+30+lh[9]+lh[10]
 payload,_=request_range(start,start+h[8]-1)
 raw=zlib.decompress(payload,-15) if h[4]==8 else payload
 assert len(raw)==h[9] and zlib.crc32(raw)&0xffffffff==h[7]
 target=folder/Path(name).name;target.write_bytes(raw);print('EXTRACTED',target,len(raw),'bytes; ZIP CRC verified')
if not found:raise RuntimeError('Windows release template not found')
