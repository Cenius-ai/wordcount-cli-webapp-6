#!/usr/bin/env python3
"""wordcount-cli — count the words in one text file.

Reads exactly one UTF-8 text file named on the command line, splits its
contents on any run of whitespace, and prints the resulting token count to
stdout as a single integer line. Standard library only, single file.

Usage:
    python wordcount.py <path>

Exit codes:
    0  words counted and printed to stdout
    1  the file could not be read (one-line message on stderr)
    2  wrong command-line usage (usage line on stderr)
"""

from __future__ import annotations

import argparse
import sys
from collections.abc import Sequence

__version__ = "1.0.0"

PROG = "wordcount.py"

EXIT_OK = 0
EXIT_IO = 1
EXIT_USAGE = 2

DESCRIPTION = "Count the words in one text file."

EPILOG = """\
examples:
  python wordcount.py notes.txt      count the words in notes.txt
  python wordcount.py --help         show this message
  python wordcount.py --version      show the version

how words are counted:
  A word is any run of non-whitespace characters, so spaces, tabs and
  newlines all separate words. An empty file counts 0. Input is assumed to
  be UTF-8 text; the whole file is read into memory once, so a file larger
  than available RAM is out of scope.

exit codes:
  0  words counted and printed to stdout
  1  the file could not be read (one-line message on stderr)
  2  wrong command-line usage (usage line on stderr)
"""


def build_parser() -> argparse.ArgumentParser:
    """Return the argument parser for the CLI."""
    parser = argparse.ArgumentParser(
        prog=PROG,
        description=DESCRIPTION,
        epilog=EPILOG,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "path",
        metavar="path",
        help="path to the UTF-8 text file to count (one file only)",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    return parser


def count_words(text: str) -> int:
    """Return the number of whitespace-separated words in ``text``."""
    return len(text.split())


def read_text(path: str) -> str:
    """Read the whole file at ``path`` as UTF-8 text.

    Raises OSError if the file cannot be opened or read, and
    UnicodeDecodeError if it is not valid UTF-8.
    """
    with open(path, "r", encoding="utf-8") as handle:
        return handle.read()


def main(argv: Sequence[str] | None = None) -> int:
    """Run the CLI and return the process exit code."""
    parser = build_parser()
    arguments = list(sys.argv[1:] if argv is None else argv)

    if not arguments:
        # argparse's own error text runs to two lines; the documented contract
        # is a single usage line on stderr followed by exit code 2.
        sys.stderr.write(parser.format_usage())
        return EXIT_USAGE

    args = parser.parse_args(arguments)

    try:
        text = read_text(args.path)
    except UnicodeDecodeError:
        print(f"error: cannot read {args.path}: file is not valid UTF-8", file=sys.stderr)
        return EXIT_IO
    except OSError:
        print(f"error: cannot read {args.path}", file=sys.stderr)
        return EXIT_IO

    print(count_words(text))
    return EXIT_OK


if __name__ == "__main__":
    sys.exit(main())
