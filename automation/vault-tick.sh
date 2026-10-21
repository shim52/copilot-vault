#!/usr/bin/env bash
# copilot-vault daily pass runner. Usage: vault-tick.sh [--dry-run] [--force]
#
# Stage 1: a headless, allowlist-only `claude -p` session does the vault pass (distill → route →
#          prep tomorrow's meetings → morning brief → Dashboard) and writes a digest file.
# Stage 2: this script delivers the digest via notify.py to ONE fixed destination (the agent itself
#          has no outbound channel — delivery is enforced by code, not by prompt).
#
# DELIVERY MODEL ("evening = the work + a ping, morning = the data"):
#   BRIEF_DATE is derived from the clock: before noon → today (morning side) else tomorrow (evening
#   side). Each side has its own stamp in state/, so an evening success never suppresses the morning
#   message, and a missed evening pass just means the morning pass builds the brief from scratch.
#   Every scheduled fire is cheap when its side is already done (instant exit, no network, no model).
#   Schedule several fires per side; the stamps make retries free and delivery near-guaranteed.
#
# Config: automation.env next to this script (written by install.sh). Test helpers:
#   DRY_RUN=1 (or --dry-run) prints the plan, no side effects; NOW_OVERRIDE="YYYY-MM-DD HH:MM"
#   simulates any moment; FORCE_RUN=1 (or --force) ignores the workday gate and existing stamps.
set -u
DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
for a in "$@"; do case "$a" in --dry-run) DRY_RUN=1;; --force) FORCE_RUN=1;; esac; done
DRY_RUN="${DRY_RUN:-0}"; FORCE_RUN="${FORCE_RUN:-0}"

# ---- Config ----
ENV_FILE="$DIR/automation.env"
if [ -f "$ENV_FILE" ]; then set -a; . "$ENV_FILE"; set +a; fi   # exported: notify.py reads NOTIFY_*
VAULT="${VAULT_PATH:?VAULT_PATH not set — run install.sh or write automation.env}"
CLAUDE_BIN="${CLAUDE_BIN:-$(command -v claude || echo "$HOME/.local/bin/claude")}"
MODEL="${MODEL:-claude-sonnet-5-5}"
WORKDAYS="${WORKDAYS:-1,2,3,4,5}"            # ISO weekdays, 1=Mon … 7=Sun
STAGE1_TIMEOUT="${STAGE1_TIMEOUT:-5400}"
NETWORK_WAIT="${NETWORK_WAIT:-300}"
CONNECTOR_TOOLS="${CONNECTOR_TOOLS:-}"       # space-separated read-only MCP tool names allowed in Stage 1
CONNECTORS_LINE="${CONNECTORS_LINE:-calendar=no chat=no tracker=no}"
PROMPT_FILE="$DIR/tick-prompt.md"
SUMMARY_FILE="${DIGEST_PATH:-$DIR/last-run-summary.txt}"
STATE="$DIR/state"; LOGS="$DIR/logs"; mkdir -p "$STATE" "$LOGS"
export PATH="/opt/homebrew/bin:/usr/local/bin:$HOME/.local/bin:/usr/bin:/bin:/usr/sbin:/sbin:$PATH"

# ---- Portable date helpers (BSD/macOS vs GNU) ----
if date -v+1d >/dev/null 2>&1; then
  date_add_days() { date -j -v+"$2"d -f '%Y-%m-%d' "$1" '+%Y-%m-%d'; }
  date_fmt() { date -j -f '%Y-%m-%d' "$1" "+$2"; }          # date_fmt YYYY-MM-DD FORMAT
else
  date_add_days() { date -d "$1 + $2 days" '+%Y-%m-%d'; }
  date_fmt() { date -d "$1" "+$2"; }
fi

