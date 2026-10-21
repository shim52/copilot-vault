# Plugging in calendar, chat and tracker

The pass works vault-only out of the box. Connectors make it a co-pilot. Everything is **read-only** and goes through Claude Code's MCP connectors (claude.ai connectors or any MCP server you've added with `claude mcp add`). The pass never writes to any external system.

## 1. Find the exact tool ids
Inside an interactive `claude` session, ask: *"list the tool names you have for calendar, chat and the issue tracker"*, or run `claude mcp list`. Tool ids look like `mcp__<server>__<tool>`. Pick only reads:

| Slot | Typical read tools | Never |
|------|--------------------|-------|
| calendar | list events, get event, search events, list calendars | create/update/delete/respond |
| chat | read channel, read thread, search, read user profile | send, draft, schedule, react, canvas |
| tracker | list cycles, list issues, get issue, list comments, list projects | save/create/update/delete anything |

## 2. Put them in `automation.env`
```
CONNECTOR_TOOLS="mcp__…__list_events mcp__…__read_channel mcp__…__read_thread mcp__…__search mcp__…__list_cycles mcp__…__list_issues"
CONNECTORS_LINE="calendar=yes chat=yes tracker=yes"
```
`CONNECTORS_LINE` is injected into the prompt so the pass knows which steps to skip honestly; the installer derives it from the tool names, but set it yourself if your server names are unusual. Anything not in `CONNECTOR_TOOLS` is refused at runtime — the error shows up in the log as a denial, so check the first run's log after adding tools.

## 3. Fill the matching answers
`CALENDAR_ID`, `TEAM_CHANNEL` (prefer the channel *id* — names get renamed), `CHAT_WORKSPACE_URL`, `CHAT_USER_ID`, `TRACKER_URL_PREFIX`, and your team name as the tracker knows it. These end up in `tick-prompt.md`; edit them there any time.

## Budget rules baked into the prompt (keep them)
Hosted connector calls are slow and dominate wall-clock, and oversized results get spilled to files the no-shell agent cannot read. Hence: one calendar read reused everywhere; at most two chat base calls plus two thread reads; tracker reads paginated at ≤25 and only on the evening side; never per-item fetches. If a new integration needs more, raise the budget deliberately in the prompt rather than letting the agent loop.

## Without connectors
The pass still distills notes, routes 📤 To raise lines, derives action items, refreshes the Dashboard, and writes a brief from the vault alone. Add meetings to the daily note by hand and it will prep them from your people pages.
