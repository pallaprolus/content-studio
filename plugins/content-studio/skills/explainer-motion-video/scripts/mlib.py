"""mlib — motion-explainer engine (pycairo + ffmpeg). Import in a per-video scenes file.
Every colour, font, size and type style comes from the chosen design system (tokens.json + font files):
run install(<system dir>) once per session, then configure(<system dir>, theme). No design values live here."""
import cairo, math, subprocess, sys, re, os, json

T, S, TS = {}, {}, {}        # colour roles (from ROLES), sizes in px (spacing/radius/stroke/size/frame), type styles
W, H, FPS = 1080, 1350, 30
HANDLE = ''                  # set by configure(..., handle=)
LOOK = 'infographic'         # 'infographic' (Living Infographic) or 'blueprint' (Blueprint Explainers)
FAM, FACES, ICON, HUES, SHADOW = {}, [], {}, [], {}
WEIGHTS = {'r': 400, 'm': 500, 's': 600, 'b': 700, 'x': 800}

# Which design-system token plays which role in the code. Only token NAMES here; values live in the system.
ROLES = {
    'Living Infographic': dict(BG='bg', CARD='card', INK='ink', MUTED='muted', A1='a1', A2='a2', A3='a3', OK='ok',
                               WARN='warn', BAD='bad', TEAL='hue-teal', INDIGO='hue-indigo', ONACC='on-accent',
                               RING='badge-ring', SHADOW='shadow-ink', GLOW='glow', DOTS='dots', HAIR='hairline'),
    'Blueprint Explainers': dict(BG='ground', CARD='panel', INK='ink', MUTED='muted', LINE='line', A1='line',
                                 A3='line', SIGNAL='signal', A2='signal', WARN='signal', OK='success', BAD='error',
                                 ONSIG='on-signal', ONACC='on-signal', GLOW='glow', GRID='grid-major',
                                 GRIDMIN='grid-minor'),
}

# ---------- design system ----------
def _rgba(v):
    """'#rrggbb' or 'rgba(r,g,b,a)' -> ((r, g, b), alpha)"""
    v = v.strip()
    if v.startswith('#'):
        h = v[1:]; return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)), 1.0
    n = [float(x) for x in re.findall(r'-?[\d.]+', v)]
    return (n[0] / 255, n[1] / 255, n[2] / 255), (n[3] if len(n) > 3 else 1.0)

def _num(v):
    return float(re.findall(r'-?[\d.]+', str(v))[0])

def _shadow(v):
    """box-shadow string -> [(dy, blur, (r, g, b), alpha), ...]; 'none' -> []"""
    out = []
    for part in re.split(r',(?![^(]*\))', v or 'none'):
        m = re.match(r'\s*(-?[\d.]+)(?:px)?\s+(-?[\d.]+)(?:px)?\s+([\d.]+)(?:px)?\s+(rgba?\([^)]*\)|#[0-9A-Fa-f]{6})', part)
        if m: rgb, al = _rgba(m.group(4)); out.append((float(m.group(2)), float(m.group(3)), rgb, al))
    return out

def install(ds):
    """Once per session: convert the system's font files to TTF in ~/.fonts, record face names and the icon map."""
    from fontTools.ttLib import TTFont
    tok = json.load(open(f'{ds}/tokens.json')); faces, icons = [], {}
    fonts_dir = os.path.expanduser('~/.fonts'); os.makedirs(fonts_dir, exist_ok=True)
    icon_fam = tok['type']['families'].get('icon', '').strip('"')
    for f in tok['type']['fonts']:
        ft = TTFont(os.path.join(ds, f['file'])); ft.flavor = None
        ft.save(os.path.join(fonts_dir, os.path.splitext(os.path.basename(f['file']))[0] + '.ttf'))
        nm = {r.nameID: r.toUnicode() for r in ft['name'].names if r.platformID == 3}
        faces.append([f['family'], int(str(f['weight']).split()[0]), f.get('style') == 'italic',
                      nm.get(1, f['family']), nm.get(2, '').startswith('Bold')])
        if f['family'] == icon_fam:
            icons = {name: cp for cp, name in ft.getBestCmap().items()}
    json.dump({'faces': faces, 'icons': icons}, open(f'{ds}/faces.json', 'w'))
    subprocess.run(['fc-cache', '-f'], check=True)
    print(f"installed {len(faces)} faces, {len(icons)} icons from {tok['name']}")

