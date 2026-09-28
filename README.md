# X Content Engine

Claude skills that turn verified AI news and AI concepts into posts on X. Built by
[@pallaprolu](https://x.com/pallaprolu) for his own account, and set up so anyone can use it by editing one
settings file. Packaged as a Claude plugin, so the skills and the code they run live in one versioned place.

Several of the news-handling ideas (a high-recall first pass, same-story merging, a defended "first public"
clock, claim-by-claim fact-checking, named AI-writing tells) are adapted from
[elvisun/newsjack](https://github.com/elvisun/newsjack).

## How it fits together

```
 Scheduled task (hourly, cloud)        post-from-radar (on request)             explainer-motion-video (on request)
 ─────────────────────────────         ─────────────────────────────            ───────────────────────────────────
 discover → first pass → merge         find row → still news? → draft          research → storyboard → render
 → origin & freshness → verify         → x-voice → independent fact-check       (Cairo + ffmpeg, design-system
 → draft (x-voice) → Notion row          subagent → you approve → post           tokens) → x-voice caption → post
                                          subagent (Claude in Chrome)
                       └──────────────── x-voice: one set of voice and hashtag rules ────────────────┘
```

| Skill | What it does |
|---|---|
| `post-from-radar` | Posts one story to X as a single post, a long post or a thread. Finds or creates the row in the AI News Radar Notion database, checks it's still news, drafts, runs the voice pass, sends the exact text to a fact-check subagent that hasn't seen the conversation, waits for approval, then posts through a browser subagent (quoting the official announcement when there is one). |
| `x-voice` | The single home for voice rules: banned hype words and stock openers, no emoji or exclamation marks, and how to choose 2 hashtags. Every other skill and the hourly task apply it. |
| `explainer-motion-video` | Makes a 45-65 s animated explainer MP4 with a synthesized score. The look comes entirely from a design system's `tokens.json` and fonts; `scripts/mlib.py` holds no design values. Two runnable templates are included. |

The hourly discovery run is a Claude scheduled task, not part of this plugin. It writes rows to the Notion
database; nothing in this repo posts on a schedule.

## Configure

Everything specific to one account lives in `plugins/x-content-engine/config.json`. The skills read it at the
start of every run, and anything you say in the conversation overrides it. If a value is missing, the skill
asks you for it.

| Setting | What it is |
|---|---|
| `x_handle` | The account posts go out from; also drawn on videos. Posting stops if the browser is signed in as someone else. |
| `x_premium` | `true` enables long posts and the 1-hour edit window; `false` limits posts to singles and threads. |
| `timezone` | Used for "is this still news" checks and the fact-checker's current date. |
| `persona` | Who is talking and to whom; x-voice uses it to set the voice. |
| `radar.notion_data_source` | Your AI News Radar database in Notion. |
| `design_systems` | Design System artifacts for videos, with themes and what each suits. |

The committed values are the author's. His Notion ID and artifact links only work with his logins, so they
expose nothing; replace them with your own.

## Requirements

- **Notion connector** in Claude, with access to a database shaped like the AI News Radar (fields listed at the
  top of `post-from-radar/SKILL.md`).
- **Claude in Chrome** on a computer that's on, with X signed in as `x_handle`. Posting happens in your browser;
  there is no X API use here. If Chrome isn't connected, the skills stop with the final text ready to post by hand.
- **A design system** for videos, published as a Claude Design System artifact with `project/tokens.json`,
  `project/README.md` and font files. The templates and `mlib.py` target Living Infographic and Blueprint
  Explainers; another system needs its token names mapped in `ROLES` in `mlib.py`.
- For rendering: Python 3 with `pycairo`, `fonttools`, `brotli`, `numpy`, plus `ffmpeg`.

## Install

In Claude Code:

```
/plugin marketplace add pallaprolus/x-content-engine
/plugin install x-content-engine@x-content-engine
```

## Layout

```
.claude-plugin/marketplace.json
plugins/x-content-engine/
  .claude-plugin/plugin.json
  config.json                account-specific settings (handle, Notion database, design systems)
  skills/
    post-from-radar/SKILL.md
    x-voice/SKILL.md
    explainer-motion-video/
      SKILL.md
      scripts/mlib.py        motion engine: tokens → colours, sizes, type styles; components; frame driver
      scripts/music.py       royalty-free ambient score synthesized with numpy
      templates/             runnable scenes.py starting points for each design system
```

## Safety

- Nothing posts without an explicit yes for that one post.
- The fact-check subagent is read-only and gets only the text, the date and source URLs as leads. Where
  subagents aren't available, the same check runs in the main conversation with the same limited inputs.
- The posting subagent only posts from `x_handle`, never likes, reposts, follows or replies, and
  checks the profile before any retry so a post is never duplicated.

## License

MIT
