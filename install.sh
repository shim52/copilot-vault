#!/usr/bin/env bash
# copilot-vault installer entry point. All logic lives in install.py (python3 is required anyway
# for the notifier). Run `./install.sh --help` or `./install.sh --print-questions` (agent-friendly).
set -euo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
command -v python3 >/dev/null 2>&1 || { echo "python3 is required (3.8+)." >&2; exit 2; }
exec python3 -I "$HERE/install.py" "$@"