def configure(ds, theme=None, size=None, fps=30, handle=''):
    """Load a design system. theme: a theme id from its tokens (default: the first). size: (w, h) or the frame tokens.
    handle: the X handle drawn by chrome() and end_card() (x_handle from the plugin's config.json)."""
    global W, H, FPS, LOOK, HANDLE
    HANDLE = handle
    tok = json.load(open(f'{ds}/tokens.json')); name = tok['name']
    themes = [t['id'] for t in tok['color']['themes']]; theme = theme or themes[0]
    def pick(v): return v.get(theme, v[themes[0]]) if isinstance(v, dict) else v
    colors = {c['name']: pick(c['value']) for c in tok['color']['tokens']}
    T.clear()
    for role, tname in ROLES[name].items():
        T[role], T[role + 'A'] = _rgba(colors[tname])
    S.clear(); SHADOW.clear()
    for fam, d in tok.items():
        if fam in ('color', 'type') or not isinstance(d, dict) or 'tokens' not in d: continue
        for x in d['tokens']:
            v = pick(x['value'])
            if fam == 'shadow': SHADOW[x['name']] = _shadow(v)
            elif re.fullmatch(r'-?[\d.]+px', str(v)): S[x['name']] = _num(v)
    FAM.clear(); FAM.update({k: v.split(',')[0].strip().strip('"') for k, v in tok['type']['families'].items()})
    TS.clear()
    for g in tok['type']['groups']:
        for st in g['styles']:
            size_ = _num(st['fontSize']); lh = st.get('lineHeight', 1.2)
            TS[st['name']] = dict(size=size_, weight=int(_num(st.get('fontWeight', 400))),
                                  fam=st.get('family', g['family']),
                                  lh=_num(lh) if 'px' in str(lh) else size_ * float(lh),
                                  track=_num(st['letterSpacing']) if 'em' in str(st.get('letterSpacing', '')) else 0)
    meta = json.load(open(f'{ds}/faces.json'))
    FACES[:] = meta['faces']; ICON.clear(); ICON.update(meta['icons'])
    LOOK = 'blueprint' if name.startswith('Blueprint') else 'infographic'
    W, H = size or (int(S.get('frame-width', 1080)), int(S.get('frame-height', 1350))); FPS = fps
    HUES[:] = [T[k] for k in ('A1', 'A2', 'A3', 'OK', 'WARN', 'TEAL', 'BAD', 'INDIGO') if k in T]

def st(name):
    """a type style from the system: dict(size, weight, fam, lh, track)"""
    return TS[name]

# ---------- math / easing ----------
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def seg(t, a, b): return clamp((t - a) / (b - a))
def lerp(a, b, u): return a + (b - a) * u
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def back(x):
    c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def env(lt, d, fi=.35, fo=.35):
    """scene alpha envelope"""
    return min(eo(seg(lt, 0, fi)), 1 - seg(lt, d - fo, d))

# ---------- text ----------
def setfont(c, size, weight='r', fam=None, italic=False):
    """fam: a family key from the system ('sans', 'mono', 'display', 'icon') or a family name; weight: letter or number."""
    family = FAM.get(fam or 'sans', fam or 'sans'); w = WEIGHTS.get(weight, weight)
    cands = [f for f in FACES if f[0] == family and f[2] == italic] or [f for f in FACES if f[0] == family]
    face, bold = (family, False)
    if cands:
        best = min(cands, key=lambda f: abs(f[1] - w)); face, bold = best[3], best[4]
    c.select_font_face(face, cairo.FONT_SLANT_ITALIC if italic else cairo.FONT_SLANT_NORMAL,
                       cairo.FONT_WEIGHT_BOLD if bold else cairo.FONT_WEIGHT_NORMAL)
    c.set_font_size(size)

def tw(c, s, size, weight='r', fam=None, italic=False):
    setfont(c, size, weight, fam, italic); return c.text_extents(s).x_advance

def text(c, s, x, y, size, col, a=1.0, weight='r', align='l', fam=None, italic=False):
    if a <= 0.003 or not s: return 0
    setfont(c, size, weight, fam, italic)
    w = c.text_extents(s).x_advance
    if align == 'c': x -= w / 2
    elif align == 'r': x -= w
    c.move_to(x, y); c.set_source_rgba(*col, a); c.show_text(s)
    c.new_path()   # IMPORTANT: clears current point, else the next arc draws a stray line
    return w

