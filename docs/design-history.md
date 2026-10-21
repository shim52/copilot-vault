# Design history — what we tried, what we kept

Kept so adopters don't relearn these the slow way.

| When | Tried | What happened | Now |
|------|-------|---------------|-----|
| early | A terminal multiplexer driving an interactive Claude session for automation | Fragile; only existed as an auth workaround | The standalone `claude` CLI authenticates headless from the login keychain (subscription, no API key). Plain scheduler + `claude -p`. |
| early | Lid-open / lid-close hooks to trigger the pass | Closing the lid is ambiguous (closing at 16:00 for a 17:00 meeting) | Time-based schedule with hardware wakes as an optional extra. |
| early | Vault under `~/Documents` | Every CLI auto-update invalidated the per-binary folder consent; headless runs hung 40–80 min on a prompt nobody could click | Vault at home root (`~/Vault`); installer refuses protected folders on macOS. |
| early | Brief led with tracker tickets and SLA fires | Ignored; not what the person opens the laptop for | Priority spine: meetings → my to-dos → team → org signals. Tracker only feeds the team board. |
| mid | One morning run at 08:30 | Laptop asleep in a bag on battery, no Wi-Fi; brief arrived at 10:00 | Evening builds tomorrow's brief; morning refreshes + delivers. Two stamps, several fires per side. |
| mid | Evening message contained the full brief | Never read at night; duplicated the morning one | Evening = short ping; morning = the data. |
| mid | Single "delivered" stamp | Once the evening delivered, the morning skipped, and anything that happened overnight was never digested | One stamp per side. |
| mid | Pass decides when an item is done | Real commitments disappeared on a "looks resolved" guess | Never auto-done, never auto-drop. Only the owner ticks. |
| mid | Bundled related asks into one bullet | Individual asks hidden until overdue | One ask = one checkbox; dedupe the same ask only. |
| mid | "You haven't replied" nudges from channel reads | Wrong twice — the person had replied in-thread; channel reads don't show who replied | Participation guard: thread read required before any nudge framing; dismissal list as backstop. |
| mid | Denylist of write tools for the headless agent | Went stale the day new write-capable connectors appeared on the account | Allowlist-only (`dontAsk` + explicit tools). |
| mid | Weekly "pick 5" triage with a Slack button, a custom URL-scheme app and a calendar event | Three distinct button failure modes (signing, keystroke drop, Launch Services forgetting hidden-folder apps); the ritual itself stopped being used | Retired. Brief lists all open items, hard-dated first. The URL-scheme app survives as an optional re-run button. |
| mid | Tracker `list_issues` with a literal "current" cycle | Silently returned zero issues for 19 days — looked like quiet nights | Resolve the cycle id first; zero issues on a live cycle = failure. |
| mid | Full-cycle tracker read in one page | 166k-char result exceeded the tool-result cap and was dumped to a file the agent couldn't read | Paginate at ≤25. |
| mid | Default chat search settings | 50k-char results spilled to a file | Small limits, newest first, no context; grep the spill file as a fallback. |
| late | Raw markdown digest posted to Slack | `-` bullets don't render in Slack | Format contract in the prompt + a Block Kit formatter in the notifier (and plain renderers for other backends). |
| late | Group meetings got an inline context blurb in the brief | Too thin to prep from | Substantive group meetings get their own seeded note (🧭 Background + 📋 Agenda) with strict exclusions for 1-1 and unapproved items. |
