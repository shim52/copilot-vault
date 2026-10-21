#!/usr/bin/env python3
"""Deliver the daily-pass digest to one fixed private destination.

The digest is light Markdown written by the agent under a FORMAT CONTRACT
(line 1 = title, "EMOJI CAPS · subtitle" headings, "- " / "  - " bullets,
"---" before a footer). This script maps that structure onto whichever
backend is configured. Exit 0 ONLY on a confirmed delivery; the runner uses
that to decide whether to stamp the day as delivered or retry later.

Usage: notify.py <digest-file>
Config (env, normally sourced from automation.env by the runner):
  NOTIFY_BACKEND   slack | discord | webhook | ntfy | desktop | file | none
  NOTIFY_URL       webhook URL (slack/discord/webhook) or ntfy topic URL
  NOTIFY_FILE      path for the "file" backend (default: ~/.copilot-vault/inbox.md)
  NOTIFY_TITLE     prefix for desktop notifications (default: Vault)
Secrets: put the webhook URL in a file and set NOTIFY_URL_FILE instead of NOTIFY_URL.
"""
import json, os, re, subprocess, sys, time, urllib.error, urllib.request

MAX_SECTION = 2900   # Slack caps a section at 3000 chars
MAX_BLOCKS = 50
HEADING = re.compile(r"^(\S+)\s+([A-Z][A-Z0-9 &/'-]{2,}?)(?:\s*[·—-]\s*(.*))?$")
TIME_LEAD = re.compile(r"^(\d{1,2}:\d{2})\s+(.*)$")


def read_digest(path):
    with open(path, encoding="utf-8") as f:
        return f.read().strip("\n")


def strip_wikilinks(s):
    return re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), s)


def parse(text):
    """-> (title, [(heading or None, [(depth, body)...])], footer_lines)"""
    lines = text.splitlines()
    title, sections, footer, cur, in_footer = "", [], [], (None, []), False
    for i, raw in enumerate(lines):
        line = raw.rstrip()
        if i == 0 and line and not line.startswith(("-", " ")):
            title = line
            continue
        if line.strip() == "---":
            in_footer = True
            continue
        if in_footer:
            if line.strip():
                footer.append(line.strip().lstrip("- "))
            continue
        if not line.strip():
            continue
        m = HEADING.match(line.strip())
        if m and not line.startswith(("-", "•", " ")):
            if cur[0] is not None or cur[1]:
                sections.append(cur)
            sub = f" · {m.group(3)}" if m.group(3) else ""
            cur = (f"{m.group(1)} {m.group(2)}{sub}", [])
            continue
        depth = (len(line) - len(line.lstrip(" "))) // 2
        body = line.strip()
        body = re.sub(r"^[-•]\s*", "", body)
        body = re.sub(r"^•\s*", "", body)
        cur[1].append((depth, body))
    if cur[0] is not None or cur[1]:
        sections.append(cur)
    return title, sections, footer


# ---------- Slack Block Kit ----------
def slack_inline(s):
    s = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"<\2|\1>", s)
    s = re.sub(r"\*\*(.+?)\*\*", r"*\1*", s)
    return strip_wikilinks(s)


def slack_bullet(depth, body):
    body = slack_inline(body)
    if depth == 0:
        if body.lower().startswith(("also:", "+")):
            return f"_{body}_"
        t = TIME_LEAD.match(body)
        if t:
            ttl, _, rest = t.group(2).partition(" · ")
            rest = re.sub(r"^(agenda\s*→)\s*\d{4}-\d{2}-\d{2}\s+", r"\1 ", rest.strip())
            out = f"•  *{t.group(1)}*  {ttl.strip()}"
            return out + (f"  ·  _{rest}_" if rest else "")
        return f"•  {body}"
    return ("        ◦  " if depth > 1 else "      ◦  ") + body


def chunk(text, limit=MAX_SECTION):
    out, cur = [], ""
    for line in text.splitlines(keepends=True):
        while len(line) > limit:
            if cur:
                out.append(cur); cur = ""
            out.append(line[:limit]); line = line[limit:]
        if len(cur) + len(line) > limit:
            out.append(cur); cur = line
        else:
            cur += line
    if cur:
        out.append(cur)
    return [c.rstrip("\n") for c in out if c.strip()]


def slack_payload(text):
    title, sections, footer = parse(text)
    blocks = []
    if title:
        blocks.append({"type": "header", "text": {"type": "plain_text", "text": strip_wikilinks(title)[:150], "emoji": True}})
    for heading, items in sections:
        if heading:
            blocks.append({"type": "divider"})
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": f"*{slack_inline(heading)}*"}})
        body = "\n".join(slack_bullet(d, b) for d, b in items)
        for c in chunk(body):
            blocks.append({"type": "section", "text": {"type": "mrkdwn", "text": c}})
    if footer:
        blocks.append({"type": "context", "elements": [{"type": "mrkdwn", "text": slack_inline(" · ".join(footer))[:MAX_SECTION]}]})
    blocks = blocks[:MAX_BLOCKS]
    return {"text": strip_wikilinks(title or text.splitlines()[0])[:300], "blocks": blocks}


