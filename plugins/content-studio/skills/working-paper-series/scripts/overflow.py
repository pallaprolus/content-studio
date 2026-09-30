"""Layout lint: text too close to its box edge, and labels sitting on boxes.

python scripts/overflow.py SERIES     (run render.py SERIES pages first; it writes SERIES/out/_series.html)
"""
import pathlib, sys
from playwright.sync_api import sync_playwright
html = pathlib.Path(sys.argv[1]) / 'out' / '_series.html'
with sync_playwright() as p:
    b = p.chromium.launch(); pg = b.new_page(viewport={'width': 1080, 'height': 1350})
    pg.goto(html.resolve().as_uri()); pg.wait_for_timeout(800)
    res = pg.evaluate("""()=>{const out=[];document.querySelectorAll('svg.wp-svg').forEach((svg,pi)=>{
      svg.querySelectorAll('.wp-item').forEach(it=>{const sh=it.querySelector('.shape'); if(!sh) return; const s=sh.getBBox();
        it.querySelectorAll('text').forEach(t=>{const r=t.getBBox(); const pad=Math.min(r.x-s.x, s.x+s.width-(r.x+r.width)); const vpad=Math.min(r.y-s.y, s.y+s.height-(r.y+r.height));
          if(pad<6||vpad<2) out.push([pi+1,it.id,t.textContent.slice(0,40),Math.round(pad),Math.round(vpad)]);});});
      const lbls=[...svg.querySelectorAll('.wp-elabel,.wp-actor text,.wp-note')].map(t=>[t,t.getBBox()]);
      const boxes=[...svg.querySelectorAll('.wp-item .shape')].map(s=>s.getBBox());
      lbls.forEach(([t,r])=>boxes.forEach(bx=>{ if(r.x<bx.x+bx.width&&r.x+r.width>bx.x&&r.y<bx.y+bx.height&&r.y+r.height>bx.y) out.push([pi+1,'LABEL-ON-BOX',t.textContent.slice(0,40),0,0]);}));
    });return out;}""")
    for r in res: print('page', r[0], r[1:])
    print(len(res), 'issues')
    b.close()
