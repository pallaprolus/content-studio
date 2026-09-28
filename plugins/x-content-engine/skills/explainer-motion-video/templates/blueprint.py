import sys; sys.path.insert(0, '.')
from mlib import *
HANDLE = "@your_handle"                                       # x_handle from the plugin's config.json
configure('ds/blueprint-explainers/project', 'blueprint', handle=HANDLE)
BG = make_bg()
SCENES = [('title', 0, 5), ('problem', 5, 13), ('flow', 13, 24), ('end', 54, 60)]
DUR = 60.0; SERIES = "RAG · 2026 EDITION"

def s_title(c, lt, d):
    a = 1 - seg(lt, d - .35, d)
    serif(c, "RAG", W / 2, 700, 'display-hero', a, 'c')
    serif(c, "the 2026 edition, in 60 seconds", W / 2, 800, 'display-md', a, 'c', T['MUTED'], italic=True)

def s_problem(c, lt, d):
    a = env(lt, d)
    bp_header(c, "01 · The problem", "LLMs are *frozen* in time.", a, lt)
    node(c, "LLM", 540, 560, 300, a, 'error', "knowledge in weights", seg(lt, .4, 1.0))
    fail_tag(c, "Cutoff", 540, 720, a * seg(lt, 1.4, 1.8))
    bp_pill(c, "What changed in the SDK last week?", 540, 880, a * seg(lt, 2, 2.4), caret=True)

def s_flow(c, lt, d):
    a = env(lt, d)
    bp_header(c, "02 · The idea", "Look it up *first*.", a, lt)
    ys = [470 + i * S['node-pitch'] for i in range(4)]
    for i, (lab, sub) in enumerate([("Question", None), ("Search", "vector + keyword"), ("Context", None), ("Answer", None)]):
        node(c, lab, 540, ys[i], 320, a, 'result' if i == 3 else 'idle', sub, seg(lt, .4 + i * .35, 1.0 + i * .35))
        if i: edge(c, 540, ys[i - 1] + 38, 540, ys[i] - 38, a, seg(lt, .7 + i * .35, 1.1 + i * .35))
    ph = (lt * .8) % 1
    if lt > 2: particle(c, 540, lerp(ys[0] + 38, ys[-1] - 38, ph), a * min(1, 4 * ph, 4 * (1 - ph)))

def s_end(c, lt, d):
    end_card(c, lt, "It grew up.", "Then it *branched*.", "Which branch are you building on?")

FUNCS = {'title': s_title, 'problem': s_problem, 'flow': s_flow, 'end': s_end}
def draw(c, t):
    c.set_source_surface(BG); c.paint()
    for name, s, e in SCENES:
        if s <= t < e or (name == SCENES[-1][0] and t >= s): FUNCS[name](c, t - s, e - s)
    if SCENES[1][1] <= t < SCENES[-1][1]: chrome(c, SERIES, "RAG", t, SCENES[-1][1])

run(draw, DUR)
