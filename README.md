# Content Studio

Claude skills and agents that turn verified AI news and AI concepts into posts and explainer videos. Built by
[@pallaprolu](https://x.com/pallaprolu) for his own account, and set up so anyone can use it by editing one
settings file. Packaged as a Claude plugin, so the skills, agents and the code they run live in one versioned place.

Several of the news-handling ideas (a high-recall first pass, same-story merging, a defended "first public"
clock, claim-by-claim fact-checking, named AI-writing tells) are adapted from
[elvisun/newsjack](https://github.com/elvisun/newsjack).

## How it fits together

Three kinds of work share one voice:

| Area | What it does | Skills and agents |
|---|---|---|
| News | Verified AI news, posted to X from the AI News Radar | `post-from-radar` |
| Explainers | Concept content researched and fact-checked before anything is built; not tied to one platform (X, YouTube, Medium) | agents `content-planner`, `content-plan-verifier` |
| Video | Explainer videos rendered from design systems, checked frame by frame before posting | `explainer-motion-video`, `working-paper-series`, agents `video-planner`, `video-verifier` |
| Shared | One set of voice and hashtag rules for everything posted on X | `x-voice` |

```
 Scheduled task (hourly, cloud)      post-from-radar (on request)          Explainers and video (on request)
 ─────────────────────────────       ─────────────────────────────         ─────────────────────────────────
 discover → first pass → merge       find row → still news? → draft        content-planner → content-plan-verifier
 → origin & freshness → verify       → x-voice → independent fact-check    → video-planner → render
 → draft (x-voice) → Notion row        subagent → you approve → post       → video-verifier → x-voice caption → post
                                        subagent (Claude in Chrome)
```

### Skills

| Skill | What it does |
|---|---|
| `post-from-radar` | Posts one story to X as a single post, a long post or a thread. Finds or creates the row in the AI News Radar Notion database, checks it's still news, drafts, runs the voice pass, sends the exact text to a fact-check subagent that hasn't seen the conversation, waits for approval, then posts through a browser subagent (quoting the official announcement when there is one). |
| `x-voice` | The single home for voice rules: banned hype words and stock openers, no emoji or exclamation marks, and how to choose 2 hashtags. Every other skill and the hourly task apply it. |
| `explainer-motion-video` | Makes a 45-65 s animated explainer MP4 with a synthesized score, in Living Infographic or Blueprint Explainers. The look comes entirely from a design system's `tokens.json` and fonts; `scripts/mlib.py` holds no design values. Two runnable templates are included. |
| `working-paper-series` | Makes a silent series of Working Paper pages (one animated figure per page, many pages joined into videos under 140 s), as in the MCP architecture series. A deterministic browser renderer draws every frame from the design system's own motion clock; the scripts also extract verification frames and lint the layout. |

### Agents

| Agent | What it does |
|---|---|
| `content-planner` | Researches a topic from primary sources in parallel briefs and writes a sourced plan: audience, freshness baseline, stale ideas, page-by-page plan with evidence and claims to check, coverage map, industry references. |
| `content-plan-verifier` | Checks the plan independently for freshness, coverage, accuracy, series design and industry evidence before anything is built. |
| `video-planner` | Turns a verified plan into a storyboard and `pages.js` for one video, then renders and self-checks it. |
| `video-verifier` | Checks the rendered video independently against the storyboard: fidelity, diagram semantics, legibility, motion and delivery. |

`examples/mcp-series-content-plan.md` is the plan behind the 35-page MCP series, as a reference for what the
content planner produces.

The hourly discovery run is a Claude scheduled task, not part of this plugin. It writes rows to the Notion
database; nothing in this repo posts on a schedule.

## Configure

Everything specific to one account lives in `plugins/content-studio/config.json`. The skills read it at the
start of every run, and anything you say in the conversation overrides it. If a value is missing, the skill
asks you for it.

| Setting | What it is |
|---|---|
| `x_handle` | The account posts go out from; also drawn on videos. Posting stops if the browser is signed in as someone else. |
| `x_premium` | `true` enables long posts and the 1-hour edit window; `false` limits posts to singles and threads. |
| `timezone` | Used for "is this still news" checks and the fact-checker's current date. |
| `persona` | Who is talking and to whom; x-voice uses it to set the voice. |
| `radar.notion_data_source` | Your AI News Radar database in Notion. |
| `design_systems` | Design System artifacts for videos: name, artifact URL, which skill renders it (`renderer`), themes and what each suits. |

The committed values are the author's. His Notion ID and artifact links only work with his logins, so they
expose nothing; replace them with your own.

## Requirements

- **Notion connector** in Claude, with access to a database shaped like the AI News Radar (fields listed at the
  top of `post-from-radar/SKILL.md`). Needed for news only.
- **Claude in Chrome** on a computer that's on, with X signed in as `x_handle`. Posting happens in your browser;
  there is no X API use here. If Chrome isn't connected, the skills stop with the final text ready to post by hand.
- **Design systems** for videos, published as Claude Design System artifacts with `project/tokens.json`,
  `project/README.md` and font files. Nothing from a design system is copied into this repo; each video fetches the
  current version. `explainer-motion-video` targets Living Infographic and Blueprint Explainers (another system
  needs its token names mapped in `ROLES` in `mlib.py`); `working-paper-series` needs Working Paper, whose
  `components/bundle.js` carries the figure builders and the motion clock.
- For `explainer-motion-video`: Python 3 with `pycairo`, `fonttools`, `brotli`, `numpy`, plus `ffmpeg`.
- For `working-paper-series`: Python 3 with `playwright` and a Chromium browser, plus `ffmpeg`.

## Install

In Claude Code:

```
/plugin marketplace add pallaprolus/content-studio
/plugin install content-studio@content-studio
```

## Layout

```
.claude-plugin/marketplace.json
plugins/content-studio/
  .claude-plugin/plugin.json
  config.json                account-specific settings (handle, Notion database, design systems)
  agents/                    content-planner, content-plan-verifier, video-planner, video-verifier
  examples/                  mcp-series-content-plan.md
  skills/
    post-from-radar/SKILL.md
    x-voice/SKILL.md
    explainer-motion-video/
      SKILL.md
      scripts/mlib.py        motion engine: tokens → colours, sizes, type styles; components; frame driver
      scripts/music.py       royalty-free ambient score synthesized with numpy
      templates/             runnable scenes.py starting points for each design system
    working-paper-series/
      SKILL.md
      scripts/render.py      frame-exact renderer: page stills, busiest moments, 30 fps video
      scripts/extract_frames.py, overflow.py, montage.sh   verification frames, layout lint, contact sheet
      template/              a one-page pages.js and a storyboard.md skeleton
```

## Safety

- Nothing posts without an explicit yes for that one post.
- The fact-check subagent is read-only and gets only the text, the date and source URLs as leads. Where
  subagents aren't available, the same check runs in the main conversation with the same limited inputs.
- The posting subagent only posts from `x_handle`, never likes, reposts, follows or replies, and
  checks the profile before any retry so a post is never duplicated.
- The planners and verifiers are separate agents, so no plan or video grades itself.

## License

MIT
