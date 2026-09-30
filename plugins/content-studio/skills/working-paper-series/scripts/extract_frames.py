"""Extract verification frames from a rendered series video for the video verifier.

python scripts/extract_frames.py SERIES VIDEO [FIRST_FOLIO]

Reads SERIES/out/timing.json (written by render.py) and writes SERIES/vq/frames/*.png plus INDEX.txt:
each page's frame 0, two frames per story step (a = 0.3 s in, first hop in flight; b = 0.7 s in,
first destination lit, second hop in flight), every page turn and the final hold.
"""
import json, os, pathlib, subprocess, sys
series = pathlib.Path(sys.argv[1]); video = sys.argv[2]; base = int(sys.argv[3]) if len(sys.argv) > 3 else 1
tm = json.loads((series / 'out' / 'timing.json').read_text())
fr = series / 'vq' / 'frames'; fr.mkdir(parents=True, exist_ok=True)
for f in fr.iterdir(): f.unlink()
idx = []
def grab(t, name):
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', f'{t:.3f}', '-i', video, '-frames:v', '1', str(fr / f'{name}.png')], check=True)
    idx.append(f'{name}.png  t={t:.2f}s')
starts, lengths = tm['starts'], tm['lengths']
for i, (s, L) in enumerate(zip(starts, lengths)):
    p = base + i; steps = int(round((L - 1) / 2)) - 1
    grab(s + 0.05, f'p{p}-frame0')
    for k in range(steps):
        grab(s + 1 + k + 0.3, f'p{p}-step{k+1}a'); grab(s + 1 + k + 0.7, f'p{p}-step{k+1}b')
    if i < len(starts) - 1: grab(s + L + 0.35, f'turn-{p}-{p+1}')
grab(tm['total'] - 0.2, 'final-hold')
(fr / 'INDEX.txt').write_text('a = 0.3 s into a step (first hop in flight); b = 0.7 s in (first destination lit; second hop in flight).\n' + '\n'.join(idx) + '\n')
print(len(idx), 'frames ->', fr)
