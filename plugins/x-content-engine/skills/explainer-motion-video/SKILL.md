---
name: "explainer-motion-video"
description: "Create animated concept-explainer videos (MP4 with synthesized music) about AI/tech topics for X or LinkedIn, rendered from one of the user's design systems (by default Living Infographic or Blueprint Explainers): storyboard, fact-check, render with Cairo + ffmpeg, post to X."
---

# Explainer motion video

Turns a concept (e.g. "how MCP works", "LLM history", "drift detection") into a 45–65 s animated explainer with
music, ready for X/LinkedIn. pycairo draws every frame, ffmpeg encodes, numpy synthesizes a royalty-free score.

**This skill holds process only; the code is in this skill's folder (`scripts/`, `templates/`). The look lives in the design systems** — every colour, font, size and
visual/motion rule. `mlib` loads them at setup, so a change to a design system shows up in the next video.

**Settings:** Read `<base>/../../config.json` directly, where `<base>` is the "Base directory for this skill" shown when this skill loaded; don't search for it. It lists
the `design_systems` (name, artifact URL, video themes, what each is for) and the `x_handle` shown in the video.
Values the user gives in the conversation win; if the file can't be read or a value is empty, ask once. The two
templates target the default systems, Living Infographic and Blueprint Explainers; another design system needs
its token names mapped in `ROLES` in `mlib.py` first.

Before storyboarding, read the chosen system's README from its artifact URL (Artifact tool, action `read`, `path: "project/README.md"`)
and follow its content fundamentals, visual foundations and motion rules. Never restate or hard-code its values.

## Workflow

1. **Research first.** Web-search anything current (dates, versions, releases, stats). Keep a source list.
   Anything from a single aggregator gets a second source or is dropped. Stable concepts need no search.
2. **Plan before building — show the user and get a go.** Reply with:
   - a storyboard table: 6–8 beats × 6–10 s each (time · beat · what moves on screen),
   - for poster-ending videos, the final poster rows (categories × chips),
   - the decisions, each with a recommendation: **design system** (from the topic, one-line reason);
     **format** (Living Infographic: build-up ending on the living-infographic poster, poster loop only, or
     timeline only; Blueprint: numbered scenes ending on an end card with a question); **theme**; **size**
     (4:5 1080×1350 default, or 16:9 1920×1080); **depth** (technical-but-accessible default, or deep for builders).
3. **Set up** (once per session) — see *Setup*.
4. **Write `scenes.py`**, starting from the matching template (see *Templates*). One function per scene;
   `draw(c, t)` dispatches by time.
5. **Review stills before rendering.** `python scenes.py stills 0 5.5 12 …` at the busiest moment of every
   scene, tile into a contact sheet with PIL, look at it with Read. Fix overlaps/overflow, re-check.
6. **Render + score + mux** — see *Render*. Then pull 9 frames from the MP4 into a contact sheet and check again.
7. **Deliver.** SendUserFile the MP4 (and the final frame as a PNG — it doubles as an image post/reply).
   If the user's computer is linked, also write it to `~/Downloads` with device_commit_files.
   Say plainly you could only check audio levels, not listen.
8. **Post to X only when asked** — see *Posting to X*.

## Setup

```bash
pip install --break-system-packages -q pycairo fonttools brotli     # libcairo and ffmpeg are usually present
mkdir -p work && cd work
```
1. Fetch the chosen design system into `work/ds/<system>/`: Artifact `read` with `path: "project/tokens.json"`
   and `out_dir` set to that folder, then one `read` with `paths` = every `"project/" + file` listed in the
   tokens' `type.fonts[].file` (same `out_dir`). The files land under `work/ds/<system>/project/`.
2. Copy `scripts/mlib.py` and `scripts/music.py` from this skill's folder (the "Base directory for this skill"
   shown when it loads) into `work/`. Never retype them from memory; if a fix is needed, edit the copy and tell
   the user so the repo can be updated.
3. `python mlib.py install ds/<system>/project` — converts the system's fonts to TTF in `~/.fonts`, records the
   face names and (Living Infographic) the icon names read from the icon font. It prints the counts.

## Engine notes (learned the hard way)

- Frame 0 is the feed thumbnail: scene 1 uses `a = 1 - seg(lt, d-.35, d)` so it never fades in.
- `text()` calls `c.new_path()` after drawing — keep that, or the next `arc` draws a stray line from the text.
- Typewriter text: always `typed(s, lt, t0, t1)` (scales by `len(s)`), or the line gets cut off.
- Wrap long lines with `wrap()`; `fit_size()` shrinks only labels that must fit a shape (poster categories).
- The poster: rays draw before the title, and the title keeps its gradient backdrop so the rays don't wash it out.
- Icons are looked up by Tabler name (`grep` the names with `python -c "import json;print([k for k in json.load(open('ds/<system>/project/faces.json'))['icons'] if 'database' in k])"`).
- Reuse one example across scenes so the video reads as one story; pace matches the story (compress time when the
  topic is acceleration).

## The library in one screen

After `configure(ds, theme)`: colours in `T` by role (`BG CARD INK MUTED A1 A2 A3 OK WARN BAD ONACC …`; Blueprint
adds `LINE SIGNAL`), sizes in `S` by token name (`S['space-frame']`, `S['node-pitch']` …), type styles via
`st('title')` → `{size, weight, fam, lh, track}`, badge hues in `HUES`.

