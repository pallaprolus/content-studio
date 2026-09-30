"""Render a Working Paper series deterministically (frame-exact, no timers).

python render.py SERIES pages             -> SERIES/out/page-<n>-frame0.png for every page
python render.py SERIES stills T1 T2 ...  -> SERIES/out/still-<T>.png (T in seconds on the series timeline)
python render.py SERIES busy              -> SERIES/out/busy-<page>-<step>.png (middle of every story step)
python render.py SERIES video OUT.mp4     -> 30 fps H.264 High, BT.709, CRF 16, silent

SERIES is a folder holding pages.js (window.SERIES = {runhead}, window.PAGES = [...]) and working-paper/, the design
system fetched from its artifact (project/tokens.json, project/components/bundle.css and bundle.js, project/fonts/*).
Set WP_DS to use a design-system folder somewhere else.
Every run also writes SERIES/out/timing.json (total, page starts, page lengths) for tools/extract_frames.py.
"""
import json, os, sys, pathlib, subprocess
from playwright.sync_api import sync_playwright

HERE = pathlib.Path(__file__).resolve().parent
SERIES = pathlib.Path(sys.argv[1]).resolve()
DS = pathlib.Path(os.environ.get('WP_DS') or SERIES / 'working-paper').resolve()
if not (DS / 'tokens.json').exists():
    sys.exit(f'No design system at {DS}: fetch the Working Paper artifact\'s project/ files there first (see SKILL.md).')
OUT = SERIES / 'out'; OUT.mkdir(exist_ok=True)
FPS = 30

tok = json.loads((DS / 'tokens.json').read_text())
first = tok['color']['themes'][0]['id']
val = lambda v: v if isinstance(v, str) else v.get(first)
css = [':root{']
for t in tok['color']['tokens']: css.append(f"--{t['name']}:{val(t['value'])};")
for fam, d in tok.items():
    if fam in ('color', 'type', 'name', 'version', 'meta'): continue
    for t in d['tokens']: css.append(f"--{t['name']}:{val(t['value'])};")
for k, v in tok['type']['families'].items(): css.append(f"--font-{k}:{v};")
css.append('}')
for f in tok['type']['fonts']:
    css.append(f"@font-face{{font-family:'{f['family']}';src:url('{(DS / f['file']).as_uri()}');font-weight:{f['weight']};font-style:{f.get('style','normal')}}}")

EXTRA = """
html,body{margin:0;background:var(--desk);overflow:hidden;width:1080px;height:1350px}
#reel{position:absolute;left:0;top:0;width:1080px;will-change:transform}
#reel .wp-page{margin-bottom:28px}
.wp-figure.tall{top:330px;height:680px}
.wp-body{-webkit-hyphens:manual}
.is-deprecated .lbl{fill:var(--muted)}
.is-deprecated .shape{stroke-dasharray:4 3}
"""

SCRIPT = """
(function(){
  var reel=document.getElementById('reel'), clocks=[], starts=[], GAP=0.7, HOLD_END=2, PAGE=1350+28;
  PAGES.forEach(function(p,i){
    var d=document.createElement('div'); d.className='wp-page';
    var head = p.title ? '<h1 class="wp-title">'+p.title+'</h1>' : '<h2 class="wp-heading">'+p.heading+'</h2>';
    d.innerHTML='<div class="wp-runhead"><span>'+((window.SERIES&&SERIES.runhead)||'')+'</span><span>'+p.runR+'</span></div><div class="wp-rule"></div>'
      +'<div class="wp-head">'+head+'<p class="wp-dek">'+p.dek+'</p></div>'
      +'<div class="wp-figure'+(p.tall?' tall':'')+'"><svg class="wp-svg" viewBox="0 0 904 '+(p.tall?680:626)+'"></svg></div>'
      +'<p class="wp-caption">'+p.caption+'</p>'
      +'<div class="wp-body"><p><span class="runin">'+p.runin+'</span> '+p.body.replace(/\//g,'/<wbr>')+'</p></div>'
      +'<div class="wp-folio">'+(p.folio||i+1)+'</div><div class="wp-credit">made by @pallaprolu</div>';
    reel.appendChild(d);
    var svg=d.querySelector('svg'); p.build(svg);
  });
  PAGES.forEach(function(p,i){ clocks.push(WorkingPaper.clock(reel.querySelectorAll('svg.wp-svg')[i], p.spec)); });
  var t=0; clocks.forEach(function(c,i){ starts.push(t); t+=c.length+(i<clocks.length-1?GAP:HOLD_END); });
  window.TOTAL=t; window.STARTS=starts; window.LENGTHS=clocks.map(function(c){return c.length;});
  function eio(x){return x<.5?4*x*x*x:1-Math.pow(-2*x+2,3)/2;}
  window.frameAt=function(T){
    var i=0; while(i<clocks.length-1 && T>=starts[i+1]) i++;
    var local=T-starts[i], L=clocks[i].length, y=i*PAGE;
    if(local<L){ clocks[i].at(local); }
    else { clocks[i].at(L-0.001);
      if(i<clocks.length-1){ var k=eio(Math.min(1,(local-L)/GAP)); y+=k*PAGE; clocks[i+1].at(0); } }
    reel.style.transform='translateY('+(-y)+'px)';
  };
  window.frameAt(0);
})();
"""

