# The daily pass — architecture

```
scheduler (launchd / systemd timer / cron)        several fires per side
        │
        ▼
vault-tick.sh ── clock → RUN_MODE + BRIEF_DATE ── workday gate ── stamp check (instant exit if done)
        │
        ├─ network-readiness gate (2 consecutive real HTTPS probes; offline → quiet exit, retry later)
        │
        ├─ Stage 1: claude -p <tick-prompt.md>   --permission-mode dontAsk  --allowedTools <allowlist>
        │             Read/Glob/Grep · Edit scoped to the vault + digest file · listed read-only connector tools
        │             NO Bash · NO Web · NO subagents · NO send/write tools of any kind
        │             → edits the vault, writes the digest file
        │
        ├─ file past-dated notes out of 03-Meetings/00-Today (deterministic shell, not the agent)
        │
        ├─ Stage 2: notify.py <digest>  → slack | discord | webhook | ntfy | desktop | file
        │
        └─ stamp state/<side>-done-<BRIEF_DATE> only if the brief exists AND delivery was confirmed
```

## Two sides, two stamps
- **Evening side** (clock ≥ 12:00; BRIEF_DATE = tomorrow): the full vault pass — distill today, build tomorrow's brief, team board delta — and a *short completion ping*. Nobody reads a long message at night; sending the brief then meant two overlapping messages.
- **Morning side** (clock < 12:00; BRIEF_DATE = today): catch up on anything since last night, refresh the brief and the Dashboard, deliver the *full* brief. Runs every morning whether or not the evening ran; if it didn't, the same jobs build the brief from scratch.
- Each side stamps only itself, so an evening success never suppresses the morning message, and every extra scheduled fire is an instant exit once its side is done. Schedule 2–3 fires per side and delivery becomes near-guaranteed without any retry logic in the scheduler.

## The sandbox, enforced by code
The agent is given an **allowlist** (`--permission-mode dontAsk` refuses anything unlisted). A denylist was used first and went stale the day a new write-capable connector appeared on the account; allowlist-only means new connectors are blocked by default. Writes are path-scoped `Edit(<vault>/**)` plus the digest file. The runner delivers the digest; the destination is fixed in a URL the agent never sees. If the agent is tricked, the worst it can do is write odd text into your own vault.

## Portability
- `bash` (not zsh), BSD/GNU `date` detection, `caffeinate` on macOS / `systemd-inhibit` on Linux, desktop notifications via `osascript` / `notify-send`.
- Schedulers: launchd plist with several `StartCalendarInterval` entries; systemd user timer with `Persistent=true` and `WakeSystem=` set from the `WAKE_MACHINE` answer; cron lines as a fallback (cron can't wake a sleeping machine — the stamps still make late back-fills harmless).
- **Opt-ins, off by default, recommended:** delivery (`NOTIFY_BACKEND`, default `none` — the brief is always in the daily note; a backend additionally pushes the digest to you) and machine wake (`WAKE_MACHINE`, default `no` — Linux: `WakeSystem=true`; macOS: the installer generates `optional/post-run-hook.sh`, a wake chain using `pmset schedule wake` that needs one sudoers line you install yourself). Both can be turned on later by editing `automation.env` / re-running the installer.
- Other macOS extras in `automation/optional/`, never wired automatically: lid-closed battery runs (`pmset -b disablesleep`) and a one-click re-run button for Slack via a custom URL scheme app. Each has a documented failure mode.

## Testing without a model
`vault-tick.sh --dry-run` prints the computed plan; `NOW_OVERRIDE="YYYY-MM-DD HH:MM"` simulates any moment (both sides, weekends, stamped days). `FORCE_RUN=1` ignores the gate and stamps for a manual run. `tests/smoke.sh` runs the installer into a temp dir and exercises all of this plus the notifier renderers.

## Operations
- Logs: `<AUTOMATION_DIR>/logs/<side>-<date>.log` and the raw `stream-json` run in `.jsonl`; `run-summary.py` prints tool counts, duration and cost after each run.
- Watchdog kills a pass after `STAGE1_TIMEOUT` seconds; the EXIT trap guarantees exactly one message per attempt, including a failure alert if the script dies early.
- Tune the prompt in `<AUTOMATION_DIR>/tick-prompt.md`; the installer never overwrites it without `--force`.
- Kill a wrongly-surfaced item permanently by adding its key to the vault's `Automation Dismissals.md`.
