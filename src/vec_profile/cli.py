from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import profile_command, summarize


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Profile local VEC scoring commands.")
    parser.add_argument("--repeat", type=int, default=1)
    parser.add_argument("--interval", type=float, default=0.05)
    parser.add_argument("--json", type=Path, dest="json_path")
    parser.add_argument("command", nargs=argparse.REMAINDER)
    args = parser.parse_args(argv)

    command = args.command[1:] if args.command and args.command[0] == "--" else args.command
    if not command:
        raise SystemExit("provide a command after --")
    if args.repeat < 1:
        raise SystemExit("--repeat must be >= 1")
    if args.interval <= 0:
        raise SystemExit("--interval must be > 0")

    rows = [
        profile_command(command, interval=args.interval)
        for _ in range(args.repeat)
    ]
    result = {"summary": summarize(rows), "runs": rows}
    print(json.dumps(result["summary"], indent=2))

    if args.json_path:
        args.json_path.parent.mkdir(parents=True, exist_ok=True)
        args.json_path.write_text(
            json.dumps(result, indent=2) + "\n",
            encoding="utf-8",
        )

    return 0 if result["summary"]["all_succeeded"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