def styled(c, s, x, y, style, col, a=1.0, align='l', upper=False):
    """draw text in a named type style, with its letter-spacing (em). y = baseline."""
    if a <= 0.003 or not s: return 0
    p = TS[style]; s = s.upper() if upper else s
    if not p['track']: return text(c, s, x, y, p['size'], col, a, p['weight'], align, p['fam'])
    setfont(c, p['size'], p['weight'], p['fam']); sp = p['size'] * p['track']
    adv = [c.text_extents(ch).x_advance for ch in s]; w = sum(adv) + sp * (len(s) - 1)
    if align == 'c': x -= w / 2
    elif align == 'r': x -= w
    c.set_source_rgba(*col, a)
    for ch, ad in zip(s, adv):
        c.move_to(x, y); c.show_text(ch); x += ad + sp
    c.new_path(); return w

def wrap(c, s, size, weight, maxw, fam=None):
    words, lines, cur = s.split(), [], ""
    for w_ in words:
        t = (cur + " " + w_).strip()
        if tw(c, t, size, weight, fam) <= maxw: cur = t
        else: lines.append(cur); cur = w_
    if cur: lines.append(cur)
    return lines

def fit_size(c, lines, size, weight, maxw, minsize=11):
    while max(tw(c, l, size, weight) for l in lines) > maxw and size > minsize: size -= .5
    return size

def icon(c, name, x, y, size, col, a=1.0):
    """a glyph from the system's icon font, by name (Living Infographic only)"""
    if a <= 0.003: return
    ch = chr(ICON[name]); setfont(c, size, fam='icon')
    e = c.text_extents(ch)
    c.move_to(x - e.x_bearing - e.width / 2, y - e.y_bearing - e.height / 2)
    c.set_source_rgba(*col, a); c.show_text(ch); c.new_path()

def typed(s, lt, t0, t1):
    """typewriter substring — ALWAYS scale by len(s)"""
    return s[:int(seg(lt, t0, t1) * len(s))]

# ---------- shapes ----------
def circle(c, x, y, r):
    c.new_path(); c.arc(x, y, max(r, .01), 0, 2 * math.pi)

def rrect(c, x, y, w, h, r):
    r = min(r, w / 2, h / 2)
    c.new_path(); c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 3 * math.pi / 2)
    c.close_path()

def shadow_circle(c, x, y, r, a, token='shadow-disc'):
    for dy, blur, rgb, al in sorted(SHADOW.get(token, []), key=lambda s: -s[1]):
        circle(c, x, y + dy, r + blur * .9); c.set_source_rgba(*rgb, al * a); c.fill()

def line(c, x1, y1, x2, y2, col, a, w=None, dash=None):
    if a <= 0.003: return
    c.new_path(); c.save()
    if dash: c.set_dash(dash)
    c.set_line_cap(cairo.LINE_CAP_ROUND); c.set_line_width(w or S.get('stroke-line', 2)); c.set_source_rgba(*col, a)
    c.move_to(x1, y1); c.line_to(x2, y2); c.stroke(); c.restore()

def dot(c, x, y, r, col, a=1.0, halo=True):
    if a <= 0.003: return
    if halo: circle(c, x, y, r * 2.6); c.set_source_rgba(*col, .18 * a); c.fill()
    circle(c, x, y, r); c.set_source_rgba(*col, a); c.fill()

def arrow_head(c, x, y, ang, size, col, a):
    c.new_path(); c.move_to(x, y)
    c.line_to(x - size * math.cos(ang - .45), y - size * math.sin(ang - .45))
    c.line_to(x - size * math.cos(ang + .45), y - size * math.sin(ang + .45))
    c.close_path(); c.set_source_rgba(*col, a); c.fill()

