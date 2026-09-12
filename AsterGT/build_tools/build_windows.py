"""Import and export only; no driving tests or demonstration capture."""
from pathlib import Path
import argparse, subprocess
root=Path(__file__).resolve().parents[1]
parser=argparse.ArgumentParser();parser.add_argument('--godot',required=True);args=parser.parse_args()
output=root.parent/'Windows-v4'/'AsterGT-v4.exe';output.parent.mkdir(exist_ok=True)
subprocess.run([args.godot,'--headless','--path',str(root),'--editor','--import','--quit'],check=True)
subprocess.run([args.godot,'--headless','--path',str(root),'--export-release','Windows Desktop',str(output)],check=True)
print(output)
