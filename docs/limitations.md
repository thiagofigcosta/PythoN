# Known limitations

These are not bugs Phase 1 forgot to fix - they are places where the scanner
deliberately stops rather than guess. Each one has a reason.

- **Nested inline blocks on one line are rejected.** `if a { if b { c } }` produces a
  diagnostic instead of transpiling. Only one level of inline block is supported per
  line.

- **The source file is the FIRST argument ending in `.py`.** A flag whose own value
  ends in `.py` (`--input=foo.py prog.py`) is taken as the source instead of `prog.py`.
  Put the source file first on the command line. This still holds whenever no literal
  `--` is used; a `--` sidesteps the ambiguity instead of resolving it, because
  everything after it is handed to the interpreter verbatim with no `.py` scan and no
  transpilation at all (`Pytho{N}.py --show-cmd -- --input=foo.py prog.py` runs plain
  `python3 --input=foo.py prog.py`, so `prog.py` had better not use curly braces).

- **Braces inside an f-string replacement field are always treated as string
  content.** Python 3.12 allows nesting the same quote character inside an f-string;
  that form is not scanned for braces.

- **`from ..module import x` is not followed.** Import resolution never walks above
  the entry file's directory, so a parent-relative import will not be collected.

- **An inline block's body cannot be continued with a backslash.** `if a { pass \`
  on one line with `}` on the next is not supported. The header's own condition may
  be continued with a backslash; only the body may not.

- **A regular-Python region must start at block depth zero.** Verbatim lines receive
  no generated indentation, so a region left in plain Python syntax has to begin
  outside any brace block.