# ---------- background ----------
def make_bg():
    bg = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); b = cairo.Context(bg)
    b.set_source_rgb(*T['BG']); b.paint()
    if LOOK == 'blueprint':          # glow at 50% 45%, then the minor and major grid
        rg = cairo.RadialGradient(W * .5, H * .45, 0, W * .5, H * .45, max(W, H) * .6)
        rg.add_color_stop_rgba(0, *T['GLOW'], T['GLOWA']); rg.add_color_stop_rgba(1, *T['GLOW'], 0)
        b.set_source(rg); b.paint()
        for pitch, role in ((S['space-4'], 'GRIDMIN'), (S['grid-pitch'], 'GRID')):
            b.set_source_rgba(*T[role], T[role + 'A']); b.set_line_width(1); p = int(pitch)
            for gx in range(0, W + 1, p): b.move_to(gx + .5, 0); b.line_to(gx + .5, H)
            for gy in range(0, H + 1, p): b.move_to(0, gy + .5); b.line_to(W, gy + .5)
            b.stroke()
        return bg
    rg = cairo.RadialGradient(W * .5, H * .38, 0, W * .5, H * .38, max(W, H) * .7)   # glow at 50% 38%, then dots
    rg.add_color_stop_rgba(0, *T['GLOW'], T['GLOWA']); rg.add_color_stop_rgba(1, *T['GLOW'], 0)
    b.set_source(rg); b.paint()
    b.set_source_rgba(*T['DOTS'], T['DOTSA']); p = int(S['dot-pitch'])
    for gx in range(int(p * .75), W, p):
        for gy in range(int(p * .75), H, p):
            b.arc(gx, gy, 1.1, 0, 2 * math.pi); b.fill()
    return bg

# ========== Living Infographic components ==========
def badge(c, name, x, y, r, col, a=1.0, s=1.0):
    """icon in a coloured disc with a ring + soft shadow. r: S['badge-r'] in scenes, S['chip-badge-r'] on the poster."""
    if a <= 0.003 or s <= 0.01: return
    rr = r * s
    shadow_circle(c, x, y, rr, a)
    circle(c, x, y, rr); c.set_source_rgba(*T['RING'], a); c.fill()
    circle(c, x, y, rr * .84); c.set_source_rgba(*col, a); c.fill()
    icon(c, name, x, y, rr, T['ONACC'], a)

def card(c, x, y, w, h, a, border=None):
    if a <= 0.003: return
    r = S['radius-card']
    for dy, blur, rgb, al in sorted(SHADOW.get('shadow-card', []), key=lambda s: -s[1]):
        k = blur * .45; rrect(c, x - k, y + dy - k, w + 2 * k, h + 2 * k, r + k); c.set_source_rgba(*rgb, al * a); c.fill()
    rrect(c, x, y, w, h, r); c.set_source_rgba(*T['CARD'], a); c.fill_preserve()
    if border: c.set_source_rgba(*border, .9 * a); c.set_line_width(S['stroke-line'])
    else: c.set_source_rgba(*T['HAIR'], T['HAIRA'] * a); c.set_line_width(S['stroke-hair'])
    c.stroke()

def pill(c, s, x, y, size, fg, bg, a=1.0, weight='s', ic=None, pad=None):
    if a <= 0.003: return 0
    pad = S['pill-pad'] if pad is None else pad
    iw = size * 1.3 if ic else 0
    w = tw(c, s, size, weight) + pad * 2 + iw; h = size * 2.0; x0 = x - w / 2
    rrect(c, x0, y - h / 2, w, h, h / 2); c.set_source_rgba(*bg, a); c.fill()
    if ic: icon(c, ic, x0 + pad + size * .5, y, size * 1.05, fg, a)
    text(c, s, x0 + pad + iw, y + size * .36, size, fg, a, weight)
    return w

def packet(c, x1, y1, x2, y2, ph, col, lab, a):
    """labelled message chip travelling from (x1,y1) to (x2,y2), ph in 0..1"""
    px, py = lerp(x1, x2, eio(ph)), lerp(y1, y2, eio(ph)); p = TS['packet']; h = S['packet-height']
    w = tw(c, lab, p['size'], p['weight'], p['fam']) + 2 * S['packet-pad']
    rrect(c, px - w / 2, py - h / 2, w, h, S['radius-packet']); c.set_source_rgba(*col, a); c.fill()
    text(c, lab, px, py + p['size'] * .35, p['size'], T['ONACC'], a, p['weight'], 'c', p['fam'])

def header(c, kicker, title, sub, a, lt, x=None, maxw=None):
    """kicker (a2 caps) + title (≤2 lines) + optional sub, rising 18px into place. Returns bottom y."""
    if a <= 0.003: return 0
    x = S['space-frame'] if x is None else x; maxw = maxw or W - 2 * x
    dy = (1 - eo(seg(lt, 0, .6))) * 18; k, t_, sb = TS['kicker'], TS['title'], TS['sub']
    text(c, kicker.upper(), x, S['kicker-y'] + dy, k['size'], T['A2'], a, k['weight'])
    y = S['title-y'] + dy
    for ln in wrap(c, title, t_['size'], t_['weight'], maxw):
        text(c, ln, x, y, t_['size'], T['INK'], a, t_['weight']); y += t_['lh']
    if sub:
        y += 2
        for ln in wrap(c, sub, sb['size'], sb['weight'], maxw):
            text(c, ln, x, y, sb['size'], T['MUTED'], a, sb['weight']); y += sb['lh']
    return y

