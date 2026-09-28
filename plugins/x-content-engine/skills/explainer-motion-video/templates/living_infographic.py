import sys; sys.path.insert(0, '.')
from mlib import *
configure('ds/living-infographic/project', 'light')          # or 'dark', size=(1920, 1080)
BG = make_bg()
SCENES = [('problem', 0, 6.5), ('arch', 6.5, 14), ('poster', 46, 57)]   # (name, start, end) — poster last
DUR = 57.0; HANDLE = "@pallaprolu"

def s_problem(c, lt, d):
    a = 1 - seg(lt, d - .35, d)             # first scene: no fade-in
    header(c, "The problem", "Every AI app needed custom glue for every tool", None, a, 1)
    badge(c, 'robot', 200, 600, S['badge-r'], T['A1'], a, back(seg(lt, .2, .7)))
    # ... more elements for this beat

def s_arch(c, lt, d):
    a = env(lt, d)                          # fade in/out
    header(c, "Architecture", "Host → Client → Server", "One MCP client per server.", a, lt)
    # ... cards, pills, packets for this beat

ROWS = [                                   # 6-8 rows, up to 6 chips each; '|' breaks a label onto two lines
    ("Archi|tecture", [('device-desktop', "Host app"), ('plug-connected', "MCP|client"), ('server', "MCP|server")]),
    ("Server|offers", [('tool', "Tools"), ('database', "Resources"), ('message', "Prompts")]),
    ("Client|offers", [('sitemap', "Roots"), ('robot', "Sampling"), ('forms', "Elicitation")]),
    ("Trans|port", [('terminal-2', "stdio"), ('world', "Streamable|HTTP")]),
    ("Secur|ity", [('lock', "OAuth 2.1"), ('shield-check', "User|consent")]),
    ("Eco|system", [('brand-github', "Registry"), ('apps', "SDKs")]),
]
def s_poster(c, lt, d):
    poster(c, lt, "MODEL CONTEXT ", "PROTOCOL", "How it works · where it's going", ROWS,
           'plug-connected', "MCP", HANDLE, footer="Next → the registry")

FUNCS = {'problem': s_problem, 'arch': s_arch, 'poster': s_poster}
def draw(c, t):
    c.set_source_surface(BG); c.paint()
    for name, s, e in SCENES:
        if s <= t < e or (name == SCENES[-1][0] and t >= s): FUNCS[name](c, t - s, e - s)
    if t < SCENES[-1][1]: progress_bar(c, t, SCENES[-1][1], HANDLE)

run(draw, DUR)
