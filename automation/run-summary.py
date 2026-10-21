#!/usr/bin/env python3
"""Summarize a stream-json run log: tool-call counts, per-tool latency, duration, cost.
Usage: run-summary.py <run.jsonl>. Purely informational; never affects delivery."""
import json, sys
from collections import Counter, defaultdict

def main(path):
    tools, started, lat = Counter(), {}, defaultdict(list)
    result = None
    with open(path, encoding="utf-8", errors="replace") as f:
        for line in f:
            try:
                ev = json.loads(line)
            except ValueError:
                continue
            if ev.get("type") == "assistant":
                for blk in ev.get("message", {}).get("content", []):
                    if blk.get("type") == "tool_use":
                        tools[blk.get("name", "?")] += 1
                        started[blk.get("id")] = ev.get("timestamp") or 0
            elif ev.get("type") == "result":
                result = ev
    if not tools and not result:
        return
    print("stage1 summary:")
    for name, n in tools.most_common():
        print(f"  {n:3d}× {name}")
    if result:
        d = result.get("duration_ms"); c = result.get("total_cost_usd"); t = result.get("num_turns")
        print(f"  turns={t} duration={round((d or 0)/1000)}s cost=${c:.2f}" if c is not None else f"  turns={t} duration={round((d or 0)/1000)}s")
        if result.get("is_error"):
            print(f"  RESULT ERROR: {str(result.get('result'))[:300]}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        main(sys.argv[1])
