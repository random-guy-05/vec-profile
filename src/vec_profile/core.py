from __future__ import annotations

import statistics
import subprocess
import tempfile
import time
from pathlib import Path

import psutil


def process_tree_rss(process: psutil.Process) -> int:
    total = 0
    try:
        total += process.memory_info().rss
        children = process.children(recursive=True)
    except (psutil.NoSuchProcess, psutil.AccessDenied):
        return total

    for child in children:
        try:
            total += child.memory_info().rss
        except (psutil.NoSuchProcess, psutil.AccessDenied):
            continue
    return total


def _tail(path: Path, max_bytes: int = 16_384) -> str:
    size = path.stat().st_size
    with path.open("rb") as handle:
        if size > max_bytes:
            handle.seek(-max_bytes, 2)
        payload = handle.read()
    return payload.decode("utf-8", errors="replace")


def profile_command(
    command: list[str],
    *,
    interval: float = 0.05,
) -> dict:
    if not command:
        raise ValueError("command must not be empty")
    if interval <= 0:
        raise ValueError("interval must be > 0")

    with tempfile.TemporaryDirectory() as temporary:
        stdout_path = Path(temporary) / "stdout.txt"
        stderr_path = Path(temporary) / "stderr.txt"
        start = time.perf_counter()

        with stdout_path.open("wb") as stdout, stderr_path.open("wb") as stderr:
            process = subprocess.Popen(command, stdout=stdout, stderr=stderr)
            ps_process = psutil.Process(process.pid)
            peak = 0

            while process.poll() is None:
                peak = max(peak, process_tree_rss(ps_process))
                time.sleep(interval)

            peak = max(peak, process_tree_rss(ps_process))
            return_code = process.wait()

        wall = time.perf_counter() - start
        return {
            "command": command,
            "returncode": return_code,
            "wall_seconds": wall,
            "peak_rss_mb": peak / (1024**2),
            "stdout_tail": _tail(stdout_path),
            "stderr_tail": _tail(stderr_path),
        }


def summarize(rows: list[dict]) -> dict:
    if not rows:
        raise ValueError("at least one run is required")
    wall = [float(row["wall_seconds"]) for row in rows]
    memory = [float(row["peak_rss_mb"]) for row in rows]
    return {
        "runs": len(rows),
        "all_succeeded": all(int(row["returncode"]) == 0 for row in rows),
        "wall_median_s": statistics.median(wall),
        "wall_min_s": min(wall),
        "wall_max_s": max(wall),
        "peak_rss_max_mb": max(memory),
        "peak_rss_median_mb": statistics.median(memory),
    }
