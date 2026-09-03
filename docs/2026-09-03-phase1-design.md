# Pytho{\} Phase 1 - Design

Status: approved 2026-09-03. Scope: harden the pre-compiler. Phase 2 (re-expressing
the language on a formal grammar) is out of scope here and is described only as the
seam Phase 1 must leave behind.

## 1. Baseline

One file, `Pytho{N}.py`, 175 lines, no tests, no runtime dependencies. It strips
`{`/`}` from a brace-flavoured Python source, re-indents with tabs into `.tmp_pythoN/`,
shells out to `python3`, and deletes the temp tree afterwards.

Measured before any change, on the shipped `examples/basic.py` and on ten probe files:
the example runs correctly, and sets, f-strings, single-line nested dicts, `try/except`,
`class` and `while` all pass. Four inputs fail, each with a Python `SyntaxError` in
generated code rather than a diagnostic pointing at the real source:

| Input | Cause |
|---|---|
| `}` inside a `#` comment | nothing tracks comment state |
| braces inside a triple-quoted string | the string-stripping regex cannot match triple quotes |
| nested multi-line dict | `dictionary` is a single boolean, not a nesting depth |
| `lambda: {"k": "v"}` | no rule separates a block brace from a literal brace |

These are structural. Deciding whether a given `}` closes a block requires knowing
whether it sits in code, a string, an f-string replacement field, a comment, or a
nested literal. That is lexical state, and no regex over one line can carry it.

Independent of brace tracking, the same file carries:

- `save_source` calls `.group()` on a possibly-`None` match, so a bare filename crashes.
- The import pattern's character class `[ .*|.*\n|.*\r]` matches a space, dot, star,
  pipe, newline or carriage return, which is unlikely to be what was meant. It misses
  `from x import y`, dotted modules, relative imports and packages.
- `replace_last` reverses the string and calls `replace`, so it is correct only for
  single-character needles.
- `os.system` interpolates an unquoted filename and discards the exit code, so a failing
  program reports success.
- `args.remove(arg)` mutates the list being iterated.
- Temp paths are built by string concatenation, which breaks for absolute inputs and for
  paths containing `..`.
- `.tmp_pythoN` is a fixed name in the working directory, so two concurrent runs
  overwrite each other's generated sources.
- `codecs.open` is deprecated and warns on every single run.

## 2. Goals and non-goals

Goals: correctness on the four failures above and on the classes of input they stand
for; the logic around the regexes rebuilt, not only the patterns; the single file
decomposed into small tested units; a real test suite; the drop-in single-file
distribution preserved.

Non-goals: parsing Python itself (the tool only needs to find block boundaries and hand
the rest to CPython); supporting brace syntax for anything that is not a compound
statement; a formal grammar (that is Phase 2); performance work.

## 3. Architecture

Nine modules under `src/pythonn/`, each with one responsibility, its own tests, and no
knowledge of its callers:

```
scanner.py    lexical state per character; the only module that knows about quoting
braces.py     classifies each brace as block or literal, using scanner output
transpiler.py block structure -> indented Python
pragmas.py    the "# Pytho{\}:" directives
imports.py    local import discovery and resolution to files
paths.py      source path -> temp tree path mapping
runner.py     executes the transpiled tree, propagates the exit code
cli.py        argument parsing and top-level error reporting
errors.py     diagnostics carrying path, line and column
```

Dependency direction is one way: `errors` and `scanner` depend on nothing; `braces`,
`pragmas` and `imports` depend on `scanner`; `transpiler` depends on `braces`; `runner`
depends on `paths`; `cli` depends on everything. No cycles, which is also what makes the
vendored concatenation in section 9 possible.

## 4. The scanner

A character-level state machine over the whole source, carrying state across physical
lines. It emits one record per physical line:

```
LineScan:
  text                 the physical line, unmodified
  code_spans           regions of the line that are real code
  trailing_comment     span of a trailing comment, or none
  bracket_depth_before round/square depth entering the line
  bracket_depth_after  round/square depth leaving the line
  in_string_before     whether the line starts inside a triple-quoted string
  in_string_after      whether it ends inside one
  braces               curly braces found in code, each with its column
  logical_line_start   index of the physical line this logical line began on
```