# ---------- plain renderers ----------
def plain_markdown(text, bold="**"):
    """Markdown that Discord / ntfy / files render well."""
    title, sections, footer = parse(text)
    out = [f"{bold}{strip_wikilinks(title)}{bold}"] if title else []
    for heading, items in sections:
        if heading:
            out.append("")
            out.append(f"{bold}{strip_wikilinks(heading)}{bold}")
        for d, b in items:
            out.append(("  " * d) + "• " + strip_wikilinks(b))
    if footer:
        out.append("")
        out.append("_" + strip_wikilinks(" · ".join(footer)) + "_")
    return "\n".join(out)


def plain_text(text):
    md = plain_markdown(text, bold="")
    md = re.sub(r"\[([^\]]+)\]\((https?://[^)\s]+)\)", r"\1 (\2)", md)
    return re.sub(r"\*\*(.+?)\*\*", r"\1", md)


# ---------- transports ----------
def post_json(url, payload, headers=None, retries=5):
    data = json.dumps(payload).encode("utf-8") if not isinstance(payload, bytes) else payload
    hdrs = {"Content-Type": "application/json"}
    hdrs.update(headers or {})
    for i in range(1, retries + 1):
        try:
            req = urllib.request.Request(url, data=data, headers=hdrs)
            with urllib.request.urlopen(req, timeout=20) as r:
                print(f"delivery HTTP {r.status}")
                return 0
        except urllib.error.HTTPError as e:
            print(f"delivery rejected (not retrying): HTTP {e.code} {e.reason}", file=sys.stderr)
            return 2
        except Exception as e:  # network blips → retry with backoff
            print(f"delivery attempt {i}/{retries} failed: {e!r}", file=sys.stderr)
            if i < retries:
                time.sleep(min(20, 5 * i))
    return 1


def resolve_url():
    url = os.environ.get("NOTIFY_URL", "").strip()
    f = os.environ.get("NOTIFY_URL_FILE", "").strip()
    if not url and f and os.path.exists(f):
        with open(f, encoding="utf-8") as fh:
            url = fh.read().strip()
    return url


def desktop(title, body):
    body = body[:230]
    if sys.platform == "darwin":
        safe = body.replace("\\", "\\\\").replace('"', '\\"')
        st = title.replace('"', "'")
        rc = subprocess.call(["osascript", "-e", f'display notification "{safe}" with title "{st}"'])
        return 0 if rc == 0 else 1
    for cmd in (["notify-send", title, body], ["termux-notification", "-t", title, "-c", body]):
        try:
            if subprocess.call(cmd) == 0:
                return 0
        except FileNotFoundError:
            continue
    print("no desktop notifier found (install libnotify / notify-send)", file=sys.stderr)
    return 1


def main():
    if len(sys.argv) < 2:
        print(__doc__); return 64
    text = read_digest(sys.argv[1])
    backend = os.environ.get("NOTIFY_BACKEND", "file").strip().lower()
    title = text.splitlines()[0] if text else "Vault digest"
    ntitle = os.environ.get("NOTIFY_TITLE", "Vault")

    if backend == "none":
        print("NOTIFY_BACKEND=none — digest left in place"); return 0
    if backend == "file":
        path = os.path.expanduser(os.environ.get("NOTIFY_FILE") or "~/.copilot-vault/inbox.md")
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"\n\n<!-- {time.strftime('%Y-%m-%d %H:%M')} -->\n{plain_markdown(text)}\n")
        print(f"appended digest to {path}")
        return 0
    if backend == "desktop":
        return desktop(f"{ntitle} · {strip_wikilinks(title)}", plain_text(text))

    url = resolve_url()
    if not url:
        print(f"NOTIFY_BACKEND={backend} but no NOTIFY_URL / NOTIFY_URL_FILE configured", file=sys.stderr)
        return 2
    if backend == "slack":
        try:
            payload = slack_payload(text)
        except Exception as e:
            print(f"block-kit build failed ({e!r}); falling back to one plain section", file=sys.stderr)
            payload = {"text": title[:300], "blocks": [{"type": "section", "text": {"type": "mrkdwn", "text": slack_inline(text)[:MAX_SECTION]}}]}
        return post_json(url, payload)
    if backend == "discord":
        body = plain_markdown(text)
        rc = 0
        for i in range(0, len(body), 1900):   # Discord caps content at 2000 chars
            rc = post_json(url, {"content": body[i:i + 1900]})
            if rc:
                break
        return rc
    if backend == "ntfy":
        return post_json(url, plain_text(text).encode("utf-8"),
                         headers={"Content-Type": "text/plain; charset=utf-8", "Title": strip_wikilinks(title)[:200], "Markdown": "yes"})
    if backend == "webhook":
        return post_json(url, {"title": strip_wikilinks(title), "text": plain_text(text), "markdown": plain_markdown(text)})
    print(f"unknown NOTIFY_BACKEND '{backend}'", file=sys.stderr)
    return 64


if __name__ == "__main__":
    sys.exit(main())
