# BOOTSTRAP.md — agent-guided setup

You are an AI agent (Claude Code or similar) helping someone set up their own copilot-vault. Follow this file; it is the whole procedure.

## 1. Understand what you're installing (30 seconds)
A private Obsidian vault + an optional daily pass. The vault is a structured place for everything a knowledge worker juggles: people and 1-1s, meetings, projects, the org, their own tasks, their team's work, their writing voice. The daily pass is a scheduled, sandboxed Claude session that keeps it alive: it distills what the person typed, files action items where they belong, preps tomorrow's meetings, and delivers a morning brief. `README.md` has the pitch; `docs/practices.md` has the reasoning.

## 2. Collect answers conversationally
Run `./install.sh --print-questions` and read the JSON. Then **talk, don't interrogate**:
- Ask the required ones first (name, role, org, team, manager, product, vault path) in one or two natural questions. Offer the defaults.
- Explain the automation opt-in using the `why` text of the `AUTOMATION` question, in your own words, honestly: it costs model usage every day and needs the machine awake; in return the vault maintains itself and they get a brief every morning. Respect a "no".
- If they say yes to automation, ask about delivery (where do they want the brief: Slack/Discord webhook, ntfy, a desktop notification, or just a file), their workdays, and rough morning/evening times. Everything else can stay default.
- Connector tool ids (`CONNECTOR_TOOLS`) are the fiddly part. If the person already has Claude Code connectors (calendar, chat, tracker), list the exact read-only tool names you can see in your own tool list and propose them; otherwise leave it empty — the pass works vault-only and they can add tools later in `automation.env`.
- On macOS, do not accept a vault path under `~/Documents`, `~/Desktop`, `~/Downloads` or iCloud: headless runs hang on a consent prompt. Suggest `~/Vault`.

## 3. Install
Write the answers to a JSON file (keys exactly as in `--print-questions`; see `copilot.config.example.json`), then:
```
./install.sh --config /path/to/answers.json --yes --json
```
`--yes` makes it non-interactive; `--json` gives you a machine-readable summary on stdout (human log on stderr). Use `--dry-run` first if you want to show the person what will be written. Existing files in the vault are never overwritten without `--force`. Re-running is safe.

## 4. Verify (do this, don't skip it)
- `bash <AUTOMATION_DIR>/vault-tick.sh --dry-run` prints the plan; the installer already ran it once.
- If they opted in, run one pass by hand so they see it work: `FORCE_RUN=1 bash <AUTOMATION_DIR>/vault-tick.sh`. It takes a few minutes. Then open `06-Daily/<date>.md`, `Dashboard.md`, `Log.md`, and the digest (inbox file or their chat).
- Check the scheduler loaded (`launchctl list | grep copilot-vault`, `systemctl --user list-timers`, or `crontab -l`).

## 5. Hand over
Relay the installer's next steps. The three that matter most: open the vault in Obsidian and start from `Index.md`; create the manager's page and one page per teammate (the `Email:` line is what lets the pass match calendar attendees); write today's daily note and try `- raise <topic> with [[Person]]` under 📤 To raise so they see the capture → route flow tomorrow.

## Removing it
`./install.sh --uninstall-schedule` removes the launchd / systemd / cron entry. The vault and `AUTOMATION_DIR` are plain folders; delete them if wanted. Nothing else is touched.
