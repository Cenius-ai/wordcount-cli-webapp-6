# Design direction — wordcount-cli

The committed direction for this build. Any surface this project renders must
consume these tokens; the tokens themselves are the source of truth and are
mirrored in the `demo.sh` block at the top of `demo.sh`.

| Token | Value |
| --- | --- |
| Archetype | `cli` |
| Surface / mode | terminal dark |
| Type personality | system monospace (the terminal's own face — no web fonts to load, none to fail offline) |
| Density | compact |
| Accent (CSS) | `oklch(0.58 0.12 201)` |
| Accent (hex, non-CSS contexts) | `#008e97` |
| Accent (ANSI, terminal output) | `38;5;30` |
| Muted text | `38;5;245` |
| Separators | box-drawing light horizontals (`─`) |
| Layout | aligned columns; help-first output |

## Rules that follow from it

1. **One accent, one meaning.** The accent marks the primary status or the
   section heading. Nothing else is coloured, and no signal is carried by
   colour alone — every coloured field sits next to a text label
   (`exit 2`, `words`, `error: ...`).
2. **Aligned columns.** Numbers are right-aligned in a fixed-width column so a
   scan down the report is a scan down the values.
3. **Monospace, no chrome.** No banners, no ASCII art, no frames around every
   line; a single box-drawing rule separates sections.
4. **Help first.** `--help` is the entry point of the tool and is written as
   the primary documentation: usage line, argument, examples, exit codes and
   the counting rule.
5. **Machine output stays plain.** Colour and rules are emitted only when
   stdout is a TTY and `NO_COLOR` is unset. Piped output is exactly the
   integer, so the design never contaminates a pipeline.

## Where the tokens appear

| Surface | Tokens applied |
| --- | --- |
| `demo.sh` section headings | accent |
| `demo.sh` separators | muted box-drawing rule |
| `demo.sh` aligned report rows | fixed-width columns |
| `demo.sh` exit-code table | muted `exit N` label, never colour alone |
| `wordcount.py --help` | layout and density (aligned option column, no decoration) |
| `wordcount.py` result | plain integer — design-free by contract |
