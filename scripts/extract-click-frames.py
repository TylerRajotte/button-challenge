import subprocess
from pathlib import Path
frames=[start+delta for start in [408,562,637,776] for delta in [-3,0,3,6,9,12,18,24,30,39]]
folder=Path('evidence/click-replay');folder.mkdir(exist_ok=True,parents=True)
select='+'.join(f'eq(n\\,{n})' for n in sorted(set(frames)))
subprocess.run(['ffmpeg','-threads','2','-hide_banner','-loglevel','error','-y','-i','reference/source.mp4','-vf',f'select={select},scale=720:540','-fps_mode','vfr','-threads','2',str(folder/'selected-%03d.png')],check=True)
for i,frame in enumerate(sorted(set(frames)),1):(folder/f'selected-{i:03d}.png').rename(folder/f'source-{frame:04d}.png')