States: code, single-quoted string, double-quoted string, triple-single, triple-double,
comment. Transitions honour backslash escapes, raw-string prefixes (where a backslash
does not escape the quote), and byte/format prefixes in any case and order.

f-strings are treated as strings in their entirety. A `{` inside an f-string is never a
brace event, which is correct for every case the tool cares about: a replacement field
containing a dict literal is still inside the string as far as block structure goes.

A logical line is the run of physical lines joined by a trailing backslash or by a
non-zero round/square bracket depth. Tracking `logical_line_start` is what lets the
block rule in section 5 read the head keyword of a header that wraps across lines.

## 5. The block-brace rule

Stated explicitly, because the current heuristic is the source of two of the four
failures. Braces are tracked on a stack, each entry tagged block or literal, so nesting
is handled by construction and `}` simply pops the top.

A `{` is a **block** open when all of these hold:

1. round/square bracket depth at that column is zero;
2. the brace stack contains no literal entry (anything nested inside a dict or set is
   itself part of that literal);
3. it is the last significant token on the logical line, where a trailing comment does
   not count as significant;
4. the first token of the logical line is a compound-statement keyword: `if`, `elif`,
   `else`, `for`, `while`, `def`, `class`, `try`, `except`, `finally`, `with`, `match`,
   `case`, or `async` followed by one of `def`, `for`, `with`.

Otherwise it is a **literal**.

One extra form, because the current tool supports it and `examples/basic.py` uses it:
an **inline block**, where a logical line whose head is a compound keyword contains a
`{ ... }` pair that opens and closes on that same logical line with nothing but an
optional comment after the `}`. The body between the braces becomes an indented line
beneath the header.

This rule alone resolves two of the four failures: `lambda: {"k": "v"}` fails clause 4,
and a nested multi-line dict fails clause 2. The scanner resolves the other two.

## 6. Transpiler

Consumes `LineScan` records plus the brace classification and emits Python. For each
line it removes block braces, replaces a block-opening `{` with `:`, and prefixes the
line with the current block depth of indentation.

Indentation is **four spaces**, not the tab the current version emits. Generated tabs
mixed with the user's own spaces inside a regular-Python region is a latent `TabError`
today; a fixture demonstrating it is written before this change is made.

Comment-only lines are emitted with their indentation, so that the generated file is
readable when `--print-output` is passed. A genuinely blank line is emitted empty rather
than as a run of spaces.

Line numbers are preserved one-for-one between source and generated file, so a traceback
from CPython points at the right source line. The transpiler never inserts or removes a
physical line. Inline blocks are the single exception, and they are rewritten as a
header line plus a body line, which shifts everything below by one; the position map
records this so diagnostics stay accurate.

## 7. Pragmas and imports

**Pragmas.** Three directives, all case-insensitive and whitespace-tolerant, recognised
only in a comment that the scanner has confirmed is a comment:

- `# Pytho{\}: Ignore file` returns the source byte-for-byte unchanged.
- `# Pytho{\}: Start regular Python` and `# Pytho{\}: End regular Python` bracket a
  region emitted verbatim, with no brace processing and no added indentation.

One compiled pattern with a named group for the verb replaces the three separate
`re.match` calls that currently re-run on every line. Because a verbatim region receives
no indentation, starting one at a non-zero block depth cannot work; today that breaks
silently, and it becomes a diagnostic.

**Imports.** The current `remove_string_contents` is deleted outright; import discovery
reads the scanner's code-only spans, so a module name mentioned inside a string is never
picked up. Discovery handles `import a`, `import a, b`, `import a as b`,
`from a.b import c`, relative `from .x import y`, and parenthesised multi-line import
lists. Resolution maps a module to `x.py` or to `x/__init__.py`, relative to the
importing file's directory, matching what the tool does today. A module is followed
only when that resolution finds an existing file; anything unresolved is assumed to be
an installed package and left to CPython. Resolution never walks upward, so a source
file cannot pull in modules from outside the tree it was invoked on.

