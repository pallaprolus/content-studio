# X Content Engine

Claude skills that turn verified AI news and AI concepts into posts on X, written by
[@pallaprolu](https://x.com/pallaprolu). Packaged as a Claude plugin, so the skills and the code they run
live in one versioned place.

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

## Requirements

- **Notion connector** in Claude, with access to a database shaped like the AI News Radar (fields listed at the
  top of `post-from-radar/SKILL.md`). The data source ID in that skill points at the author's workspace and
  only works with his login; replace it with your own.
- **Claude in Chrome** on a computer that's on, with X signed in. Posting happens in your browser; there is
  no X API use here.
- **A design system** for videos, published as a Claude Design System artifact with `project/tokens.json`,
  `project/README.md` and font files. The links in `explainer-motion-video/SKILL.md` are the author's private
  artifacts; point them at your own.
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
- The fact-check subagent is read-only and gets only the text, the date and source URLs as leads.
- The posting subagent only posts from the author's account, never likes, reposts, follows or replies, and
  checks the profile before any retry so a post is never duplicated.

## License

MIT
