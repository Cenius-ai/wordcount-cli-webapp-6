# Install — wordcount-cli

One package manager: **pip** (`requirements.txt` is the dependency manifest;
the project ships no lockfile-based alternative). Every command below is
copy-pasteable from the repository root.

Nothing here installs system packages, starts a service, or asks a question.
`install.sh` installs, self-checks and **exits**; running the tool is a
separate command.

## 1. Prerequisites

| Requirement | Version | Notes |
| --- | --- | --- |
| Python | 3.8 or newer | Verified on 3.11. `python3 --version` |
| pip | any recent version | `install.sh` upgrades it |
| Network | only for `install.sh` | The tool itself never touches the network |

The word counter imports nothing outside the standard library, so you can skip
straight to step 4 if you only want to try it.

## 2. Install the project dependencies and the console entry point

```bash
bash install.sh
```

This runs, in order: upgrade `pip`/`setuptools`/`wheel` → install
`requirements.txt` (pytest 8.3.3) → `pip install -e .` (adds the `wordcount`
command to PATH) → import self-check. It is idempotent and ends by printing
the commands to run next.

Prefer to do it by hand?

```bash
python3 -m pip install --upgrade pip setuptools wheel
python3 -m pip install -r requirements.txt
python3 -m pip install --no-build-isolation -e .
```

## 3. Verify the setup against the bundled sample data

The project ships its sample input files in `examples/` — there is no database
and no seed step to run. Exercise them end-to-end, non-interactively:

```bash
bash demo.sh
```

The demo counts the three sample files, prints the exit-code contract for the
missing-path / empty-file / no-argument cases, and times a generated 10 MB file.
It always exits 0.

## 4. Run it

```bash
python3 wordcount.py examples/release-notes.txt   # -> 203
```

or, after step 2, via the installed entry point:

```bash
wordcount examples/release-notes.txt
```

Both forms print a single integer line to stdout and exit 0. A file that
cannot be read prints `error: cannot read <path>` to stderr and exits 1; a
malformed command line prints the usage line to stderr and exits 2.

## 5. Run the test suite

```bash
python3 -m pytest
```

17 tests, no network, no fixtures to download, no prompts.

## Troubleshooting

| Symptom | Cause | Fix |
| --- | --- | --- |
| `ModuleNotFoundError: No module named 'pytest'` | Step 2 was skipped | `python3 -m pip install -r requirements.txt` |
| `wordcount: command not found` | The entry point was not installed | `python3 -m pip install --no-build-isolation -e .`, or just use `python3 wordcount.py` |
| `error: cannot read <path>` | The path is missing, a directory, unreadable, or not UTF-8 | Check the path; non-UTF-8 input is out of scope |
| `usage: wordcount.py [-h] [--version] path` | No path given, or more than one | Pass exactly one file path |

## Environment variables

None. `wordcount.py` reads no environment variables and needs no `.env` file;
`.env.example` is committed only so the conventional setup step is a documented
no-op.