The recursive walk becomes an iterative worklist over a visited set. The current
implementation both mutates a shared set and returns nested concatenations, so it
revisits files and can return duplicates; a worklist is cycle-safe and returns each file
once.

## 8. Paths, execution, CLI, errors

**Paths.** All inputs are resolved to absolute paths, a common root is computed across
every file that will be transpiled, and the temp tree mirrors each file's path relative
to that root. This is what makes absolute inputs and `..` components work, and it keeps
sibling imports resolving because the mirrored layout preserves directory structure.

The temp tree is created with `tempfile.mkdtemp` rather than a fixed `.tmp_pythoN` in the
working directory. Two concurrent runs no longer overwrite each other, and nothing is
left in the project tree. `--keep-temp` preserves it and prints its location, which is
the debugging affordance the fixed name accidentally provided.

**Execution.** `subprocess.run` with an argument list and no shell, replacing
`os.system` with an interpolated string. The child's exit code becomes the tool's exit
code, so a failing program is reported as failing. The temp tree is removed in a
`finally`, as it is today.

**CLI.** `argparse`, preserving every existing flag and its meaning: `-v`/`--version`
for the interpreter version suffix, `--show-cmd`, `--print-output`, `-h`. One flag is
added, `--keep-temp` from earlier in this section; nothing is removed or renamed.
Arguments after the source file are passed through to the program unchanged. Invoked
with no
source file it drops into an interactive interpreter, as it does now.

**Errors.** A single exception type carrying path, line, column and message, rendered
with the offending source line and a caret. Unbalanced braces, a `}` with no opener, and
a verbatim region opened at depth are all reported this way, against the real source
position, and exit with status 2. The distinction that matters: a Pytho{\} error is the
tool's fault to report clearly; a Python error in the user's program is passed through
untouched.

## 9. Vendoring

`scripts/build_vendor.py` concatenates the modules in dependency order into the root
`Pytho{N}.py`: it strips intra-package imports, hoists and de-duplicates the standard
library imports, and writes a header marking the file generated. The root file stays the
whole product, so the README's promise - drop one file into your project, no
dependencies - is preserved exactly.

`tests/test_vendor_drift.py` rebuilds into a temporary location and fails if the result
differs from the checked-in file, so a change made in `src/` without rebuilding cannot
merge. This is the same sources-plus-vendorable-copy-bound-by-a-drift-test arrangement
already used elsewhere for shell code.

## 10. Testing

pytest, as a development dependency only; the runtime keeps zero dependencies and the
README says so explicitly.

The order matters. **The first test written pins the current output of
`examples/basic.py` byte-for-byte**, before any production code is touched. That
characterization test is the safety net for everything that follows: it is what proves
the rewrite did not change behaviour that already worked.

Then, in order:

- unit tests per module, against the interfaces in section 3 rather than internals;
- golden fixtures, each a directory holding `input.py`, the expected transpiled
  `expected.py`, and the expected `expected_stdout.txt`, so both the transformation and
  the execution are asserted;
- one regression fixture for each of the four confirmed failures in section 1;
- error-path tests asserting the diagnostic's path, line and column, not just that
  something was raised;
- the vendor drift test from section 9.

## 11. Compatibility

Every input that works today must keep working; the characterization test enforces it
for the shipped example. Three behaviours change deliberately, each because the current
one is a defect:

1. Generated indentation is four spaces instead of tabs, removing the `TabError` latent
   in mixing generated tabs with a user's spaces.
2. The temp tree moves out of the project directory into a per-run temporary directory.
3. The exit code is the program's, where it was previously always zero.

## 12. The seam Phase 2 needs

The scanner in section 4 is a hand-written lexer, and the brace stack in section 5 is a
hand-written parser for a one-production grammar. Phase 2 replaces both with the generic
formal-language modules, so the interfaces above are drawn where that substitution is
possible: `scanner` and `braces` are the only modules that know the syntax, and
`transpiler` consumes their output rather than the source text. Replacing them is then a
change behind an interface rather than a rewrite.

The golden fixture corpus from section 10 is what proves the replacement is faithful, so
it is written to be reusable against a second implementation from the start.