- Shared: `text`, `styled(c, s, x, y, style, col)` (a named type style with its tracking), `wrap`, `fit_size`,
  `typed`, `circle`, `rrect`, `line`, `dot`, `arrow_head`, `make_bg`, easing `seg lerp eo eio back env`.
- Living Infographic: `header(kicker, title, sub)`, `badge(icon, x, y, r, hue)`, `card`, `pill`, `packet`,
  `progress_bar`, `poster(…)`.
- Blueprint: `serif(text, x, y, style)` (`*word*` = italic in signal), `bp_header(kicker, title)`, `node(label, cx,
  cy, w, a, state, sub, p)` (states idle/active/result/error; outline draws on with `p`), `edge(…, p, signal)`,
  `particle`, `bp_pill(text, cx, cy, a, state, caret)`, `fail_tag(word, cx, cy)`, `chrome(series, label, t,
  t_end)`, `end_card(lt, line_a, line_b, question)`.

## Scene recipes (Living Infographic, patterns that worked)

- **Tangle → hub:** N×M curved red connectors appear, counter "4 × 5 = 20 integrations", then collapse into one hub
  with N+M blue spokes and flowing dots. Great "why this exists" opener.
- **Host → Client → Server:** big host card with an LLM badge + client pills; server cards on the right; `packet()`
  chips labelled `request` / `result` shuttle along the connections.
- **Two-column cards:** "SERVER OFFERS" / "CLIENT OFFERS", three badge + name + wrapped description items each, lighting up in sequence.
- **Sequence diagram:** two badges with dashed lifelines; numbered arrows (`line` + `arrow_head`) with monospace
  labels (`tools/list`, `tools/call …`); user question bubble on top, typed answer bubble at the bottom.
- **Lanes:** stacked cards "LOCAL / REMOTE" with a transport pill on the line, a lock badge mid-line, then a consent card with an Allow → Allowed button.
- **Vertical timeline:** dot + date (accent) + badge + title + one-line description, ~0.75 s apart; a "Next on the roadmap" card with 3 chips.
- **Growth bubbles + counter:** circles sized ∝ cube-root of the quantity with a log-interpolated big counter (e.g. parameters).
- **Attention arcs:** words in a row, cubic Bézier arcs between all pairs, one highlighted pair in the accent color.
- **Living-infographic poster** (`mlib.poster`): hub on the left, 6–8 alternating blue/pink category nodes on an arc,
  beams from the hub with a sweeping highlight, connector lines with flowing dots, icon chips with 1–2-line labels,
  slow rotating rays. Build it over ~3.5 s, hold ≥7 s.

## Templates

`templates/living_infographic.py` and `templates/blueprint.py` in this skill's folder are complete, runnable
starting points (both render as-is once Setup is done). Copy the matching one to `work/scenes.py`, keep the
`draw()`/`run()` scaffolding, and replace the scenes, `SCENES` timings, `DUR` and the poster `ROWS` or end card
with the storyboard. The design-system path in `configure()` must match the folder used in Setup, and `HANDLE`
must be the settings' `x_handle`.

## Render

```bash
python scenes.py stills 0 5.5 11 20 28 35 45 56          # review first
python scenes.py video video.mp4                         # ~1 min for 57 s at 4:5 on 2 cores
python music.py 57 "0,6.5,14,22,30,36,46" 46 music.wav   # DUR, scene cuts, poster/end-card start (DUR-1 if none)
ffmpeg -y -i video.mp4 -i music.wav -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k \
  -af "loudnorm=I=-20:TP=-2:LRA=9" -ar 44100 -shortest -movflags +faststart final.mp4
ffmpeg -v error -y -i final.mp4 -vf "select='not(mod(n\,190))',scale=360:-1,tile=3x3" -frames:v 1 -vsync 0 sheet.png
```
QA checklist: H.264 High + yuv420p + AAC, ≤140 s, a few MB; no text overflowing shapes; no stray lines; every
typed line completes; frame 0 is a readable title card; facts match sources; the design system's rules hold.

## Posting to X (Claude in Chrome) — only after the user picks the caption

- Caption: offer 2–3 options via AskUserQuestion: a hook line, one line on what the video covers, end with a
  question (replies drive reach), then the hashtags. Run every option through the x-voice skill first. Every
  factual claim in a caption must be in the video's source list.
- The upload tool only accepts files shared with the session: stage the file first with
  `device_stage_files` (e.g. from `~/Downloads`; request folder access if needed) and upload from
  `/mnt/user-data/uploads/...`.
- If Claude in Chrome isn't connected, stop here: the MP4 and the chosen caption are already delivered, so the user
  can post them by hand or say "post it" again once Chrome is open.
- Open `https://x.com/compose/post` and check the browser is signed in as the settings' `x_handle`; if not, stop
  and report. `find` "file input inside the modal composer dialog" — the page also has a
  timeline composer with its own file input; uploading there attaches to the wrong post.
- **Upload the video first, then click the text box and type.** Typing first once left the upload stuck on
  "Preparing media…"; if that happens for >60 s, close the dialog → Discard → start over.
- Dismiss informational popups (e.g. "Downloadable videos → Got it"), wait for the video preview / "Ready",
  screenshot to verify text + media, click Post.
- Verify on the `x_handle` profile page, report the status URL, close the tab. Mention anything notable (e.g. Premium users
  can download the video; toggle via Edit on the video).
