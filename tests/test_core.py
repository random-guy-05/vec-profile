import sys

import pytest

from vec_profile.core import profile_command, summarize


def test_profile_success_captures_output_and_memory():
    result = profile_command(
        [
            sys.executable,
            "-c",
            "import time; x=[0]*500000; print('ok'); time.sleep(.08)",
        ],
        interval=0.01,
    )
    assert result["returncode"] == 0
    assert result["wall_seconds"] >= 0.08
    assert result["peak_rss_mb"] > 0
    assert "ok" in result["stdout_tail"]


def test_large_stdout_does_not_deadlock():
    result = profile_command(
        [sys.executable, "-c", "print('x'*200000)"],
        interval=0.005,
    )
    assert result["returncode"] == 0
    assert len(result["stdout_tail"]) <= 16_384


def test_summary():
    summary = summarize(
        [
            {"wall_seconds": 1, "peak_rss_mb": 2, "returncode": 0},
            {"wall_seconds": 3, "peak_rss_mb": 4, "returncode": 0},
        ]
    )
    assert summary["wall_median_s"] == 2
    assert summary["peak_rss_max_mb"] == 4


def test_empty_summary_rejected():
    with pytest.raises(ValueError):
        summarize([])
