"""Cross-platform native bundle with the appropriate bundled app icon."""
from pathlib import Path
import subprocess
import sys
root=Path(__file__).resolve().parent.parent
icon=root/'glassbalance'/'assets'/('glassbalance_icon.ico' if sys.platform=='win32' else 'glassbalance_icon.png')
args=[sys.executable,'-m','PyInstaller','--noconfirm','--clean','--windowed','--onedir','--name','GlassBalance','--add-data',f'glassbalance/assets{":" if sys.platform!="win32" else ";"}glassbalance/assets','--icon',str(icon),'app.py']
subprocess.run(args,cwd=root,check=True)