def progress_bar(c, t, t_end, handle):
    pa = 1 - seg(t, t_end - .5, t_end)
    if pa <= 0: return
    x = S['space-frame']; h = S['progress-height']; y = H - 44; hs = TS['handle']
    rrect(c, x, y, W - 2 * x, h, S['radius-bar']); c.set_source_rgba(*T['HAIR'], T['HAIRA'] * pa); c.fill()
    rrect(c, x, y, max(h, (W - 2 * x) * t / t_end), h, S['radius-bar']); c.set_source_rgba(*T['A2'], .8 * pa); c.fill()
    text(c, handle, W - x, y - 16, hs['size'], T['MUTED'], .8 * pa, hs['weight'], 'r')

def poster(c, lt, title_a, title_b, subtitle, rows, hub_icon, hub_label, handle, footer=None, top=None, spacing=None):
    """the living infographic. rows: [(category 'Line1|Line2', [(icon, 'label|line2'), ...]), ...] (6-8 rows, ≤6 chips)"""
    a = min(1.0, eo(seg(lt, 0, .5)))
    top = S['poster-top'] if top is None else top; spacing = S['row-pitch'] if spacing is None else spacing
    n = len(rows); HR, DR, CR = S['hub-r'], S['disc-r'], S['chip-badge-r']
    ys = [top + i * spacing for i in range(n)]
    hub = (112, (ys[0] + ys[-1]) / 2)
    half = (ys[-1] - ys[0]) / 2 + 30
    geo = [(262 + 105 * (1 - ((y - hub[1]) / half) ** 2), y) for y in ys]
    for k in range(18):                                   # rays
        ang = math.pi * .5 + k * (math.pi * 2 / 18) + lt * .05
        c.new_path(); c.move_to(*hub); c.arc(hub[0], hub[1], 1600, ang - .07, ang + .07); c.close_path()
        c.set_source_rgba(*T['GLOW'], (.5 if T['GLOWA'] > .3 else .05) * a); c.fill()
    g = cairo.LinearGradient(0, 0, 0, 190); g.add_color_stop_rgba(0, *T['BG'], .95 * a); g.add_color_stop_rgba(1, *T['BG'], 0)
    c.set_source(g); c.rectangle(0, 0, W, 190); c.fill()   # title backdrop so rays don't wash it out
    pt, ps = TS['poster-title'], TS['poster-subtitle']
    ts = fit_size(c, [title_a + title_b], pt['size'], pt['weight'], W - 80)
    w1 = tw(c, title_a, ts, pt['weight']); w2 = tw(c, title_b, ts, pt['weight']); x0 = W / 2 - (w1 + w2) / 2
    text(c, title_a, x0, 92, ts, T['INK'], a, pt['weight']); text(c, title_b, x0 + w1, 92, ts, T['A2'], a, pt['weight'])
    text(c, subtitle, W / 2, 138, ps['size'], T['INK'], a * .8, ps['weight'], 'c')
    sweep = (lt * .9) % (n + 2)
    for i, (x, y) in enumerate(geo):                      # beams
        p = seg(lt, .2 + i * .32, .7 + i * .32)
        if p <= 0: continue
        ang = math.atan2(y - hub[1], x - hub[0]); nx, ny = -math.sin(ang), math.cos(ang)
        ex, ey = lerp(hub[0], x, eo(p)), lerp(hub[1], y, eo(p)); cr = 50 * eo(p)
        c.new_path(); c.move_to(hub[0] + nx * 14, hub[1] + ny * 14); c.line_to(ex + nx * cr, ey + ny * cr)
        c.line_to(ex - nx * cr, ey - ny * cr); c.line_to(hub[0] - nx * 14, hub[1] - ny * 14); c.close_path()
        hl = max(0, 1 - abs(sweep - i - 1) / 1.2) if lt > 3.2 else 0
        c.set_source_rgba(*(T['A2'] if i % 2 else T['A1']), (.16 + .22 * hl) * a); c.fill()
    hs = back(seg(lt, 0, .5))                             # hub
    shadow_circle(c, *hub, HR * hs, a)
    circle(c, *hub, HR * hs); c.set_source_rgba(*T['CARD'], a); c.fill()
    c.set_line_width(S['stroke-hub']); circle(c, *hub, (HR - 14) * hs); c.set_source_rgba(*T['A3'], a); c.stroke()
    pul = .5 + .5 * math.sin(lt * 3)
    circle(c, *hub, (HR + 8 + 8 * pul) * hs); c.set_source_rgba(*T['A3'], .15 * (1 - pul) * a)
    c.set_line_width(S['stroke-pulse']); c.stroke()
    icon(c, hub_icon, hub[0], hub[1] - 10, (HR - 14) * hs, T['A3'], a)
    text(c, hub_label, hub[0], hub[1] + 44, 22 * hs, T['A3'], a, 'x', 'c')
    fo, hp = TS['follow'], TS['handle-poster']
    text(c, "Follow", hub[0], hub[1] + 128, fo['size'], T['INK'], a * .8, fo['weight'], 'c')
    text(c, handle, hub[0], hub[1] + 154, hp['size'], T['INK'], a, hp['weight'], 'c')
    cl_, ca = TS['chip-label'], TS['category']
    for i, ((cat, items), (x, y)) in enumerate(zip(rows, geo)):   # rows
        p = seg(lt, .4 + i * .32, .9 + i * .32)
        if p <= 0: continue
        col = T['A2'] if i % 2 else T['A1']; r = DR
        yl = y - 44; xs = x + math.sqrt(max(r * r - 44 * 44, 0)); xe = W - 28
        line(c, xs, yl, lerp(xs, xe, eo(p)), yl, T['INK'], .85 * a)
        m = len(items); cx0 = x + 88; span = W - 30 - cx0
        for k, (ic, lab) in enumerate(items):
            q = seg(lt, .7 + i * .32 + k * .06, 1.1 + i * .32 + k * .06)
            if q <= 0: continue
            cx = cx0 + (k + .5) * span / m
            line(c, cx, yl, cx, y - 30, T['INK'], .85 * a * q)
            dot(c, cx, yl, 3, T['INK'], a * q, False)
            badge(c, ic, cx, y - 2, CR, HUES[(i * 3 + k) % len(HUES)], a, back(q))
            for j, ln in enumerate(lab.split('|')):
                text(c, ln, cx, y + 44 + j * cl_['lh'], cl_['size'] - (1 if m >= 5 else 0), T['INK'], a * q, cl_['weight'], 'c')
        if p >= 1:
            for k in range(2):
                ph = (lt * .22 + k * .5 + i * .13) % 1
                dot(c, lerp(xs, xe, ph), yl, S['dot-r'], col, a * .9)
        s = back(p)
        shadow_circle(c, x, y, r * s, a)
        circle(c, x, y, r * s); c.set_source_rgba(*col, a); c.fill()
        cl = cat.split('|')
        fs = fit_size(c, cl, ca['size'] - (1 if len(cl) > 1 else 0), ca['weight'], 2 * r * s - 14)
        for j, ln in enumerate(cl):
            text(c, ln, x, y + fs * .38 - (len(cl) - 1) * fs * .6 + j * fs * 1.2, fs, T['ONACC'], a, ca['weight'], 'c')
    if footer:
        f = TS['footer']
        text(c, footer, W / 2, H - 20, f['size'], T['MUTED'], a * seg(lt, 3.4, 3.9), f['weight'], 'c')

