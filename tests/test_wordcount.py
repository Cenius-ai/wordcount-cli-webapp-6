"""Tests for the wordcount.py single-file CLI.

Most tests run the real CLI in a subprocess so stdout, stderr and the exit
code are asserted exactly as a shell caller sees them. Two tests import the
module to pin the small in-process API.
"""

from __future__ import annotations

import subprocess
import sys
import time
from pathlib import Path

import wordcount

ROOT = Path(__file__).resolve().parents[1]
CLI = ROOT / "wordcount.py"


def run_cli(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    """Run the CLI with ``args`` and capture stdout/stderr as text."""
    return subprocess.run(
        [sys.executable, str(CLI), *args],
        capture_output=True,
        text=True,
        cwd=str(cwd or ROOT),
        check=False,
    )


def write(path: Path, text: str, encoding: str = "utf-8") -> Path:
    """Write ``text`` to ``path`` and return the path."""
    path.write_text(text, encoding=encoding)
    return path


# --- F1: counting words in a file -------------------------------------------


def test_counts_words_separated_by_spaces(tmp_path: Path) -> None:
    target = write(tmp_path / "sample.txt", "one two three")
    result = run_cli(str(target))
    assert result.returncode == 0
    assert result.stdout == "3\n"
    assert result.stderr == ""


def test_counts_words_separated_by_newlines_and_tabs(tmp_path: Path) -> None:
    target = write(tmp_path / "mixed.txt", "alpha\tbeta\ngamma\r\ndelta\t\tepsilon\n")
    result = run_cli(str(target))
    assert result.returncode == 0
    assert result.stdout == "5\n"


def test_empty_file_prints_zero(tmp_path: Path) -> None:
    target = write(tmp_path / "empty.txt", "")
    result = run_cli(str(target))
    assert result.returncode == 0
    assert result.stdout == "0\n"
    assert result.stderr == ""


def test_whitespace_only_file_prints_zero(tmp_path: Path) -> None:
    target = write(tmp_path / "blank.txt", " \n\t\n   \n")
    result = run_cli(str(target))
    assert result.returncode == 0
    assert result.stdout == "0\n"


def test_utf8_words_are_counted(tmp_path: Path) -> None:
    target = write(tmp_path / "utf8.txt", "café crème 東京 naïve\n")
    result = run_cli(str(target))
    assert result.returncode == 0
    assert result.stdout == "4\n"


def test_success_stdout_is_exactly_one_integer_line(tmp_path: Path) -> None:
    target = write(tmp_path / "two.txt", "hello world")
    result = run_cli(str(target))
    assert result.stdout == "2\n"
    assert result.stdout.count("\n") == 1
    assert result.stdout.strip().isdigit()


def test_counts_a_ten_megabyte_file_quickly(tmp_path: Path) -> None:
    line = "alpha beta gamma delta epsilon zeta eta theta\n"
    target = tmp_path / "big.txt"
    with target.open("w", encoding="utf-8") as handle:
        for _ in range(240_000):
            handle.write(line)
    assert target.stat().st_size > 10 * 1024 * 1024

    started = time.perf_counter()
    result = run_cli(str(target))
    elapsed = time.perf_counter() - started

    assert result.returncode == 0
    assert result.stdout == f"{240_000 * 8}\n"
    assert elapsed < 5.0, f"counting 10 MB took {elapsed:.2f}s"


# --- F1 error path: unreadable input ----------------------------------------


def test_missing_file_reports_error_and_exits_one(tmp_path: Path) -> None:
    result = run_cli("missing.txt", cwd=tmp_path)
    assert result.returncode == 1
    assert result.stderr == "error: cannot read missing.txt\n"
    assert result.stdout == ""


def test_directory_argument_is_reported_as_unreadable(tmp_path: Path) -> None:
    result = run_cli(str(tmp_path))
    assert result.returncode == 1
    assert result.stderr == f"error: cannot read {tmp_path}\n"
    assert result.stdout == ""


def test_non_utf8_file_is_rejected(tmp_path: Path) -> None:
    target = tmp_path / "latin1.txt"
    target.write_bytes("caf\xe9 cr\xe8me\n".encode("latin-1"))
    result = run_cli(str(target))
    assert result.returncode == 1
    assert result.stderr == f"error: cannot read {target}: file is not valid UTF-8\n"
    assert result.stdout == ""


# --- F2: command-line surface -----------------------------------------------


def test_no_arguments_prints_usage_to_stderr_and_exits_two() -> None:
    result = run_cli()
    assert result.returncode == 2
    assert result.stdout == ""
    assert result.stderr == "usage: wordcount.py [-h] [--version] path\n"


def test_help_goes_to_stdout_and_exits_zero() -> None:
    result = run_cli("--help")
    assert result.returncode == 0
    assert result.stderr == ""
    assert result.stdout.startswith("usage: wordcount.py")
    assert "path" in result.stdout
    assert "python wordcount.py notes.txt" in result.stdout


def test_short_help_flag_behaves_like_long_help() -> None:
    assert run_cli("-h").stdout == run_cli("--help").stdout


def test_version_goes_to_stdout_and_exits_zero() -> None:
    result = run_cli("--version")
    assert result.returncode == 0
    assert result.stdout == f"wordcount.py {wordcount.__version__}\n"
    assert result.stderr == ""


def test_two_paths_are_rejected_with_exit_two(tmp_path: Path) -> None:
    first = write(tmp_path / "a.txt", "one")
    second = write(tmp_path / "b.txt", "two")
    result = run_cli(str(first), str(second))
    assert result.returncode == 2
    assert result.stdout == ""
    assert "usage" in result.stderr


# --- in-process API ---------------------------------------------------------


def test_count_words_api() -> None:
    assert wordcount.count_words("") == 0
    assert wordcount.count_words("one two three") == 3
    assert wordcount.count_words("one\ttwo\nthree four") == 4


def test_read_text_api_round_trips_utf8(tmp_path: Path) -> None:
    target = write(tmp_path / "round.txt", "naïve café\n")
    assert wordcount.read_text(str(target)) == "naïve café\n"
