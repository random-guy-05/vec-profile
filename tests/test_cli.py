import json
import subprocess
import sys


def test_cli_json_roundtrip(tmp_path):
    output = tmp_path / "profile.json"
    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "vec_profile.cli",
            "--repeat",
            "2",
            "--json",
            str(output),
            "--",
            sys.executable,
            "-c",
            "print('profile-me')",
        ],
        capture_output=True,
        text=True,
        check=False,
    )
    assert result.returncode == 0, result.stderr
    payload = json.loads(output.read_text())
    assert payload["summary"]["runs"] == 2
    assert payload["summary"]["all_succeeded"] is True