# ---- File past-dated meeting notes out of the 00-Today inbox (deterministic; the agent never moves files) ----
file_away() {   # file_away <cutoff YYYY-MM-DD>: notes dated BEFORE the cutoff leave the inbox
  local cutoff="$1" inbox="$VAULT/03-Meetings/00-Today" moved=0 f base d mtype scope dest
  [ -d "$inbox" ] || return 0
  for f in "$inbox"/*.md; do
    [ -e "$f" ] || continue
    base="$(basename "$f")"; d="${base:0:10}"
    [[ "$d" =~ ^[0-9]{4}-[0-9]{2}-[0-9]{2}$ ]] || continue
    [[ "$d" < "$cutoff" ]] || continue          # keep today's / upcoming notes findable in the inbox
    mtype="$(sed -n 's/^meeting-type:[[:space:]]*//p' "$f" | head -1 | tr -d '[:space:]')"
    scope="Group"; [ "$mtype" = "1-1" ] && scope="1-1s"
    dest="$VAULT/03-Meetings/$scope/${d:0:7}/$(date_fmt "$d" '%G-W%V')/$d"; mkdir -p "$dest"
    mv -n "$f" "$dest/" && { echo "00-Today: filed [$scope] $base"; moved=$((moved+1)); }
  done
  echo "00-Today: filed $moved note(s)"
}
# Standalone: vault-tick.sh --file-away [YYYY-MM-DD]  — file notes dated before the cutoff (default: today) and exit
if [ "${1:-}" = "--file-away" ]; then file_away "${2:-$(date +%Y-%m-%d)}"; exit 0; fi

# ---- Clock ----
if [ -n "${NOW_OVERRIDE:-}" ]; then
  TODAY="${NOW_OVERRIDE%% *}"; HHMM="${NOW_OVERRIDE##* }"; HHMM="${HHMM/:/}"
else
  TODAY="$(date +%Y-%m-%d)"; HHMM="$(date +%H%M)"
fi
TOMORROW="$(date_add_days "$TODAY" 1)"
HOUR=$((10#${HHMM:0:2}))
if [ "$HOUR" -lt 12 ]; then BRIEF_DATE="$TODAY"; RUN_MODE="morning"; else BRIEF_DATE="$TOMORROW"; RUN_MODE="evening"; fi
STAMP="$STATE/${RUN_MODE}-done-${BRIEF_DATE}"
LOG="$LOGS/${RUN_MODE}-${TODAY}.log"; RUN_JSONL="$LOGS/${RUN_MODE}-${TODAY}.jsonl"
[ "$DRY_RUN" = 1 ] || exec > >(tee -a "$LOG") 2>&1

# ---- Workday gate (on BRIEF_DATE) ----
DOW="$(date_fmt "$BRIEF_DATE" '%u')"
is_workday() { case ",$WORKDAYS," in *",$DOW,"*) return 0;; *) return 1;; esac; }
if ! is_workday && [ "$FORCE_RUN" != 1 ]; then
  echo "$TODAY $HHMM — BRIEF_DATE=$BRIEF_DATE (ISO dow $DOW) is not a workday ($WORKDAYS); skipping."; exit 0
fi

if [ "$DRY_RUN" = 1 ]; then
  echo "DRY_RUN plan:"
  echo "  NOW=${NOW_OVERRIDE:-live} HHMM=$HHMM  TODAY=$TODAY  BRIEF_DATE=$BRIEF_DATE  RUN_MODE=$RUN_MODE"
  echo "  vault=$VAULT  claude=$CLAUDE_BIN  model=$MODEL  backend=${NOTIFY_BACKEND:-file}"
  echo "  connectors: $CONNECTORS_LINE  (tools: ${CONNECTOR_TOOLS:-none})"
  if [ -f "$STAMP" ] && [ "$FORCE_RUN" != 1 ]; then echo "  scenario: $RUN_MODE side already done for $BRIEF_DATE → would exit instantly";
  elif [ "$RUN_MODE" = morning ]; then echo "  scenario: morning — refresh today's brief, deliver the FULL brief";
  else echo "  scenario: evening — full vault pass, build tomorrow's brief, send a short ping"; fi
  exit 0
fi

