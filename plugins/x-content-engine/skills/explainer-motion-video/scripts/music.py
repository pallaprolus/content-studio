#!/usr/bin/env python3
"""Soft ambient score synthesized from scratch (no licensing issues).
Usage: python music.py DUR "0,6.5,14,22,30,36,46" POSTER_START out.wav
Chord changes land on scene cuts; a bell arpeggio accelerates until POSTER_START, then a chime and sparse bells."""
import numpy as np, wave, sys

DUR = float(sys.argv[1]); CUTS = [float(x) for x in sys.argv[2].split(',')] + [DUR]
PSTART = float(sys.argv[3]); OUT = sys.argv[4]
SR = 44100; N = int(SR * DUR); t = np.arange(N) / SR
def mid(n): return 440.0 * 2 ** ((n - 69) / 12)
PROG = [[50, 57, 61, 64, 66], [47, 54, 57, 61, 62], [43, 50, 54, 57, 62], [45, 52, 57, 59, 64]]  # Dmaj9 Bm9 Gmaj7 Asus
nseg = len(CUTS) - 1
CH = [PROG[i % 4] for i in range(nseg - 1)] + [[50, 57, 61, 64, 69]]  # resolve on D

def gate(a, b, xf=1.2):
    g = np.clip((t - (a - xf / 2)) / xf, 0, 1) * np.clip(((b + xf / 2) - t) / xf, 0, 1)
    return 0.5 - 0.5 * np.cos(np.pi * g)

rng = np.random.default_rng(3); pad = np.zeros(N)
for i, notes in enumerate(CH):
    g = gate(CUTS[i], CUTS[i + 1]); idx = g > 0; tt = t[idx]
    for n in notes[1:]:
        for det in (-0.12, 0.0, 0.11):
            ff = mid(n) * 2 ** (det / 12); ph = rng.uniform(0, 2 * np.pi)
            v = sum((0.55 ** (h - 1)) / h * np.sin(2 * np.pi * ff * h * tt + ph * h) for h in range(1, 5))
            pad[idx] += g[idx] * v * 0.06
    pad[idx] += g[idx] * 0.11 * np.sin(2 * np.pi * mid(notes[0] - 12) * tt)
pad *= 0.85 + 0.15 * np.sin(2 * np.pi * t / 7.5)

bell = np.zeros(N)
def add_bell(start, f, amp):
    s = int(start * SR); e = min(N, s + int(2.2 * SR))
    if s >= N: return
    tt = np.arange(e - s) / SR
    env = np.exp(-tt * 3.2) * np.clip(tt / 0.004, 0, 1)
    v = np.sin(2 * np.pi * f * tt) + .25 * np.sin(4 * np.pi * f * tt) * np.exp(-tt * 6) + .08 * np.sin(2 * np.pi * f * 3.01 * tt) * np.exp(-tt * 9)
    bell[s:e] += amp * env * v
pos, k = 0.6, 0
while pos < PSTART - 0.2:
    ci = max(i for i in range(nseg) if CUTS[i] <= pos); notes = CH[ci]
    pattern = [notes[2], notes[3], notes[4], notes[4] + 5, notes[3]]
    prog = (pos - 0.6) / max(1, PSTART - 0.6)
    add_bell(pos, mid(pattern[k % 5] + 12), 0.05 + 0.03 * prog)
    pos += 0.95 * (1 - prog) + 0.26 * prog; k += 1
for j, n in enumerate([62, 69, 74, 78]): add_bell(PSTART + .1 + j * .12, mid(n + 12), 0.07)
j, p = 0, PSTART + 2.0
while p < DUR - 2:
    add_bell(p, mid([66, 69, 73, 74, 69, 66, 64, 62][j % 8] + 12), 0.035); p += 1.1; j += 1

noise = np.convolve(rng.standard_normal(N), np.ones(60) / 60, mode='same'); sw = np.zeros(N)
for cpt in CUTS[1:-1]: sw += noise * np.exp(-((t - cpt + 0.15) / 0.35) ** 2) * 0.10
mix = pad + bell + sw

def reverb(x, seed, secs=2.8):
    r = np.random.default_rng(seed); L = int(secs * SR); tt = np.arange(L) / SR
    ir = np.convolve(r.standard_normal(L) * np.exp(-tt * 2.4), np.ones(20) / 20, mode='same'); ir /= np.sqrt(np.sum(ir ** 2))
    M = 1 << int(np.ceil(np.log2(len(x) + L)))
    return np.fft.irfft(np.fft.rfft(x, M) * np.fft.rfft(ir, M), M)[:len(x)]
L = .62 * mix + .38 * reverb(mix, 11); R = .62 * mix + .38 * reverb(mix, 12) + .15 * np.roll(bell, int(.012 * SR))
fade = np.clip(t / 1.5, 0, 1) * np.clip((DUR - t) / 2.5, 0, 1); L *= fade; R *= fade
pk = max(np.abs(L).max(), np.abs(R).max()); st = np.stack([L, R], 1) / pk * 0.5
with wave.open(OUT, 'wb') as w:
    w.setnchannels(2); w.setsampwidth(2); w.setframerate(SR); w.writeframes((st * 32767).astype('<i2').tobytes())
print('ok', OUT)