def page_html():
    return f"""<!doctype html><html lang="en" data-theme="{first}"><head><meta charset="utf-8">
<style>{''.join(css)}</style><style>{(DS/'components/bundle.css').read_text()}</style><style>{EXTRA}</style>
<script>{(DS/'components/bundle.js').read_text()}</script>
<script>{(SERIES/'pages.js').read_text()}</script>
</head><body><div id="reel"></div><script>{SCRIPT}</script></body></html>"""

def open_page(p):
    b = p.chromium.launch()
    pg = b.new_page(viewport={'width': 1080, 'height': 1350}, device_scale_factor=1)
    errs = []
    pg.on('pageerror', lambda e: errs.append(str(e)))
    pg.on('console', lambda m: errs.append('console:' + m.text) if m.type == 'error' else None)
    f = OUT / '_series.html'; f.write_text(page_html())
    pg.goto(f.as_uri()); pg.wait_for_timeout(600)
    pg.evaluate('document.fonts.ready')
    return b, pg, errs

mode = sys.argv[2]
with sync_playwright() as p:
    b, pg, errs = open_page(p)
    total = pg.evaluate('TOTAL'); starts = pg.evaluate('STARTS'); lengths = pg.evaluate('LENGTHS')
    print('total', round(total, 2), 'starts', [round(x, 2) for x in starts], 'lengths', lengths)
    (OUT / 'timing.json').write_text(json.dumps({'total': total, 'starts': starts, 'lengths': lengths}))
    if mode == 'stills':
        for T in sys.argv[3:]:
            pg.evaluate(f'frameAt({float(T)})'); pg.screenshot(path=str(OUT / f'still-{T}.png'))
    elif mode == 'pages':
        for i, s in enumerate(starts):
            pg.evaluate(f'frameAt({s})'); pg.screenshot(path=str(OUT / f'page-{i+1}-frame0.png'))
    elif mode == 'busy':
        # busiest moment of each page: middle of each story step, loop 1
        for i, s in enumerate(starts):
            steps = int(round((lengths[i] - 1) / 2)) - 1
            for k in range(steps):
                T = s + 1 + k + 0.45
                pg.evaluate(f'frameAt({T})'); pg.screenshot(path=str(OUT / f'busy-{i+1}-{k+1}.png'))
    elif mode == 'video':
        out = sys.argv[3]
        n = int(total * FPS) + 1
        ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'image2pipe', '-framerate', str(FPS), '-c:v', 'png', '-i', '-',
                               '-vf', 'scale=out_color_matrix=bt709:out_range=tv', '-c:v', 'libx264', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-colorspace', 'bt709', '-color_primaries', 'bt709', '-color_trc', 'bt709', '-crf', '16', '-preset', 'medium',
                               '-movflags', '+faststart', out], stdin=subprocess.PIPE)
        for k in range(n):
            pg.evaluate(f'frameAt({k / FPS})')
            ff.stdin.write(pg.screenshot(type='png'))
            if k % 300 == 0: print('frame', k, '/', n, flush=True)
        ff.stdin.close(); ff.wait()
        print('wrote', out)
    b.close()
print('errors:', errs or 'none')