# ---- Instant exit when this side is already done ----
if [ -f "$STAMP" ] && [ "$FORCE_RUN" != 1 ]; then
  echo "✓ $RUN_MODE side already done for $BRIEF_DATE — nothing to do."; exit 0
fi

# ---- Delivery helpers ----
DELIVERED=0
deliver() {   # deliver <file> → 0 only on confirmed delivery
  DELIVERED=1
  /usr/bin/env python3 -I "$DIR/notify.py" "$1"; local rc=$?
  echo "deliver rc=$rc @ $(date '+%H:%M:%S')"
  return $rc
}
fail() {      # fail <message> [permanent:0|1]  — record + deliver a failure; never stamps
  echo "✗ FAIL: $1"
  printf '🔒 Vault pass (%s) — FAILED\n- %s\n%s\n---\n- log: %s\n' "$BRIEF_DATE" "$1" \
    "$([ "${2:-0}" = 1 ] && echo '- ⚠️ looks like a config/code issue — a re-run will NOT fix it' || true)" "$LOG" > "$SUMMARY_FILE"
  deliver "$SUMMARY_FILE"
}
on_exit() {
  [ -n "${KEEPAWAKE_PID:-}" ] && kill "$KEEPAWAKE_PID" 2>/dev/null
  if [ "$DELIVERED" = 0 ]; then
    echo "EXIT trap: run ended before delivering — sending failure alert."
    printf '🔒 Vault pass (%s) — run ended unexpectedly before delivery.\n---\n- log: %s\n' "$BRIEF_DATE" "$LOG" > "$SUMMARY_FILE" 2>/dev/null
    deliver "$SUMMARY_FILE"
  fi
}
trap on_exit EXIT; trap 'exit 130' INT; trap 'exit 143' TERM

# ---- Keep the machine awake for the run (best-effort, platform-specific) ----
if command -v caffeinate >/dev/null 2>&1; then caffeinate -s -i -w $$ & KEEPAWAKE_PID=$!;
elif command -v systemd-inhibit >/dev/null 2>&1; then systemd-inhibit --what=idle:sleep --why="copilot-vault pass" sleep "$STAGE1_TIMEOUT" & KEEPAWAKE_PID=$!; fi

echo "===== $RUN_MODE pass @ $(date) (BRIEF_DATE=$BRIEF_DATE) ====="
[ -x "$CLAUDE_BIN" ] || { fail "claude CLI not found at $CLAUDE_BIN" 1; exit 1; }
[ -f "$PROMPT_FILE" ] || { fail "prompt file missing: $PROMPT_FILE" 1; exit 1; }
cd "$VAULT" || { fail "cannot cd to vault $VAULT" 1; exit 1; }
rm -f "$SUMMARY_FILE"

# ---- Network-readiness gate (cold wakes often have no DNS yet; require 2 consecutive real HTTPS hits) ----
wait_for_network() {
  local cap="$1" step=5 waited=0 streak=0 ever=0
  probe() { /usr/bin/env python3 -I - <<'PY' 2>/dev/null
import sys, urllib.request, urllib.error
try:
    urllib.request.urlopen("https://api.anthropic.com/", timeout=5)
except urllib.error.HTTPError:
    pass
except Exception:
    sys.exit(1)
PY
  }
  while [ "$waited" -lt "$cap" ]; do
    if probe; then ever=1; streak=$((streak+1)); [ "$streak" -ge 2 ] && { echo "network ready after ${waited}s"; return 0; }
    else streak=0; fi
    sleep "$step"; waited=$((waited+step))
  done
  [ "$ever" = 0 ] && return 2 || return 1
}
wait_for_network "$NETWORK_WAIT"; NET=$?
if [ "$NET" = 2 ]; then
  echo "offline this window — cannot run or deliver; exiting quietly (a later fire retries)."; DELIVERED=1; exit 0
fi
[ "$NET" = 1 ] && echo "WARN: network flaky — proceeding anyway"