# ========== Blueprint Explainers components ==========
def serif(c, s, x, y, style, a=1.0, align='l', col=None, italic=False):
    """a display style line; wrap one word in *asterisks* to set it italic in signal. italic=True sets the whole
    line italic in col (e.g. the muted title-card subtitle). y = baseline."""
    if a <= 0.003 or not s: return 0
    size = TS[style]['size'] if isinstance(style, str) else style
    if italic:
        w = tw(c, s, size, 'r', 'display', True); x -= w / 2 if align == 'c' else (w if align == 'r' else 0)
        text(c, s, x, y, size, col or T['INK'], a, 'r', 'l', 'display', True); return w
    parts = [(p, i % 2 == 1) for i, p in enumerate(s.split('*')) if p]
    w = sum(tw(c, p, size, 'r', 'display', it) for p, it in parts)
    x -= w / 2 if align == 'c' else (w if align == 'r' else 0)
    for p, it in parts:
        x += text(c, p, x, y, size, T['SIGNAL'] if it else (col or T['INK']), a, 'r', 'l', 'display', it)
    return w

def bp_header(c, kicker, title, a, lt):
    """kicker (signal) above a display-lg headline (1-2 lines, split with '\\n') at headline-top; rises 50px over 0.45s."""
    if a <= 0.003: return 0
    dy = (1 - eo(seg(lt, 0, .45))) * 50; ha = a * eo(seg(lt, 0, .45)); d = TS['display-lg']; top = S['headline-top']
    styled(c, kicker, S['space-frame'], top - 38 + TS['kicker']['size'] * .75, 'kicker', T['SIGNAL'], a, upper=True)
    y = top + d['size'] * .78 + dy
    for ln in title.split('\n'):
        serif(c, ln, S['space-frame'], y, 'display-lg', ha); y += d['lh']
    return y

