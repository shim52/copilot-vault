#!/usr/bin/env python3
"""copilot-vault installer — bootstraps a private Obsidian vault with an AI co-pilot.

Designed to be driven by a human OR by an AI agent:
  --print-questions      JSON list of every question (key, prompt, default, choices, why)
  --config FILE          answers as JSON ({"key": value}); unknown keys are ignored
  --set key=value        override a single answer (repeatable); env CV_<KEY> also works
  --yes                  non-interactive: never prompt, use config/env/defaults; fail if a required
                         answer is missing
  --dry-run              show what would be written/installed, touch nothing
  --json                 machine-readable summary on stdout (human text goes to stderr)
  --force                overwrite files that already exist in the vault (default: keep them)
  --uninstall-schedule   remove the launchd/systemd/cron entry and exit
Answer precedence: --set > env CV_* > --config > interactive prompt > default.
"""
import argparse, datetime, json, os, platform, re, shutil, stat, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
VAULT_SRC = os.path.join(HERE, "vault")
AUTO_SRC = os.path.join(HERE, "automation")

QUESTIONS = [
    # key, prompt, default, choices, required, why
    ("USER_NAME", "Your name (as you'd like the co-pilot to address you)", None, None, True,
     "Used in page titles and the daily-pass prompt."),
    ("ROLE", "Your role / job title", "Team Lead", None, True,
     "Frames the vault: the same structure works for engineers, managers, PMs, designers, researchers."),
    ("ORG_NAME", "Organization name", "My Company", None, True, "Page titles only."),
    ("TEAM_NAME", "Your team's name", "My Team", None, True, "Names the 04-My-Team pages and the tracker team lookup."),
    ("MANAGER_NAME", "Your manager's name (a person page will be linked)", "My Manager", None, True,
     "#raise-mgr items are prefixed with this person; their 1-1 prep seeds those items."),
    ("PRODUCT_NAME", "What do you build / the product name", "Our Product", None, True,
     "The vault refers to it by this name consistently."),
    ("NEW_TO_ROLE", "Are you new to this role? (yes = 30-60-90 onboarding track; no = seed the vault from what you already know)", "no", ["yes", "no"], False,
     "Both tracks live in 00-Start/; this only chooses which one the Index, Log and next steps point you to first."),
    ("VAULT_PATH", "Where to create the vault (absolute path; NOT inside Documents/Desktop/iCloud on macOS)",
     os.path.join(os.path.expanduser("~"), "Vault"), None, True,
     "macOS gates Documents/Desktop behind per-binary consent prompts; a headless run cannot click them. Home root is safe."),
    ("DRAFT_LANGUAGE", "Language for drafts written in your voice", "English", None, False, "Used by the as-me skill."),
    ("USER_EMAIL", "Your work email (for calendar attendee matching)", "", None, False, "Local part is matched against person pages."),
    ("CALENDAR_ID", "Calendar id to read (usually your work email)", "", None, False, "Passed to the calendar connector."),
    ("TEAM_CHANNEL", "Your team's chat channel (name or id, e.g. #my-team or C0123)", "", None, False,
     "The one channel the pass reads for org signals and meeting context."),
    ("CHAT_WORKSPACE_URL", "Chat workspace URL for permalinks (e.g. https://acme.slack.com)", "", None, False,
     "Lets every cited message be a clickable link."),
    ("CHAT_USER_ID", "Your chat user id (e.g. U0123)", "", None, False,
     "The participation guard checks whether YOU already replied before nudging you."),
    ("TRACKER_NAME", "Issue tracker name (Linear, Jira, GitHub Issues…)", "the tracker", None, False, "Naming only."),
    ("TRACKER_URL_PREFIX", "Ticket URL prefix so IDs become links (e.g. https://linear.app/acme/issue/)", "", None, False,
     "Tickets are always rendered as clickable links."),
    ("CONNECTORS_LINE", "One line describing your connected read-only sources (for the vault's CLAUDE.md)",
     "Calendar, chat and issue tracker via Claude Code connectors (read-only).", None, False, "Documentation only."),
    # automation
    ("AUTOMATION", "Install the daily pass automation? (yes/no)", "yes", ["yes", "no"], False,
     "The daily pass is what turns the vault into a co-pilot: every evening it distills what you typed, files action items "
     "where they belong, preps tomorrow's meetings from your people pages, and writes a morning brief; every morning it "
     "refreshes and delivers that brief. Without it the vault still works as a well-structured knowledge base you drive by hand."),
    ("AUTOMATION_DIR", "Where to install the automation", os.path.join(os.path.expanduser("~"), ".copilot-vault"), None, False, ""),
    ("WORKDAYS", "Workdays as ISO weekday numbers (1=Mon … 7=Sun)", "1,2,3,4,5", None, False,
     "Briefs are built only for these days (e.g. 7,1,2,3,4 for a Sun–Thu week)."),
    ("MORNING_TIMES", "Morning fire times (comma list, local time)", "06:30,08:00,08:45", None, False,
     "Several fires per side; each is a free instant exit once delivered, so retries are built in."),
    ("EVENING_TIMES", "Evening fire times (comma list, local time)", "18:00,21:00", None, False, "Builds tomorrow's brief the night before."),
    ("MODEL", "Model for the daily pass", "claude-sonnet-5-5", None, False, "Any Claude model id your CLI accepts."),
    ("NOTIFY_BACKEND", "Where to deliver the digest", "file", ["slack", "discord", "webhook", "ntfy", "desktop", "file", "none"], False,
     "slack/discord/webhook/ntfy need a URL; desktop = OS notification; file = append to an inbox markdown file."),
    ("NOTIFY_URL", "Webhook / topic URL for the chosen backend (stored in a chmod-600 file)", "", None, False,
     "Destination is baked into the URL, so the sender cannot redirect it."),
    ("SCHEDULER", "How to schedule it", "auto", ["auto", "launchd", "systemd", "cron", "none"], False,
     "auto = launchd on macOS, systemd user timer on Linux, cron as fallback. none = you run vault-tick.sh yourself."),
    ("CONNECTOR_TOOLS", "Read-only connector tool names the pass may call (space-separated MCP tool ids; empty = vault-only)",
     "", None, False, "Exact tool ids as `claude mcp` / your connector lists them. Nothing outside this list is callable."),
]
KEYS = [q[0] for q in QUESTIONS]


