---
name: "post-from-radar"
description: "Post to X: a story from the user's AI News Radar Notion database or any AI/tech announcement they ask to share, as a single post, long post or thread, fact-checked first. Use when they say 'post [topic]', 'post to X about ...', 'post the [story] one', 'share/tweet this announcement', or ask what to post."
---

# Post from AI News Radar

## Settings
Read `config.json` at the plugin root (two folders above this skill's base directory: `<base>/../../config.json`) before step 1. It gives `x_handle`, `x_premium`, `timezone` and `radar.notion_data_source`. Values the user gives in the conversation win. If the file can't be read or a value is empty, ask the user once for it. Below, HANDLE means `x_handle` and TZ means `timezone`.

AI News Radar is a Notion database, usually filled by a scheduled discovery task.
- Data source: `radar.notion_data_source` from the settings.
- Key fields: Story, Status (New / Posted / Skipped / Needs check), Verification, Freshness (Fresh (under 24h) / New development / Older context / Clock unconfirmed), Importance, Announced (the first-public date), First Reported By, Official Source, Other Sources, Key Facts, X Post, X Thread, Long Post, Dedupe Key.

Every news or announcement post on X goes through this skill, including announcements that aren't in the Radar yet (step 1 logs them first). Voice and hashtags come from the x-voice skill. Concept explainer videos go through explainer-motion-video instead.

If `x_premium` is true, the account can publish long posts (up to ~25,000 characters; the timeline shows only the first ~280 behind "Show more") and edit a post within about 1 hour of publishing. If it is false, offer only single posts and threads, and treat posts as final once published.

The user asking to post one story is permission to publish that one post, long post or thread. Never post anything else.

Two steps run as separate subagents, each for a reason: the fact-check (step 5) so the text is checked by a worker that didn't write it, and the posting (step 7) so the browser's screenshots and retries stay out of this conversation. Everything else runs here, because it needs the conversation and the user.

## 1. Find the row first (never create a duplicate)
- Query the data source (rows mode) with Story `string_contains` a keyword from the request. Try 1-2 keywords before concluding it's missing.
- If several rows match the same news, use the oldest one as canonical. Mark the others Status "Skipped" and prefix their Story with "DUPLICATE - ". An "Update: " row is a separate development, not a duplicate.
- If the user asks "what should I post", list rows with Status "New", Freshness "Fresh (under 24h)" or "New development" first, sorted by Importance, and recommend one with a one-line reason.
- If no row exists (for example, the user names an announcement the Radar hasn't logged): research it (WebSearch for the product plus the current month and year, including any rebrand; WebFetch the official blog or release notes for the date, each feature and any rollout caveats), then create one row with the full schema, including Freshness, Announced and First Reported By.

## 2. Check it is still news
- Work out the story's age from Announced (and Freshness) against now.
- Search once for the story's core entities to see whether anything newer has happened since the row was logged (a new version, a rollback, an official correction). If so, tell the user and fold the new fact in, or post the newer development instead.
- Over 24 hours old and not a new development: say so. Offer to frame it as a take or context post rather than news, and remove "today", "just", "new" and "announced" from the draft.
- If Freshness is "Clock unconfirmed" or Status is "Needs check", say so and ask before posting.
- If Status is already "Posted", say so and don't post again unless the user confirms.

## 3. Pick the format and draft
- If the user named the format, use it.
- Otherwise recommend one, with a one-line reason:
  - **Single post** for a straightforward release or a number. This is the default.
  - **Long post** when the story is one mechanism, gotcha or limitation plus a practitioner take. It needs more than 280 characters but not a step-by-step. Good for Medium stories with a real angle.
  - **Thread** when the explanation has several distinct steps (what happened, why, how it works, what to do). It is usually High importance.
- Start from the row's draft for that format, or write it if the row lacks one:
  - Single post: 280 characters or fewer (X counts each URL as 23; a quoted post's link doesn't count), with the official link and hashtags per x-voice.
  - Long post: 600-1,500 characters, plain text (no markdown).
    - The first ~250 characters must stand alone as the hook with the key fact.
    - Then 2-4 short paragraphs: what it is, how it works, limits/caveats, and "My take:".
    - End with the official link and hashtags per x-voice.
  - Thread: 3-6 posts numbered 1/ ..., each 280 characters or fewer, the link in the last post, and any opinion marked "My take".
- Count length with Bash.

## 4. Voice pass
Apply the x-voice skill to the draft and fix every hit. This is now the candidate text: the exact words that would go out.

## 5. Independent fact-check (subagent)
Launch one general-purpose Agent that has not seen this conversation. (If this environment can't launch subagents, run the same check here instead: work from only the candidate text and the source URLs, not the row's Key Facts or anything said earlier, and follow the instructions below yourself.) Give it only:
- the candidate text verbatim (every post of a thread),
- the current date and time (TZ),
- the row's Official Source and Other Sources URLs, labelled as leads to start from, not as proof.
Don't pass the row's Key Facts, your reasoning or what you expect it to find; it should reach its own verdict.

Instruct it:
- Read-only. Use only WebSearch and WebFetch. Never post, never edit Notion, never rewrite the text.
- **List the check-worthy claims** in the text: numbers, dates, versions, names and titles, quotes, superlatives ("first", "largest", "only", "fastest") and comparisons. Skip opinion (anything labelled "My take") and plain puffery. Split compound sentences: "X launched Y with a 1M context" is two claims. Finish the list before checking anything.
- **Check each claim on its own.** Its own memory is never evidence.
  - Climb to the primary source: the company post, docs, changelog, model card, filing or paper. A secondary outlet is enough only when no primary exists; an aggregator or listicle never is.
  - Read laterally: if a source's authority is unclear, check who publishes it before trusting it.
  - Count independence honestly: two outlets reprinting the same press release are one source.
  - For a superlative or comparison, find a source that defines the comparison set; without one the claim is Missing source.
  - Words like "today", "just", "new" and "latest" are claims about timing: check them against the current date.
- **Label each claim:** Verified (a source it opened says it; give the URL), Disputed (a credible source contradicts it; give the URL), Unverifiable (it couldn't settle it) or Missing source (the claim needs a citation and none can be found).
- **Return** a table of claim, label, source URL and a one-line note, then one verdict: "Clear" (every claim Verified), "Fix" (some claims need rewording or dropping) or "Stop" (a Disputed claim is the core of the story).

Then, back here:
- **Clear:** go on.
- **Fix:** reword or drop every claim that isn't Verified. Edits may only remove or soften claims. If a fix adds a new factual claim, send just that claim back to a fresh check before using it. Re-run the x-voice pass if the wording changed.
- **Stop:** tell the user what was disputed and by which source, and don't post.

## 6. Show the user and wait
Give the format recommendation, the fact-check table, the final text (with a one-line note of any fact or voice fixes) and what was dropped or changed. Save the final text back to the row (X Post, Long Post or X Thread). Wait for a yes, unless the user already said "post it".

## 7. Post (subagent)
Launch one general-purpose Agent with the final text verbatim, HANDLE, the story's product and company names, and its Announced date. If Claude in Chrome isn't connected, don't launch it: the final text is already saved on the row, so tell the user to open Chrome with the extension and say "post it" again, or to post the text themselves. Instruct it to:
- Read the chrome-browser skill if one is listed (it covers Claude in Chrome's tools, tabs and site permissions).
- Load the Claude in Chrome tools in ONE ToolSearch call: tabs_context_mcp, navigate, computer, read_page, tabs_create_mcp, tabs_close_mcp, browser_batch, find, get_page_text. Call tabs_context_mcp with createIfEmpty and work only in that new tab.

**Single post or long post: quote the official announcement when one exists.**
1. Find it on X: search `x.com/search?q=<product> (from:<company> OR from:<ceo> OR from:<product account>) since:<date>&f=live`, then `"<product>" filter:verified since:<date>&f=top`.
   - Prefer, in order: the product's own account, the company account, the CEO's own announcement post. Never a news aggregator.
   - Check the handle: an account with 0 posts, 0 followers or no verification is a squatter; don't quote or tag it. Use the handle the company itself tags in its post.
   - Open the post, confirm its text matches the announcement, and note its status URL.
2. On the post page: `find` the Repost button in the main post's action bar, click it, `find` the "Quote" menu item, click it, wait ~5s, then screenshot and CONFIRM the composer shows "Add a comment" with the quoted card. If it shows a blank "What's happening?" composer, close it, reload the post and retry once.
3. Click the comment box and type the text exactly (keep a long post's paragraph breaks). Screenshot and confirm the counter isn't negative and the quoted card is present, then click Post once. If the counter goes negative on a long post, Premium long posts aren't active: stop and report.
4. If no official post exists, post it plain via x.com/compose/post with the same checks.

**Thread:** at x.com/compose/post, type post 1, then add each post with the "+" button. Dismiss autocomplete by clicking elsewhere in the text, and never pick a suggestion. Screenshot and check the text and counters, then click "Post all" once.

**Duplicate guard:** never click Post a second time without first confirming on HANDLE's profile page (x.com/<handle without @>) that the first didn't publish.

**Verify:** confirm on HANDLE's profile page (the profile, not search; search indexing lags) that the post (or every thread post, in order) is live, with the quote if one was used. For a long post, open it and check the full text past "Show more".

**Limits:** post only from HANDLE; if the browser is signed in to a different account, stop and report. Don't like, repost, follow, reply or boost. Close every tab it opened. Stop and report on a login wall, a permission prompt, or errors after 2-3 tries.

The subagent returns: the post URLs, the time it was posted, the quoted post's URL and author (if any), and any problems (for example a squatter handle it skipped).

## 8. Close out
- Update the row: Status "Posted". Put the text that actually went out into the matching field.
- Reply briefly with:
  - the posted text or a link to it
  - which account was quoted and why (if any)
  - anything dropped or changed during the fact-check and voice pass
  - if `x_premium` is true, the time the edit window closes (about 1 hour after posting), in case the user wants a wording change
  - Sources (official source, the quoted X post, plus the X post URL)
- Edits (only when `x_premium` is true): if the user asks for a wording fix within the edit window, send any new or changed factual claim through the step 5 check first, then use the post's "..." menu > Edit via the step 7 subagent pattern. Never delete and repost unless the user asks.