def _glow(c, path_fn, a=1.0):
    """the glow-signal shadow as stacked strokes (none in paper)"""
    for dy, blur, rgb, al in SHADOW.get('glow-signal', []):
        for wdt, k in ((blur, .12), (blur * .55, .2), (blur * .3, .35)):
            path_fn(); c.set_line_width(wdt); c.set_source_rgba(*rgb, al * k * a); c.stroke()

def chrome(c, series, label, t, t_end, handle=None):
    """series top-left (muted), scene label top-right (signal), progress bar at 1286 with glow, handle above it."""
    handle = HANDLE if handle is None else handle
    x = S['space-frame']; cs = TS['chrome']['size']
    styled(c, series, x, 56 + cs * .8, 'chrome', T['MUTED'], upper=True)
    styled(c, label, W - x, 56 + cs * .8, 'chrome', T['SIGNAL'], align='r', upper=True)
    styled(c, handle, W - x, 1286 - 20, 'chrome', T['MUTED'], align='r')
    rrect(c, x, 1286, W - 2 * x, 3, 1.5); c.set_source_rgba(*T['GRID'], T['GRIDA'] * 2); c.fill()
    pw = max(3, (W - 2 * x) * clamp(t / t_end))
    _glow(c, lambda: rrect(c, x, 1286, pw, 3, 1.5))
    rrect(c, x, 1286, pw, 3, 1.5); c.set_source_rgba(*T['SIGNAL'], 1); c.fill()

def node(c, label, cx, cy, w=300, a=1.0, state='idle', sub=None, p=1.0, h=76):
    """panel box (radius-node) with a 2.2px outline that draws on with p (0..1).
    state: idle (line) · active (signal + glow) · result (success) · error (error). Label node-label, sub below it."""
    if a <= 0.003: return
    x, y, r = cx - w / 2, cy - h / 2, S['radius-node']
    col = {'idle': T['LINE'], 'active': T['SIGNAL'], 'result': T['OK'], 'error': T['BAD']}[state]
    per = 2 * (w + h) - 8 * r + 2 * math.pi * r
    rrect(c, x, y, w, h, r); c.set_source_rgba(*T['CARD'], a * seg(p, .3, 1)); c.fill()
    if state == 'active': _glow(c, lambda: rrect(c, x, y, w, h, r), a)
    c.save(); rrect(c, x, y, w, h, r); c.set_dash([per * eio(p), per]); c.set_line_width(2.2)
    c.set_source_rgba(*col, a); c.stroke(); c.restore()
    la = a * seg(p, .6, 1)
    if sub:
        styled(c, label, cx, cy - 2, 'node-label', T['INK'], la, 'c', True)
        text(c, sub, cx, cy + 22, 14, T['MUTED'], la, 'r', 'c', 'mono')
    else:
        styled(c, label, cx, cy + 8, 'node-label', T['INK'], la, 'c', True)

def edge(c, x1, y1, x2, y2, a=1.0, p=1.0, signal=False):
    """straight edge node-edge to node-edge that draws on with p; signal=True for the highlighted path."""
    if a <= 0.003 or p <= 0: return
    col = T['SIGNAL'] if signal else T['LINE']; w = S['stroke-strong'] if signal else S['stroke-edge']
    line(c, x1, y1, lerp(x1, x2, eio(p)), lerp(y1, y2, eio(p)), col, a, w)

def particle(c, x, y, a=1.0, r=6):
    """4.5–8px signal dot with the glow-signal halo; fade it in and out at each end of its path."""
    if a <= 0.003: return
    for dy, blur, rgb, al in SHADOW.get('glow-signal', []):
        for k, m in ((blur / r * .65, .12), (blur / r * .45, .26)): circle(c, x, y, r * k); c.set_source_rgba(*rgb, al * m * a); c.fill()
    circle(c, x, y, r); c.set_source_rgba(*T['SIGNAL'], a); c.fill()

