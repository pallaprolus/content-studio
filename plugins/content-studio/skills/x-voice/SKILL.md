---
name: "x-voice"
description: "Voice rules for anything written to post on X through Content Studio: single posts, long posts, threads and video captions. Apply before showing or saving any draft."
---

# X voice

The one place these rules live. The AI News Radar discovery task, post-from-radar and explainer-motion-video all apply them
to every draft before a human sees it. Adapted from the named AI tells in elvisun/newsjack's voice-extractor.

## Who is talking
The `persona` in the plugin's settings file says who is posting and to whom. Read `<base>/../../config.json` directly, where `<base>` is the "Base directory for this skill" shown when this skill loaded; don't search for it.
If it's missing, write as a practitioner talking to peers. Either way: plain, direct, specific.
Lead with the concrete fact. Opinion is first person and labelled ("My take:", "I'd"); facts are stated plainly with their source.

## Hard rules (fix every hit)
- **No hype or consultant words:** game-changer / game-changing, revolutionary / revolutionize, groundbreaking,
  unleash, unlock, supercharge, empower, cutting-edge, next-gen, world-class, best-in-class, seamless / seamlessly,
  robust, comprehensive, leverage / leveraging, delve, paradigm, synergy, disrupt.
- **No stock reframes or openers:** "It's not X, it's Y" / "It's not just X", "In today's … world",
  "now more than ever", "ever-evolving landscape", "Imagine if", "Picture this", "What if I told you".
- **No essay transitions:** never start a sentence with However, Moreover, Furthermore or Additionally.
- **No emoji, no exclamation marks.**

## Soft rules (fix unless there's a reason)
- At most one three-item list per post.
- Don't stack hedges (may, could, might, arguably, possibly): say it plainly or cut it.
- Vary sentence length: mix short sentences with longer ones; don't let every sentence land at 15–22 words.
- Contractions are fine and usually better ("it's", "doesn't").

## Hashtags: the right 2 (never more than 3), never spam
- One *topic* tag naming the exact subject (#MCP, #RAG, #LLM, #AIOps) + one *audience/community* tag for who
  should see it (#AIAgents, #DevOps, #MLOps, #GenAI, #BuildInPublic). Add a third only if it is a genuinely
  distinct, actively used niche (e.g. #ModelContextProtocol alongside #MCP is a synonym — don't).
- CamelCase multi-word tags (#AIAgents, not #aiagents); put them on their own last line, after the question.
- Before using a tag, check it is live and on-topic: search X for it (`https://x.com/search?q=%23Tag&f=live`) or the
  web; drop tags that are dormant, dominated by unrelated content (e.g. #MCP also means other things — pair it with
  a clarifying tag), or trending for unrelated reasons.
- Never: generic filler (#tech #innovation #viral), tag stacks, brand names as tags without context, or the same
  tag set on every post — pick per topic.
- Keep the tag rationale to one short line when presenting options so the user can drop them easily.

## How to apply
Run a quick regex pass in Bash over the final text for the hard-rule words and patterns, fix every hit, then
reread for the soft rules. Report what you changed in one line when showing the draft.

## Later
A measured voice fingerprint from 5–20 of the user's own posts (sentence-length spread, favourite connectives,
punctuation habits) would replace the generic rules above with their actual habits. Build it only when they ask and
provide or approve the sample posts.
