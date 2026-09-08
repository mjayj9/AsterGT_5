from pathlib import Path
import imageio_ffmpeg, subprocess
from PIL import Image, ImageDraw
out=Path(r'C:\Users\admin\Documents\Codex\2026-09-08\fable-5-1-vs-fable-at-3\work\video')
out.mkdir(parents=True,exist_ok=True)
subprocess.run([imageio_ffmpeg.get_ffmpeg_exe(),'-hide_banner','-loglevel','error','-i',r'C:\Users\admin\Downloads\m2-res_290p.mp4','-vf','fps=1','-y',str(out/'frame_%03d.png')],check=True)
frames=sorted(out.glob('frame_*.png'))
for k in range(3):
    sheet=Image.new('RGB',(1708,5*320),(24,25,30)); d=ImageDraw.Draw(sheet)
    for j,f in enumerate(frames[k*10:(k+1)*10]):
        x=(j%2)*854;y=(j//2)*320
        sheet.paste(Image.open(f),(x,y+25)); d.text((x+10,y+5),f'{k*10+j:02d}s',fill='white')
    sheet.save(out/f'contact_{k+1}.jpg')
print('Decoded full video. Contact sheets:',len(frames),'frames')
