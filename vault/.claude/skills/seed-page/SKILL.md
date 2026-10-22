---
name: seed-page
description: Use when the vault owner asks to seed, fill, bootstrap or populate an empty or thin vault page from connected sources — e.g. "seed the product page", "fill in How We Work from Confluence", "populate Team Overview", "what do we know about <system>, write it up". Reads connected sources read-only, drafts the page with citations, and routes unknowns to Open Questions.
---

# Seed a page from what already exists

The org / product / team / knowledge pages ship as empty section shells. Instead of the owner typing what the org already wrote down somewhere, read it and draft the page.

## Steps

1. **Read the target page** and keep its sections; the shell is the outline. Note what `CLAUDE.md` says about the page's purpose.
2. **Gather, read-only**, in this order: the vault (daily and meeting notes, Log, other pages), then connected sources named in `CLAUDE.md` — wiki/docs search for the page's title and obvious synonyms, the team's chat channel pinned/recent messages, the tracker's project or cycle list, a calendar scan for recurring rituals when the page is about process. Stop at a handful of sources; this is a first draft, not an audit.
3. **Draft into the sections**: short bullets, durable facts only, each with a source — a `[[wikilink]]` for vault sources, a Markdown link for external ones. No narrative paragraphs. Skip anything you couldn't source; never fill a gap with a plausible guess.
4. **Mark freshness**: set `verified:` (and `updated:` where the page has it) to today.
5. **Route what's missing**: each section you could not fill, and each contradiction between sources, becomes one `- [ ]` in `00-Start/Open Questions.md` under the right heading, phrased as a question for a named person when obvious.
6. **Show the diff before writing** when the page already has owner-written content; for an empty shell, write it and summarize what landed and what went to Open Questions. Append one line to `Log.md`.

## Never
- Write to any external source, or send anything.
- Reproduce sensitive raw material (customer data, HR, compensation, private messages) — summarize the fact, link the source.
- Pad: an empty section with an Open Question beats a filled one with invented content.