# ---- Stage 1: the vault pass ----
PROMPT="RUN_MODE: ${RUN_MODE}
TODAY: ${TODAY}
BRIEF_DATE: ${BRIEF_DATE}
CONNECTORS: ${CONNECTORS_LINE}

$(cat "$PROMPT_FILE")"

# Allowlist-only: dontAsk refuses every tool not listed, so connectors added later are blocked by
# default. Writes are path-scoped to the vault + the digest file (Edit rules cover Write).
# --setting-sources user keeps the vault's interactive .claude/settings*.json allows out of this run.
ALLOWED=( "Read" "Glob" "Grep" "ToolSearch" "TaskCreate" "TaskUpdate" "TaskList" "TodoWrite"
          "Edit(//${VAULT#/}/**)" "Edit(//${SUMMARY_FILE#/})" )   # "//" = absolute path in permission rules
for t in $CONNECTOR_TOOLS; do ALLOWED+=("$t"); done
echo "▶ Stage 1: vault pass (allowlist: ${#ALLOWED[@]} tools)…"
: > "$RUN_JSONL"
"$CLAUDE_BIN" -p "$PROMPT" \
  --permission-mode dontAsk --setting-sources user \
  --allowedTools "${ALLOWED[@]}" \
  --disallowedTools "Bash" "WebFetch" "WebSearch" "Task" "Agent" \
  --model "$MODEL" --verbose --output-format stream-json > "$RUN_JSONL" 2>>"$LOG" &
CLAUDE_PID=$!
( sleep "$STAGE1_TIMEOUT"; kill -0 "$CLAUDE_PID" 2>/dev/null && { echo "⏱ watchdog: TIMEOUT after ${STAGE1_TIMEOUT}s — terminating"; kill -TERM "$CLAUDE_PID"; sleep 5; kill -KILL "$CLAUDE_PID" 2>/dev/null; } ) &
WATCHDOG=$!
wait "$CLAUDE_PID"; RC=$?
kill "$WATCHDOG" 2>/dev/null; wait "$WATCHDOG" 2>/dev/null
echo "stage1 exit=$RC @ $(date '+%H:%M:%S')"
/usr/bin/env python3 -I "$DIR/run-summary.py" "$RUN_JSONL" 2>/dev/null || true

# ---- File past-dated meeting notes out of the 00-Today inbox ----
file_away "$BRIEF_DATE"

# ---- Classify + deliver ----
BRIEF_OK=0
if [ ! -f "$SUMMARY_FILE" ]; then
  printf '🔒 Vault pass (%s) — FAILED: no digest produced (stage1 exit %s).\n---\n- log: %s\n' "$BRIEF_DATE" "$RC" "$LOG" > "$SUMMARY_FILE"
elif [ "$RC" -ne 0 ]; then
  printf -- '- ⚠️ stage1 exited non-zero (%s) — the brief above may be incomplete\n' "$RC" >> "$SUMMARY_FILE"
elif grep -q "## ☀️ Morning brief" "$VAULT/06-Daily/${BRIEF_DATE}.md" 2>/dev/null; then
  BRIEF_OK=1
else
  printf -- '- ⚠️ brief heading not found in 06-Daily/%s.md — generation may have failed\n' "$BRIEF_DATE" >> "$SUMMARY_FILE"
fi
deliver "$SUMMARY_FILE"; DRC=$?

if [ "$BRIEF_OK" = 1 ] && [ "$DRC" = 0 ]; then
  : > "$STAMP"; echo "stamped $(basename "$STAMP") — this side is done for $BRIEF_DATE"
else
  echo "NOT stamped (brief_ok=$BRIEF_OK deliver_rc=$DRC) — the next scheduled fire retries"
fi
[ -x "$DIR/optional/post-run-hook.sh" ] && "$DIR/optional/post-run-hook.sh" "$RUN_MODE" "$BRIEF_DATE" "$HHMM" "$BRIEF_OK" || true
echo "------------------------------------------------------------"; cat "$SUMMARY_FILE"; echo "------------------------------------------------------------"
exit "$RC"