def log(*a):
    print(*a, file=sys.stderr)


def load_config(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    return {k: ("yes" if v is True else "no" if v is False else str(v)) for k, v in data.items() if k in KEYS}


def ask(prompt, default, choices):
    hint = f" [{default}]" if default not in (None, "") else ""
    if choices:
        hint = f" ({'/'.join(choices)})" + hint
    while True:
        try:
            ans = input(f"{prompt}{hint}: ").strip()
        except EOFError:
            ans = ""
        if not ans and default is not None:
            return default
        if choices and ans not in choices:
            log(f"  choose one of: {', '.join(choices)}")
            continue
        if ans or default is not None:
            return ans
        log("  (required)")


def collect(args):
    answers = {}
    cfg = load_config(args.config) if args.config else {}
    overrides = {}
    for s in args.set or []:
        k, _, v = s.partition("=")
        if k not in KEYS:
            sys.exit(f"unknown key in --set: {k}. Valid keys: {', '.join(KEYS)}")
        overrides[k] = v
    interactive = sys.stdin.isatty() and not args.yes
    for key, prompt, default, choices, required, _why in QUESTIONS:
        if key in overrides:
            val = overrides[key]
        elif os.environ.get(f"CV_{key}") is not None:
            val = os.environ[f"CV_{key}"]
        elif key in cfg:
            val = cfg[key]
        elif interactive:
            if key not in ("USER_NAME", "ROLE", "ORG_NAME", "TEAM_NAME", "MANAGER_NAME", "PRODUCT_NAME", "NEW_TO_ROLE", "VAULT_PATH", "AUTOMATION") \
                    and answers.get("AUTOMATION") == "no" and key in AUTOMATION_KEYS:
                val = default or ""
            else:
                if _why and key in ("AUTOMATION", "VAULT_PATH"):
                    log(f"\n  ℹ {_why}")
                val = ask(prompt, default, choices)
        else:
            val = default if default is not None else ""
        if choices and val not in choices:
            sys.exit(f"{key}: '{val}' is not one of {choices}")
        if required and not val:
            sys.exit(f"missing required answer: {key} (pass --set {key}=… or put it in --config)")
        answers[key] = val
    answers["VAULT_PATH"] = os.path.abspath(os.path.expanduser(answers["VAULT_PATH"]))
    answers["AUTOMATION_DIR"] = os.path.abspath(os.path.expanduser(answers["AUTOMATION_DIR"]))
    return answers


AUTOMATION_KEYS = {"AUTOMATION_DIR", "WORKDAYS", "MORNING_TIMES", "EVENING_TIMES", "MODEL", "NOTIFY_BACKEND", "NOTIFY_URL",
                   "SCHEDULER", "CONNECTOR_TOOLS"}


def validate(a):
    errs = []
    if platform.system() == "Darwin":
        low = a["VAULT_PATH"].lower()
        for bad in ("/documents/", "/desktop/", "/downloads/", "mobile documents"):
            if bad in low + "/":
                errs.append(f"VAULT_PATH is under a macOS-protected folder ({bad.strip('/')}); headless runs will hang on a consent prompt. Use e.g. ~/Vault.")
    for k in ("MORNING_TIMES", "EVENING_TIMES"):
        for t in a[k].split(","):
            if not re.fullmatch(r"\d{1,2}:\d{2}", t.strip()):
                errs.append(f"{k}: '{t}' is not HH:MM")
    for d in a["WORKDAYS"].split(","):
        if d.strip() not in list("1234567"):
            errs.append(f"WORKDAYS: '{d}' is not 1..7")
    if a["AUTOMATION"] == "yes" and a["NOTIFY_BACKEND"] in ("slack", "discord", "webhook", "ntfy") and not a["NOTIFY_URL"]:
        errs.append(f"NOTIFY_BACKEND={a['NOTIFY_BACKEND']} needs NOTIFY_URL")
    if errs:
        sys.exit("\n".join("✗ " + e for e in errs))


def placeholders(a):
    today = datetime.date.today().isoformat()
    p = {k: a[k] for k in KEYS}
    p.update({
        "TODAY": today, "HOME": os.path.expanduser("~"),
        "DIGEST_PATH": os.path.join(a["AUTOMATION_DIR"], "last-run-summary.txt"),
        "AUTOMATION_DIR": a["AUTOMATION_DIR"],
        "LAUNCHD_LABEL": "com.copilot-vault.brief",
        "CALENDAR_ID": a["CALENDAR_ID"] or a["USER_EMAIL"] or "primary",
        "TEAM_CHANNEL": a["TEAM_CHANNEL"] or "(team channel not configured)",
        "CHAT_WORKSPACE_URL": a["CHAT_WORKSPACE_URL"].rstrip("/") or "https://<chat-workspace>",
        "CHAT_USER_ID": a["CHAT_USER_ID"] or "(unknown — never claim you replied)",
        "TRACKER_URL_PREFIX": a["TRACKER_URL_PREFIX"] or "https://<tracker>/",
        "USER_EMAIL": a["USER_EMAIL"] or "(email not configured)",
        "START_NEXT": ("work through [[Onboarding Checklist]] and agree the [[30-60-90 Plan]]; create person pages as you meet people; start the daily note."
                       if a["NEW_TO_ROLE"] == "yes" else
                       "work through [[Seed the Vault]] — people pages with today's 📦 Open items first, then commitments into [[My Tasks]]; start the daily note."),
    })
    return p


def subst(text, p):
    def rep(m):
        return p.get(m.group(1), m.group(0))
    return re.sub(r"\{\{([A-Z_]+)\}\}", rep, text)


def copy_vault(a, p, dry, force):
    created, kept = [], []
    for root, dirs, files in os.walk(VAULT_SRC):
        rel = os.path.relpath(root, VAULT_SRC)
        dest_dir = os.path.join(a["VAULT_PATH"], subst(rel, p)) if rel != "." else a["VAULT_PATH"]
        if not dry:
            os.makedirs(dest_dir, exist_ok=True)
        for fn in files:
            src = os.path.join(root, fn)
            dst = os.path.join(dest_dir, ".gitignore" if fn == "gitignore.template" else subst(fn, p))   # the template vault must be committable; the installed vault ignores everything
            if os.path.exists(dst) and not force:
                kept.append(dst); continue
            if not dry:
                with open(src, encoding="utf-8") as f:
                    body = f.read()
                with open(dst, "w", encoding="utf-8") as f:
                    f.write(subst(body, p))
            created.append(dst)
    return created, kept


def write(path, body, dry, mode=None):
    if dry:
        return
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(body)
    if mode is not None:
        os.chmod(path, mode)


def connectors_line(tools):
    t = tools.lower()
    cal = "yes" if "calendar" in t else "no"
    chat = "yes" if any(x in t for x in ("slack", "teams", "discord", "chat")) else "no"
    trk = "yes" if any(x in t for x in ("linear", "jira", "github", "issue", "tracker")) else "no"
    return f"calendar={cal} chat={chat} tracker={trk}"


def install_automation(a, p, dry, force):
    d = a["AUTOMATION_DIR"]
    out = {"dir": d, "files": []}
    for fn in ("vault-tick.sh", "notify.py", "run-summary.py", "tick-prompt.md"):
        src = os.path.join(AUTO_SRC, fn)
        dst = os.path.join(d, fn)
        with open(src, encoding="utf-8") as f:
            body = f.read()
        if fn == "tick-prompt.md":
            body = subst(body, p)
        if os.path.exists(dst) and not force and fn == "tick-prompt.md":
            out.setdefault("kept", []).append(dst)       # the prompt is the one file people tune by hand
        else:
            write(dst, body, dry, 0o755 if fn.endswith((".sh", ".py")) else 0o644)
        out["files"].append(dst)
    if not dry:
        for sub in ("optional", "schedulers"):
            dsub = os.path.join(d, sub)
            if os.path.isdir(dsub):
                shutil.rmtree(dsub)
            shutil.copytree(os.path.join(AUTO_SRC, sub), dsub)
        os.makedirs(os.path.join(d, "state"), exist_ok=True); os.makedirs(os.path.join(d, "logs"), exist_ok=True)
    url_file = os.path.join(d, "notify-url")
    if a["NOTIFY_URL"]:
        write(url_file, a["NOTIFY_URL"].strip() + "\n", dry, 0o600)
    env = f'''# copilot-vault automation config (generated {p["TODAY"]} by install.sh; edit freely, no reload needed)
VAULT_PATH="{a["VAULT_PATH"]}"
CLAUDE_BIN=""
MODEL="{a["MODEL"]}"
WORKDAYS="{a["WORKDAYS"]}"
STAGE1_TIMEOUT="5400"
NETWORK_WAIT="300"
NOTIFY_BACKEND="{a["NOTIFY_BACKEND"]}"
NOTIFY_URL_FILE="{url_file}"
NOTIFY_FILE="{os.path.join(d, "inbox.md")}"
NOTIFY_TITLE="Vault"
DIGEST_PATH="{p["DIGEST_PATH"]}"
CONNECTOR_TOOLS="{a["CONNECTOR_TOOLS"].strip()}"
CONNECTORS_LINE="{connectors_line(a["CONNECTOR_TOOLS"])}"
'''
    write(os.path.join(d, "automation.env"), env, dry, 0o600)
    out["env"] = os.path.join(d, "automation.env")
    return out


def times(a):
    m = [t.strip() for t in a["MORNING_TIMES"].split(",") if t.strip()]
    e = [t.strip() for t in a["EVENING_TIMES"].split(",") if t.strip()]
    return [tuple(int(x) for x in t.split(":")) for t in m + e]


def pick_scheduler(a):
    s = a["SCHEDULER"]
    if s != "auto":
        return s
    if platform.system() == "Darwin":
        return "launchd"
    if shutil.which("systemctl") and subprocess.call(["systemctl", "--user", "status"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL) in (0, 3):
        return "systemd"
    return "cron" if shutil.which("crontab") else "none"


def install_schedule(a, p, dry):
    kind = pick_scheduler(a)
    d = a["AUTOMATION_DIR"]
    info = {"kind": kind}
    if kind == "none":
        return info
    tt = times(a)
    if kind == "launchd":
        intervals = "\n".join(f"        <dict><key>Hour</key><integer>{h}</integer><key>Minute</key><integer>{m}</integer></dict>" for h, m in tt)
        with open(os.path.join(AUTO_SRC, "schedulers", "launchd.plist.template"), encoding="utf-8") as f:
            body = subst(f.read(), dict(p, LAUNCHD_INTERVALS=intervals))
        plist = os.path.join(os.path.expanduser("~/Library/LaunchAgents"), p["LAUNCHD_LABEL"] + ".plist")
        info["file"] = plist
        if not dry:
            write(plist, body, dry)
            uid = os.getuid()
            subprocess.call(["launchctl", "bootout", f"gui/{uid}", plist], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            rc = subprocess.call(["launchctl", "bootstrap", f"gui/{uid}", plist])
            info["loaded"] = rc == 0
    elif kind == "systemd":
        oncal = "\n".join(f"OnCalendar=*-*-* {h:02d}:{m:02d}:00" for h, m in tt)
        udir = os.path.expanduser("~/.config/systemd/user")
        for tpl, name in (("systemd.service.template", "copilot-vault.service"), ("systemd.timer.template", "copilot-vault.timer")):
            with open(os.path.join(AUTO_SRC, "schedulers", tpl), encoding="utf-8") as f:
                write(os.path.join(udir, name), subst(f.read(), dict(p, SYSTEMD_ONCALENDAR=oncal)), dry)
        info["file"] = os.path.join(udir, "copilot-vault.timer")
        if not dry:
            subprocess.call(["systemctl", "--user", "daemon-reload"])
            info["loaded"] = subprocess.call(["systemctl", "--user", "enable", "--now", "copilot-vault.timer"]) == 0
    elif kind == "cron":
        lines = "\n".join(f"{m} {h} * * * /bin/bash {d}/vault-tick.sh >> {d}/logs/cron.out 2>&1" for h, m in tt)
        info["lines"] = lines
        if not dry:
            cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
            cur = "\n".join(l for l in cur.splitlines() if "copilot-vault" not in l and "vault-tick.sh" not in l)
            new = cur.rstrip("\n") + "\n# copilot-vault daily pass\n" + lines + "\n"
            info["loaded"] = subprocess.run(["crontab", "-"], input=new, text=True).returncode == 0
    return info


def uninstall_schedule(a):
    uid = os.getuid()
    plist = os.path.expanduser("~/Library/LaunchAgents/com.copilot-vault.brief.plist")
    if os.path.exists(plist):
        subprocess.call(["launchctl", "bootout", f"gui/{uid}", plist]); os.remove(plist); log("removed", plist)
    udir = os.path.expanduser("~/.config/systemd/user")
    if os.path.exists(os.path.join(udir, "copilot-vault.timer")):
        subprocess.call(["systemctl", "--user", "disable", "--now", "copilot-vault.timer"])
        for n in ("copilot-vault.timer", "copilot-vault.service"):
            os.remove(os.path.join(udir, n))
        log("removed systemd user timer")
    if shutil.which("crontab"):
        cur = subprocess.run(["crontab", "-l"], capture_output=True, text=True).stdout
        new = "\n".join(l for l in cur.splitlines() if "copilot-vault" not in l and "vault-tick.sh" not in l)
        if new != cur.rstrip("\n"):
            subprocess.run(["crontab", "-"], input=new + "\n", text=True); log("removed cron lines")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--print-questions", action="store_true")
    ap.add_argument("--config"); ap.add_argument("--set", action="append")
    ap.add_argument("--yes", action="store_true"); ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--json", action="store_true"); ap.add_argument("--force", action="store_true")
    ap.add_argument("--uninstall-schedule", action="store_true")
    args = ap.parse_args()

    if args.print_questions:
        print(json.dumps([{"key": k, "prompt": pr, "default": d, "choices": c, "required": r, "why": w,
                           "automation_only": k in AUTOMATION_KEYS} for k, pr, d, c, r, w in QUESTIONS], indent=2, ensure_ascii=False))
        return 0
    if args.uninstall_schedule:
        uninstall_schedule({}); return 0

    a = collect(args)
    validate(a)
    p = placeholders(a)
    dry = args.dry_run
    summary = {"dry_run": dry, "vault": a["VAULT_PATH"], "automation": a["AUTOMATION"] == "yes"}

    log(f"\n▶ Vault → {a['VAULT_PATH']}" + (" (dry run)" if dry else ""))
    created, kept = copy_vault(a, p, dry, args.force)
    summary["vault_files_written"] = len(created); summary["vault_files_kept"] = len(kept)
    if kept:
        log(f"  kept {len(kept)} existing file(s) (use --force to overwrite)")
    write(os.path.join(a["VAULT_PATH"], ".copilot-vault.json"),
          json.dumps({k: v for k, v in a.items() if k != "NOTIFY_URL"}, indent=2, ensure_ascii=False) + "\n", dry)
    log(f"  wrote {len(created)} file(s)")

    if a["AUTOMATION"] == "yes":
        log(f"▶ Automation → {a['AUTOMATION_DIR']}")
        summary["automation_install"] = install_automation(a, p, dry, args.force)
        claude = shutil.which("claude")
        summary["claude_cli"] = claude
        if not claude:
            log("  ⚠ `claude` CLI not found on PATH — install Claude Code and log in, or set CLAUDE_BIN in automation.env")
        sched = install_schedule(a, p, dry)
        summary["schedule"] = sched
        log(f"  scheduler: {sched.get('kind')}" + (f" → {sched.get('file')}" if sched.get("file") else "") +
            ("" if sched.get("loaded", True) else "  ⚠ not loaded"))
        if not dry:
            r = subprocess.run(["/bin/bash", os.path.join(a["AUTOMATION_DIR"], "vault-tick.sh"), "--dry-run"], capture_output=True, text=True)
            summary["tick_dry_run_ok"] = r.returncode == 0
            log("  runner self-check: " + ("ok" if r.returncode == 0 else f"FAILED\n{r.stdout}{r.stderr}"))
    next_steps = [
        f"Open {a['VAULT_PATH']} in Obsidian (File → Open folder as vault). Start at Index.md.",
        (f"Open 00-Start/Onboarding Checklist.md and the 30-60-90 Plan; create 02-People/{a['MANAGER_NAME']}.md from 99-Templates/Person.md as a first page."
         if a["NEW_TO_ROLE"] == "yes" else
         f"Open 00-Start/Seed the Vault.md: create 02-People/ pages (manager {a['MANAGER_NAME']} first) with today's 📦 Open items, then dump commitments into My Tasks."),
        "Run `claude` inside the vault — CLAUDE.md teaches it the rules. Try: \"ingest this doc\", \"lint the vault\", \"draft a reply as me\".",
    ]
    if a["AUTOMATION"] == "yes":
        next_steps += [
            f"First pass by hand to see it work: FORCE_RUN=1 bash {a['AUTOMATION_DIR']}/vault-tick.sh   (then check 06-Daily/ and the digest)",
            f"Add read-only connector tool ids to CONNECTOR_TOOLS in {a['AUTOMATION_DIR']}/automation.env to plug in calendar / chat / tracker.",
            f"Tune the prompt at {a['AUTOMATION_DIR']}/tick-prompt.md; add wrongly-surfaced items to the vault's 'Automation Dismissals.md'.",
        ]
    summary["next_steps"] = next_steps
    log("\n✓ Done. Next steps:")
    for i, s in enumerate(next_steps, 1):
        log(f"  {i}. {s}")
    if args.json:
        print(json.dumps(summary, indent=2, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    sys.exit(main())