def bp_pill(c, s, cx, cy, a=1.0, state='idle', caret=False):
    """question/answer pill: panel fill, 2.2px outline (ink; success for an answer, error for a failure), body text."""
    if a <= 0.003: return 0
    b = TS['body']; tw_ = tw(c, s, b['size'], b['weight']); h = 2 * S['radius-pill'] - 6; w = tw_ + 2 * S['space-3']
    col = {'idle': T['INK'], 'answer': T['OK'], 'error': T['BAD']}[state]
    rrect(c, cx - w / 2, cy - h / 2, w, h, h / 2); c.set_source_rgba(*T['CARD'], a); c.fill_preserve()
    c.set_line_width(2.2); c.set_source_rgba(*col, a); c.stroke()
    text(c, s, cx - tw_ / 2, cy + b['size'] * .36, b['size'], T['INK'], a, b['weight'])
    if caret:
        c.rectangle(cx + tw_ / 2 + 3, cy - b['size'] * .45, 3, b['size'] * .9); c.set_source_rgba(*T['SIGNAL'], a); c.fill()
    return w

def fail_tag(c, s, cx, cy, a=1.0):
    """× + uppercase word in a panel box with an error outline, e.g. CUTOFF, OUTDATED."""
    if a <= 0.003: return
    lab = "× " + s.upper(); nl = TS['node-label']
    w = tw(c, lab, nl['size'], nl['weight'], nl['fam']) * (1 + nl['track']) + 2 * S['space-3']; h = 66
    rrect(c, cx - w / 2, cy - h / 2, w, h, S['radius-node']); c.set_source_rgba(*T['CARD'], a); c.fill_preserve()
    c.set_line_width(2.2); c.set_source_rgba(*T['BAD'], a); c.stroke()
    styled(c, lab, cx, cy + 8, 'node-label', T['INK'], a, 'c')

def end_card(c, lt, line_a, line_b, question, handle=None):
    """display-xl statement that slams from 1.8x (line_b may hold *italic*), the body-lg question, then the handle."""
    handle = HANDLE if handle is None else handle
    a = eo(seg(lt, 0, .45)); s = 1 + .8 * (1 - eo(seg(lt, 0, .45))); d = TS['display-xl']
    c.save(); c.translate(W / 2, 560); c.scale(s, s)
    serif(c, line_a, 0, 0, 'display-xl', a, 'c'); serif(c, line_b, 0, d['lh'], 'display-xl', a, 'c'); c.restore()
    qa = seg(lt, .8, 1.3); q = TS['body-lg']
    text(c, question, W / 2, 900, q['size'], T['INK'], qa, q['weight'], 'c')
    styled(c, handle, W / 2, 980, 'chrome', T['MUTED'], qa, 'c')

# ---------- driver ----------
def run(draw, dur):
    """CLI: python scenes.py stills 0 5.5 12 ...   |   python scenes.py video out.mp4"""
    surf = cairo.ImageSurface(cairo.FORMAT_ARGB32, W, H); c = cairo.Context(surf)
    fo = cairo.FontOptions(); fo.set_antialias(cairo.ANTIALIAS_GRAY); fo.set_hint_style(cairo.HINT_STYLE_NONE)
    c.set_font_options(fo)
    if sys.argv[1] == 'stills':
        for ts in sys.argv[2:]:
            draw(c, float(ts)); surf.write_to_png(f"still_{float(ts):05.1f}.png")
        return
    ff = subprocess.Popen(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'rawvideo', '-pix_fmt', 'bgra',
                           '-s', f'{W}x{H}', '-r', str(FPS), '-i', '-', '-c:v', 'libx264', '-preset', 'slow',
                           '-crf', '17', '-profile:v', 'high', '-pix_fmt', 'yuv420p', '-movflags', '+faststart',
                           sys.argv[2]], stdin=subprocess.PIPE)
    for f in range(int(dur * FPS)):
        draw(c, f / FPS); surf.flush(); ff.stdin.write(bytes(surf.get_data()))
    ff.stdin.close(); ff.wait()

if __name__ == '__main__' and len(sys.argv) > 2 and sys.argv[1] == 'install':
    install(sys.argv[2])
