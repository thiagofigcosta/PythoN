# Examples

Every file here runs. To try one:

```
./Pytho\{N\}.py examples/<file>.py
```

| File | What it shows |
|---|---|
| `basic.py` | A tour of the syntax, and the original example this project shipped with |
| `data_structures.py` | Dicts, sets, comprehensions - braces used as DATA rather than as blocks |
| `control_flow.py` | `if`/`elif`/`else`, loops, `break`/`continue`, `with`, inline blocks, nesting |
| `functions.py` | Defaults, `*args`/`**kwargs`, closures, decorators, generators, lambdas |
| `classes.py` | Inheritance, properties, `@staticmethod`/`@classmethod`, dunder methods |
| `exceptions.py` | `try`/`except`/`else`/`finally`, custom exceptions, context managers |
| `strings.py` | Braces inside strings and comments, f-strings, multi-line strings |
| `match_statement.py` | `match`/`case` as a statement AND as ordinary variable names |
| `pragmas.py` | The three directives that opt out of brace syntax |
| `pragmas_regular_python.py` | A file marked `Ignore file`, imported by the one above |
| `basic_external_file.py` | A local import, transpiled along with whatever imports it |
| `another_basic_external_file.py` | A local import reached indirectly, two hops from the entry file |
| `basic_external_regularpy_file.py` | Another `Ignore file`, imported from `basic.py` |

## The interesting ones

`strings.py` and `match_statement.py` are worth reading even if you know the syntax,
because they cover the two cases a brace-based pre-compiler finds genuinely hard.

A `}` is only the end of a block when it is really code. Inside a string, inside a
comment, inside a dict or a set, it is just a character - and `strings.py` puts a
closing brace in every one of those positions at once.

`match` and `case` are *soft* keywords: they head a match statement, and they are
also legal variable names. `match_statement.py` uses both readings in the same file,
including `match = {"still": "just a dictionary"}` two lines after a real match
statement with a list pattern.

## Known limitations

`docs/limitations.md` lists what the pre-compiler deliberately refuses rather than
guesses at - nested inline blocks, a backslash-continued inline body, and a verbatim
region opened inside a block, among others. None of them appear in these examples,
because none of them work.
