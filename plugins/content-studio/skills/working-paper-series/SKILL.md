---
name: working-paper-series
description: "Make a silent Working Paper explainer video series (MCP was the first) on an architecture topic: plan and verify the content, storyboard and render each act frame-exactly, verify the video, post as an X thread."
---

# Working Paper explainer series

Use this when the user asks for a Working Paper video, "like the MCP series", or a new architecture series (RAG, agents, AIOps). For a short explainer with music in Living Infographic or Blueprint Explainers, use explainer-motion-video instead. The output is one or more silent 4:5 videos (1080x1350, H.264, under 140 s each) of animated research-note pages, posted on X as a reply chain.

**Settings:** read `<base>/../../config.json` directly, where `<base>` is the "Base directory for this skill" shown when this skill loaded. It gives the `x_handle` and, under `design_systems`, the Working Paper artifact URL (the entry whose `renderer` is `working-paper-series`).

**Where things live**
- This skill's folder: `scripts/render.py` (frame-exact renderer), `scripts/extract_frames.py`, `scripts/overflow.py`, `scripts/montage.sh`, and `template/` (a one-page `pages.js` and a `storyboard.md` skeleton).
- The plugin's `agents/`: content-planner, content-plan-verifier, video-planner, video-verifier. The plugin's `examples/mcp-series-content-plan.md` shows what a finished plan looks like.
- The design system is the Working Paper artifact. It is never copied into the plugin, so every series renders with its current version.
- The MCP series is the worked example: on the user's Mac, `~/Downloads/mcp-act1` to `mcp-act5` (`source/pages.js`, `source/storyboard.md`); on X, Act I https://x.com/pallaprolu/status/2104998213761617937 with Acts II-V as replies.

## Setup (once per session)

```bash
pip install --break-system-packages -q playwright    # Chromium and ffmpeg are usually present; never run "playwright install" where a browser is preinstalled
```

For each series folder (for example `work/rag-act1/`), copy `template/pages.js` and `template/storyboard.md` in, then fetch the design system into `work/rag-act1/working-paper/`:

1. Artifact `read` on the Working Paper URL with `paths`: `project/tokens.json`, `project/README.md`, `project/components/bundle.css`, `project/components/bundle.js`, and `out_dir` set to a scratch folder.
2. A second `read` with `paths` set to every `"project/" + file` listed in the tokens' `type.fonts[].file`, using the same `out_dir`.
3. Move the contents of `<out_dir>/project/` to `work/rag-act1/working-paper/`, keeping `components/` and `fonts/`.

Read `working-paper/README.md` before planning pages: it holds every layout and motion rule.

## Steps

1. **Scope.** Ask only what changes the build: audience (default: expert enterprise engineers), angle, one video or a series, and any of the user's own material to build on (check their Downloads for related decks).
2. **Plan.** Run the content-planner agent: parallel research from primary sources, then a plan with audience, freshness baseline, stale ideas, running example, page-by-page plan with evidence and claims to check, coverage map and industry references.
3. **Verify the plan independently.** Run the content-plan-verifier agent, which has not seen the research. Apply every finding; re-run until PASS.
4. **Storyboard and build each act.** Run the video-planner agent for one act at a time. It writes `storyboard.md` and `pages.js` (starting with `window.SERIES = { runhead: '2026 Working Note on <Topic>' }`).
5. **Render and self-check** from this skill's `scripts/`:
   ```
   python render.py SERIES pages          # SERIES/out/page-N-frame0.png
   python overflow.py SERIES              # must report 0 issues
   bash montage.sh SERIES                 # contact sheet
   python render.py SERIES busy           # middle of every step
   python render.py SERIES video OUT.mp4
   python extract_frames.py SERIES OUT.mp4 FIRST_FOLIO
   ```
6. **Verify the video independently.** Give the frames, `INDEX.txt`, the video and the storyboard to the video-verifier agent. Fix every finding, including cosmetic ones, re-render, and re-verify until PASS. Record each pass in the storyboard.
7. **Deliver.** Send the MP4. If the user's computer is linked, save to `~/Downloads/<series>-actN/`: the final mp4, a title card (page 1 frame 0), and `source/` with only `pages.js`, `storyboard.md` and a short README. Never copy the design system or scripts into act folders.
8. **Captions and posting.** Draft captions with the x-voice skill; the user picks. Post only with their explicit approval, from Claude in Chrome: act 1 as a new post, each later act as a reply to the previous one, with video plus caption. The X persona is independent of the user's employer: no employer names.

## Rules that verification kept catching

- Senders are never lit. A box lights when the dot lands on it (`light` at about 0.35 beat, `light2` at about 0.8). When the hub sends or acts alone, use `hubNow`: only its verb lights.
- A reply returns through every hop its request took. Dashed means reply or async only. Annotation lines are plain `noArrow`, never dashed, and never carry a pulse.
- Hub verbs appear only when one names the action. They light one at a time, colour only, never bold. Forwarding without a named action gets no verb.
- No ambient cycling in teaching figures. Frame 0 of every page is a finished still.
- Text: US spelling; non-breaking hyphens (U+2011) inside words and dates in dek, caption and body; no text on lines or box edges; decks must not overstate the sources.
- Once a video is posted, never change it; carry fixes into later acts.
- To stop a render, use `kill $(pgrep -f "^python3 render.py")`. Never `pkill -f`, which kills the calling shell.
- To upload a video to X from Chrome, stage it from the user's Mac with device_stage_files and upload from `/mnt/user-data/uploads/...`. Paths under `/mnt/user-data/outputs` are rejected.
