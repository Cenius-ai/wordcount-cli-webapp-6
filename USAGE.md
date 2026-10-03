# Usage — wordcount-cli

Every walkthrough below uses the real command and the files that ship in
`examples/`. Copy-paste from the repository root.

## Count the words in a file

```bash
$ python3 wordcount.py examples/release-notes.txt
203
```

`203` is the only thing on stdout — no headers, no padding — so the output can
be captured or piped directly.

```bash
$ python3 wordcount.py examples/release-notes.txt > count.txt
$ cat count.txt
203
```

## Words are split on any whitespace

Spaces, tabs and newlines all separate words, and runs of whitespace collapse:

```bash
$ printf 'alpha\tbeta\ngamma  delta\n' > /tmp/mixed.txt
$ python3 wordcount.py /tmp/mixed.txt
4
```

## An empty file is a result, not an error

```bash
$ python3 wordcount.py examples/empty.txt
0
$ echo $?
0
```

A file containing only whitespace also counts 0.

## A path that cannot be read

The message names the path and nothing lands on stdout, so a caller that pipes
the output never receives a bogus number:

```bash
$ python3 wordcount.py missing.txt
error: cannot read missing.txt
$ echo $?
1
```

The same exit code 1 covers a directory argument, a permission failure and a
file that is not valid UTF-8 (that last one adds `: file is not valid UTF-8` to
the message).

## Forgetting the path

```bash
$ python3 wordcount.py
usage: wordcount.py [-h] [--version] path
$ echo $?
2
```

Usage errors exit 2, so a shell script can tell "I called it wrong" apart from
"the file could not be read".

## Help and version

```bash
$ python3 wordcount.py --help
usage: wordcount.py [-h] [--version] path
...
$ python3 wordcount.py --version
wordcount.py 1.0.0
```

`--help` prints to stdout and exits 0, so it is safe to pipe into `less`.
`-h` is the same thing.

## Use it inside a script

```bash
#!/usr/bin/env bash
set -euo pipefail

for draft in docs/*.md; do
  words=$(python3 wordcount.py "$draft")
  printf '%s: %s words\n' "$draft" "$words"
done
```

Because the count is a bare integer on stdout and every failure exits non-zero,
`set -e` catches a bad path immediately instead of counting a phantom zero.

## The recorded demo

```bash
$ bash demo.sh
```

Non-interactive and safe to re-run: it counts the bundled samples, shows the
exit-code contract for four representative invocations, and times a generated
10 MB file. It honours `NO_COLOR` and always exits 0.

## Throughput

The plan's budget is 10 MB in under a second; the test suite asserts the same
file size with a 5 s ceiling to stay robust on slow machines. On the build
machine the 10 MB file is counted in roughly 0.4 s.

## What it deliberately does not do

One file per run. No stdin, no directories, no globbing, no aggregation, no
word-frequency or unique-word statistics, no CJK/hyphenation-aware
tokenization, and no encoding auto-detection — the input is UTF-8 text.
