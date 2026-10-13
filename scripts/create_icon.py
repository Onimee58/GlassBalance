"""Generate the bundled GlassBalance G + Wallet visual identity, no network needed."""
from pathlib import Path
import io
import cairosvg
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
ASSETS = ROOT / 'glassbalance' / 'assets'
ASSETS.mkdir(parents=True, exist_ok=True)
SVG = '''<svg xmlns="http://www.w3.org/2000/svg" width="512" height="512" viewBox="0 0 512 512">
<defs>
 <linearGradient id="bg" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#183a60"/><stop offset="0.55" stop-color="#0a2339"/><stop offset="1" stop-color="#063e42"/></linearGradient>
 <linearGradient id="g" x1="0" y1="0" x2="1" y2="1"><stop stop-color="#adfff0"/><stop offset="0.35" stop-color="#36dcce"/><stop offset="0.78" stop-color="#1186cb"/><stop offset="1" stop-color="#12559e"/></linearGradient>
 <linearGradient id="wallet" x1="0" y1="0" x2="0" y2="1"><stop stop-color="#166b8c"/><stop offset="1" stop-color="#07324d"/></linearGradient>
</defs>
<rect x="12" y="12" width="488" height="488" rx="112" fill="url(#bg)" stroke="#3dbaca" stroke-width="8"/>
<path d="M384 126 A167 167 0 1 0 306 413" stroke="url(#g)" stroke-width="70" fill="none" stroke-linecap="round"/>
<path d="M285 248 H395 V320 H320" fill="none" stroke="url(#g)" stroke-width="55" stroke-linejoin="round" stroke-linecap="round"/>
<rect x="206" y="302" width="223" height="135" rx="29" fill="#051a2c" opacity=".65"/>
<rect x="204" y="292" width="218" height="132" rx="25" fill="url(#wallet)" stroke="#6df0dc" stroke-width="8"/>
<rect x="201" y="267" width="166" height="45" rx="15" fill="#087ba4" stroke="#66d9dd" stroke-width="6"/>
<rect x="324" y="335" width="112" height="48" rx="17" fill="#064260" stroke="#68e9d9" stroke-width="5"/>
<circle cx="402" cy="359" r="10" fill="#6affdb"/>
</svg>'''
(ASSETS / 'glassbalance_icon.svg').write_text(SVG, encoding='utf-8')
raw=cairosvg.svg2png(bytestring=SVG.encode(),output_width=512,output_height=512)
icon=Image.open(io.BytesIO(raw)).convert('RGBA')
icon.save(ASSETS / 'glassbalance_icon.png',optimize=True)
icon.save(ASSETS / 'glassbalance_icon.ico',format='ICO',sizes=[(16,16),(24,24),(32,32),(48,48),(64,64),(128,128),(256,256)])
print('Created G + Wallet icon: SVG / PNG / Windows ICO')
if __name__=='__main__':
 pass
